from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from delivery_service.core.config import get_settings
from delivery_service.services.exchange_rate import (
    EXCHANGE_RATE_CACHE_KEY,
    ExchangeRateService,
)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_usd_rub_rate_from_cache() -> None:
    redis_client = AsyncMock()
    exchange_rate_client = AsyncMock()

    redis_client.get.return_value = "81.4077"

    service = ExchangeRateService(redis_client, exchange_rate_client)

    result = await service.get_usd_rub_rate()

    assert result == Decimal("81.4077")
    redis_client.get.assert_awaited_once_with(EXCHANGE_RATE_CACHE_KEY)
    exchange_rate_client.get_usd_rub_rate.assert_not_awaited()
    redis_client.set.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_usd_rub_rate_from_external_api_and_cache_it() -> None:
    settings = get_settings()

    redis_client = AsyncMock()
    exchange_rate_client = AsyncMock()

    redis_client.get.return_value = None
    exchange_rate_client.get_usd_rub_rate.return_value = Decimal("81.4077")

    service = ExchangeRateService(redis_client, exchange_rate_client)

    result = await service.get_usd_rub_rate()

    assert result == Decimal("81.4077")
    redis_client.get.assert_awaited_once_with(EXCHANGE_RATE_CACHE_KEY)
    exchange_rate_client.get_usd_rub_rate.assert_awaited_once_with()
    redis_client.set.assert_awaited_once_with(
        EXCHANGE_RATE_CACHE_KEY,
        "81.4077",
        ex=settings.redis.exchange_rate_ttl_seconds,
    )
