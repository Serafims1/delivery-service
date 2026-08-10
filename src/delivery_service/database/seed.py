import asyncio

from sqlalchemy import select

from delivery_service.database.session import async_session_factory
from delivery_service.models.parcel_type import ParcelType

PARCEL_TYPES = (
    "Одежда",
    "Электроника",
    "Разное",
)


async def seed_parcel_types() -> None:
    async with async_session_factory() as session:
        for parcel_type_name in PARCEL_TYPES:
            statement = select(ParcelType).where(
                ParcelType.name == parcel_type_name,
            )

            result = await session.execute(statement)
            existing_parcel_type = result.scalar_one_or_none()

            if existing_parcel_type is None:
                parcel_type = ParcelType(name=parcel_type_name)
                session.add(parcel_type)

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_parcel_types())
