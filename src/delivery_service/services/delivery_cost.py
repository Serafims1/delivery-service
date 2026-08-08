from decimal import Decimal

from delivery_service.core.exceptions import ParcelNotFoundError
from delivery_service.database.uow import UnitOfWork
from delivery_service.repositories.parcel import ParcelRepository
from delivery_service.services.exchange_rate import ExchangeRateService


class DeliveryCostService:
    def __init__(
        self,
        parcel_repo: ParcelRepository,
        rate_service: ExchangeRateService,
        uow: UnitOfWork,
    ) -> None:
        self.parcel_repo = parcel_repo
        self.rate_service = rate_service
        self.uow = uow

    async def calculate(self, parcel_id: int) -> None:
        parcel = await self.parcel_repo.get_parcel_by_id_and_not_session(
            parcel_id=parcel_id
        )

        if parcel is None:
            raise ParcelNotFoundError("Посылка отсутствует")

        if parcel.delivery_cost_rub is not None:
            return

        rate = await self.rate_service.get_usd_rub_rate()

        delivery_cost = (
            parcel.weight * Decimal("0.5") + parcel.content_value_usd * Decimal("0.01")
        ) * rate

        parcel.delivery_cost_rub = delivery_cost.quantize(Decimal("0.01"))
        await self.uow.commit()
