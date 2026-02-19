import logging

from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.exc import OperationalError, IntegrityError, SQLAlchemyError

from src.app.calendar.schemas import DateOperationType, DateOperationSchema, DateItemSchema, DateOperationResultSchema
from src.app.calendar.models import SelectedDateModel
from src.app.core.database import db
from src.app.core import exceptions

logger = logging.getLogger(__name__)


class CalendarSQLAlchemyRepository:
    def __init__(self, db_sessionmaker: async_sessionmaker):
        self.db_sessionmaker = db_sessionmaker

    async def process_batch(self, user_id: str, batch: list[DateOperationSchema]) -> list[DateOperationResultSchema]:
        batch_results: list[DateOperationResultSchema] = []

        logger.info("Start batch processing: operation_count=%s", len(batch))
        async with self.db_sessionmaker.begin() as db_session:
            db_session: AsyncSession

            for date_oper in batch:
                date_oper: DateOperationSchema
                savepoint = await db_session.begin_nested()

                try:
                    date_item: DateItemSchema = date_oper.item

                    if date_oper.oper_type == DateOperationType.INSERT:
                        statement = (
                            insert(SelectedDateModel)
                            .values(
                                user_id=user_id,
                                calendar_date=date_item.calendar_date,
                                color_bg=date_item.color_bg,
                                color_text=date_item.color_text,
                            )
                            .returning(SelectedDateModel.__table__.columns)
                        )
                    elif date_oper.oper_type == DateOperationType.DELETE:
                        statement = (
                            delete(SelectedDateModel)
                            .where(
                                SelectedDateModel.user_id == user_id,
                                SelectedDateModel.calendar_date == date_item.calendar_date,
                            )
                            .returning(SelectedDateModel.__table__.columns)
                        )

                    execution_result = await db_session.execute(statement)
                    processed_date_item = execution_result.mappings().first()

                    if not processed_date_item and date_oper.oper_type == DateOperationType.DELETE:
                        raise exceptions.NotFoundError("Date for user was not found")
                    
                    result_date_item = DateItemSchema(
                        calendar_date=processed_date_item["calendar_date"],
                        color_bg=processed_date_item["color_bg"],
                        color_text=processed_date_item["color_text"],
                    )
                    result_date_oper = DateOperationSchema(
                        oper_type=date_oper.oper_type,
                        item=result_date_item,
                    )
                    batch_results.append(DateOperationResultSchema(ok=True, operation=result_date_oper))

                    await savepoint.commit()
                except exceptions.NotFoundError as err:
                    await savepoint.rollback()
                    logger.exception("Date to be removed for user was not found")
                    batch_results.append(DateOperationResultSchema(ok=False, operation=date_oper, message=str(err)))
                except IntegrityError as err:
                    await savepoint.rollback()
                    logger.exception("Date to be add for user already exists")
                    batch_results.append(DateOperationResultSchema(ok=False, operation=date_oper, message="Date for user already exists"))
                except OperationalError as err:
                    await savepoint.rollback()
                    logger.exception("Database unavailable")
                    batch_results.append(DateOperationResultSchema(ok=False, operation=date_oper, message="Database unavailable"))
                except SQLAlchemyError as err:
                    await savepoint.rollback()
                    logger.exception("Unexpected database error")
                    batch_results.append(DateOperationResultSchema(ok=False, operation=date_oper, message="Unexpected database error"))

        logger.info(f"Finish batch processing")
        return batch_results

    async def get_dates_for_user(self, user_id: str) -> list[DateItemSchema]:
        dates: list[DateItemSchema] = []

        logger.info("Retrieving dates for user")
        async with self.db_sessionmaker() as db_session:
            db_session: AsyncSession

            try:
                statement = select(SelectedDateModel).where(SelectedDateModel.user_id == user_id)
                execution_result = await db_session.execute(statement)
                date_rows = execution_result.scalars().all()
            except OperationalError as err:
                logger.exception("Database unavailable")
                raise exceptions.ServiceUnavailableError("Database unavailable") from err
            except SQLAlchemyError as err:
                logger.exception("Unexpected database error")
                raise exceptions.NotImplementedError("Unexpected database error") from err

        if date_rows:
            for date_row in date_rows:
                date_item = DateItemSchema(
                    calendar_date=date_row.calendar_date,
                    color_bg=date_row.color_bg,
                    color_text=date_row.color_text,
                )
                dates.append(date_item)
            logger.info("Successfully retrieved dates for user: date_count=%s", len(dates))
        else:
            logger.info("Dates were not found for user")

        return dates


calendar_repo = CalendarSQLAlchemyRepository(db_sessionmaker=db.sessionmaker)
