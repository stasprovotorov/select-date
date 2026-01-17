from app.config import settings as global_settings
from urllib.parse import urljoin
from pydantic import BaseModel, HttpUrl, SecretStr


class Settings(BaseModel):
    DOMAIN: HttpUrl = global_settings.AUTH0_DOMAIN
    AUDIENCE: HttpUrl = global_settings.AUTH0_AUDIENCE
    CLIENT_ID: str = global_settings.AUTH0_CLIENT_ID
    CLIENT_SECRET: SecretStr = global_settings.AUTH0_CLIENT_SECRET
    SCOPE: str = global_settings.AUTH0_SCOPE
    ALGORITHM: str = global_settings.AUTH0_ALGORITHM
    REDIRECT_URI: HttpUrl = urljoin(DOMAIN.encoded_string(), global_settings.AUTH0_REDIRECT_PATH)
    TOKEN_URL: HttpUrl = urljoin(DOMAIN.encoded_string(), global_settings.AUTH0_TOKEN_PATH)
    AUTHORIZE_URL: HttpUrl = urljoin(DOMAIN.encoded_string(), global_settings.AUTH0_AUTHORIZE_PATH)
    JWKS_URL: HttpUrl = urljoin(DOMAIN.encoded_string(), global_settings.AUTH0_JWKS_PATH)
    LOGOUT_URL: HttpUrl = urljoin(DOMAIN.encoded_string(), global_settings.AUTH0_LOGOUT_PATH)


settings = Settings()
