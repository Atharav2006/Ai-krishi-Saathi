from typing import Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.api import deps
from app.models.forecast import CropPriceForecast
from app.schemas.forecast import DistrictForecastResponse, CropForecastGroup, DailyForecast

router = APIRouter()

@router.get("", response_model=DistrictForecastResponse)
def get_forecasts(
    district: str,
    crops: str = Query(..., description="Comma separated list of crops"),
    days: int = 7,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Retrieve price forecasts for a specific district and list of crops.
    """
    crop_list = [c.strip().lower() for c in crops.split(",")]
    district_lower = district.strip().lower()
    
    print(f"DEBUG: Forecast requested for district='{district}' (lowered='{district_lower}') crops={crop_list}")
    
    # Query database with direct indexed filters
    forecasts_db = db.query(CropPriceForecast).filter(
        CropPriceForecast.district == district_lower,
        CropPriceForecast.crop.in_(crop_list)
    ).order_by(
        CropPriceForecast.crop,
        CropPriceForecast.forecast_date
    ).all()

    print(f"DEBUG: Found {len(forecasts_db)} forecast rows in DB for '{district_lower}'")

    # Group by crop
    grouped_data = {}
    for row in forecasts_db:
        if row.crop not in grouped_data:
            grouped_data[row.crop] = []
        
        # Limit to requested days
        if len(grouped_data[row.crop]) < days:
            grouped_data[row.crop].append(DailyForecast(
                date=row.forecast_date,
                price=row.predicted_price,
                confidence=row.confidence
            ))
            
    print(f"DEBUG: Found {len(forecasts_db)} forecast rows in DB for '{district_lower}' with crops={crop_list}")
    
    # Structure response to group by crop
    response_groups = []
    for crop_name, days_data in grouped_data.items():
        response_groups.append(CropForecastGroup(
            crop=crop_name,
            forecast=days_data
        ))

    return DistrictForecastResponse(
        district=district,
        forecasts=response_groups
    )
