from typing import TYPE_CHECKING
import json

from src.app.auth.schemas import Session
from src.app.auth.utils import get_session_id, get_session_key
from src.app.core.config import settings
from src.app.core.redis import client as redis_client

if TYPE_CHECKING:
    from redis import Redis


class SessionService:
    def __init__(self, storage: "Redis") -> None:
        self.storage = storage

    async def create_session(self, user: dict) -> str:
        session_id = get_session_id()
        session_key = get_session_key(session_id)
        session = Session(user=user)

        await self.storage.set(
            name=session_key,
            value=session.model_dump_json(),
            ex=settings.SESSION_TTL
        )

        return session_id

    async def get_session(self, session_id: str) -> dict | None:
        session_key = get_session_key(session_id)
        session = await self.storage.get(session_key)

        if session:
            session_dict = json.loads(session)
            return session_dict
    
    async def remove_session(self, session_id: str) -> None:
        session_key = get_session_key(session_id)
        await self.storage.delete(session_key)


session_service = SessionService(redis_client)
