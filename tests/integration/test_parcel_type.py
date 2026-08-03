import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.models.parcel_type import ParcelType
from delivery_service.repositories.parcel_type import ParcelTypeRepository


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_all_parcel_types(
    test_session: AsyncSession, parcel_types: list[ParcelType]
) -> None:
    repository = ParcelTypeRepository(test_session)

    result = await repository.get_all()

    assert len(result) == 3
    assert [parcel_type.id for parcel_type in result] == [1, 2, 3]
    assert [parcel_type.name for parcel_type in result] == [
        "Одежда",
        "Электроника",
        "Разное",
    ]
