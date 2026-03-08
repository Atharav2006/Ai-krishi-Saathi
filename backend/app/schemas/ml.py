import uuid
from typing import List, Optional
from pydantic import BaseModel, Field

# Price Forecasting Schemas
class PriceForecastRequest(BaseModel):
    crop_id: uuid.UUID
    district_id: uuid.UUID
    recent_price_series: Optional[List[float]] = Field(default_factory=list, description="Optional trailing 7-day price context")

class PriceForecastResponse(BaseModel):
    predicted_price: float
    trend_direction: str = Field(description="'up', 'down', or 'stable'")
    confidence_score: float = Field(ge=0.0, le=1.0)
    model_version: str
    model_config = {"protected_namespaces": ()}

# Disease Detection Schemas
class DiseaseDetectionResponse(BaseModel):
    disease_class: str
    confidence: float = Field(ge=0.0, le=1.0)
    advisory_text: str
    model_version: str
    model_config = {"protected_namespaces": ()}
