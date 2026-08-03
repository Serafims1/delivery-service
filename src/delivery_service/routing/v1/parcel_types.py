from fastapi import APIRouter

from delivery_service.database.session import SessionDep
from delivery_service.models.parcel_type import ParcelType
from delivery_service.repositories.parcel_type import ParcelTypeRepository
from delivery_service.schemas.parcel_type import ParcelTypeRead
from delivery_service.services.parcel_type import ParcelTypeService

router = APIRouter(prefix="/parcel-types", tags=["ParcelTypes"])


@router.get("", response_model=list[ParcelTypeRead])
async def get_parcel_types(session: SessionDep) -> list[ParcelType]:
    repository = ParcelTypeRepository(session)
    service = ParcelTypeService(repository)

    parcel_types = await service.get_all()
    return parcel_types
