"""
Shared monitoring helper used by both ML inference services.
Builds a non-blocking background thread to write the prediction log,
ensuring zero impact on inference response time.
"""
import hashlib
import json
import logging
import threading
import uuid
from typing import Any, Optional

from sqlalchemy.orm import sessionmaker

from app.schemas.monitoring import PredictionLogCreate
from app.crud.crud_monitoring import create_prediction_log

logger = logging.getLogger("krishi_saathi.monitoring.writer")


def compute_input_hash(payload: dict) -> str:
    """SHA-256 of the canonical (sorted-key) JSON serialization of the input payload."""
    canonical = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


def log_prediction_async(
    *,
    session_factory: sessionmaker,
    user_id: Optional[uuid.UUID],
    model_type: str,
    model_version: str,
    input_payload: dict,
    predicted_value: Any,
    confidence_score: float,
    latency_ms: float,
) -> None:
    """
    Fire-and-forget background write. Spawns a daemon thread so it never
    blocks the FastAPI response path. The thread creates its own short-lived
    DB session and closes it cleanly regardless of success or failure.
    """
    input_hash = compute_input_hash(input_payload)
    log_obj = PredictionLogCreate(
        user_id=user_id,
        model_type=model_type,
        model_version=model_version,
        input_hash=input_hash,
        predicted_value=str(predicted_value),
        confidence_score=confidence_score,
        latency_ms=latency_ms,
    )

    def _write():
        db = session_factory()
        try:
            create_prediction_log(db, obj_in=log_obj)
        except Exception as exc:
            logger.error(f"Background prediction log write failed: {exc}")
        finally:
            db.close()

    t = threading.Thread(target=_write, daemon=True)
    t.start()
