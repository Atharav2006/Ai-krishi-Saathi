import uuid
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


class ModelRegistryCreate(BaseModel):
    model_type: str
    model_version: str
    status: str = "candidate"
    trained_at: Optional[datetime] = None
    metrics_snapshot: Optional[dict[str, Any]] = None

    model_config = {"protected_namespaces": ()}


class ModelRegistryOut(BaseModel):
    id: uuid.UUID
    model_type: str
    model_version: str
    status: str
    trained_at: Optional[datetime]
    metrics_snapshot: Optional[dict[str, Any]]
    created_at: datetime

    model_config = {"from_attributes": True, "protected_namespaces": ()}


class PromoteModelRequest(BaseModel):
    candidate_id: uuid.UUID = Field(..., description="UUID of the candidate model to promote to active.")
