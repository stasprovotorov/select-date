import logging
import json
from aiohttp import TCPConnector, ClientSession

import redis

from src.app.core.settings import Environment, settings
from src.app.core.redis import async_redis
from src.app.core import exceptions

logger = logging.getLogger(__name__)


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
                logger.error(f"Failed to retrieve JWT from Auth0: response_code={response.status}")
                raise exceptions.ServiceUnavailableError(f"Unsuccessful response code {response.status} from Auth0 API.")

            try:
                body: dict = await response.json()
            except json.JSONDecodeError as error:
                logger.error("Error decoding Auth0 response for the JWT request.", exc_info=True)
                raise exceptions.UnprocessableEntityError("Failed to decode response body from Auth0 to JSON.") from error

    id_token = body.get("id_token")

    if not id_token:
        logger.error("No 'id_token' found in the Auth0 response to the JWT request.")
        raise exceptions.UnauthorizedError("ID token not found in response body.")
    
    logger.info("JWT successfully obtained and decoded.")
    return id_token


async def fetch_jwks() -> dict:
    jwks_from_redis = None

    try:
        jwks_from_redis = await async_redis.client.get(settings.DB_REDIS_KEY_JWKS)
        logger.info("Retrieved JWKS from Redis.")
    except redis.ConnectionError as error:
        logger.warning("Failed to retrieve JWKS from Redis: no connection to the server.")

    if jwks_from_redis:
        try:
            jwks_dict = json.loads(jwks_from_redis)
            logger.info("JWKS successfully decoded.")
            return jwks_dict
        except json.JSONDecodeError as error:
            logger.error("Failed to decode JWKS from Redis.", exc_info=True)

    connector = None
    if settings.ENVIRONMENT == Environment.DEVELOPMENT:
        connector = TCPConnector(ssl=False)

    async with ClientSession(connector=connector) as session:
        async with session.get(settings.AUTH0_JWKS_URL) as response:
            if response.status != 200:
                logger.error(f"Failed to retrieve JWKS from Auth0: response_code={response.status}")
                raise exceptions.ServiceUnavailableError(f"Unsuccessful response code {response.status} from Auth0 API.")
            
            try:
                jwks_dict = await response.json()
            except json.JSONDecodeError as error:
                logger.error("Failed to decode JWKS from Auth0.", exc_info=True)
                raise exceptions.UnprocessableEntityError("Failed to decode response body from Auth0 to JSON.") from error
            
    jwks_json_str = json.dumps(jwks_dict, ensure_ascii=False)

    try:
        await async_redis.client.set(
            name=settings.DB_REDIS_KEY_JWKS, 
            value=jwks_json_str, 
            ex=settings.DB_REDIS_TTL_JWKS
        )
        logger.info("JWKS stored in Redis.")
    except redis.ConnectionError as error:
        logger.warning("Failed to store JWKS in Redis: no connection to the server.")

    logger.info("JWKS successfully retrieved.")
    return jwks_dict
