import time
import secrets
from functools import lru_cache
from src.app.core.config import settings as global_settings


class Session:
    def __init__(self, user: dict, created_at: int, expires_at: int) -> None:
        self.user = user
        self.created_at = created_at
        self.expires_at = expires_at

    def set_expires_at(self, value: int) -> None:
        self.expires_at = value


class SessionService:
    def __init__(self, ttl: int = global_settings.SESSION_TTL) -> None:
        self.store = {}
        self.ttl = ttl

    def create_session(self, user: dict) -> str:
        sid = secrets.token_urlsafe(32)
        session = Session(user, int(time.time()), int(time.time()) + self.ttl)
        self.store[sid] = session
        return sid

    def get_session(self, sid: str, refresh: bool = False) -> Session | None:
        session: Session = self.store.get(sid)
        if not session:
            return None
        if session.expires_at < int(time.time()):
            return self.store.pop(sid, None)
        if refresh:
            session.set_expires_at(int(time.time() + self.ttl))
        return session
    
    def remove_session(self, session_id: str) -> None:
        return self.store.pop(session_id, None)


@lru_cache
def get_session_service() -> SessionService:
    return SessionService()
