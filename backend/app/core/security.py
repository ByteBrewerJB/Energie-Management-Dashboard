from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    expires_delta = timedelta(minutes=expires_minutes or settings.access_token_expires_minutes)
    expire = datetime.utcnow() + expires_delta
    to_encode = {"sub": str(subject), "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
