from src.app.calendar.repository.base import CalendarRepository
from src.app.calendar.schemas import DateOperationSchema, DateOperationResultSchema, DateItemSchema


class CalendarService:
    def __init__(self, repository: CalendarRepository) -> None:
        self.repository = repository

    async def procces_dates(self, user_id: str, dates: list[DateOperationSchema]) -> DateOperationResultSchema:
        result = await self.repository.process_batch(user_id, dates)
        return result
    
    async def get_dates_by_user(self, user_id: str) -> list[DateItemSchema]:
        result = await self.repository.get_dates_by_user(user_id)
        return result
    