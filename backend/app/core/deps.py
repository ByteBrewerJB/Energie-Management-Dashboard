from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.security import verify_password
from ..db.session import get_db
from ..models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/token")


def get_db_session() -> Generator[Session, None, None]:
    yield from get_db()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_current_user(db: Session = Depends(get_db_session), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kon toegang niet autoriseren",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")  # type: ignore[assignment]
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.get(User, int(user_id))
    if user is None or not user.is_active:
        raise credentials_exception
    return user
