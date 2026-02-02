from enum import Enum
from urllib.parse import urljoin
from pathlib import Path

from pydantic import HttpUrl, SecretStr, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT_DIRECTORY: Path = Path(__file__).parent.parent.parent.parent.resolve()
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

    DB_REDIS_HOST: str
    DB_REDIS_PORT: int
    DB_REDIS_DECODE_RESPONSES: bool
    DB_REDIS_KEY_PREFIX_SESSION: str
    DB_REDIS_KEY_JWKS: str
    DB_REDIS_TTL_JWKS: int

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

    # Composite fields
    AUTH0_TOKEN_URL: str | None = None
    AUTH0_AUTHORIZE_URL: str | None = None
    AUTH0_JWKS_URL: str | None = None
    AUTH0_LOGOUT_URL: str | None = None
    AUTH0_REDIRECT_URI: str | None = None

    model_config = SettingsConfigDict(
        env_file=f"{BACKEND_ROOT_DIRECTORY}/.env",
        env_file_encoding="utf-8"
    )

    @model_validator(mode="after")
    def build_composite_fields(self):
        self.AUTH0_TOKEN_URL = urljoin(self.AUTH0_DOMAIN.encoded_string(), self.AUTH0_TOKEN_PATH)
        self.AUTH0_AUTHORIZE_URL = urljoin(self.AUTH0_DOMAIN.encoded_string(), self.AUTH0_AUTHORIZE_PATH)
        self.AUTH0_JWKS_URL = urljoin(self.AUTH0_DOMAIN.encoded_string(), self.AUTH0_JWKS_PATH)
        self.AUTH0_LOGOUT_URL = urljoin(self.AUTH0_DOMAIN.encoded_string(), self.AUTH0_LOGOUT_PATH)
        self.AUTH0_REDIRECT_URI = urljoin(self.APP_BACKEND_BASE_URL.encoded_string(), f"{self.APP_BACKEND_API_PATH}{self.AUTH0_REDIRECT_PATH}")
        return self


settings = Settings()
