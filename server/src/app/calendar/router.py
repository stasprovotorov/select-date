from fastapi import APIRouter, Depends, Body
from src.app.calendar.schemas import DatesByUserSchema, DateBatchResponseSchema, DateBatchRequestSchema
from src.app.auth.dependencies import require_auth
from src.app.calendar.dependencies import get_sqlalchemy_repository
from src.app.calendar.service import CalendarService

router = APIRouter(prefix="/api/v1")


@router.get("/user/me/dates", response_model=DatesByUserSchema)
async def get_dates_by_user(
    user: dict = Depends(require_auth),
    repository = Depends(get_sqlalchemy_repository)
) -> DatesByUserSchema:
    service = CalendarService(repository)
    user_id = user["sub"]
    
    try:
        dates_by_user = await service.get_dates_by_user(user_id)
    except Exception as err:
        return DatesByUserSchema(ok=False, message=str(err))
    return DatesByUserSchema(ok=True, item=dates_by_user)


@router.post("/dates/bacth", response_model=DateBatchResponseSchema)
async def process_date_batch(
    user: dict = Depends(require_auth),
    payload: DateBatchRequestSchema = Body(...),
    repository = Depends(get_sqlalchemy_repository)
) -> DateBatchResponseSchema:
    service = CalendarService(repository)
    user_id = user["sub"]
    batch = payload.batch

    try:
        result = await service.procces_dates(user_id, batch)
    except Exception as err:
        return DateBatchResponseSchema(ok=False, message=str(err))
    return DateBatchResponseSchema(ok=True, result=result)
