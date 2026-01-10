from functools import lru_cache
from fastapi import Depends, Cookie, HTTPException
from sessions import UserSession

@lru_cache
def get_user_session_service() -> UserSession:
    return UserSession()

async def get_current_user_session(
    sid: str | None = Cookie(None),
    user_sessions: UserSession = Depends(get_user_session_service)
):
    if not sid:
        raise HTTPException(status_code=401, detail="Missing sid.")
    session = user_sessions.get_session(sid)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return session


async def get_user_sessions(
    user_sessions: UserSession = Depends(get_user_session_service)
):
    return user_sessions
