from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.exc import SQLAlchemyError
from src.app.calendar.repository.base import CalendarRepository
from src.app.calendar.schemas import DateOperationSchema, DateOperationResultSchema, DateOperationType, DateItemSchema
from src.app.calendar.models import SelectedDateModel
from src.app.calendar.exceptions import DatabaseError


class SqlAlchemyCalendarRepository(CalendarRepository):
    def __init__(self, async_session: AsyncSession):
        self.async_session = async_session

    async def process_batch(self, user_id: str, batch: list[DateOperationSchema]) -> list[DateOperationResultSchema]:
        batch_results = []

        async with self.async_session.begin() as session:
            for date_oper in batch:
                savepoint = await session.begin_nested()

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

                    execution_result = await session.execute(statement)
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

    async def get_dates_by_user(self, user_id: str) -> list[DateItemSchema]:
        dates = []

        async with self.async_session as session:
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
