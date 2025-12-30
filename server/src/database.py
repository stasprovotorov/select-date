from datetime import date

from fastapi import HTTPException
from sqlalchemy import Date, String, select, delete, insert, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from schemas import SelectedDateSchema, DateItemSchema, DateOperationSchema, DateOperationResultSchema, ApiDateItemResult, DateOperationType


class Base(DeclarativeBase):
    pass


class SelectedDateModel(Base):
    __tablename__ = "selected_dates"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    calendar_date: Mapped[date] = mapped_column(Date, primary_key=True)
    color_bg: Mapped[str] = mapped_column(String, nullable=False)
    color_text: Mapped[str] = mapped_column(String, nullable=False)


class DatabaseError(HTTPException):
    """
    HTTPException subclass for database related errors.
    """
    def __init__(self, status_code: int = 500, detail: str = "Internal database error"):
        super().__init__(status_code=status_code, detail=detail)


class DatabaseProvider:
    """
    Provider class that offers utilities for interacting with the SQLite database:
    initializing the schema, and performing data retrieval, insertion, and deletion.
    """
    DATABASE_URL: str = "sqlite+aiosqlite:///database.db"
    _engine: AsyncEngine | None = None
    _async_session: async_sessionmaker[AsyncSession] | None = None

    @classmethod
    def set_engine(cls) -> AsyncEngine:
        """
        Create the async SQLite engine if it is not set.
        """
        if cls._engine is None:
            cls._engine = create_async_engine(cls.DATABASE_URL)

    @classmethod
    def _get_async_session(cls) -> async_sessionmaker[AsyncSession]:
        """
        Create an asynchronous session factory for database sessions.
        """
        if cls._engine is None:
            cls.set_engine()
        if cls._async_session is None:
            cls._async_session = async_sessionmaker(cls._engine)
        return cls._async_session

    @classmethod
    async def initialize_database(cls):
        """
        Initialize database and create tables if they don't exist. Idempotent.
        """
        cls.set_engine()
        async with cls._engine.begin() as connection:
            await connection.execute(text("PRAGMA journal_mode=WAL"))
            await connection.run_sync(Base.metadata.create_all)

    @classmethod
    async def process_batch(cls, user_id: str, batch: list[DateOperationSchema]) -> list[DateOperationResultSchema]:
        batch_results = []
        async_session = cls._get_async_session()

        async with async_session.begin() as connection:
            for date_oper in batch:
                savepoint = await connection.begin_nested()

                try:
                    date_item = date_oper.item
                    if date_oper.oper_type == DateOperationType.INSERT:
                        statement = insert(SelectedDateModel).values(
                            user_id=user_id,
                            calendar_date=date_item.calendar_date,
                            color_bg=date_item.color_bg,
                            color_text=date_item.color_text
                        ).returning(SelectedDateModel.__table__.columns)
                    elif date_oper.oper_type == DateOperationType.DELETE:
                        statement = delete(SelectedDateModel).where(
                            SelectedDateModel.user_id == user_id,
                            SelectedDateModel.calendar_date == date_item.calendar_date
                        ).returning(SelectedDateModel.__table__.columns)

                    execution_result = await connection.execute(statement)
                    date_item_row = execution_result.mappings().first()

                    if not date_item_row and date_oper.oper_type == DateOperationType.DELETE:
                        raise DatabaseError(404, "Specified date not found for the user")
                    
                    date_item_out = DateItemSchema(
                        calendar_date=date_item_row["calendar_date"],
                        color_bg=date_item_row["color_bg"],
                        color_text=date_item_row["color_text"]
                    )
                    date_oper_out = DateOperationSchema(
                        oper_type=date_oper.oper_type,
                        item=date_item_out
                    )
                    batch_results.append(DateOperationResultSchema(ok=True, operation=date_oper_out))

                    await savepoint.commit()
                except SQLAlchemyError as err:
                    await savepoint.rollback()
                    batch_results.append(DateOperationResultSchema(ok=False, operation=date_oper, message=repr(err)))

        return batch_results
        
    @classmethod
    async def get_dates_by_user(cls, user_id: str) -> list[DateItemSchema]:
        dates = []
        async_session = cls._get_async_session()

        async with async_session() as session:
            try:
                statement = select(SelectedDateModel).where(SelectedDateModel.user_id == user_id)
                execution_result = await session.execute(statement)
                date_rows = execution_result.scalars().all()
            except SQLAlchemyError as err:
                raise DatabaseError(500, repr(err))

        if date_rows:
            for date_row in date_rows:
                date_item = DateItemSchema(
                    calendar_date=date_row.calendar_date,
                    color_bg=date_row.color_bg,
                    color_text=date_row.color_text
                )
                dates.append(date_item)
                
        return dates
    