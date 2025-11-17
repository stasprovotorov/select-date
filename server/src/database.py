from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Date
from sqlalchemy import insert, delete
from datetime import date
from schemas import SelectedDateSchema


class Base(DeclarativeBase):
    pass


class SelectedDateModel(Base):
    __tablename__ = "selected_dates"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    calendar_date: Mapped[date] = mapped_column(Date, primary_key=True)
    color: Mapped[str] = mapped_column(String, nullable=False)
    color_text: Mapped[str] = mapped_column(String, nullable=False)


class DatabaseProvider:
    def __init__(self):
        self.database_url = "sqlite+aiosqlite:///database.db"
        self.engine = create_async_engine(self.database_url)
        self.sessions = async_sessionmaker(self.engine)

    async def initialize_database(self):
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def add_selected_date(self, user_id: str, selected_date: SelectedDateSchema):
        month = selected_date.month + 1
        date_data = date(selected_date.year, month, selected_date.day)
        async with self.sessions() as session:
            statement = insert(SelectedDateModel).values(
                user_id=user_id,
                calendar_date=date_data,
                color=selected_date.color,
                color_text=selected_date.textColor
            )
            await session.execute(statement)
            await session.commit()

    async def delete_selected_date(self, user_id: str, selected_date: SelectedDateSchema):
        month = selected_date.month + 1
        date_data = date(selected_date.year, month, selected_date.day)
        async with self.sessions() as session:
            statement = delete(SelectedDateModel).where(
                SelectedDateModel.user_id == user_id, 
                SelectedDateModel.calendar_date == date_data
            )
            await session.execute(statement)
            await session.commit()
