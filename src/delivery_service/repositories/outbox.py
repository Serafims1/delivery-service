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
