import json
from aiohttp import TCPConnector, ClientSession

import redis

from src.app.core.settings import Environment, settings
from src.app.core.redis import async_redis
from src.app.auth.exceptions import (
    AuthTokenUnsuccessfulResponseError,
    AuthTokenJsonDecodeError,
    AuthTokenIdTokenNotFoundError
)


async def fetch_token(code: str) -> dict:
    connector = None
    if settings.ENVIRONMENT == Environment.DEVELOPMENT:
        connector = TCPConnector(ssl=False)
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    request_body = {
        "client_id": settings.AUTH0_CLIENT_ID,
        "client_secret": settings.AUTH0_CLIENT_SECRET.get_secret_value(),
        "code": code,
        "redirect_uri": settings.AUTH0_REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    async with ClientSession(connector=connector) as session:
        async with session.post(settings.AUTH0_TOKEN_URL, headers=headers, data=request_body) as response:
            if response.status != 200:
                # Log it.
                raise AuthTokenUnsuccessfulResponseError

            try:
                body: dict = await response.json()
            except json.JSONDecodeError as error:
                # Log it.
                raise AuthTokenJsonDecodeError from error

    id_token = body.get("id_token")

    if not id_token:
        # Log it.
        raise AuthTokenIdTokenNotFoundError
    # Log it.
    return id_token


async def fetch_jwks() -> dict:
    jwks_from_redis = None

    try:
        jwks_from_redis = await async_redis.client.get(settings.DB_REDIS_KEY_JWKS)
    except redis.ConnectionError as error:
        # Log it.
        pass

    if jwks_from_redis:
        try:
            jwks_dict = json.loads(jwks_from_redis)
            # Log it.
            return jwks_dict
        except json.JSONDecodeError as error:
            # Log it.
            pass

    connector = None
    if settings.ENVIRONMENT == Environment.DEVELOPMENT:
        connector = TCPConnector(ssl=False)

    async with ClientSession(connector=connector) as session:
        async with session.get(settings.AUTH0_JWKS_URL) as response:
            if response.status != 200:
                raise AuthTokenUnsuccessfulResponseError
            
            try:
                jwks_dict = await response.json()
            except json.JSONDecodeError as error:
                # Log it.
                raise AuthTokenJsonDecodeError from error
            
    jwks_json_str = json.dumps(jwks_dict, ensure_ascii=False)

    try:
        await async_redis.client.set(
            name=settings.DB_REDIS_KEY_JWKS, 
            value=jwks_json_str, 
            ex=settings.DB_REDIS_TTL_JWKS
        )
    except redis.ConnectionError as error:
        # Log it.
        pass

    return jwks_dict
