from redis.asyncio import Redis, ConnectionError
from src.app.core.config import settings


class AsyncRedis:
    def __init__(self, host: str, port: int, decode_responses: bool) -> None:
        self.host = host
        self.port = port
        self.decode_responses = decode_responses
        self.client = Redis(
            host=self.host,
            port=self.port,
            decode_responses=self.decode_responses
        )

    async def check_redis_server_connection(self):
        try:
            await self.client.ping()
            # Log it.
        except ConnectionError:
            # Log it.
            raise


async_redis = AsyncRedis(
    host=settings.DB_REDIS_HOST, 
    port=settings.DB_REDIS_PORT, 
    decode_responses=settings.DB_REDIS_DECODE_RESPONSES
)
