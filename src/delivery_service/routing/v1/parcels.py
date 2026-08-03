from fastapi import APIRouter, status

from delivery_service.database.session import SessionDep
from delivery_service.dependencies.session import SessionIdDep
from delivery_service.repositories.parcel import ParcelRepository
from delivery_service.repositories.parcel_type import ParcelTypeRepository
from delivery_service.schemas.parcel import ParcelCreate, ParcelCreateResponse
from delivery_service.services.parcel import ParcelService

router = APIRouter(prefix="/parcels", tags=["Parcels"])


@router.post(
    "", response_model=ParcelCreateResponse, status_code=status.HTTP_201_CREATED
)
async def create_parcel(
    session: SessionDep, session_id: SessionIdDep, parcel_data: ParcelCreate
) -> ParcelCreateResponse:
    parcel_repository = ParcelRepository(session)
    parcel_type_repository = ParcelTypeRepository(session)

    service = ParcelService(parcel_repository, parcel_type_repository)

    parcel = await service.create_parcel(parcel_data=parcel_data, session_id=session_id)

    return ParcelCreateResponse(id=parcel.id)
