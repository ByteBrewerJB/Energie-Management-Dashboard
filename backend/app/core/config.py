from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    project_name: str = "JouleJournal"
    api_v1_prefix: str = "/api"
    secret_key: str = Field("CHANGEME_SUPER_SECRET_KEY", alias="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expires_minutes: int = Field(60 * 24, alias="ACCESS_TOKEN_EXPIRES_MINUTES")
    database_url: str = Field("sqlite:///./joulejournal.db", alias="DATABASE_URL")
    first_superuser_email: str = Field("admin@joulejournal.local", alias="FIRST_SUPERUSER_EMAIL")
    first_superuser_password: str = Field("ChangeMe123!", alias="FIRST_SUPERUSER_PASSWORD")
    backend_cors_origins: List[str] = Field(default_factory=list)
    debug: bool = Field(False, alias="DEBUG")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
