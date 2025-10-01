from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserRead(UserBase):
    id: int
    is_active: bool
    is_superuser: bool

    model_config = ConfigDict(from_attributes=True)
