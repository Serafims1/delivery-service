from loguru import logger

from delivery_service.core.exceptions import (
    ParcelNotFoundError,
    ParcelTypeNotFoundError,
)
from delivery_service.database.uow import UnitOfWork
from delivery_service.models.parcel import Parcel
from delivery_service.repositories.outbox import OutboxRepository
from delivery_service.repositories.parcel import ParcelRepository
from delivery_service.repositories.parcel_type import ParcelTypeRepository
from delivery_service.schemas.parcel import ParcelCreate, ParcelListItem


class ParcelService:
    def __init__(
        self,
        parcel_repo: ParcelRepository,
        parcel_type_repo: ParcelTypeRepository,
        outbox_repo: OutboxRepository,
        uow: UnitOfWork,
    ) -> None:
        self.parcel_repo = parcel_repo
        self.parcel_type_repo = parcel_type_repo
        self.outbox_repo = outbox_repo
        self.uow = uow

    async def create_parcel(self, parcel_data: ParcelCreate, session_id: str) -> Parcel:
        parcel_type = await self.parcel_type_repo.get_by_id(parcel_data.parcel_type_id)

        if parcel_type is None:
            logger.warning(
                "Parcel type not found | parcel_type_id={}",
                parcel_data.parcel_type_id,
            )
            raise ParcelTypeNotFoundError("Отсутствует тип посылки")

        parcel = await self.parcel_repo.register_parcel(
            parcel_data=parcel_data, session_id=session_id
        )

        await self.outbox_repo.create_event(
            event_type="parcel.created", payload={"parcel_id": parcel.id}
        )

        await self.uow.commit()

        logger.info(
            "Parcel created | parcel_id={} | parcel_type_id={}",
            parcel.id,
            parcel.parcel_type_id,
        )

        return parcel

    async def get_all_parcels(
        self,
        session_id: str,
        limit: int,
        offset: int,
        parcel_type_id: int | None = None,
        has_delivery_cost: bool | None = None,
    ) -> list[ParcelListItem]:

        return await self.parcel_repo.get_list_parcels(
            session_id=session_id,
            limit=limit,
            offset=offset,
            parcel_type_id=parcel_type_id,
            has_delivery_cost=has_delivery_cost,
        )

    async def get_parcel_by_id(self, session_id: str, parcel_id: int) -> ParcelListItem:
        parcel = await self.parcel_repo.get_parcel_by_id(
            session_id=session_id, parcel_id=parcel_id
        )

        if parcel is None:
            logger.warning("Parcel not found | parcel_id={}", parcel_id)
            raise ParcelNotFoundError("Посылка отсутствует")

        return parcel
