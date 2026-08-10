import pytest
from httpx import AsyncClient

from delivery_service.models.parcel_type import ParcelType


@pytest.mark.asyncio
@pytest.mark.smoke
async def test_get_parcel_types(
    client: AsyncClient, parcel_types: list[ParcelType]
) -> None:
    response = await client.get("/api/v1/parcel-types")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "Одежда"},
        {"id": 2, "name": "Электроника"},
        {"id": 3, "name": "Разное"},
    ]
