from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.schemas.token import Token

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests.

    This endpoint authenticates a user based on a username and password and
    returns a JWT access token.

    Args:
        form_data: An OAuth2PasswordRequestForm object containing the
                   username and password.

    Returns:
        A Token object containing the access token and token type.

    Raises:
        HTTPException: 401 Unauthorized if the username or password is
                       incorrect.
    """
    # In a real app, you would look up the user in the database and use hashed passwords.
    # For this simple case, we are comparing the plain text admin password from settings.
    is_correct_username = form_data.username == settings.ADMIN_USER
    is_correct_password = form_data.password == settings.ADMIN_PASSWORD

    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": settings.ADMIN_USER}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
