from fastapi import Depends, Body, APIRouter
from schemas import DateBatchRequestSchema, DateBatchResponseSchema, DateOperationSchema, DateItemSchema, DatesByUserSchema
from database import DatabaseProvider as dp
from deps import get_current_user_session

dates_router = APIRouter()

@dates_router.get("/api/v1/users/me/dates", response_model=DatesByUserSchema)
async def get_dates_by_user(
    session: dict = Depends(get_current_user_session)
) -> DatesByUserSchema:
    user_id = session["user"]["sub"]

    try:
        dates: list[DateItemSchema] = await dp.get_dates_by_user(user_id)
    except Exception as err:
        return DatesByUserSchema(ok=False, message=repr(err))
    return DatesByUserSchema(ok=True, item=dates)


@dates_router.post("/api/v1/dates/batch", response_model=DateBatchResponseSchema)
async def process_batch(
    payload: DateBatchRequestSchema = Body(...),
    session: dict = Depends(get_current_user_session)
) -> DateBatchResponseSchema:
    user_id = session["user"]["sub"]
    batch: list[DateOperationSchema] = payload.batch

    try:
        results = await dp.process_batch(user_id, batch)
    except Exception as err:
        return DateBatchResponseSchema(ok=False, message=str(err))
    return DateBatchResponseSchema(ok=True, result=results)
