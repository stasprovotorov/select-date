import json
import logging

import redis

from src.app.core.settings import settings
from src.app.core.redis import async_redis
from src.app.auth.schemas import Session
from src.app.auth.utils import get_session_id, get_session_key
from src.app.core import exceptions

logger = logging.getLogger(__name__)


class SessionService:
    def __init__(self, storage: redis.Redis) -> None:
        self.storage = storage

    async def create_session(self, user: dict) -> str:
        session_id = get_session_id()
        session_key = get_session_key(session_id)
        session = Session(user=user)

        try:
            await self.storage.set(
                name=session_key,
                value=session.model_dump_json(),
                ex=settings.SESSION_TTL
            )
            logger.info(f"Session created in Redis: session_key={session_key}.")
        except redis.ConnectionError as error:
            logger.error("No connection to the Redis server.")
            raise exceptions.ServiceUnavailableError("Failed to set session object in the server.") from error

        return session_id

    async def get_session(self, session_id: str) -> dict | None:
        session_key = get_session_key(session_id)

        try:
            session = await self.storage.get(session_key)

            if not session:
                raise exceptions.NotFoundError("Session was not found in the server.")
            
            session_dict = json.loads(session)
            logger.info(f"Session retrieved from Redis: session_key={session_key}.")
            return session_dict
        except redis.ConnectionError as error:
            logger.error("No connection to the Redis server.")
            raise exceptions.ServiceUnavailableError("Failed to obtain session object from the server.") from error
        except json.JSONDecodeError as error:
            logger.error(f"Failed to serialize session data received from Redis to JSON: session_key={session_key}.")
            raise exceptions.UnprocessableEntityError("Failed to deserialize session object from the server.") from error
        except exceptions.NotFoundError as error:
            logger.error(f"No session found on the Redis server: session_key={session_key}.")
            raise
    
    async def remove_session(self, session_id: str) -> None:
        session_key = get_session_key(session_id)

        try:
            entry_count = await self.storage.delete(session_key)
            if entry_count == 0:
                logger.warning(f"No session found for deletion on the Redis server: session_key={session_key}.")
            logger.info(f"Session has been deleted from the Redis server: session_key={session_key}.")
        except redis.ConnectionError as error:
            logger.error("No connection to the Redis server.")
            raise exceptions.ServiceUnavailableError("Failed to delete session object from the server.") from error


session_service = SessionService(storage=async_redis.client)
