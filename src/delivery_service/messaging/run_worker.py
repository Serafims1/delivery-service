import asyncio

from delivery_service.database.session import async_session_factory
from delivery_service.database.uow import UnitOfWork
from delivery_service.integrations.exchange_rate import ExchangeRateClient
from delivery_service.integrations.redis import create_redis_client
from delivery_service.messaging.consumer import ParcelCreatedConsumer
from delivery_service.messaging.rabbitmq import (
    create_channel_and_queue,
    create_rabbitmq_connection,
)
from delivery_service.repositories.parcel import ParcelRepository
from delivery_service.services.delivery_cost import DeliveryCostService
from delivery_service.services.exchange_rate import ExchangeRateService


async def main() -> None:
    connection = await create_rabbitmq_connection()
    channel, queue = await create_channel_and_queue(connection)

    redis_client = create_redis_client()
    exchange_rate_client = ExchangeRateClient()

    async with async_session_factory() as session:
        parcel_repo = ParcelRepository(session)
        uow = UnitOfWork(session)

        rate_service = ExchangeRateService(
            redis_client=redis_client,
            exchange_rate_client=exchange_rate_client,
        )

        delivery_cost_service = DeliveryCostService(
            parcel_repo=parcel_repo,
            rate_service=rate_service,
            uow=uow,
        )

        consumer = ParcelCreatedConsumer(
            queue=queue,
            delivery_cost_service=delivery_cost_service,
        )

        await consumer.consume()


if __name__ == "__main__":
    asyncio.run(main())
