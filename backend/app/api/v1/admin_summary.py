"""
api/v1/admin_summary.py
------------------------
System-wide KPIs for the admin dashboard banner.
"""
from datetime import datetime, timedelta, timezone
import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api import deps
from app.models.user import User
from app.models.monitoring import PredictionLog
from app.models.model_registry import ModelRegistry, ModelStatusEnum
from app.models.retraining import ModelRetrainingJob, RetrainingStatus

router = APIRouter()
logger = logging.getLogger("krishi_saathi.api.admin")


@router.get(
    "/system-summary",
    summary="Get top level system KPIs (Admin Only)",
)
def get_system_summary(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),  # Requires valid JWT
):
    # Enforce admin role
    if current_user.role.name != "Admin":
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )

    now = datetime.now(timezone.utc)
    twenty_four_hours_ago = now - timedelta(hours=24)

    # 1. Total predictions last 24h
    predictions_24h = (
        db.query(PredictionLog)
        .filter(PredictionLog.created_at >= twenty_four_hours_ago)
        .count()
    )

    # 2. Active degraded models (models currently serving but marked degraded)
    degraded_active = (
        db.query(ModelRegistry)
        .filter(ModelRegistry.status == ModelStatusEnum.degraded)
        .count()
    )

    # 3. Pending/Running retraining jobs
    active_jobs = (
        db.query(ModelRetrainingJob)
        .filter(ModelRetrainingJob.status.in_([RetrainingStatus.pending, RetrainingStatus.running]))
        .count()
    )

    return {
        "predictions_last_24h": predictions_24h,
        "degraded_models_count": degraded_active,
        "pending_retraining_jobs": active_jobs,
    }
