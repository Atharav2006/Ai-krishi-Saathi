import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ─── Prediction Log ────────────────────────────────────────────────────────────

class PredictionLogCreate(BaseModel):
    """Schema used internally by inference services to insert a log row."""
    user_id: Optional[uuid.UUID] = None
    model_type: str  # "price_forecast" | "disease_detection"
    model_version: str
    input_hash: str
    predicted_value: str
    confidence_score: float
    latency_ms: float


class PredictionLogOut(BaseModel):
    id: uuid.UUID
    model_type: str
    model_version: str
    predicted_value: str
    confidence_score: float
    latency_ms: float
    created_at: datetime

    model_config = {"from_attributes": True, "protected_namespaces": ()}


# ─── Ground Truth ──────────────────────────────────────────────────────────────

class GroundTruthCreate(BaseModel):
    prediction_id: uuid.UUID
    actual_value: str = Field(..., description="For price: numeric string. For disease: class name.")


class GroundTruthOut(BaseModel):
    id: uuid.UUID
    prediction_id: uuid.UUID
    actual_value: str
    recorded_at: datetime

    model_config = {"from_attributes": True, "protected_namespaces": ()}


# ─── Model Metric ─────────────────────────────────────────────────────────────

class ModelMetricOut(BaseModel):
    id: uuid.UUID
    model_type: str
    model_version: str
    metric_name: str
    metric_value: float
    window_start: datetime
    window_end: datetime
    created_at: datetime

    model_config = {"from_attributes": True, "protected_namespaces": ()}
