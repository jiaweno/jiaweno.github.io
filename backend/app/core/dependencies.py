from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError #, jwt # jwt is not directly used here, but JWTError is
import uuid # Import uuid

from app.core.security import decode_token
from app.services import user_service # This will import the user_service module
from app.db.session import get_db
from app.models.user_models import User as PydanticUser # Pydantic model for response

# The tokenUrl should be the full path to the login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> PydanticUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None: # Check if payload itself is None first
        raise credentials_exception

    user_id_str = payload.get("sub")
    if user_id_str is None: # Then check if "sub" is missing
        raise credentials_exception
    
    try:
        user_id = uuid.UUID(user_id_str) # Convert sub to UUID
    except ValueError:
        raise credentials_exception # Invalid UUID format

    user = user_service.get_user_by_id(db, user_id=user_id) # Use the imported user_service
    if user is None:
        raise credentials_exception
    
    # Ensure your PydanticUser model can be created from the ORM model
    # This requires Config.orm_mode = True (Pydantic V1) or Config.from_attributes = True (Pydantic V2)
    # in your user_models.User Pydantic class.
    return PydanticUser.from_orm(user)

def get_current_active_user(current_user: PydanticUser = Depends(get_current_user)) -> PydanticUser:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

def get_current_active_superuser(current_user: PydanticUser = Depends(get_current_active_user)) -> PydanticUser:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges"
        )
    return current_user
