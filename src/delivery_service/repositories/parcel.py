from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.models.parcel import Parcel
from delivery_service.schemas.parcel import ParcelCreate


class ParcelRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register_parcel(
        self, parcel_data: ParcelCreate, session_id: str
    ) -> Parcel:
        parcel = Parcel(**parcel_data.model_dump(), session_id=session_id)

        self.session.add(parcel)
        await self.session.flush()

        return parcel
