from abc import ABC, abstractmethod
from src.app.calendar.schemas import DateItemSchema, DateOperationSchema, DateOperationResultSchema


class CalendarRepository(ABC):
    @abstractmethod
    async def process_batch(self, user_id: str, batch: list[DateOperationSchema]) -> list[DateOperationResultSchema]:
        pass

    @abstractmethod
    async def get_dates_by_user(cls, user_id: str) -> list[DateItemSchema]:
        pass
