from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from delivery_service.database.base import Base


class Parcel(Base):
    __tablename__ = "parcels"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    weight: Mapped[Decimal] = mapped_column(Numeric(10, 3))
    content_value_usd: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    delivery_cost_rub: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )
    parcel_type_id: Mapped[int] = mapped_column(
        ForeignKey("parcel_types.id"),
        index=True,
    )
