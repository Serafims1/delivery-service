from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.models.parcel_type import ParcelType


class ParcelTypeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self) -> list[ParcelType]:
        query = select(ParcelType).order_by(ParcelType.id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, parcel_type_id: int) -> ParcelType | None:
        query = select(ParcelType).where(ParcelType.id == parcel_type_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
