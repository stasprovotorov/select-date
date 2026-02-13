import asyncio
import secrets

import logging
import time
import json
from datetime import datetime
import secrets
import jwt
from jwt.algorithms import RSAAlgorithm
from jwt.exceptions import (
    DecodeError, 
    InvalidKeyError, 
    InvalidAlgorithmError, 
    InvalidAudienceError, 
    InvalidIssuerError
)

from src.app.auth.schemas import UserSessionSchema
from src.app.auth.repository import UserSessionSQLAlchemyRepository, UserSessionRedisRepository, user_session_db_repo, user_session_cache_repo
from src.app.core.settings import settings
from src.app.core import exceptions

logger = logging.getLogger(__name__)


def validate_jwt(token: str, jwks: dict) -> dict:
    public_key = None

    unverified_header = jwt.get_unverified_header(token)
    kid_jwt = unverified_header.get("kid")

    if not kid_jwt:
        logger.error("No 'kid' found in the JWT header.")
        raise exceptions.NotFoundError("The key 'kid' was not found in the JWT's header.")
    logger.info("Received 'kid' from the JWT header.")

    keys = jwks.get("keys")

    for jwk in keys:
        kid_jwk = jwk.get("kid")

        if kid_jwt == kid_jwk:
            try:
                public_key = RSAAlgorithm.from_jwk(jwk)
                logger.info("Public key retrieved from JWK.")
            except InvalidKeyError as error:
                logger.error("Failed to obtain public key from JWT.")
                raise exceptions.UnprocessableEntityError("Failed to obtain the public key from JWK.") from error

    if not public_key:
        logger.error("No matching 'kid' found between the JWT and the JWKS.")
        raise exceptions.NotFoundError("No JWK was found for the given JWKS.")

    try:
        payload = jwt.decode(
            jwt=token,
            key=public_key,
            algorithms=settings.AUTH0_ALGORITHM,
            audience=settings.AUTH0_CLIENT_ID,
            issuer=settings.AUTH0_DOMAIN.encoded_string(),
            leeway=5
        )
        logger.info("JWT successfully decoded.")
        return payload
    except (TypeError, DecodeError, InvalidAlgorithmError, InvalidAudienceError, InvalidIssuerError) as error:
        logger.error("Failed to decode the JWT.", exc_info=True)
        raise exceptions.UnprocessableEntityError("Failed to decode JWT.") from error


class UserSessionService:
    def __init__(
        self, 
        user_session_db_repo: UserSessionSQLAlchemyRepository, 
        user_session_cache_repo: UserSessionRedisRepository,
    ) -> None:
        self.db_repo = user_session_db_repo
        self.cache_repo = user_session_cache_repo


    @staticmethod
    def create_user_session(user: dict) -> UserSessionSchema:
        user_session_id = secrets.token_urlsafe(32)
        user_json_str = json.dumps(user)
        epoch_now = int(time.time())
        created_at = datetime.fromtimestamp(epoch_now)
        expires_at = datetime.fromtimestamp(epoch_now + settings.USER_SESSION_TTL)

        logger.info("Created user sesson")
        return UserSessionSchema(
            id=user_session_id,
            user=user_json_str,
            created_at=created_at,
            expires_at=expires_at,
        )

    @staticmethod
    def is_expired_db_user_session(user_session: UserSessionSchema) -> bool:
        expires_at = user_session.expires_at.timestamp()
        epoch_now = int(time.time())

        if expires_at <= epoch_now:
            return True
        return False

    async def set_user_session(self, user: dict) -> UserSessionSchema:
        user_session: UserSessionSchema = self.create_user_session(user)

        inserted_user_session = await self.db_repo.insert_user_session(user_session)
        await self.cache_repo.set_user_session(user_session)

        return inserted_user_session


    async def get_user_session(self, user_session_id: str) -> UserSessionSchema:
        cached_user_session = await self.cache_repo.get_user_session(user_session_id)

        if not cached_user_session:
            try:
                db_user_session: UserSessionSchema = await self.db_repo.select_user_session(user_session_id)
                is_expired: bool = self.is_expired_db_user_session(db_user_session)

                if is_expired:
                    logger.info("User session has expired and will be remove from database")
                    await self.delete_user_session(user_session_id)
                    raise exceptions.UnauthorizedError("User session has expired")

                return db_user_session
            except exceptions.NotFoundError as err:
                raise exceptions.UnauthorizedError("User session was not found in database") from err
            
        return cached_user_session

    async def delete_user_session(self, user_session_id: str) -> UserSessionSchema:
        deleted_user_session = await self.db_repo.delete_user_session(user_session_id)
        await self.cache_repo.delete_user_session(user_session_id)

        return deleted_user_session


user_session_service = UserSessionService(user_session_db_repo, user_session_cache_repo)
