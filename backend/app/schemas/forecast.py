from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field

# Base Schema
class ForecastBase(BaseModel):
    crop: str
    forecast_date: date
    predicted_price: float
    confidence: float

# Individual Prediction Node
class DailyForecast(BaseModel):
    date: date
    price: float
    confidence: float

# Crop Grouping Node
class CropForecastGroup(BaseModel):
    crop: str
    forecast: List[DailyForecast]

# Main API Response
class DistrictForecastResponse(BaseModel):
    district: str
    forecasts: List[CropForecastGroup]

# Database Schema
class CropPriceForecastInDB(ForecastBase):
    id: str
    district: str
    model_version: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
