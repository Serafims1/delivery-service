import json

import aio_pika
from aio_pika.abc import AbstractChannel
from loguru import logger

from delivery_service.database.uow import UnitOfWork
from delivery_service.repositories.outbox import OutboxRepository


class OutboxPublisher:
    def __init__(
        self,
        outbox_repo: OutboxRepository,
        rabbitmq_channel: AbstractChannel,
        uow: UnitOfWork,
    ) -> None:
        self.outbox_repo = outbox_repo
        self.rabbitmq_channel = rabbitmq_channel
        self.uow = uow

    async def publish_pending(self) -> None:
        events = await self.outbox_repo.get_unprocessed_events()

        for event in events:
            body = json.dumps(
                {
                    "event_type": event.event_type,
                    "payload": event.payload,
                }
            ).encode()

            message = aio_pika.Message(
                body=body,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )

            await self.rabbitmq_channel.default_exchange.publish(
                message, routing_key="parcel.created"
            )

            await self.outbox_repo.mark_processed(event)
            await self.uow.commit()
            logger.info(
                "Event published | event_id={} | event_type={}",
                event.id,
                event.event_type,
            )
