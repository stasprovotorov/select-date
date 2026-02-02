import secrets
from urllib.parse import urlencode
from src.app.core.settings import settings


def build_login_uri(auth_state: str) -> str:
    query_parameters = {
        "response_type": "code",
        "client_id": settings.AUTH0_CLIENT_ID,
        "audience": settings.AUTH0_AUDIENCE,
        "redirect_uri": settings.AUTH0_REDIRECT_URI,
        "scope": settings.AUTH0_SCOPE,
        "state": auth_state,
        "prompt": "select_account"
    }
    return f"{settings.AUTH0_AUTHORIZE_URL}?{urlencode(query_parameters)}"


def build_logout_uri() -> str:
    query_parameters = {
        "client_id": settings.AUTH0_CLIENT_ID,
        "returnTo": settings.APP_FRONTEND_BASE_URL
    }
    return f"{settings.AUTH0_LOGOUT_URL}?{urlencode(query_parameters)}"


def get_session_id() -> str:
    session_id = secrets.token_urlsafe(32)
    return session_id


def get_session_key(session_id: str) -> str:
    return f"{settings.DB_REDIS_KEY_PREFIX_SESSION}:{session_id}"
