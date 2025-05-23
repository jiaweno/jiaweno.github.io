from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # For login form
from sqlalchemy.orm import Session
from typing import Any
import uuid # ensure uuid is imported

from app.db.session import get_db
from app.models.user_models import User as PydanticUser, UserCreate, Token # Pydantic models
from app.services import user_service # This will import the module
from app.core.security import create_access_token, create_refresh_token
from app.core.dependencies import get_current_active_user
# from app.core.config import settings # settings is not directly used here

router = APIRouter()

@router.post("/register", response_model=PydanticUser, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
    db_user = user_service.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    created_user = user_service.create_user(db=db, user=user_in)
    # Convert SQLAlchemy model to Pydantic model for the response
    # The PydanticUser model should have from_attributes=True in its Config
    return PydanticUser.from_orm(created_user)

@router.post("/login", response_model=Token)
def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    # form_data.username corresponds to the 'username' field in the OAuth2 form, which we use for email
    user = user_service.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id)}) # user.id is UUID, convert to str for JWT
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.get("/me", response_model=PydanticUser)
def read_users_me(current_user: PydanticUser = Depends(get_current_active_user)) -> Any:
    # current_user is already a Pydantic model because get_current_active_user returns a PydanticUser
    return current_user

# Example of a protected route requiring superuser privileges:
# @router.get("/all", response_model=list[PydanticUser])
# def read_all_users(
#     db: Session = Depends(get_db),
#     current_superuser: PydanticUser = Depends(get_current_active_superuser) # Dependency for superuser
# ):
#     users = db.query(UserModel).all() # Example: directly query all, better to have a service function
#     return [PydanticUser.from_orm(user) for user in users]
