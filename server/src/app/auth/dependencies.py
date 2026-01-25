import secrets
from fastapi import Depends, Query, Cookie
from src.app.auth.sessions import SessionService, session_service
from src.app.auth.exceptions import UserNotAuthorized, AuthStatesNotMatched
from src.app.auth.client import fetch_jwks, fetch_token
from src.app.auth.service import validate_jwt


async def get_session_service() -> SessionService:
    return session_service


async def require_auth(
    session_id: str | None = Cookie(None), 
    session_service: SessionService = Depends(get_session_service)
) -> dict:
    session = await session_service.get_session(session_id)
    if not session:
        raise UserNotAuthorized()
    return session["user"]


async def validate_state(state: str | None = Query(None), auth_state: str | None = Cookie(None)) -> None:
    if not secrets.compare_digest(state, auth_state):
        raise AuthStatesNotMatched()


async def get_authorized_user(code: str):
    jwks = await fetch_jwks()
    jwt = await fetch_token(code)
    user = validate_jwt(jwt, jwks)
    return user
