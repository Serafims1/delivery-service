import aio_pika
from aio_pika.abc import AbstractChannel, AbstractQueue, AbstractRobustConnection

from delivery_service.core.config import get_settings


async def create_rabbitmq_connection() -> AbstractRobustConnection:
    settings = get_settings()

    return await aio_pika.connect_robust(
        host=settings.rabbitmq.host,
        port=settings.rabbitmq.port,
        login=settings.rabbitmq.user,
        password=settings.rabbitmq.password,
    )


async def create_channel_and_queue(
    connection: AbstractRobustConnection,
) -> tuple[AbstractChannel, AbstractQueue]:
    channel = await connection.channel()

    queue = await channel.declare_queue("parcel.created", durable=True)

    return channel, queue
