from collections.abc import AsyncGenerator

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from delivery_service.core.config import get_settings

settings = get_settings()

DATABASE_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=settings.database.user,
    password=settings.database.password,
    host=settings.database.host,
    port=settings.database.port,
    database=settings.database.name,
)

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_factory() as session:
        yield session
