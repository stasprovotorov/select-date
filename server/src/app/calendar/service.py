from src.app.calendar.schemas import DateOperationSchema, DateOperationResultSchema, DateItemSchema
from src.app.calendar.repository import CalendarSQLAlchemyRepository, calendar_repo


class CalendarService:
    def __init__(self, calendar_repo: CalendarSQLAlchemyRepository) -> None:
        self.repo = calendar_repo

    async def process_date_operations(self, user_id: str, dates: list[DateOperationSchema]) -> list[DateOperationResultSchema]:
        result: list[DateOperationResultSchema] = await self.repo.process_batch(user_id, dates)
        return result
    
    async def get_dates_for_user(self, user_id: str) -> list[DateItemSchema]:
        result: list[DateItemSchema] = await self.repo.get_dates_for_user(user_id)
        return result


calendar_service = CalendarService(calendar_repo=calendar_repo)
