from src.app.calendar.repository import CalendarSQLAlchemyRepository, calendar_repo
from src.app.calendar.service import CalendarService, calendar_service


def get_calendar_repo() -> CalendarSQLAlchemyRepository:
    return calendar_repo

def get_calendar_service() -> CalendarService:
    return calendar_service
