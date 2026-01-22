from src.app.calendar.repository import SqlAlchemyCalendarRepository
from src.app.core.database import async_db


async def get_sqlalchemy_repository() -> SqlAlchemyCalendarRepository:
    return SqlAlchemyCalendarRepository(async_session=async_db.async_session)
