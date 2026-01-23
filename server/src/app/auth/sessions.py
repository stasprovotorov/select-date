import time
import json
import secrets
from functools import lru_cache
from redis.asyncio import Redis
from src.app.core.config import settings as global_settings
from src.app.core.redis import client as redis_client


class SessionService:
    def __init__(self, storage: Redis) -> None:
        self.storage = storage

    async def create_session(self, user: dict) -> str:
        session_id = secrets.token_urlsafe(32)
        storage_key = f"session:{session_id}"
        storage_value = {
            "user": user,
            "created_at": int(time.time()),
            "expires_at": int(time.time()) + global_settings.SESSION_TTL
        }
        await self.storage.set(
            storage_key,
            json.dumps(storage_value, ensure_ascii=False),
            ex=global_settings.SESSION_TTL
        )
        return session_id

    async def get_session(self, session_id: str) -> dict | None:
        session = await self.storage.get(f"session:{session_id}")
        if session:
            return json.loads(session)
        return None
    
    async def remove_session(self, session_id: str) -> None:
        session = await self.storage.delete(f"session:{session_id}")
        return session


@lru_cache
def get_session_service() -> SessionService:
    return SessionService(storage=redis_client)
