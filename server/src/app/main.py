from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.database import async_db
from src.app.config import settings as global_settings
from src.app.auth.router import router as auth_router
from src.app.calendar.router import router as calendar_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await async_db.initialize_async_database()
    yield
    await async_db.shutdown_async_database()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[global_settings.APP_FRONTEND_BASE_URL],
    allow_credentials=global_settings.APP_BACKEND_ALLOW_CREDENTIALS,
    allow_methods=[global_settings.APP_BACKEND_ALLOW_METHODS],
    allow_headers=[global_settings.APP_BACKEND_ALLOW_HEADERS]
)

app.include_router(auth_router)
app.include_router(calendar_router)
