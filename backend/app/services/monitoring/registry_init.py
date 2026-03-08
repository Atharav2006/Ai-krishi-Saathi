"""
services/monitoring/registry_init.py
--------------------------------------
Startup auto-registration: scans the ml_pipeline/models/ directory for
known model files and registers them as 'active' in the model_registry table
if no entries exist yet for that model_type.

This ensures that models trained externally (via the ml_pipeline scripts)
are automatically tracked from the first API boot without manual intervention.
"""
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.crud.crud_model_registry import (
    get_active_model,
    create_model_entry,
)

logger = logging.getLogger("krishi_saathi.monitoring.registry_init")

MODEL_DIR = Path(__file__).parents[4] / "ml_pipeline" / "models"

# Map model_type → ordered list of candidate file patterns to look for
MODEL_FILE_PATTERNS: dict[str, list[str]] = {
    "price_forecast": [
        "price_forecast.onnx",
        "price_forecast_rf.joblib",
        "price_forecast_lstm.onnx",
    ],
    "disease_detection": [
        "disease_model.tflite",
        "disease_model.onnx",
    ],
}


def _extract_version_from_path(path: Path, fallback_version: str) -> str:
    """
    Attempt to extract a version tag from file name or mtime.
    Uses file modification time as version when no embedded tag is found.
    """
    # Try to find a version pattern like _v1.2.3 or _20240215 in the stem
    match = re.search(r"v(\d+[\.\d]*)|(20\d{6})", path.stem)
    if match:
        return match.group(0)
    # Fall back to ISO date of file mtime
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        return mtime.strftime("%Y%m%d")
    except OSError:
        return fallback_version


def auto_register_models(db: Session) -> None:
    """
    Called once at application startup (inside lifespan).
    For each model type:
      - Skip if an active entry already exists in the registry.
      - Scan model directory for known artifact files.
      - Register the first found file as 'active'.
    """
    for model_type, file_patterns in MODEL_FILE_PATTERNS.items():
        existing_active = get_active_model(db, model_type=model_type)
        if existing_active:
            logger.info(
                f"Registry OK | type={model_type} | active_version={existing_active.model_version}"
            )
            continue

        registered = False
        for filename in file_patterns:
            model_path = MODEL_DIR / filename
            if model_path.exists():
                version = _extract_version_from_path(model_path, fallback_version="v1.0.0")
                try:
                    mtime = datetime.fromtimestamp(model_path.stat().st_mtime, tz=timezone.utc)
                except OSError:
                    mtime = None

                create_model_entry(
                    db,
                    model_type=model_type,
                    model_version=version,
                    status="active",  # First-boot: promote directly to active
                    trained_at=mtime,
                    metrics_snapshot=None,  # Will be populated by daily metric job
                )
                logger.info(
                    f"Auto-registered | type={model_type} | version={version} "
                    f"| file={filename} | status=active"
                )
                registered = True
                break  # Only register the first (most preferred) found artifact

        if not registered:
            logger.warning(
                f"No model artifact found for type={model_type}. "
                "Registry entry will be created after training completes."
            )
