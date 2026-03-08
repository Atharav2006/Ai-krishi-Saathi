"""
api/v1/feedback.py
------------------
Ground truth capture endpoint: allows farmers/officers to record what actually
happened after receiving a prediction, enabling model performance measurement.
"""
import uuid
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api import deps
from app.models.user import User
from app.schemas.monitoring import GroundTruthCreate, GroundTruthOut
from app.crud.crud_monitoring import (
    get_prediction_log,
    get_ground_truth_for_prediction,
    create_ground_truth,
)

router = APIRouter()
logger = logging.getLogger("krishi_saathi.api.feedback")


@router.post(
    "/ground-truth",
    response_model=GroundTruthOut,
    status_code=status.HTTP_201_CREATED,
    summary="Submit ground truth for a past prediction",
)
def submit_ground_truth(
    *,
    db: Session = Depends(deps.get_db),
    payload: GroundTruthCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Records the real-world outcome for a previously made prediction.

    - **prediction_id**: UUID of the prediction from `/ml/predict-price` or `/ml/detect-disease`
    - **actual_value**: The true observed value (e.g., "1450.0" for price, "Leaf_Blight" for disease)

    Returns HTTP 404 if the prediction does not exist.
    Returns HTTP 409 if ground truth has already been recorded for this prediction.

    Secured: requires a valid JWT; accessible by Farmer or Officer roles.
    """
    # 1. Ensure the referenced prediction exists
    prediction = get_prediction_log(db, prediction_id=payload.prediction_id)
    if not prediction:
        logger.warning(
            f"Ground truth submitted for non-existent prediction: {payload.prediction_id} "
            f"by user: {current_user.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction {payload.prediction_id} not found.",
        )

    # 2. Prevent duplicate ground truth entries (UniqueConstraint on prediction_id)
    existing = get_ground_truth_for_prediction(db, prediction_id=payload.prediction_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Ground truth for prediction {payload.prediction_id} has already been recorded "
                f"on {existing.recorded_at.isoformat()}."
            ),
        )

    # 3. Persist
    try:
        record = create_ground_truth(db, obj_in=payload)
    except IntegrityError:
        # Race condition: two concurrent requests for the same prediction_id
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ground truth already recorded (concurrent write detected).",
        )

    logger.info(
        f"Ground truth recorded | prediction={payload.prediction_id} "
        f"| actual={payload.actual_value} | user={current_user.id}"
    )
    return record
