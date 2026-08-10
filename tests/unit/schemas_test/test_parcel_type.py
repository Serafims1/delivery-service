import pytest
from pydantic import ValidationError

from delivery_service.schemas.parcel_type import ParcelTypeRead


@pytest.mark.unit
def test_parcel_type_read_success() -> None:
    parcel_type = ParcelTypeRead(
        id=2,
        name="Одежда",
    )

    assert parcel_type.id == 2
    assert parcel_type.name == "Одежда"


@pytest.mark.unit
def test_parcel_type_read_negative() -> None:
    with pytest.raises(ValidationError):
        ParcelTypeRead(
            id=-3,
            name="",
        )
