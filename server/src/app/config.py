from enum import Enum
from functools import lru_cache
from pathlib import Path
from pydantic import HttpUrl, SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT_DIRECTORY: Path = Path(__file__).parent.parent.parent.resolve()
PATH_REGEX_PATTERN = r"^(/[0-9A-Za-z._-]+)+"


class Environment(str, Enum):
    DEVELOPMENT = "DEV"
    PRODUCTION = "PROD"


class Settings(BaseSettings):
    ENVIRONMENT: Environment

    APP_BACKEND_BASE_URL: HttpUrl
    APP_BACKEND_API_PATH: str = Field(pattern=PATH_REGEX_PATTERN)
    APP_BACKEND_ALLOW_CREDENTIALS: bool
    APP_BACKEND_ALLOW_METHODS: str
    APP_BACKEND_ALLOW_HEADERS: str

    APP_FRONTEND_BASE_URL: HttpUrl

    SESSION_TTL: int

    DB_SQLITE_URL: str
    DB_SQLITE_JOURNAL_MODE: str

    AUTH0_DOMAIN: HttpUrl
    AUTH0_JWKS_PATH: str = Field(pattern=PATH_REGEX_PATTERN)
    AUTH0_TOKEN_PATH: str = Field(pattern=PATH_REGEX_PATTERN)
    AUTH0_AUTHORIZE_PATH: str = Field(pattern=PATH_REGEX_PATTERN)
    AUTH0_AUDIENCE: HttpUrl
    AUTH0_ALGORITHM: str
    AUTH0_CLIENT_ID: str
    AUTH0_CLIENT_SECRET: SecretStr
    AUTH0_SCOPE: str
    AUTH0_REDIRECT_PATH: str = Field(pattern=PATH_REGEX_PATTERN)
    AUTH0_LOGOUT_PATH: str = Field(pattern=PATH_REGEX_PATTERN)

    model_config = SettingsConfigDict(
        env_file=f"{BACKEND_ROOT_DIRECTORY}/.env",
        env_file_encoding="utf-8"
    )


settings = Settings()
