import time
import secrets

class UserSession:
    def __init__(self, ttl: int = 3600) -> None:
        self.sessions = {}
        self.ttl = ttl

    def create_session(self, user: dict) -> str:
        sid = secrets.token_urlsafe(32)
        self.sessions[sid] = {
            "user": user,
            "created_at": int(time.time()),
            "expires_at": int(time.time()) + self.ttl
        }
        return sid

    def get_session(self, sid: str | None) -> dict:
        if not sid:
            return None
        session = self.sessions.get(sid)
        if not session:
            return None
        if session["expires_at"] < int(time.time()):
            del self.sessions[sid]
            return None
        session["expires_at"] = int(time.time()) + self.ttl
        return session

    def remove_session(self, sid: str) -> None:
        self.sessions.pop(sid, None)
