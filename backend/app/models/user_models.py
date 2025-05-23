from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: uuid.UUID
    # For Pydantic V2, use from_attributes = True
    # For Pydantic V1, use orm_mode = True
    class Config:
        from_attributes = True # Changed from orm_mode to from_attributes


class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

# New Token Schemas
class TokenData(BaseModel):
    user_id: Optional[uuid.UUID] = None

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
