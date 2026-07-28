from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ParcelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=30)
    weight: Decimal = Field(gt=0, max_digits=10, decimal_places=3)
    parcel_type_id: int = Field(gt=0)
    content_value_usd: Decimal = Field(max_digits=12, ge=0, decimal_places=2)


class ParcelRead(ParcelCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(gt=0)
    delivery_cost_rub: Decimal | None = Field(
        None, max_digits=12, decimal_places=2, ge=0
    )
