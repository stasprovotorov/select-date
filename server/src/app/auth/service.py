import logging
from datetime import datetime
import time
import secrets
import json

from src.app.auth.schemas import SessionSchema
from src.app.auth.repository import SessionSQLAlchemyRepository, SessionRedisRepository, session_db_repo, session_cache_repo
from src.app.core.config import settings
from src.app.core import exceptions

logger = logging.getLogger(__name__)


class SessionService:
    def __init__(
        self, 
        session_db_repo: SessionSQLAlchemyRepository, 
        session_cache_repo: SessionRedisRepository,
    ) -> None:
        self.db_repo = session_db_repo
        self.cache_repo = session_cache_repo


    def _create_session(self, user: dict) -> SessionSchema:
        sid = secrets.token_urlsafe(32)
        user_json_str = json.dumps(user)
        epoch_now = int(time.time())
        created_at = datetime.fromtimestamp(epoch_now)
        expires_at = datetime.fromtimestamp(epoch_now + settings.SESSION_TTL)

        logger.info("Created sesson for user")
        return SessionSchema(
            id=sid,
            user=user_json_str,
            created_at=created_at,
            expires_at=expires_at,
        )

    def _is_expired_db_session(self, session: SessionSchema) -> bool:
        expires_at = session.expires_at.timestamp()
        epoch_now = int(time.time())

        if expires_at <= epoch_now:
            return True
        return False

    async def set_session(self, user: dict) -> SessionSchema:
        session: SessionSchema = self._create_session(user)

        inserted_session = await self.db_repo.insert_session(session)
        await self.cache_repo.set_session(session)

        return inserted_session


    async def get_session(self, sid: str) -> SessionSchema:
        cached_session = await self.cache_repo.get_session(sid)

        if not cached_session:
            try:
                db_session: SessionSchema = await self.db_repo.select_session(sid)
                is_expired: bool = self._is_expired_db_session(db_session)

                if is_expired:
                    logger.info("Session has expired and will be remove from database")
                    await self.delete_session(sid)
                    raise exceptions.NotFoundError("No active session for user")

                return db_session
            except exceptions.NotFoundError as err:
                raise exceptions.UnauthorizedError("Session was not found in database") from err
            
        return cached_session

    async def delete_session(self, sid: str) -> SessionSchema:
        deleted_session = await self.db_repo.delete_session(sid)
        await self.cache_repo.delete_session(sid)

        return deleted_session


session_service = SessionService(session_db_repo, session_cache_repo)
