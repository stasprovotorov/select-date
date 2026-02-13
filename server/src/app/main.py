from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.app.core.logs import setup_logging
from src.app.core.database import db
from src.app.core.redis import redis_adapter
from src.app.core.settings import settings
from src.app.core.exceptions import ApplicationBaseError
from src.app.auth.router import router as auth_router
from src.app.calendar.router import router as calendar_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await db.initialize_database()
    await redis_adapter.ping()
    yield
    await db.shutdown_database()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.APP_FRONTEND_BASE_URL],
    allow_credentials=settings.APP_BACKEND_ALLOW_CREDENTIALS,
    allow_methods=[settings.APP_BACKEND_ALLOW_METHODS],
    allow_headers=[settings.APP_BACKEND_ALLOW_HEADERS]
)


@app.exception_handler(ApplicationBaseError)
async def application_error_handler(_: Request, exc: ApplicationBaseError):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.message})


app.include_router(auth_router)
app.include_router(calendar_router)
