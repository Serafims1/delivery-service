from aio_pika.abc import AbstractChannel

from delivery_service.database.session import async_session_factory
from delivery_service.database.uow import UnitOfWork
from delivery_service.messaging.outbox_publisher import OutboxPublisher
from delivery_service.messaging.rabbitmq import (
    create_channel_and_queue,
    create_rabbitmq_connection,
)
from delivery_service.repositories.outbox import OutboxRepository


async def publish_once(channel: AbstractChannel) -> None:
    async with async_session_factory() as session:
        outbox_repo = OutboxRepository(session)
        uow = UnitOfWork(session)

        publisher = OutboxPublisher(
            outbox_repo=outbox_repo,
            rabbitmq_channel=channel,
            uow=uow,
        )

        await publisher.publish_pending()


async def main() -> None:
    connection = await create_rabbitmq_connection()
    channel, _ = await create_channel_and_queue(connection)

    while True:
        await publish_once(channel)
        await asyncio.sleep(300)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
