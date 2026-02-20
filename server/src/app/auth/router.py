import secrets

from fastapi import APIRouter, Depends, Cookie
from fastapi.responses import Response, RedirectResponse

from src.app.auth.service import SessionService
from src.app.auth.schemas import SessionSchema
from src.app.auth.dependencies import require_auth, validate_state, get_authorized_user, get_session_service
from src.app.auth.utils import build_login_uri
from src.app.core.config import settings


router = APIRouter(prefix="/api/v1/auth")


@router.get("/me")
async def me(user: dict = Depends(require_auth)) -> dict:
    return user


@router.get("/login")
async def login(auth_state: str | None = Cookie(None)) -> RedirectResponse:
    auth_state = auth_state or secrets.token_urlsafe(32)
    login_uri = build_login_uri(auth_state)
    response = RedirectResponse(login_uri)
    response.set_cookie(key="auth_state", value=auth_state, path="/", secure=False, httponly=True, samesite="lax")
    return response


@router.get("/login/callback", dependencies=[Depends(validate_state)])
async def login_callback(
    user: dict = Depends(get_authorized_user),
    session_service: SessionService = Depends(get_session_service),
) -> RedirectResponse:
    session: SessionSchema =  await session_service.set_session(user)
    response = RedirectResponse(url=settings.APP_FRONTEND_BASE_URL, status_code=302)
    response.set_cookie(key="sid", value=session.id, max_age=settings.SESSION_TTL, path="/", secure=False, httponly=True, samesite="lax")
    response.delete_cookie(key="auth_state", path="/")
    return response


@router.post("/logout")
async def logout(
    response: Response,
    sid: str | None = Cookie(None),
    session_service: SessionService = Depends(get_session_service),
) -> dict:
    await session_service.delete_session(sid)
    response.delete_cookie(key="sid", path="/", secure=False, httponly=True, samesite="lax")
    return {"redirectTo": settings.AUTH0_LOGOUT_URI}
