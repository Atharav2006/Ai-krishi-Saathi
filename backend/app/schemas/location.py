import uuid
from pydantic import BaseModel, ConfigDict

class StateBase(BaseModel):
    name: str

class State(StateBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

class DistrictBase(BaseModel):
    name: str
    state_id: uuid.UUID

class District(DistrictBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)
