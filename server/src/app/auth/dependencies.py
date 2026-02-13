import json
import logging
import secrets

from fastapi import Depends, Query, Cookie

from src.app.auth.client import fetch_jwks, fetch_token
from src.app.auth.service import validate_jwt
from src.app.auth.service import UserSessionService, user_session_service
from src.app.core import exceptions

from src.app.auth.schemas import UserSessionSchema

logger = logging.getLogger(__name__)


async def get_user_session_service() -> UserSessionService:
    return user_session_service


async def require_auth(
    session_id: str | None = Cookie(None), 
    user_session_service: UserSessionService = Depends(get_user_session_service)
) -> dict:
    if not session_id:
        logger.warning("User session ID not provided in cookie")
        raise exceptions.BadRequestError("User session ID not found")

    user_session: UserSessionSchema = await user_session_service.get_user_session(session_id)
    user = user_session.user
    user = json.loads(user)

    logger.info(f"User authenticated")
    return user


async def validate_state(
    state: str | None = Query(None), 
    auth_state: str | None = Cookie(None)
) -> None:
    if not secrets.compare_digest(state, auth_state):
        logger.error("The 'state' value from the request does not match the one from Auth0.")
        raise exceptions.UnauthorizedError("Authorization states do not match.")


async def get_authorized_user(code: str) -> dict:
    jwt = await fetch_token(code)
    jwks = await fetch_jwks()
    user_info = validate_jwt(jwt, jwks)
    logger.info("Authorized user data successfully retrieved.")    
    return user_info
