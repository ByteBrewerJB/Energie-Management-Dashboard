from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List

from pydantic import BaseModel, ConfigDict, Field


def _parse_env_file(path: Path) -> Dict[str, str]:
    """Parse a minimal subset of .env files.

    The project previously relied on ``pydantic-settings`` to read configuration
    from environment variables and an optional ``.env`` file. In offline
    environments this extra dependency was missing, which prevented the
    application from starting. To keep the behaviour familiar we read the file
    ourselves, supporting ``KEY=VALUE`` pairs and ignoring blank lines or
    comments.
    """

    if not path.exists():
        return {}

    values: Dict[str, str] = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _merge_env_vars(env_file_values: Dict[str, str], process_env: Iterable[tuple[str, str]]) -> Dict[str, str]:
    merged = dict(env_file_values)
    for key, value in process_env:
        merged[key] = value
    return merged


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)

    project_name: str = "JouleJournal"
    api_v1_prefix: str = "/api"
    secret_key: str = "CHANGEME_SUPER_SECRET_KEY"
    algorithm: str = "HS256"
    access_token_expires_minutes: int = 60 * 24
    database_url: str = "sqlite:///./joulejournal.db"
    first_superuser_email: str = "admin@joulejournal.local"
    first_superuser_password: str = "ChangeMe123!"
    backend_cors_origins: List[str] = Field(default_factory=list)
    debug: bool = False

    @classmethod
    def load(cls, env_file: str = ".env") -> "Settings":
        backend_dir = Path(__file__).resolve().parent.parent.parent
        env_path = (backend_dir / env_file).resolve()

        env_values = _merge_env_vars(
            _parse_env_file(env_path),
            os.environ.items(),
        )

        data: Dict[str, object] = {}
        field_to_env = {
            "project_name": "PROJECT_NAME",
            "api_v1_prefix": "API_V1_PREFIX",
            "secret_key": "SECRET_KEY",
            "algorithm": "ALGORITHM",
            "access_token_expires_minutes": "ACCESS_TOKEN_EXPIRES_MINUTES",
            "database_url": "DATABASE_URL",
            "first_superuser_email": "FIRST_SUPERUSER_EMAIL",
            "first_superuser_password": "FIRST_SUPERUSER_PASSWORD",
            "backend_cors_origins": "BACKEND_CORS_ORIGINS",
            "debug": "DEBUG",
        }

        for field_name, env_key in field_to_env.items():
            if env_key in env_values:
                data[field_name] = env_values[env_key]

        origins = data.get("backend_cors_origins")
        if isinstance(origins, str):
            data["backend_cors_origins"] = [
                origin.strip()
                for origin in origins.split(",")
                if origin.strip()
            ]

        return cls(**data)


@lru_cache()
def get_settings() -> Settings:
    return Settings.load()


settings = get_settings()
