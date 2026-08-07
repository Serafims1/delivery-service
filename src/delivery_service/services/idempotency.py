from redis.asyncio import Redis

from delivery_service.core.config import get_settings


class IdempotencyService:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def acquire(self, key: str) -> bool:
        settings = get_settings()

        res = await self.redis_client.set(
            key, "processing", nx=True, ex=settings.redis.idempotency_ttl_seconds
        )

        return bool(res)

    async def release(self, key: str) -> None:
        await self.redis_client.delete(key)

    async def success_result(self, key: str, parcel_id: int) -> None:
        settings = get_settings()

        answer = f"done:{parcel_id}"

        await self.redis_client.set(
            key, answer, ex=settings.redis.idempotency_ttl_seconds
        )

    async def repeat_request_answer(self, key: str) -> int | None:
        res = await self.redis_client.get(key)

        if res is None:
            return None

        if isinstance(res, bytes):
            res = res.decode()

        if res == "processing":
            return None

        parts = res.split(":")
        return int(parts[1])
