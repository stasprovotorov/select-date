from redis.asyncio import Redis
from src.app.core.config import settings as global_settings


client = Redis(
    host=global_settings.DB_REDIS_HOST, 
    port=global_settings.DB_REDIS_PORT, 
    decode_responses=global_settings.DB_REDIS_DECODE_RESPONSES
)
