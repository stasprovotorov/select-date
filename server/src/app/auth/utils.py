from urllib.parse import urlencode

from src.app.core.config import settings


def build_login_uri(auth_state: str) -> str:
    query_parameters = {
        "response_type": "code",
        "client_id": settings.AUTH0_CLIENT_ID,
        "audience": settings.AUTH0_AUDIENCE,
        "redirect_uri": settings.AUTH0_REDIRECT_URI,
        "scope": settings.AUTH0_SCOPE,
        "state": auth_state,
        "prompt": "select_account",
    }
    return f"{settings.AUTH0_AUTHORIZE_URL}?{urlencode(query_parameters)}"
