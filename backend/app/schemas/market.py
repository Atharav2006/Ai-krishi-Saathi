import uuid
from datetime import date
from pydantic import BaseModel, ConfigDict
from decimal import Decimal

class MarketBase(BaseModel):
    name: str
    district_id: uuid.UUID

class Market(MarketBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

class MandiPriceBase(BaseModel):
    market_id: uuid.UUID
    crop_id: uuid.UUID
    price_date: date
    min_price: float
    max_price: float
    modal_price: float

class MandiPrice(MandiPriceBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

class PaginatedMandiPriceResponse(BaseModel):
    total: int
    page: int
    size: int
    data: list[MandiPrice]
