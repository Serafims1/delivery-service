from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.database.uow import UnitOfWork
from delivery_service.integrations.exchange_rate import ExchangeRateClient
from delivery_service.integrations.redis import create_redis_client
from delivery_service.messaging.consumer import ParcelCreatedConsumer
from delivery_service.messaging.outbox_publisher import OutboxPublisher
from delivery_service.messaging.rabbitmq import (
    create_channel_and_queue,
    create_rabbitmq_connection,
)
from delivery_service.models.outbox_event import OutboxEvent
from delivery_service.models.parcel import Parcel
from delivery_service.models.parcel_type import ParcelType
from delivery_service.repositories.outbox import OutboxRepository
from delivery_service.repositories.parcel import ParcelRepository
from delivery_service.services.delivery_cost import DeliveryCostService
from delivery_service.services.exchange_rate import ExchangeRateService


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delivery_cost_calculated_after_parcel_created(
    client: AsyncClient, parcel_types: list[ParcelType], test_session: AsyncSession
) -> None:
    header = {"Idempotency-Key": str(uuid4())}

    payload = {
        "name": "MacBook",
        "weight": 2.1,
        "parcel_type_id": parcel_types[0].id,
        "content_value_usd": 1800,
    }

    response = await client.post("/api/v1/parcels", json=payload, headers=header)

    assert response.status_code == 201

    parcel_id = response.json()["id"]

    query = (
        select(OutboxEvent)
        .where(OutboxEvent.event_type == "parcel.created")
        .where(OutboxEvent.payload["parcel_id"].as_integer() == parcel_id)
    )

    result = await test_session.execute(query)
    event = result.scalars().one_or_none()

    assert event is not None
    assert event.processed is False

    connection = await create_rabbitmq_connection()
    channel, queue = await create_channel_and_queue(connection)

    outbox_repo = OutboxRepository(test_session)
    publisher_uow = UnitOfWork(test_session)

    publisher = OutboxPublisher(
        outbox_repo=outbox_repo,
        rabbitmq_channel=channel,
        uow=publisher_uow,
    )

    await publisher.publish_pending()

    await test_session.refresh(event)
    assert event.processed is True

    parcel_repo = ParcelRepository(test_session)
    uow = UnitOfWork(test_session)

    redis_client = create_redis_client()
    exchange_rate_client = ExchangeRateClient()

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

    message = await queue.get()

    if message is not None:
        async with message.process():
            await consumer.process_message(message)

    parcel_query = select(Parcel).where(Parcel.id == parcel_id)
    parcel_result = await test_session.execute(parcel_query)
    parcel = parcel_result.scalars().one()

    assert parcel.delivery_cost_rub is not None
    assert parcel.delivery_cost_rub > 0
