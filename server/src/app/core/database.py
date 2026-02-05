import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.app.core.settings import settings
from src.app.calendar.models import Base

logger = logging.getLogger(__name__)


class AsyncDatabase:
    def __init__(self):
        self.url = settings.DB_SQLITE_URL
        self.async_engine = create_async_engine(self.url)
        self.async_session = async_sessionmaker(bind=self.async_engine)

    async def initialize_async_database(self):
        logger.info("Asynchronous SQLite database initialization started.")

        async with self.async_engine.begin() as connection:
            journal_mode = f"PRAGMA journal_mode={settings.DB_SQLITE_JOURNAL_MODE}"
            logger.info(f"Set jounal mode. Execute: {journal_mode}.")
            await connection.execute(text(journal_mode))

            logger.info("Create tables.")
            await connection.run_sync(Base.metadata.create_all)

        logger.info("Asynchronous SQLite database initialization finished.")

    async def shutdown_async_database(self):
        logger.info("Asynchronous SQLite database shutdown started.")

        async with self.async_engine.begin() as connection:
            logger.info("Save data from WAL. Execute: PRAGMA wal_checkpoint(FULL).")
            await connection.execute(text("PRAGMA wal_checkpoint(FULL)"))

        logger.info("Asynchronous SQLite database shutdown finished.")


async_db: AsyncDatabase = AsyncDatabase()
