"""
api/v1/degradation_history.py
------------------------------
Read-only endpoint to list recent degradation events for the dashboard timeline.
"""
from typing import List, Any
import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from datetime import datetime
import uuid

from app.api import deps
from app.models.user import User
from app.models.monitoring import ModelDegradationLog, ModelType

router = APIRouter()
logger = logging.getLogger("krishi_saathi.api.degradation")


class DegradationLogOut(BaseModel):
    id: uuid.UUID
    model_type: str
    model_version: str
    metric_name: str
    metric_value: float
    threshold: float
    triggered_at: datetime
    model_config = ConfigDict(from_attributes=True)


@router.get(
    "/{model_type}",
    response_model=List[DegradationLogOut],
    summary="List recent threshold breaches (Admin Only)",
)
def get_degradation_logs(
    model_type: str,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.get_current_active_user),
) -> Any:
    return (
        db.query(ModelDegradationLog)
        .filter(ModelDegradationLog.model_type == ModelType(model_type))
        .order_by(ModelDegradationLog.triggered_at.desc())
        .limit(limit)
        .all()
    )
