from decimal import Decimal

import pytest
from pydantic import ValidationError

from delivery_service.schemas.parcel import ParcelCreate, ParcelRead


@pytest.mark.unit
def test_parcel_create_success() -> None:
    parcel = ParcelCreate(
        name="iphone",
        weight=Decimal("0.85"),
        parcel_type_id=2,
        content_value_usd=Decimal("799"),
    )

    assert parcel.name == "iphone"
    assert parcel.weight == Decimal("0.85")
    assert parcel.parcel_type_id == 2
    assert parcel.content_value_usd == Decimal("799.00")


@pytest.mark.unit
def test_parcel_create_negative() -> None:
    with pytest.raises(ValidationError):
        ParcelCreate(
            name="",
            weight=Decimal("12.8523"),
            parcel_type_id=-1,
            content_value_usd=Decimal("799.123121"),
        )


@pytest.mark.unit
def test_parcel_read_success() -> None:
    parcel = ParcelRead(
        id=1,
        name="iphone",
        weight=Decimal("0.85"),
        parcel_type_id=2,
        content_value_usd=Decimal("799"),
        delivery_cost_rub=None,
    )

    assert parcel.id == 1
    assert parcel.delivery_cost_rub is None


@pytest.mark.unit
def test_parcel_read_negative() -> None:
    with pytest.raises(ValidationError):
        ParcelRead(
            id=-12,
            name="iphone",
            weight=Decimal("0.85"),
            parcel_type_id=2,
            content_value_usd=Decimal("799"),
            delivery_cost_rub=None,
        )


@pytest.mark.unit
def test_parcel_read_delivery_negative() -> None:
    with pytest.raises(ValidationError):
        ParcelRead(
            id=1,
            name="iphone",
            weight=Decimal("0.85"),
            parcel_type_id=2,
            content_value_usd=Decimal("799"),
            delivery_cost_rub=Decimal("-12343.89"),
        )
