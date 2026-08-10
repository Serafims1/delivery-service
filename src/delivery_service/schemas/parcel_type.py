from pydantic import BaseModel, ConfigDict, Field


class ParcelTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=30)
