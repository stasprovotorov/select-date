from datetime import date
from sqlalchemy import Integer, String, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SelectedDateModel(Base):
    __tablename__ = "selected_dates"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    calendar_date: Mapped[date] = mapped_column(Date, primary_key=True)
    color: Mapped[str] = mapped_column(String, nullable=False)
    color_text: Mapped[str] = mapped_column(String, nullable=False)
