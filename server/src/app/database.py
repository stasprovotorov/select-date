from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.app.config import settings as global_settings
from src.app.calendar.models import Base


class AsyncDatabase:
    def __init__(self):
        self.sqlite_url = global_settings.DB_URL
        self.async_engine = create_async_engine(self.sqlite_url)
        self.async_session = async_sessionmaker(bind=self.async_engine)

    async def initialize_async_database(self):
        async with self.async_engine.begin() as connection:
            await connection.execute(text("PRAGMA journal_mode=WAL"))
            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)


async_db: AsyncDatabase = AsyncDatabase()
