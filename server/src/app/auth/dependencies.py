import secrets

from fastapi import Depends, Query, Cookie

from src.app.auth.sessions import SessionService, session_service
from src.app.auth.client import fetch_jwks, fetch_token
from src.app.auth.service import validate_jwt
from src.app.auth.exceptions import (
    AuthStateNotMatchError,
    AuthSessionIdNotFound, 
    AuthSessionError
)


async def get_session_service() -> SessionService:
    return session_service


async def require_auth(
    session_id: str | None = Cookie(None), 
    session_service: SessionService = Depends(get_session_service)
) -> dict:
    if not session_id:
        # Log it.
        raise AuthSessionIdNotFound

    try:    
        session = await session_service.get_session(session_id)
    except AuthSessionError as error:
        # Log it.
        raise

    user = session["user"]
    # Log it.
    return user


async def validate_state(
    state: str | None = Query(None), 
    auth_state: str | None = Cookie(None)
) -> None:
    if not secrets.compare_digest(state, auth_state):
        # Log it.
        raise AuthStateNotMatchError


async def get_authorized_user(code: str) -> dict:
    jwt = await fetch_token(code)
    # Log it.

    jwks = await fetch_jwks()
    # Log it.

    user_info = validate_jwt(jwt, jwks)
    # Log it.
    
    return user_info
