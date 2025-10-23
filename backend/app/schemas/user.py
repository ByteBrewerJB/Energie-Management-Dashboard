import re
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None

    _EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not cls._EMAIL_PATTERN.fullmatch(value):
            raise ValueError("Invalid email address format")
        return value


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
