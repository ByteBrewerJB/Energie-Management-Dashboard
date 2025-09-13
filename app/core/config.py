import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Manages the application settings.

    This class loads configuration variables from environment variables or uses
    default values if they are not set. It centralizes all configuration
    for easy management.

    Attributes:
        ADMIN_USER: The username for the admin user.
        ADMIN_PASSWORD: The password for the admin user.
        SECRET_KEY: The secret key for signing JWTs.
        ALGORITHM: The algorithm used for JWT encoding.
        ACCESS_TOKEN_EXPIRE_MINUTES: The expiry time for access tokens in minutes.
        LOG_LEVEL: The logging level for the application.
    """
    # Application settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "ERROR")

    # Admin credentials
    ADMIN_USER: str = os.getenv("ADMIN_USER", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "secret")

    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "a_very_secret_key_that_should_be_changed")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 1 day

    # CORS settings
    BACKEND_CORS_ORIGINS: list[str] = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:5201,http://127.0.0.1:5201").split(",")


settings = Settings()
