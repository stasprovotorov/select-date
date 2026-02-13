from datetime import datetime

from pydantic import BaseModel


class UserSessionSchema(BaseModel):
    id: str
    user: str
    created_at: datetime
    expires_at: datetime
