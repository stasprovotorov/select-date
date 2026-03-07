from typing import TYPE_CHECKING
import logging
import json

from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError

from src.app.auth.schemas import SessionSchema
from src.app.auth.models import SessionModel
from src.app.core.database import db
from src.app.core.cache import redis_adapter
from src.app.core import exceptions
from src.app.core.config import settings

if TYPE_CHECKING:
    from src.app.core.cache import RedisAdapter

logger = logging.getLogger(__name__)


class SessionSQLAlchemyRepository:
    def __init__(self, db_sessionmaker: async_sessionmaker) -> None:
        self.db_sessionmaker = db_sessionmaker

    async def select_session(self, sid: str) -> SessionSchema:
        try:
            async with self.db_sessionmaker() as db_session:
                db_session: AsyncSession

                statement = (
                    select(SessionModel.__table__)
                    .where(SessionModel.id == sid)
                )
                execution_result = await db_session.execute(statement)
                selected_session = execution_result.mappings().first()

            if not selected_session:
                raise exceptions.NotFoundError("User session with given ID was not found in database")

            logger.info("Retrieved user session from database: sid=%s", sid)
            return SessionSchema(**selected_session)
        except exceptions.NotFoundError:
            logger.exception("User session with given ID was not found: sid=%s", sid)
            raise
        except OperationalError as err:
            logger.exception("Failed to retrieve user session from database: sid=%s", sid)
            raise exceptions.ServiceUnavailableError("Database unavailable") from err
        except SQLAlchemyError as err:
            logger.exception("Unexpected database error")
            raise exceptions.NotImplementedError("Unexpected database error")

    async def insert_session(self, session: SessionSchema) -> SessionSchema:
        try:
            async with self.db_sessionmaker() as db_session:
                db_session: AsyncSession

                statement = (
                    insert(SessionModel.__table__)
                    .values(
                        id=session.id, 
                        user=session.user,
                        created_at=session.created_at, 
                        expires_at=session.expires_at,
                    )
                    .returning(SessionModel.__table__.columns)
                )

                execution_result = await db_session.execute(statement)
                inserted_session = execution_result.mappings().first()
                await db_session.commit()

            logger.info("Session stored in database: sid=%s", session.id)
            return SessionSchema(**inserted_session)
        except OperationalError as err:
            logger.exception("Failed to store session in database: sid=%s", session.id)
            raise exceptions.ServiceUnavailableError("Database unavailable") from err
        except IntegrityError as err:
            logger.exception("Session with given ID already exists: sid=%s", session.id)
            raise exceptions.UnauthorizedError("Failed to create session in database") from err
        except SQLAlchemyError as err:
            logger.exception("Unexpected database error")
            raise exceptions.NotImplementedError("Unexpected database error")

    async def delete_session(self, sid: str) -> SessionSchema:
        try:
            async with self.db_sessionmaker() as db_session:
                db_session: AsyncSession

                statement = (
                    delete(SessionModel.__table__)
                    .where(SessionModel.id == sid)
                    .returning(SessionModel.__table__.columns)
                )
                execution_result = await db_session.execute(statement)
                deleted_session = execution_result.mappings().first()

                if not deleted_session:
                    raise exceptions.NotFoundError("Session with given ID was not found in database")
                
                await db_session.commit()

            logger.info("Removed session from database: sid=%s", sid)
            return SessionSchema(**deleted_session)
        except exceptions.NotFoundError:
            logger.exception("Session with given ID was not found: sid=%s", sid)
            raise
        except OperationalError as err:
            logger.exception("Failed to remove session in database: sid=%s", sid)
            raise exceptions.ServiceUnavailableError("Database unavailable") from err
        except SQLAlchemyError as err:
            logger.exception("Unexpected database error")
            raise exceptions.NotImplementedError("Unexpected database error")


class SessionRedisRepository:
    def __init__(self, redis_adapter: "RedisAdapter") -> None:
        self.redis = redis_adapter

    @staticmethod
    def _get_session_key(sid: str) -> str:
        return f"{settings.DB_REDIS_KEY_PREFIX_SESSION}:{sid}"

    async def set_session(self, session: SessionSchema) -> bool:
        session_key: str = self._get_session_key(session.id)

        try:
            result: bool = await self.redis.set(
                key=session_key, 
                value=session.model_dump_json(), 
                ttl=settings.SESSION_TTL,
            )
            logger.info("Session stored in cache: sid=%s", session.id)
            return result
        except Exception:
            logger.exception("Failed to store session in cache: sid=%s", session.id)
            raise

    async def get_session(self, sid: str) -> SessionSchema | None:
        session_key: str = self._get_session_key(sid)

        try:
            session: str = await self.redis.get(session_key)

            if not session:
                return None
            
            session = json.loads(session)
            logger.info("Retrieved session from cache: sid=%s", sid)
            return SessionSchema(**session)
        except Exception:
            logger.exception("Failed to retrieve session from cache: sid=%s", sid)
            raise

    async def delete_session(self, sid: str) -> bool:
        session_key: str = self._get_session_key(sid)

        try:
            result: bool = await self.redis.delete(session_key)
            if not result:
                raise exceptions.NotFoundError("Session was not found in cache")
            return result
        except Exception:
            logger.exception("Failed to remove session from cache: sid=%s", sid)
            raise


session_db_repo = SessionSQLAlchemyRepository(db_sessionmaker=db.sessionmaker)
session_cache_repo = SessionRedisRepository(redis_adapter=redis_adapter)
