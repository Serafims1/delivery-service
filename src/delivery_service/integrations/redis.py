from redis.asyncio import Redis

from delivery_service.core.config import get_settings


def create_redis_client() -> Redis:
    setting = get_settings()
    return Redis(
        host=setting.redis.host,
        port=setting.redis.port,
        db=setting.redis.db,
        decode_responses=True,
    )
