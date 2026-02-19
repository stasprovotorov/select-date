from datetime import datetime

from pydantic import BaseModel


class SessionSchema(BaseModel):
    id: str
    user: str
    created_at: datetime
    expires_at: datetime
