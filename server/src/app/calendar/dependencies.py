from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.app.calendar.models import Base
from src.app.calendar.repository.crud import SqlAlchemyCalendarRepository
from src.app.config import settings as global_settings


async def get_sqlalchemy_repository() -> SqlAlchemyCalendarRepository:
    async_engine = create_async_engine(global_settings.DB_URL)
    Base.metadata.create_all(async_engine)
    async_session = async_sessionmaker(bind=async_engine)
    return SqlAlchemyCalendarRepository(async_session=async_session())
