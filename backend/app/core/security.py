import base64
import binascii
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt

from .config import settings

_PASSWORD_ALGORITHM = "pbkdf2_sha256"
_PBKDF2_ITERATIONS = 390_000
_SALT_BYTES = 16


def _pbkdf2(password: str, salt: bytes, iterations: int) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        algorithm, iter_str, b64_salt, b64_hash = hashed_password.split("$", 3)
        iterations = int(iter_str)
    except (ValueError, TypeError):
        return False

    if algorithm != _PASSWORD_ALGORITHM:
        return False

    try:
        salt = base64.b64decode(b64_salt)
        expected_hash = base64.b64decode(b64_hash)
    except (binascii.Error, ValueError):
        return False

    new_hash = _pbkdf2(plain_password, salt, iterations)
    return hmac.compare_digest(new_hash, expected_hash)


def get_password_hash(password: str) -> str:
    salt = secrets.token_bytes(_SALT_BYTES)
    derived = _pbkdf2(password, salt, _PBKDF2_ITERATIONS)
    return "$".join(
        (
            _PASSWORD_ALGORITHM,
            str(_PBKDF2_ITERATIONS),
            base64.b64encode(salt).decode("ascii"),
            base64.b64encode(derived).decode("ascii"),
        )
    )


def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    expires_delta = timedelta(minutes=expires_minutes or settings.access_token_expires_minutes)
    expire = datetime.utcnow() + expires_delta
    to_encode = {"sub": str(subject), "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
