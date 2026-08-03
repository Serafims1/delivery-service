import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.models.parcel import Parcel
from delivery_service.models.parcel_type import ParcelType


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_parcel_success(
    client: AsyncClient, parcel_types: list[ParcelType]
) -> None:
    payload = {
        "name": "MacBook",
        "weight": 2.1,
        "parcel_type_id": 2,
        "content_value_usd": 1800,
    }

    response = await client.post("/api/v1/parcels", json=payload)

    assert response.status_code == 201
    assert "id" in response.json()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_parcel_with_unknown_type(
    client: AsyncClient, parcel_types: list[ParcelType], test_session: AsyncSession
) -> None:
    payload = {
        "name": "MacBook",
        "weight": 2.1,
        "parcel_type_id": 99,
        "content_value_usd": 1800,
    }

    response = await client.post("/api/v1/parcels", json=payload)

    assert response.status_code == 404
    assert response.json() == {"detail": "Отсутствует тип посылки"}

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_create_parcel_saves_session_id(
        client: AsyncClient, parcel_types: list[ParcelType], test_session: AsyncSession
    ) -> None:
        payload = {
            "name": "MacBook",
            "weight": 2.1,
            "parcel_type_id": 2,
            "content_value_usd": 1800,
        }

        response = await client.post("/api/v1/parcels", json=payload)

        assert response.status_code == 201

        parcel_id = response.json()["id"]

        parcel = await test_session.get(Parcel, parcel_id)

        assert parcel is not None
        assert parcel.session_id
