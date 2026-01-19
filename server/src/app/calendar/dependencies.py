from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.app.calendar.models import Base
from src.app.calendar.repository.crud import SqlAlchemyCalendarRepository
from src.app.config import settings as global_settings
from src.app.database import async_db


async def get_sqlalchemy_repository() -> SqlAlchemyCalendarRepository:
    return SqlAlchemyCalendarRepository(async_session=async_db.async_session())
