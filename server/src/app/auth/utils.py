from urllib.parse import urlencode
from src.app.config import settings as global_settings
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
