from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.models.outbox_event import OutboxEvent


class OutboxRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_event(
        self, event_type: str, payload: dict[str, int]
    ) -> OutboxEvent:
        event = OutboxEvent(event_type=event_type, payload=payload)

        self.session.add(event)
        await self.session.flush()

        return event

    async def get_unprocessed_events(self) -> list[OutboxEvent]:
        query = select(OutboxEvent).where(OutboxEvent.processed.is_(False))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def mark_processed(self, event: OutboxEvent) -> None:
        event.processed = True
        await self.session.flush()
