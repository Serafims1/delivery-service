from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from delivery_service.database.base import Base


class ParcelType(Base):
    __tablename__ = "parcel_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
