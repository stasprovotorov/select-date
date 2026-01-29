import json
from aiohttp import TCPConnector, ClientSession, ClientError
from src.app.auth.exceptions import AuthTokenError
from src.app.core.config import Environment
from src.app.core.config import settings as global_settings
from src.app.auth.config import settings as auth_settings
from src.app.core.redis import async_redis


async def fetch_token(code: str) -> dict:
    connector = None
    if global_settings.ENVIRONMENT == Environment.DEVELOPMENT:
        connector = TCPConnector(ssl=False)
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    request_body = {
        "client_id": auth_settings.CLIENT_ID,
        "client_secret": auth_settings.CLIENT_SECRET.get_secret_value(),
        "code": code,
        "redirect_uri": auth_settings.REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    try:
        async with ClientSession(connector=connector) as session:
            async with session.post(auth_settings.TOKEN_URL, headers=headers, data=request_body) as response:
                if response.status != 200:
                    raise AuthTokenError(f"Failed to fetch token from Auth0. HTTP code: {response.status}.")

                try:
                    response_body = await response.json()
                except Exception as err:
                    AuthTokenError(401, f"Failed to parse response as JSON. Error message: {err}")

                id_token = response_body.get("id_token")

                if not id_token:
                    raise AuthTokenError(401, "Failed to find id_token in response body.")
                
                return id_token
            
    except ClientError as err:
        raise AuthTokenError(401, f"Failed to request token from Auth0. Error message: {err}")


async def fetch_jwks() -> dict:
    jwks_from_redis = await async_redis.client.get(global_settings.DB_REDIS_KEY_JWKS)

    if jwks_from_redis:
        jwks_dict = json.loads(jwks_from_redis)
        return jwks_dict

    connector = None
    if global_settings.ENVIRONMENT == Environment.DEVELOPMENT:
        connector = TCPConnector(ssl=False)

    try:
        async with ClientSession(connector=connector) as session:
            async with session.get(auth_settings.JWKS_URL) as response:
                if response.status != 200:
                    raise AuthTokenError(401, f"Failed to obtain JWKS from Auth0: HTTP {response.status}")
                
                try:
                    jwks_dict = await response.json(content_type=None)
                    jwks_json_str = json.dumps(jwks_dict, ensure_ascii=False)

                    await async_redis.client.set(
                        name=global_settings.DB_REDIS_KEY_JWKS, 
                        value=jwks_json_str, 
                        ex=global_settings.DB_REDIS_TTL_JWKS
                    )

                    return jwks_dict
                except Exception as err:
                    AuthTokenError(401, f"Failed to parse response as JSON. Error message: {err}")

    except ClientError as err:
        raise AuthTokenError(401, f"Failed to request JWKS from Auth0. Error message: {err}")
