import uuid
from pydantic import BaseModel, ConfigDict

class CropBase(BaseModel):
    name: str
    scientific_name: str | None = None

class Crop(CropBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)
