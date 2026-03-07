import logging
import json
from aiohttp import TCPConnector, ClientSession

from src.app.core.config import Environment, settings
from src.app.core.cache import redis_adapter
from src.app.core import exceptions

logger = logging.getLogger(__name__)


async def fetch_jwt(code: str) -> dict:
    connector = None    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    request_body = {
        "client_id": settings.AUTH0_CLIENT_ID,
        "client_secret": settings.AUTH0_CLIENT_SECRET.get_secret_value(),
        "code": code,
        "redirect_uri": settings.AUTH0_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    if settings.ENVIRONMENT == Environment.DEVELOPMENT:
        connector = TCPConnector(ssl=False)

    async with ClientSession(connector=connector) as session:
        async with session.post(settings.AUTH0_TOKEN_URL, headers=headers, data=request_body) as response:
            if response.status != 200:
                logger.error("Failed to retrieve JWT from Auth0 API: response_code=%s", response.status)
                raise exceptions.ServiceUnavailableError(f"Unsuccessful request to Auth0 API: response code = {response.status}")

            try:
                body: dict = await response.json()
            except json.JSONDecodeError as err:
                logger.exception("Failed to decode Auth0 response body to JSON")
                raise exceptions.UnprocessableEntityError("Failed to decode Auth0 response body to JSON") from err

    id_token = body.get("id_token")

    if not id_token:
        logger.error("No ID token found in the Auth0")
        raise exceptions.NotFoundError("No ID token found in the Auth0")
    
    logger.info("JWT successfully retrieved")
    return id_token


async def fetch_jwks() -> dict:
    jwks = None
    connector = None

    try:
        jwks: str = await redis_adapter.get(settings.DB_REDIS_KEY_JWKS)
        if jwks:
            logger.info("Retrieved JWKS from Redis")
            try:
                jwks = json.loads(jwks)
            except json.JSONDecodeError as err:
                logger.exception("Failed to decode JWKS from Redis")
        else:
            logger.info("JWKS was not found from Redis")
    except Exception:
        logger.exception("Failed to retrieve JWKS from Redis")    
    
    if settings.ENVIRONMENT == Environment.DEVELOPMENT:
        connector = TCPConnector(ssl=False)

    async with ClientSession(connector=connector) as session:
        async with session.get(settings.AUTH0_JWKS_URL) as response:
            if response.status != 200:
                logger.error("Failed to retrieve JWKS from Auth0 API: response_code=%s", response.status)
                raise exceptions.ServiceUnavailableError(f"Unsuccessful response code {response.status} from Auth0")
            
            try:
                jwks = await response.json()
            except json.JSONDecodeError as err:
                logger.exception("Failed to decode JWKS from Auth0")
                raise exceptions.UnprocessableEntityError("Failed to decode response body from Auth0 to JSON") from err
            
    jwks_redis: dict = json.dumps(jwks, ensure_ascii=False)

    try:
        await redis_adapter.set(
            key=settings.DB_REDIS_KEY_JWKS, 
            value=jwks_redis, 
            ttl=settings.DB_REDIS_TTL_JWKS,
        )
        logger.info("JWKS stored in Redis")
    except Exception:
        logger.exception("Failed to store JWKS in Redis")

    logger.info("JWKS successfully retrieved from Auth0")
    return jwks
