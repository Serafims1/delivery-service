from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select
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

    headers = {"Idempotency-Key": str(uuid4())}

    response = await client.post("/api/v1/parcels", json=payload, headers=headers)

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

    headers = {"Idempotency-Key": str(uuid4())}

    response = await client.post("/api/v1/parcels", json=payload, headers=headers)

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

        headers = {"Idempotency-Key": str(uuid4())}

        response = await client.post("/api/v1/parcels", json=payload, headers=headers)

        assert response.status_code == 201

        parcel_id = response.json()["id"]

        parcel = await test_session.get(Parcel, parcel_id)

        assert parcel is not None
        assert parcel.session_id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_parcels_returns_only_current_session(
    client: AsyncClient, parcel_types: list[ParcelType], test_session: AsyncSession
) -> None:
    payload1 = {
        "name": "MacBook",
        "weight": 2.1,
        "parcel_type_id": 2,
        "content_value_usd": 1800,
    }

    header1 = {"Idempotency-Key": str(uuid4())}
    header2 = {"Idempotency-Key": str(uuid4())}

    payload2 = {
        "name": "AirPods",
        "weight": 0.4,
        "parcel_type_id": 2,
        "content_value_usd": 300,
    }

    response1 = await client.post("/api/v1/parcels", json=payload1, headers=header1)
    response2 = await client.post("/api/v1/parcels", json=payload2, headers=header2)

    foreign_parcel = Parcel(
        name="Кроссовки",
        weight=0.5,
        parcel_type_id=1,
        content_value_usd=150,
        delivery_cost_rub=None,
        session_id="another-session-id",
    )

    test_session.add(foreign_parcel)
    await test_session.commit()

    response = await client.get("/api/v1/parcels")
    data = response.json()

    assert response1.status_code == 201
    assert response2.status_code == 201
    assert response.status_code == 200
    assert len(data) == 2
    assert {item["name"] for item in data} == {"MacBook", "AirPods"}
    assert all("parcel_type_name" in item for item in data)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_parcels_filters_by_type_and_delivery_cost(
    client: AsyncClient,
    parcel_types: list[ParcelType],
    test_session: AsyncSession,
) -> None:
    create_response = await client.post(
        "/api/v1/parcels",
        json={
            "name": "MacBook",
            "weight": 2.1,
            "parcel_type_id": parcel_types[0].id,
            "content_value_usd": 1800,
        },
        headers={"Idempotency-Key": str(uuid4())},
    )

    assert create_response.status_code == 201

    parcel_id = create_response.json()["id"]
    created_parcel = await test_session.get(Parcel, parcel_id)

    assert created_parcel is not None

    session_id = created_parcel.session_id

    test_session.add_all(
        [
            Parcel(
                name="AirPods",
                weight=0.4,
                parcel_type_id=parcel_types[1].id,
                content_value_usd=300,
                delivery_cost_rub=None,
                session_id=session_id,
            ),
            Parcel(
                name="Кроссовки",
                weight=0.5,
                parcel_type_id=parcel_types[1].id,
                content_value_usd=150,
                delivery_cost_rub=15000,
                session_id=session_id,
            ),
        ]
    )
    await test_session.commit()

    response = await client.get(
        "/api/v1/parcels",
        params={
            "parcel_type_id": parcel_types[1].id,
            "has_delivery_cost": True,
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["name"] == "Кроссовки"
    assert data[0]["parcel_type_id"] == parcel_types[1].id
    assert data[0]["delivery_cost_rub"] is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_parcels_applies_pagination(
    client: AsyncClient,
    parcel_types: list[ParcelType],
) -> None:
    payload1 = {
        "name": "MacBook",
        "weight": 2.1,
        "parcel_type_id": parcel_types[0].id,
        "content_value_usd": 1800,
    }

    payload2 = {
        "name": "AirPods",
        "weight": 0.4,
        "parcel_type_id": parcel_types[0].id,
        "content_value_usd": 300,
    }

    payload3 = {
        "name": "Кроссовки",
        "weight": 0.3,
        "parcel_type_id": parcel_types[0].id,
        "content_value_usd": 100,
    }

    header1 = {"Idempotency-Key": str(uuid4())}
    header2 = {"Idempotency-Key": str(uuid4())}
    header3 = {"Idempotency-Key": str(uuid4())}

    response1 = await client.post("/api/v1/parcels", json=payload1, headers=header1)
    response2 = await client.post("/api/v1/parcels", json=payload2, headers=header2)
    response3 = await client.post("/api/v1/parcels", json=payload3, headers=header3)

    assert response1.status_code == 201
    assert response2.status_code == 201
    assert response3.status_code == 201

    response = await client.get(
        "/api/v1/parcels",
        params={
            "limit": 1,
            "offset": 1,
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["name"] == "AirPods"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_parcel_by_id_success(
    client: AsyncClient, parcel_types: list[ParcelType]
) -> None:
    create_response = await client.post(
        "/api/v1/parcels",
        json={
            "name": "MacBook",
            "weight": 2.1,
            "parcel_type_id": parcel_types[0].id,
            "content_value_usd": 1800,
        },
        headers={"Idempotency-Key": str(uuid4())},
    )

    assert create_response.status_code == 201

    data = create_response.json()
    parcel_id = data["id"]

    response = await client.get(
        f"/api/v1/parcels/{parcel_id}",
    )

    data = response.json()

    assert response.status_code == 200
    assert data["id"] == parcel_id
    assert data["name"] == "MacBook"
    assert data["parcel_type_id"] == parcel_types[0].id
    assert data["delivery_cost_rub"] is None
    assert "parcel_type_name" in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_parcel_by_id_foreign_session_returns_404(
    client: AsyncClient, parcel_types: list[ParcelType], test_session: AsyncSession
) -> None:
    foreign_parcel = Parcel(
        name="Кроссовки",
        weight=0.5,
        parcel_type_id=parcel_types[0].id,
        content_value_usd=150,
        delivery_cost_rub=None,
        session_id="another-session-id",
    )

    test_session.add(foreign_parcel)
    await test_session.commit()

    parcel_id = foreign_parcel.id

    assert parcel_id is not None

    response = await client.get(
        f"/api/v1/parcels/{parcel_id}",
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Посылка отсутствует"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_parcel_with_same_idempotency_key_returns_same_id(
    client: AsyncClient, parcel_types: list[ParcelType], test_session: AsyncSession
) -> None:
    payload = {
        "name": "MacBook",
        "weight": 2.1,
        "parcel_type_id": parcel_types[0].id,
        "content_value_usd": 1800,
    }

    header = {"Idempotency-Key": str(uuid4())}

    response1 = await client.post("/api/v1/parcels", headers=header, json=payload)

    assert response1.status_code == 201
    first_id = response1.json()["id"]

    response2 = await client.post("/api/v1/parcels", headers=header, json=payload)

    assert response2.status_code == 201
    second_id = response2.json()["id"]

    assert first_id == second_id

    result = await test_session.execute(select(Parcel))
    parcels = result.scalars().all()

    assert len(parcels) == 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_idempotency_key_is_released_after_parcel_creation_error(
    client: AsyncClient, parcel_types: list[ParcelType]
) -> None:
    header = {"Idempotency-Key": str(uuid4())}

    payload = {
        "name": "MacBook",
        "weight": 2.1,
        "parcel_type_id": 9999,
        "content_value_usd": 1800,
    }

    response1 = await client.post("/api/v1/parcels", json=payload, headers=header)

    assert response1.status_code == 404

    payload2 = {
        "name": "MacBook",
        "weight": 2.1,
        "parcel_type_id": parcel_types[0].id,
        "content_value_usd": 1800,
    }

    response2 = await client.post("/api/v1/parcels", json=payload2, headers=header)

    assert response2.status_code == 201
    assert "id" in response2.json()
