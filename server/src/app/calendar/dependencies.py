from src.app.calendar.repository import SqlAlchemyCalendarRepository
from src.app.core.database import db


async def get_sqlalchemy_repository() -> SqlAlchemyCalendarRepository:
    return SqlAlchemyCalendarRepository(async_session=db.sessionmaker)
