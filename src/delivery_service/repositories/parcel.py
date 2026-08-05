from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from delivery_service.models.parcel import Parcel
from delivery_service.models.parcel_type import ParcelType
from delivery_service.schemas.parcel import ParcelCreate, ParcelListItem


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

    async def get_list_parcels(
        self,
        session_id: str,
        limit: int,
        offset: int,
        parcel_type_id: int | None = None,
        has_delivery_cost: bool | None = None,
    ) -> list[ParcelListItem]:

        query = self._build_parcel_query(session_id)

        if parcel_type_id is not None:
            query = query.where(Parcel.parcel_type_id == parcel_type_id)

        if has_delivery_cost is True:
            query = query.where(Parcel.delivery_cost_rub.is_not(None))

        if has_delivery_cost is False:
            query = query.where(Parcel.delivery_cost_rub.is_(None))

        query = query.order_by(Parcel.id)

        query = query.offset(offset).limit(limit)

        result = await self.session.execute(query)

        rows = result.mappings().all()

        return [ParcelListItem.model_validate(row) for row in rows]

    def _build_parcel_query(self, session_id: str) -> Select[Any]:
        query = (
            select(
                Parcel.id,
                Parcel.name,
                Parcel.weight,
                Parcel.parcel_type_id,
                Parcel.content_value_usd,
                Parcel.delivery_cost_rub,
                ParcelType.name.label("parcel_type_name"),
            )
            .join(ParcelType, Parcel.parcel_type_id == ParcelType.id)
            .where(Parcel.session_id == session_id)
        )
        return query

    async def get_parcel_by_id(
        self, session_id: str, parcel_id: int
    ) -> ParcelListItem | None:
        query = self._build_parcel_query(session_id)

        query = query.where(Parcel.id == parcel_id)

        result = await self.session.execute(query)
        row = result.mappings().one_or_none()

        if row is None:
            return None

        return ParcelListItem.model_validate(row)
