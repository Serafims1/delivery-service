from loguru import logger
from redis.asyncio import Redis
from redis.exceptions import RedisError

from delivery_service.core.config import get_settings


class IdempotencyService:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    def _build_key(self, session_id: str, key: str) -> str:
        return f"idempotency:parcel:create:{session_id}:{key}"

    async def acquire(self, session_id: str, key: str) -> bool:
        settings = get_settings()
        redis_key = self._build_key(session_id, key)

        res = await self.redis_client.set(
            redis_key, "processing", nx=True, ex=settings.redis.idempotency_ttl_seconds
        )

        return bool(res)

    async def release(self, session_id: str, key: str) -> None:
        redis_key = self._build_key(session_id, key)

        await self.redis_client.delete(redis_key)

    async def success_result(self, session_id: str, key: str, parcel_id: int) -> None:
        settings = get_settings()
        redis_key = self._build_key(session_id, key)

        answer = f"done:{parcel_id}"

        try:
            await self.redis_client.set(
                redis_key, answer, ex=settings.redis.idempotency_ttl_seconds
            )
        except RedisError:
            logger.exception(
                "Failed to save idempotency result | parcel_id={}",
                parcel_id,
            )

    async def repeat_request_answer(self, session_id: str, key: str) -> int | None:
        redis_key = self._build_key(session_id, key)

        res = await self.redis_client.get(redis_key)

        if res is None:
            return None

        if isinstance(res, bytes):
            res = res.decode()

        if res == "processing":
            return None

        if not res.startswith("done:"):
            return None

        parcel_id = res.removeprefix("done:")

        if not parcel_id.isdigit():
            return None

        return int(parcel_id)
