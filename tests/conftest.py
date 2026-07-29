from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from delivery_service.database.base import Base
from delivery_service.database.session import get_session
from delivery_service.main import app
from delivery_service.models.parcel_type import ParcelType

TEST_DATABASE_URL = URL.create(
    drivername="postgresql+asyncpg",
    username="postgres",
    password="2026project2026",
    host="postgres_test",
    port=5432,
    database="delivery_test",
)

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)

test_session_factory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture
async def setup_test_database() -> AsyncGenerator[None]:
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest_asyncio.fixture
async def test_session(setup_test_database: None) -> AsyncGenerator[AsyncSession]:
    async with test_session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def parcel_types(test_session: AsyncSession) -> list[ParcelType]:
    parcel_types = [
        ParcelType(id=3, name="Разное"),
        ParcelType(id=1, name="Одежда"),
        ParcelType(id=2, name="Электроника"),
    ]

    test_session.add_all(parcel_types)
    await test_session.flush()

    return parcel_types


@pytest_asyncio.fixture
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    async def override_get_session() -> AsyncGenerator[AsyncSession]:
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
