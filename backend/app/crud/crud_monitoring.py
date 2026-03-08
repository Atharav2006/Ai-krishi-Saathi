"""
crud/crud_monitoring.py
-----------------------
Database access layer for the monitoring tables.
All write operations are designed to be called from a background thread/task
so they never block the inference-critical response path.
"""
import uuid
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.monitoring import PredictionLog, GroundTruthLog, ModelMetric, ModelType, ModelDegradationLog
from app.schemas.monitoring import PredictionLogCreate, GroundTruthCreate

logger = logging.getLogger("krishi_saathi.crud.monitoring")


# ─── Prediction Logs ─────────────────────────────────────────────────────────

def create_prediction_log(db: Session, *, obj_in: PredictionLogCreate) -> PredictionLog:
    """
    Insert a prediction log record. Called from a background thread.
    Uses its own short-lived session to avoid polluting the request session.
    """
    record = PredictionLog(
        id=uuid.uuid4(),
        user_id=obj_in.user_id,
        model_type=ModelType(obj_in.model_type),
        model_version=obj_in.model_version,
        input_hash=obj_in.input_hash,
        predicted_value=obj_in.predicted_value,
        confidence_score=obj_in.confidence_score,
        latency_ms=obj_in.latency_ms,
    )
    try:
        db.add(record)
        db.commit()
        db.refresh(record)
        logger.debug(f"Prediction log written: id={record.id} type={obj_in.model_type}")
        return record
    except Exception as exc:
        db.rollback()
        logger.error(f"Failed to write prediction log: {exc}")
        raise


# ─── Ground Truth ─────────────────────────────────────────────────────────────

def get_prediction_log(db: Session, *, prediction_id: uuid.UUID) -> Optional[PredictionLog]:
    return db.query(PredictionLog).filter(PredictionLog.id == prediction_id).first()


def get_ground_truth_for_prediction(
    db: Session, *, prediction_id: uuid.UUID
) -> Optional[GroundTruthLog]:
    return (
        db.query(GroundTruthLog)
        .filter(GroundTruthLog.prediction_id == prediction_id)
        .first()
    )


def create_ground_truth(
    db: Session, *, obj_in: GroundTruthCreate
) -> GroundTruthLog:
    """
    Insert ground truth. Raises IntegrityError if a duplicate exists
    (caught by the API layer which returns HTTP 409).
    """
    record = GroundTruthLog(
        id=uuid.uuid4(),
        prediction_id=obj_in.prediction_id,
        actual_value=obj_in.actual_value,
    )
    try:
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    except IntegrityError:
        db.rollback()
        raise


# ─── Model Metrics ─────────────────────────────────────────────────────────────

def create_model_metric(
    db: Session,
    *,
    model_type: str,
    model_version: str,
    metric_name: str,
    metric_value: float,
    window_start: datetime,
    window_end: datetime,
) -> ModelMetric:
    record = ModelMetric(
        id=uuid.uuid4(),
        model_type=ModelType(model_type),
        model_version=model_version,
        metric_name=metric_name,
        metric_value=metric_value,
        window_start=window_start,
        window_end=window_end,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_logs_for_window(
    db: Session,
    *,
    model_type: str,
    window_start: datetime,
    window_end: datetime,
    limit: int = 50_000,
):
    """
    Efficient indexed range query fetching predictions with ground truth for
    metric computation. Uses JOIN to avoid N+1. Capped at 50k rows per window.
    """
    return (
        db.query(PredictionLog, GroundTruthLog)
        .join(GroundTruthLog, GroundTruthLog.prediction_id == PredictionLog.id)
        .filter(
            PredictionLog.model_type == ModelType(model_type),
            PredictionLog.created_at >= window_start,
            PredictionLog.created_at <= window_end,
        )
        .limit(limit)
        .all()
    )
