import logging

from redis.asyncio import Redis, ConnectionError

from src.app.core.config import settings
from src.app.core import exceptions

logger = logging.getLogger(__name__)


class RedisAdapter:
    # TODO Password requirement for production
    def __init__(self, host: str, port: int, decode_responses: bool = True) -> None:
        self.redis_client = Redis(host=host, port=port, decode_responses=decode_responses)

    async def ping(self) -> None:
        try:
            await self.redis_client.ping()
            logger.info("Successfully connected to Redis")
        except ConnectionError as err:
            logger.exception("Redis connection failed")
            raise exceptions.ServiceUnavailableError("Redis unavailable") from err

    async def set(self, key: str, value: str, ttl: int | None = None) -> bool:
        try:
            result: bool = await self.redis_client.set(key, value, ttl)
            logger.info("Set value in Redis")
            return result
        except ConnectionError as err:
            logger.exception("Failed to set value in Redis")
            raise exceptions.ServiceUnavailableError("Redis unavailable") from err
    
    async def get(self, key: str) -> str | None:
        logger.info("Retrieving value from Redis")
        try:
            value: str = await self.redis_client.get(key)
            return value
        except ConnectionError as err:
            logger.exception("Failed to get value from Redis")
            raise exceptions.ServiceUnavailableError("Redis unavailable") from err
    
    async def delete(self, key: str) -> bool:
        try:
            result: int = await self.redis_client.delete(key)
            if result == 1:
                logger.info("Removed value from Redis")
                return True
            logger.warning("Key to be removed was not found in Redis")
            return False
        except ConnectionError as err:
            logger.exception("Failed to remove value from Redis")
            raise exceptions.ServiceUnavailableError("Redis unavailable") from err


redis_adapter = RedisAdapter(
    host=settings.DB_REDIS_HOST, 
    port=settings.DB_REDIS_PORT,
    decode_responses=settings.DB_REDIS_DECODE_RESPONSES,
)
