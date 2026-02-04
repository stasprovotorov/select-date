import logging
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

logger = logging.getLogger(__name__)


async def get_session_service() -> SessionService:
    return session_service


async def require_auth(
    session_id: str | None = Cookie(None), 
    session_service: SessionService = Depends(get_session_service)
) -> dict:
    if not session_id:
        logger.warning("Session ID not provided in the cookie.")
        raise AuthSessionIdNotFound

    try:    
        session = await session_service.get_session(session_id)
    except AuthSessionError:
        logger.warning(f"Session ID not found in Redis: session_id={session_id}.")
        raise

    user = session["user"]
    logger.info(f"User successfully authenticated: session_id={session_id}.")
    return user


async def validate_state(
    state: str | None = Query(None), 
    auth_state: str | None = Cookie(None)
) -> None:
    if not secrets.compare_digest(state, auth_state):
        logger.error("The 'state' value from the request does not match the one from Auth0.")
        raise AuthStateNotMatchError


async def get_authorized_user(code: str) -> dict:
    jwt = await fetch_token(code)
    jwks = await fetch_jwks()
    user_info = validate_jwt(jwt, jwks)
    logger.info("Authorized user data successfully retrieved.")    
    return user_info
