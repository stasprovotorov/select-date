from datetime import datetime

from sqlalchemy import String, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.app.core.models import Base


class UserSessionTable(Base):
    __tablename__ = "user_session"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user: Mapped[str] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
