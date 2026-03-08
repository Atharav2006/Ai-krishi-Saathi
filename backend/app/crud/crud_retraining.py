"""
crud/crud_retraining.py
------------------------
Database access layer for model_retraining_jobs.
All status transitions are atomic single-row updates committed immediately.
"""
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.retraining import ModelRetrainingJob, RetrainingStatus, RetrainingTrigger

logger = logging.getLogger("krishi_saathi.crud.retraining")


def create_retraining_job(
    db: Session,
    *,
    model_type: str,
    old_model_version: str,
    triggered_by: str = "degradation",
) -> ModelRetrainingJob:
    """Insert a new retraining job with status=pending."""
    record = ModelRetrainingJob(
        id=uuid.uuid4(),
        model_type=model_type,
        triggered_by=RetrainingTrigger(triggered_by),
        status=RetrainingStatus.pending,
        old_model_version=old_model_version,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info(f"Retraining job created | id={record.id} | type={model_type} | version={old_model_version}")
    return record


def get_pending_jobs(db: Session, *, model_type: Optional[str] = None) -> list[ModelRetrainingJob]:
    """
    Fetch all pending retraining jobs, optionally filtered by model_type.
    Uses composite index ix_retraining_jobs_model_type_status.
    """
    q = db.query(ModelRetrainingJob).filter(
        ModelRetrainingJob.status == RetrainingStatus.pending
    )
    if model_type:
        q = q.filter(ModelRetrainingJob.model_type == model_type)
    return q.order_by(ModelRetrainingJob.created_at.asc()).all()


def has_pending_or_running_job(db: Session, *, model_type: str) -> bool:
    """
    Check whether a pending or running job already exists for this model_type.
    Prevents duplicate job submission when degradation fires repeatedly.
    """
    count = (
        db.query(ModelRetrainingJob)
        .filter(
            ModelRetrainingJob.model_type == model_type,
            ModelRetrainingJob.status.in_([RetrainingStatus.pending, RetrainingStatus.running]),
        )
        .limit(1)
        .count()
    )
    return count > 0


def mark_job_running(db: Session, *, job: ModelRetrainingJob) -> ModelRetrainingJob:
    job.status = RetrainingStatus.running
    job.started_at = datetime.now(timezone.utc)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def mark_job_success(
    db: Session,
    *,
    job: ModelRetrainingJob,
    new_model_version: str,
) -> ModelRetrainingJob:
    job.status = RetrainingStatus.success
    job.new_model_version = new_model_version
    job.completed_at = datetime.now(timezone.utc)
    db.add(job)
    db.commit()
    db.refresh(job)
    logger.info(f"Retraining job succeeded | id={job.id} | new_version={new_model_version}")
    return job


def mark_job_failed(
    db: Session,
    *,
    job: ModelRetrainingJob,
    error_message: str,
    new_model_version: Optional[str] = None,
) -> ModelRetrainingJob:
    job.status = RetrainingStatus.failed
    job.completed_at = datetime.now(timezone.utc)
    job.error_message = error_message[:2000]  # Truncate to fit Text column safely
    if new_model_version:
        job.new_model_version = new_model_version
    db.add(job)
    db.commit()
    db.refresh(job)
    logger.error(f"Retraining job failed | id={job.id} | error={error_message[:200]}")
    return job
