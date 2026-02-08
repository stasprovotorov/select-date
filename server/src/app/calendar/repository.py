import logging

from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.app.calendar.schemas import DateOperationSchema, DateOperationResultSchema, DateOperationType, DateItemSchema
from src.app.calendar.models import SelectedDateModel
from src.app.core import exceptions

logger = logging.getLogger(__name__)


class SqlAlchemyCalendarRepository:
    def __init__(self, async_session: AsyncSession):
        self.async_session = async_session

    async def process_batch(self, user_id: str, batch: list[DateOperationSchema]) -> list[DateOperationResultSchema]:
        batch_results = []

        logger.info(f"Batch processing started: operation count {len(batch)}.")
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
                        logger.warning(f"Date to be deleted for the user was not found in the database: user_id={user_id}, calendar_date={date_item.calendar_date}")
                        raise exceptions.NotFoundError("Specified date not found for the user.")
                    
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
                except (SQLAlchemyError, exceptions.NotFoundError) as error:
                    await savepoint.rollback()
                    message = repr(error)
                    logger.error("Date operation cancelled.", exc_info=True)
                    batch_results.append(DateOperationResultSchema(ok=False, operation=date_oper, message=message))

        logger.info(f"Batch processing finished.")
        return batch_results

    async def get_dates_by_user(self, user_id: str) -> list[DateItemSchema]:
        dates = []

        logger.info(f"Retrieving dates for the user from database: user_id={user_id}.")
        async with self.async_session() as session:
            try:
                statement = select(SelectedDateModel).where(SelectedDateModel.user_id == user_id)
                execution_result = await session.execute(statement)
                date_rows = execution_result.scalars().all()
            except SQLAlchemyError as error:
                logger.error(f"Failed to retrieve dates for the user from database: user_id={user_id}.", exc_info=True)
                raise exceptions.NotImplementedError("Failed to retrieve dates for the user from database.") from error

        if date_rows:
            for date_row in date_rows:
                date_item = DateItemSchema(
                    calendar_date=date_row.calendar_date,
                    color_bg=date_row.color_bg,
                    color_text=date_row.color_text
                )
                dates.append(date_item)

        logger.info(f"Successfully retrieved dates for the user: user_id={user_id}.")
        return dates
