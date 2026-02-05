from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app.core.logs import setup_logging
from src.app.core.database import async_db
from src.app.core.redis import async_redis
from src.app.core.settings import settings
from src.app.auth.router import router as auth_router
from src.app.calendar.router import router as calendar_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await async_db.initialize_async_database()
    await async_redis.check_redis_server_connection()
    yield
    await async_db.shutdown_async_database()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.APP_FRONTEND_BASE_URL],
    allow_credentials=settings.APP_BACKEND_ALLOW_CREDENTIALS,
    allow_methods=[settings.APP_BACKEND_ALLOW_METHODS],
    allow_headers=[settings.APP_BACKEND_ALLOW_HEADERS]
)

app.include_router(auth_router)
app.include_router(calendar_router)
