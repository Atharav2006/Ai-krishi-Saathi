import uuid
from typing import Any, List
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/crops", response_model=List[schemas.Crop])
def read_crops(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve master crop listing parameters.
    """
    return crud.crop.get_multi(db, skip=skip, limit=limit)

@router.get("/mandi-prices", response_model=schemas.PaginatedMandiPriceResponse)
def read_mandi_prices(
    db: Session = Depends(deps.get_db),
    crop_id: uuid.UUID = Query(None, description="Filter by crop UUID"),
    district_id: uuid.UUID = Query(None, description="Filter globally across a district UUID"),
    start_date: date = Query(None),
    end_date: date = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
) -> Any:
    """
    Analytics API fetching aggregated timeseries datasets for Mandi prices.
    Highly optimized for caching and charts.
    """
    skip = (page - 1) * size
    
    total, items = crud.mandi_price.get_paginated(
        db, 
        crop_id=crop_id, 
        district_id=district_id, 
        start_date=start_date, 
        end_date=end_date,
        skip=skip, 
        limit=size
    )
    
    return schemas.PaginatedMandiPriceResponse(
        total=total,
        page=page,
        size=size,
        data=items
    )
