from delivery_service.models.parcel_type import ParcelType
from delivery_service.repositories.parcel_type import ParcelTypeRepository


class ParcelTypeService:
    def __init__(self, repository: ParcelTypeRepository) -> None:
        self.repository = repository

    async def get_all(self) -> list[ParcelType]:
        parcel_types = await self.repository.get_all()
        return parcel_types
