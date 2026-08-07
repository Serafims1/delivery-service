from fastapi import APIRouter, Header, HTTPException, status

from delivery_service.database.session import SessionDep
from delivery_service.dependencies.session import SessionIdDep
from delivery_service.integrations.redis import create_redis_client
from delivery_service.repositories.parcel import ParcelRepository
from delivery_service.repositories.parcel_type import ParcelTypeRepository
from delivery_service.schemas.parcel import (
    ParcelCreate,
    ParcelCreateResponse,
    ParcelListItem,
)
from delivery_service.services.idempotency import IdempotencyService
from delivery_service.services.parcel import ParcelService

router = APIRouter(prefix="/parcels", tags=["Parcels"])


@router.post(
    "", response_model=ParcelCreateResponse, status_code=status.HTTP_201_CREATED
)
async def create_parcel(
    session: SessionDep,
    session_id: SessionIdDep,
    parcel_data: ParcelCreate,
    idempotency_key: str = Header(alias="Idempotency-Key"),
) -> ParcelCreateResponse:
    parcel_repository = ParcelRepository(session)
    parcel_type_repository = ParcelTypeRepository(session)

    redis_client = create_redis_client()

    service = ParcelService(parcel_repository, parcel_type_repository)
    idempotency_service = IdempotencyService(redis_client)

    acquired = await idempotency_service.acquire(idempotency_key)

    if not acquired:
        res = await idempotency_service.repeat_request_answer(idempotency_key)

        if res is not None:
            return ParcelCreateResponse(id=res)

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Request with this Idempotency-Key is already processing",
        )

    try:
        parcel = await service.create_parcel(
            parcel_data=parcel_data, session_id=session_id
        )
    except Exception:
        await idempotency_service.release(idempotency_key)
        raise

    await idempotency_service.success_result(idempotency_key, parcel.id)

    return ParcelCreateResponse(id=parcel.id)


@router.get("", response_model=list[ParcelListItem])
async def get_all_parcels(
    session: SessionDep,
    session_id: SessionIdDep,
    limit: int = 10,
    offset: int = 0,
    parcel_type_id: int | None = None,
    has_delivery_cost: bool | None = None,
) -> list[ParcelListItem]:
    parcel_repository = ParcelRepository(session)
    parcel_type_repository = ParcelTypeRepository(session)
    service = ParcelService(parcel_repository, parcel_type_repository)

    parcels = await service.get_all_parcels(
        session_id=session_id,
        limit=limit,
        offset=offset,
        parcel_type_id=parcel_type_id,
        has_delivery_cost=has_delivery_cost,
    )

    return parcels


@router.get("/{parcel_id}", response_model=ParcelListItem)
async def get_parcel_by_id(
    session: SessionDep, session_id: SessionIdDep, parcel_id: int
) -> ParcelListItem:
    parcel_repository = ParcelRepository(session)
    parcel_type_repository = ParcelTypeRepository(session)

    service = ParcelService(parcel_repository, parcel_type_repository)

    parcel = await service.get_parcel_by_id(session_id=session_id, parcel_id=parcel_id)

    return parcel
