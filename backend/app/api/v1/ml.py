import uuid
from typing import Any
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.schemas import ml as ml_schemas
from app.api import deps
from app.services.ml.price_forecast_service import price_forecast_service
from app.services.ml.disease_detection_service import disease_detection_service

router = APIRouter()

@router.post("/predict-price", response_model=ml_schemas.PriceForecastResponse)
def predict_price(
    request_data: ml_schemas.PriceForecastRequest,
    current_user: Any = Depends(deps.get_current_active_user)
) -> Any:
    """
    Predicts the trailing futuristic pricing for a specific crop/district.
    Secured by active session.
    """
    try:
        response = price_forecast_service.predict(request_data)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference Engine Error: {str(e)}")


@router.post("/detect-disease", response_model=ml_schemas.DiseaseDetectionResponse)
async def detect_disease(
    file: UploadFile = File(...),
    crop_id: str = Form("demo_crop"),
    district_id: str = Form("demo_district"),
) -> Any:
    """
    Analyzes visual agronomic uploads in real-time.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")
        
    try:
        response = await disease_detection_service.predict_from_image(file)
        return response
    except Exception as e:
        import traceback
        with open("backend_traceback.log", "w") as f:
            traceback.print_exc(file=f)
        raise HTTPException(status_code=500, detail=f"Computer Vision Engine Error: {str(e)}")
