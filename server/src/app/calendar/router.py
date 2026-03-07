from fastapi import APIRouter, Depends, Body

from src.app.auth.dependencies import require_auth
from src.app.calendar.schemas import DatesForUserSchema, DateBatchResponseSchema, DateBatchRequestSchema
from src.app.calendar.dependencies import get_calendar_service
from src.app.calendar.service import CalendarService

router = APIRouter(prefix="/api/v1")


@router.get("/users/me/dates", response_model=DatesForUserSchema)
async def get_dates_by_user(
    user: dict = Depends(require_auth),
    service: CalendarService = Depends(get_calendar_service),
) -> dict:
    user_id = user["sub"]
    dates = await service.get_dates_for_user(user_id)
    return {"ok": True, "item": dates}


@router.post("/dates/batch", response_model=DateBatchResponseSchema)
async def process_date_batch(
    user: dict = Depends(require_auth),
    payload: DateBatchRequestSchema = Body(...),
    service: CalendarService = Depends(get_calendar_service),
) -> DateBatchResponseSchema:
    user_id = user["sub"]
    batch = payload.batch

    try:
        result = await service.process_date_operations(user_id, batch)
    except Exception as err:
        return {"ok": False, "message": str(err)}
    return {"ok": True, "result": result}
