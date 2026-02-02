import time
from pydantic import BaseModel
from src.app.core.settings import settings


class Session(BaseModel):
    user: dict
    created_at: int = int(time.time())
    expires_at: int = created_at + settings.SESSION_TTL
