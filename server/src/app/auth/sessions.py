import json

import redis

from src.app.core.config import settings
from src.app.core.redis import async_redis
from src.app.auth.schemas import Session
from src.app.auth.utils import get_session_id, get_session_key
from src.app.auth.exceptions import (
    AuthSessionGetError, 
    AuthSessionSetError,
    AuthSessionDeleteError,
    AuthSessionNotFoundError, 
    AuthSessionDeserializationError
)


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
        except redis.ConnectionError as error:
            # Log it.
            raise AuthSessionSetError from error

        return session_id

    async def get_session(self, session_id: str) -> dict | None:
        session_key = get_session_key(session_id)

        try:
            session = await self.storage.get(session_key)

            if not session:
                raise AuthSessionNotFoundError
            
            session_dict = json.loads(session)
            return session_dict
        except redis.ConnectionError as error:
            # Log it.
            raise AuthSessionGetError from error
        except json.JSONDecodeError as error:
            # Log it.
            raise AuthSessionDeserializationError from error
        except AuthSessionNotFoundError as error:
            # Log it.
            raise
    
    async def remove_session(self, session_id: str) -> None:
        session_key = get_session_key(session_id)

        try:
            entry_count = await self.storage.delete(session_key)
            if entry_count == 0:
                # Log it.
                pass
            # Log it.
        except redis.ConnectionError as error:
            # Log it.
            raise AuthSessionDeleteError from error


session_service = SessionService(storage=async_redis.client)
