from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth import auth_router
from dates import dates_router
from database import DatabaseProvider as dp

@asynccontextmanager
async def lifespan(app: FastAPI):
    await dp.initialize_database()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(dates_router, tags=["calendar"])
