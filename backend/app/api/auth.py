from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..core.deps import authenticate_user, get_current_user, get_db_session, get_user_by_email
from ..core.security import create_access_token, get_password_hash
from ..models.user import User
from ..schemas.auth import Token
from ..schemas.user import UserCreate, UserRead

router = APIRouter()


@router.post("/token", response_model=Token)
def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_session),
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Ongeldige inloggegevens")
    token = create_access_token(user.id)
    return Token(access_token=token)


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db_session)) -> User:
    existing = get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mailadres bestaat al")
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user
