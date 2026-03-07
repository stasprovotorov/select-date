import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.app.core.config import settings
from src.app.core.models import Base

# Side effect imports for Base.metadata.create_all execution
from src.app.auth.models import SessionModel
from src.app.calendar.models import SelectedDateModel

logger = logging.getLogger(__name__)


class SQLiteAsyncDatabase:
    def __init__(self, url: str) -> None:
        self.url = url
        self.engine = create_async_engine(self.url)
        self.sessionmaker = async_sessionmaker(bind=self.engine)

    async def initialize_database(self) -> None:
        logger.info("Database initialization started")
        logger.info("Database URL: %s", self.url)

        async with self.engine.begin() as connection:
            journal_mode = f"PRAGMA journal_mode={settings.DB_SQLITE_JOURNAL_MODE};"
            statement = text(journal_mode)
            logger.info("Executing statement: %s", journal_mode)
            await connection.execute(statement)
            # logger.info("Creating tables")
            # await connection.run_sync(Base.metadata.create_all)

        logger.info("Database initialization finished")

    async def shutdown_database(self) -> None:
        logger.info("Database shutdown started")

        async with self.engine.begin() as connection:
            wal_checkpoint = f"PRAGMA wal_checkpoint({settings.DB_SQLITE_WAL_CHECKPOINT});"
            statement = text(wal_checkpoint)
            logger.info("Executing statement: %s", wal_checkpoint)
            await connection.execute(statement)

        logger.info("Database shutdown finished")


db = SQLiteAsyncDatabase(settings.DB_SQLITE_URL)
