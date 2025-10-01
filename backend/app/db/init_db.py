from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.security import get_password_hash
from ..models.user import User
from . import base
from .session import SessionLocal, engine


def init_db() -> None:
    base.Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        if not db.query(User).filter(User.email == settings.first_superuser_email).first():
            super_user = User(
                email=settings.first_superuser_email,
                full_name="Beheerder",
                hashed_password=get_password_hash(settings.first_superuser_password),
                is_active=True,
                is_superuser=True,
            )
            db.add(super_user)
            db.commit()
    finally:
        db.close()
