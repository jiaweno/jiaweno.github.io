from typing import Optional
from sqlalchemy.orm import Session
from app.db.models_sqlalchemy import User as UserModel # SQLAlchemy model
from app.models.user_models import UserCreate, UserUpdate # Pydantic models
from app.core.security import get_password_hash, verify_password
import uuid # Added import for uuid

def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[UserModel]:
    return db.query(UserModel).filter(UserModel.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[UserModel]:
    return db.query(UserModel).filter(UserModel.email == email).first()

def create_user(db: Session, user: UserCreate) -> UserModel:
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_active=user.is_active, # Pydantic model UserCreate has is_active
        is_superuser=user.is_superuser # Pydantic model UserCreate has is_superuser
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[UserModel]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not user.is_active: # Check is_active attribute from SQLAlchemy model
        return None # Or raise an exception for inactive user
    if not verify_password(password, user.hashed_password):
        return None
    return user

# Add update_user if needed later
# def update_user(db: Session, user: UserModel, user_update: UserUpdate) -> UserModel:
#     update_data = user_update.model_dump(exclude_unset=True) # Use model_dump for Pydantic v2
#     if "password" in update_data and update_data["password"]:
#         hashed_password = get_password_hash(update_data["password"])
#         update_data["hashed_password"] = hashed_password
#         del update_data["password"] # Remove plain password
#     else: # Ensure hashed_password is not accidentally set to None if password is not being updated or is empty
#       if "password" in update_data:
#         del update_data["password"]


#     for field, value in update_data.items():
#         setattr(user, field, value)
    
#     db.add(user)
#     db.commit()
#     db.refresh(user)
#     return user
