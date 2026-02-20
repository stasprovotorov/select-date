import json
import logging
import secrets

from fastapi import Depends, Query, Cookie

from src.app.auth.client import fetch_jwks, fetch_jwt
from src.app.auth.security import validate_jwt
from src.app.auth.schemas import SessionSchema
from src.app.auth.service import SessionService, session_service
from src.app.core.exceptions import UnauthorizedError

logger = logging.getLogger(__name__)


def get_session_service() -> SessionService:
    return session_service


async def require_auth(
    sid: str | None = Cookie(None), 
    session_service: SessionService = Depends(get_session_service),
) -> dict:
    if not sid:
        logger.warning("User not authenticated: cookie with session ID was not provided")
        raise UnauthorizedError("Cookie with session ID was not provided")

    try:
        session: SessionSchema = await session_service.get_session(sid)
    except Exception:
        logger.exception("User not authenticated")
        raise

    user = json.loads(session.user)

    logger.info("User authenticated")
    return user


def validate_state(
    state: str | None = Query(None), 
    auth_state: str | None = Cookie(None),
) -> None:
    if not secrets.compare_digest(state, auth_state):
        logger.error("The state from the request does not match the one from Auth0")
        raise UnauthorizedError("States do not match")


async def get_authorized_user(code: str) -> dict:
    try:
        jwt = await fetch_jwt(code)
        jwks = await fetch_jwks()
        user = validate_jwt(jwt, jwks)
    except Exception as err:
        logger.exception("Failed to authenticate user")
        raise UnauthorizedError("User unauthorized") from err
    
    logger.info("Retrieved authorized user from Auth0")
    return user
