from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    """
    Base user schema with common attributes.
    """
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    """
    Schema for creating a new user (includes password).
    """
    password: str


class UserLogin(BaseModel):
    """
    Schema for user login.
    """
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """
    Schema for updating user information.
    """
    full_name: str | None = None
    email: EmailStr | None = None


class UserInDB(UserBase):
    """
    Schema for user as stored in database (includes hashed password).
    """
    id: int
    hashed_password: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class User(UserBase):
    """
    Schema for user response (excludes password).
    """
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
