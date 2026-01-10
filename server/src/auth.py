import os
from dotenv import load_dotenv
from typing import Annotated
import json
import jwt
from aiohttp import ClientSession, ClientError, TCPConnector
from fastapi import HTTPException, Depends, APIRouter, Cookie, Response
from fastapi.responses import RedirectResponse, JSONResponse
from sessions import UserSession
import secrets
import urllib
from deps import get_current_user_session, get_user_sessions


load_dotenv()
APP_ENV = os.getenv("APP_ENV")
APP_CLIENT_URL = os.getenv("APP_CLIENT_URL")
DOMAIN = os.getenv("AUTH0_DOMAIN")
AUDIENCE = os.getenv("AUTH0_AUDIENCE")
ALGORITHMS = os.getenv("AUTH0_ALGORITHMS")
JWKS = os.getenv("AUTH0_JWKS")
CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
REDIRECT_URI = os.getenv("AUTH0_REDIRECT_URI")
SCOPE = os.getenv("AUTH0_SCOPE")
TOKEN_URL = f"{DOMAIN.rstrip('/')}/oauth/token"

auth_router = APIRouter()


class AuthError(HTTPException):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail


@auth_router.get("/me")
async def me(session: dict = Depends(get_current_user_session)) -> dict:
    if not session:
        raise HTTPException(status_code=401, detail="Unauthenticated")
    return {"ok": True, "user": session["user"]}


@auth_router.get("/login")
async def login(auth_state: str = Cookie(None)) -> RedirectResponse:
    state = auth_state or secrets.token_urlsafe(32)
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "audience": AUDIENCE,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "state": state,
        "prompt": "select_account"
    }
    url = f"{DOMAIN}authorize?{urllib.parse.urlencode(params)}"
    res = RedirectResponse(url)
    res.set_cookie("auth_state", state, httponly=True, secure=False, samesite="lax", max_age=300, path="/")
    return res


@auth_router.get("/login/callback")
async def callback(
    code: str | None = None, 
    state: str | None = None, 
    auth_state: str| None = Cookie(None),
    user_session = Depends(get_user_sessions)
):
    if not code or not state or not auth_state or state != auth_state:
        raise AuthError(400, "Invalid state or missing code")
    
    connector = None
    if APP_ENV == "development":
        connector = TCPConnector(ssl=False)

    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        async with ClientSession(connector=connector) as session:
            async with session.post(TOKEN_URL, headers=headers, data=data) as response:
                if response.status != 200:
                    raise AuthError(401, "Fetch JWT from Auth0 error.")
                
                body = await response.json()
                jwt = body.get("id_token")

                if not jwt:
                    raise AuthError(401, "Can't find id_token in response body.")
                
                jwt_valid = await validate_jwt(jwt)
                print("jwt_valid", jwt_valid)
                sid = user_session.create_session(jwt_valid)
    except json.JSONDecodeError as err:
        raise AuthError(401, str(err))
    except ClientError as err:
        raise AuthError(401, "Failed to obtain JWT from Auth0")
        
    redirect_res = RedirectResponse(APP_CLIENT_URL, status_code=302)
    redirect_res.set_cookie("sid", sid, httponly=True, secure=False, samesite="lax", max_age=1000, path="/")
    redirect_res.delete_cookie("auth_state", path="/")

    return redirect_res


@auth_router.post("/logout")
async def logout(
    res: Response, 
    sid: str | None = Cookie(None),
    user_session = Depends(get_user_sessions)
):
    user_session.remove_session(sid)
    params = {"client_id": CLIENT_ID, "returnTo": "http://localhost:3000"}
    url = f"{DOMAIN}v2/logout?{urllib.parse.urlencode(params)}"
    return JSONResponse({"redirectTo": url})


async def fetch_jwks(url: str) -> dict:
    """Fetch JWKS from the Auth0 API"""

    connector = None
    if APP_ENV == "development":
        connector = TCPConnector(ssl=False)

    try:
        async with ClientSession(connector=connector) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise AuthError(401, f"Failed to obtain JWKS from Auth0: HTTP {resp.status}")
                jwks = await resp.json(content_type=None)
                return jwks
    except json.JSONDecodeError as err:
        raise AuthError(401, "Invalid JWKS JSON") from err
    except ClientError as err:
        raise AuthError(401, "Failed to obtain JWKS from Auth0") from err


async def validate_jwt(token):
    """JSON Web Token validation"""
    
    if not all([DOMAIN, AUDIENCE, ALGORITHMS, JWKS]):
        raise AuthError(401, "Missing required config variable(s)")

    jwks = await fetch_jwks(JWKS)
    unverified_header = jwt.get_unverified_header(token)

    jwt_kid = unverified_header.get("kid")
    if not jwt_kid:
        raise AuthError(401, 'Missing "kid" (key ID) in JWT header')
    
    public_key = None
    is_jwk_found = False

    for jwk in jwks["keys"]:
        if jwk["kid"] == jwt_kid:
            try:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
                is_jwk_found = True
                break
            except Exception as err:
                raise AuthError(401, "Failed to create PSA public key from JWK") from err

    if not is_jwk_found:
        raise AuthError(401, "Unable to find JWK for JWT kid")

    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=ALGORITHMS,
            audience=CLIENT_ID,
            issuer=DOMAIN,
            leeway=5
        )
        return payload
    except jwt.ExpiredSignatureError as err:
        raise AuthError(401, "Token is expired") from err
    except jwt.InvalidAudienceError as err:
        raise AuthError(401, "Incorrect audience, please check the audience") from err
    except jwt.InvalidIssuerError as err:
        raise AuthError(401, "Incorrect issuer, please check the issuer") from err
    except Exception as err:
        raise AuthError(401, "Unable to parse authentication token") from err
