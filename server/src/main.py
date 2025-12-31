from typing import Annotated
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Body

from auth import requires_auth
from schemas import DateBatchRequestSchema, DateBatchResponseSchema, DateOperationSchema, DateItemSchema, DatesByUserSchema
from database import DatabaseProvider as dp


@asynccontextmanager
async def lifespan(app: FastAPI):
    await dp.initialize_database()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/api/v1/users/me/dates", response_model=DatesByUserSchema)
async def get_dates_by_user(token: Annotated[str, Depends(requires_auth)]) -> DatesByUserSchema:
    user_id = token["sub"]

    try:
        dates: list[DateItemSchema] = await dp.get_dates_by_user(user_id)
    except Exception as err:
        return DatesByUserSchema(ok=False, message=repr(err))
    return DatesByUserSchema(ok=True, items=dates)


@app.post("/api/v1/dates/batch", response_model=DateBatchResponseSchema)
async def process_batch(
    token: Annotated[str, Depends(requires_auth)],
    payload: DateBatchRequestSchema = Body(...)
) -> DateBatchResponseSchema:
    user_id = token["sub"]
    batch: list[DateOperationSchema] = payload.batch

    try:
        results = await dp.process_batch(user_id, batch)
    except Exception as err:
        return DateBatchResponseSchema(ok=False, message=str(err))
    return DateBatchResponseSchema(ok=True, results=results)
