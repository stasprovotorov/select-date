from datetime import date

from fastapi import HTTPException
from sqlalchemy import Date, String, select, delete, insert, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from schemas import SelectedDateSchema, DateItemSchema, ApiDateItemResult


class Base(DeclarativeBase):
    pass


class SelectedDateModel(Base):
    __tablename__ = "selected_dates"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    calendar_date: Mapped[date] = mapped_column(Date, primary_key=True)
    color: Mapped[str] = mapped_column(String, nullable=False)
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
    async def add_selected_date(cls, user_id: str, selected_date: SelectedDateSchema) -> dict:
        """
        Insert a selected date.
        On unique constraint violation raise DatabaseError with 409 status code.
        """
        month = selected_date.month + 1 # Fuck yeah! \m_
        date_data = date(selected_date.year, month, selected_date.day)
        AsyncSessions = cls._get_async_session()

        async with AsyncSessions() as session:
            try:
                stmt = insert(SelectedDateModel).values(
                    user_id=user_id,
                    calendar_date=date_data,
                    color=selected_date.color,
                    color_text=selected_date.textColor
                ).returning(
                    SelectedDateModel.user_id,
                    SelectedDateModel.calendar_date,
                    SelectedDateModel.color,
                    SelectedDateModel.color_text
                )

                result = await session.execute(stmt)
                row = result.mappings().first()
                inserted_date = dict(row)

                await session.commit()
                return dict(inserted_date)
            
            except IntegrityError as e:
                await session.rollback()
                raise DatabaseError(409, "Record already exists for this user and date.") from e

    @classmethod
    async def delete_selected_date(cls, user_id: str, selected_date: SelectedDateSchema) -> dict:
        """
        Delete selected date by user_id and calendar_date.
        If nothing was deleted, raise DatabaseError with 404 status code.
        """
        month = selected_date.month + 1 # This must be fixed on the client side
        date_data = date(selected_date.year, month, selected_date.day)
        AsyncSessions = cls._get_async_session()

        async with AsyncSessions() as session:
            stmt = delete(SelectedDateModel).where(
                SelectedDateModel.user_id == user_id, 
                SelectedDateModel.calendar_date == date_data
            ).returning(
                SelectedDateModel.user_id,
                SelectedDateModel.calendar_date,
                SelectedDateModel.color,
                SelectedDateModel.color_text
            )

            result = await session.execute(stmt)
            row = result.mappings().first()

            if not row:
                await session.rollback()
                raise DatabaseError(404, "Selected date not found for the user")
            
            deleted_date = dict(row)
            await session.commit()
            return dict(deleted_date)

    @classmethod
    async def process_batch(cls, user_id: str, date_batch: list[DateItemSchema]) -> ApiDateItemResult:
        batch_results = []
        async_session = cls._get_async_session()

        async with async_session.begin() as connection:
            for date_item in date_batch:
                savepoint = await connection.begin_nested()
                date_obj = date.fromisoformat(date_item.date)

                try:
                    if date_item.action == "select":
                        statement = insert(SelectedDateModel).values(
                            user_id=user_id,
                            calendar_date=date_obj,
                            color=date_item.color,
                            color_text=date_item.textColor
                        ).returning(SelectedDateModel.__table__.columns)
                    elif date_item.action == "deselect":
                        statement = delete(SelectedDateModel).where(
                            SelectedDateModel.user_id == user_id,
                            SelectedDateModel.calendar_date == date_obj
                        ).returning(SelectedDateModel.__table__.columns)
                    else:
                        raise DatabaseError(422, "Unknown action for date")
                    
                    execution_result = await connection.execute(statement)
                    date_item_row = execution_result.mappings().first()
                    date_value: date = date_item_row["calendar_date"]
                    date_iso = date_value.isoformat()

                    batch_results.append(
                        ApiDateItemResult(
                            ok=True,
                            action=date_item.action,
                            date=date_iso,
                            color=date_item_row["color"],
                            textColor=date_item_row["color_text"]
                        )
                    )
                    await savepoint.commit()
                except Exception as error:
                    await savepoint.rollback()

                    batch_results.append(
                        ApiDateItemResult(
                            ok=False,
                            action=date_item.action,
                            date=date_item.date,
                            color=date_item.color if date_item.action == "select" else None,
                            textColor=date_item.textColor if date_item.action == "select" else None,
                            message=str(error)
                        )
                    )
        return batch_results
        
    @classmethod
    async def get_user_dates(cls, user_id: str) -> dict:
        AsyncSessions = cls._get_async_session()

        async with AsyncSessions() as session:
            stmt = select(SelectedDateModel).where(SelectedDateModel.user_id == user_id)
            result = await session.execute(stmt)
            rows = result.scalars().all()

        selected_dates = []
        for date in rows:
            selected_date = {
                "action": "select",
                "date": date.calendar_date,
                "color": date.color,
                "textColor": date.color_text
            }
            selected_dates.append(selected_date)

        return selected_dates
    