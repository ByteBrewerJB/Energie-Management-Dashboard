from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.schemas.token import TokenData

# This will be the URL that clients use to get the token (the login endpoint)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """
    Decode the JWT token to get the current user.
    This will be used as a dependency to protect routes.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        # In a real app with users, you would load the user from the DB here.
        # For this app, the username is sufficient.
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    # Check if the user from the token is the admin user
    if token_data.username != settings.ADMIN_USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have permissions to perform this action"
        )

    return token_data.username
