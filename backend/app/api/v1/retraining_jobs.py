"""
api/v1/retraining_jobs.py
--------------------------
Read-only endpoint to list retraining jobs for the admin data table.
"""
from typing import List, Any, Optional
import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from datetime import datetime
import uuid

from app.api import deps
from app.models.user import User
from app.models.retraining import ModelRetrainingJob

router = APIRouter()
logger = logging.getLogger("krishi_saathi.api.retraining")


class RetrainingJobOut(BaseModel):
    id: uuid.UUID
    model_type: str
    triggered_by: str
    status: str
    old_model_version: str
    new_model_version: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


@router.get(
    "",
    response_model=List[RetrainingJobOut],
    summary="List all retraining jobs (Admin Only)",
)
def list_retraining_jobs(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.get_current_active_user),
) -> Any:
    return (
        db.query(ModelRetrainingJob)
        .order_by(ModelRetrainingJob.created_at.desc())
        .limit(limit)
        .all()
    )
