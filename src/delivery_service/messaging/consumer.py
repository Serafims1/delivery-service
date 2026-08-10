import json

from aio_pika.abc import AbstractIncomingMessage, AbstractQueue
from loguru import logger

from delivery_service.database.uow import UnitOfWork
from delivery_service.services.delivery_cost import DeliveryCostService


class ParcelCreatedConsumer:
    def __init__(
        self,
        queue: AbstractQueue,
        delivery_cost_service: DeliveryCostService,
        uow: UnitOfWork,
    ) -> None:
        self.queue = queue
        self.delivery_cost_service = delivery_cost_service
        self.uow = uow

    async def process_message(self, message: AbstractIncomingMessage) -> None:
        data = json.loads(message.body.decode())
        parcel_id = data["payload"]["parcel_id"]

        try:
            await self.delivery_cost_service.calculate(parcel_id)

            logger.info(
                "Message processed | parcel_id={}",
                parcel_id,
            )

        except Exception:
            await self.uow.rollback()

            logger.exception("Message processing failed | parcel_id={}", parcel_id)

            raise

    async def consume(self) -> None:
        async with self.queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process(requeue=True):
                    await self.process_message(message)
