from decimal import Decimal

import httpx

from delivery_service.core.config import get_settings


class ExchangeRateClient:
    async def get_usd_rub_rate(self) -> Decimal:
        settings = get_settings()

        async with httpx.AsyncClient(
            timeout=settings.exchange_rate.request_timeout_seconds
        ) as client:
            response = await client.get(settings.exchange_rate.url)

            response.raise_for_status()

            data = response.json()

            usd = data["Valute"]["USD"]

            value = Decimal(str(usd["Value"]))
            nominal = Decimal(str(usd["Nominal"]))

            return value / nominal
