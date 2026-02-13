from typing import TYPE_CHECKING
import logging
import json

from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError

from src.app.auth.schemas import UserSessionSchema
from src.app.auth.models import UserSessionTable
from src.app.core.database import db
from src.app.core.redis import redis_adapter
from src.app.core import exceptions
from src.app.core.settings import settings

if TYPE_CHECKING:
    from src.app.core.redis import RedisAdapter

logger = logging.getLogger(__name__)


class UserSessionSQLAlchemyRepository:
    def __init__(self, db_session_maker: async_sessionmaker) -> None:
        self.db_session_maker = db_session_maker

    @staticmethod
    def _mask_user_session_id(user_session_id: str) -> str:
        mask = "*" * (len(user_session_id) - 8)
        return user_session_id[:4] + mask + user_session_id[-4:]

    async def select_user_session(self, user_session_id: str) -> UserSessionSchema:
        masked_sid = self._mask_user_session_id(user_session_id)

        try:
            async with self.db_session_maker() as db_session:
                db_session: AsyncSession

                statement = (
                    select(UserSessionTable.__table__)
                    .where(UserSessionTable.id == user_session_id)
                )
                execution_result = await db_session.execute(statement)
                selected_user_session = execution_result.mappings().first()

            if not selected_user_session:
                raise exceptions.NotFoundError("User session with given ID was not found in database")

            logger.info("Retrieved user session from database: sid=%s", masked_sid)
            return UserSessionSchema(**selected_user_session)
        except exceptions.NotFoundError:
            logger.exception("User session with given ID was not found: sid=%s", masked_sid)
            raise
        except OperationalError as err:
            logger.exception("Failed to retrieve user session from database: sid=%s", masked_sid)
            raise exceptions.ServiceUnavailableError("Database unavailable") from err
        except SQLAlchemyError as err:
            logger.exception("Unexpected database error")
            raise exceptions.NotImplementedError("Unexpected database error")

    async def insert_user_session(self, user_session: UserSessionSchema) -> UserSessionSchema:
        masked_sid = self._mask_user_session_id(user_session.id)

        try:
            async with self.db_session_maker() as db_session:
                db_session: AsyncSession

                statement = (
                    insert(UserSessionTable.__table__)
                    .values(
                        id=user_session.id, 
                        user=user_session.user,
                        created_at=user_session.created_at, 
                        expires_at=user_session.expires_at,
                    )
                    .returning(UserSessionTable.__table__.columns)
                )

                execution_result = await db_session.execute(statement)
                inserted_user_session = execution_result.mappings().first()
                await db_session.commit()

            logger.info("Session stored in database: sid=%s", masked_sid)
            return UserSessionSchema(**inserted_user_session)
        except OperationalError as err:
            logger.exception("Failed to store user session in database: sid=%s", masked_sid)
            raise exceptions.ServiceUnavailableError("Database unavailable") from err
        except IntegrityError as err:
            logger.exception("User session with given ID already exists: sid=%s", masked_sid)
            raise exceptions.UnauthorizedError("Failed to create user session in database") from err
        except SQLAlchemyError as err:
            logger.exception("Unexpected database error")
            raise exceptions.NotImplementedError("Unexpected database error")

    async def delete_user_session(self, user_session_id: str) -> UserSessionSchema:
        masked_sid = self._mask_user_session_id(user_session_id)

        try:
            async with self.db_session_maker() as db_session:
                db_session: AsyncSession

                statement = (
                    delete(UserSessionTable.__table__)
                    .where(UserSessionTable.id == user_session_id)
                    .returning(UserSessionTable.__table__.columns)
                )
                execution_result = await db_session.execute(statement)
                deleted_user_session = execution_result.mappings().first()

                if not deleted_user_session:
                    raise exceptions.NotFoundError("User session with given ID was not found in database")
                
                await db_session.commit()

            logger.info("Removed user session from database: sid=%s", masked_sid)
            return UserSessionSchema(**deleted_user_session)
        except exceptions.NotFoundError:
            logger.exception("User session with given ID was not found: sid=%s", masked_sid)
            raise
        except OperationalError as err:
            logger.exception("Failed to remove user session in database: sid=%s", masked_sid)
            raise exceptions.ServiceUnavailableError("Database unavailable") from err
        except SQLAlchemyError as err:
            logger.exception("Unexpected database error")
            raise exceptions.NotImplementedError("Unexpected database error")


class UserSessionRedisRepository:
    def __init__(self, redis_adapter: "RedisAdapter") -> None:
        self.redis = redis_adapter

    @staticmethod
    def _get_user_session_key(user_session_id: str) -> str:
        return f"{settings.DB_REDIS_KEY_PREFIX_USER_SESSION}:{user_session_id}"

    @staticmethod
    def _mask_user_session_id(user_session_id: str) -> str:
        mask = "*" * (len(user_session_id) - 8)
        return user_session_id[:4] + mask + user_session_id[-4:]

    async def set_user_session(self, user_session: UserSessionSchema) -> bool:
        user_session_key: str = self._get_user_session_key(user_session.id)
        masked_sid = self._mask_user_session_id(user_session.id)

        try:
            result: bool = await self.redis.set(
                key=user_session_key, 
                value=user_session.model_dump_json(), 
                ttl=settings.USER_SESSION_TTL,
            )
            logger.info("Session stored in cache: sid=%s", masked_sid)
            return result
        except Exception:
            logger.exception("Failed to store session in cache: sid=%s", masked_sid)
            raise

    async def get_user_session(self, user_session_id: str) -> UserSessionSchema | None:
        user_session_key: str = self._get_user_session_key(user_session_id)
        masked_sid = self._mask_user_session_id(user_session_id)

        try:
            user_session: str = await self.redis.get(user_session_key)

            if not user_session:
                return None
            
            user_session = json.loads(user_session)
            logger.info("Retrieved session from cache: sid=%s", masked_sid)
            return UserSessionSchema(**user_session)
        except Exception:
            logger.exception("Failed to retrieve session from cache: sid=%s", masked_sid)
            raise

    async def delete_user_session(self, user_session_id: str) -> bool:
        user_session_key: str = self._get_user_session_key(user_session_id)
        masked_sid: str = self._mask_user_session_id(user_session_id)

        try:
            result: bool = await self.redis.delete(user_session_key)
            if not result:
                raise exceptions.NotFoundError("Session was not found in cache")
            return result
        except Exception:
            logger.exception("Failed to remove session from cache: sid=%s", masked_sid)
            raise


user_session_db_repo = UserSessionSQLAlchemyRepository(db_session_maker=db.sessionmaker)
user_session_cache_repo = UserSessionRedisRepository(redis_adapter=redis_adapter)
