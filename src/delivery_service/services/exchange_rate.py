from contextlib import suppress
from decimal import Decimal

from redis.asyncio import Redis
from redis.exceptions import RedisError

from delivery_service.core.config import get_settings
from delivery_service.integrations.exchange_rate import ExchangeRateClient

EXCHANGE_RATE_CACHE_KEY = "exchange_rate:USD:RUB"


class ExchangeRateService:
    def __init__(self, redis_client: Redis, exchange_rate_client: ExchangeRateClient):
        self.redis_client = redis_client
        self.exchange_rate_client = exchange_rate_client

    async def get_usd_rub_rate(self) -> Decimal:
        settings = get_settings()

        try:
            cached_rate = await self.redis_client.get(EXCHANGE_RATE_CACHE_KEY)
        except RedisError:
            cached_rate = None

        if cached_rate is not None:
            if isinstance(cached_rate, bytes):
                cached_rate = cached_rate.decode()

            return Decimal(cached_rate)

        rate = await self.exchange_rate_client.get_usd_rub_rate()

        with suppress(RedisError):
            await self.redis_client.set(
                EXCHANGE_RATE_CACHE_KEY,
                str(rate),
                ex=settings.redis.exchange_rate_ttl_seconds,
            )

        return rate
