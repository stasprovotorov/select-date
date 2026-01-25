import secrets
from urllib.parse import urlencode
from src.app.core.config import settings as global_settings
from src.app.auth.config import settings as auth_settings


def build_login_uri(auth_state: str) -> str:
    query_parameters = {
        "response_type": "code",
        "client_id": auth_settings.CLIENT_ID,
        "audience": auth_settings.AUDIENCE,
        "redirect_uri": auth_settings.REDIRECT_URI,
        "scope": auth_settings.SCOPE,
        "state": auth_state,
        "prompt": "select_account"
    }
    return f"{auth_settings.AUTHORIZE_URL}?{urlencode(query_parameters)}"


def build_logout_uri() -> str:
    query_parameters = {
        "client_id": auth_settings.CLIENT_ID,
        "returnTo": global_settings.APP_FRONTEND_BASE_URL
    }
    return f"{auth_settings.LOGOUT_URL}?{urlencode(query_parameters)}"


def get_session_id() -> str:
    session_id = secrets.token_urlsafe(32)
    return session_id


def get_session_key(session_id: str) -> str:
    return f"{global_settings.DB_REDIS_KEY_PREFIX_SESSION}:{session_id}"
