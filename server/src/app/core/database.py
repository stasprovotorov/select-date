from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.app.core.settings import settings
from src.app.calendar.models import Base


class AsyncDatabase:
    def __init__(self):
        self.url = settings.DB_SQLITE_URL
        self.async_engine = create_async_engine(self.url)
        self.async_session = async_sessionmaker(bind=self.async_engine)

    async def initialize_async_database(self):
        async with self.async_engine.begin() as connection:
            journal_mode = f"PRAGMA journal_mode={settings.DB_SQLITE_JOURNAL_MODE}"
            await connection.execute(text(journal_mode))
            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)

    async def shutdown_async_database(self):
        async with self.async_engine.begin() as connection:
            await connection.execute(text("PRAGMA wal_checkpoint(FULL)"))


async_db: AsyncDatabase = AsyncDatabase()
