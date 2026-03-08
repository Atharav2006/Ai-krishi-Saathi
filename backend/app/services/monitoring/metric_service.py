"""
services/monitoring/metric_service.py
--------------------------------------
Computes rolling 30-day performance metrics, then evaluates each metric
against configured thresholds. Triggers degradation marking and logging
when a breach is detected — with dedup guards to prevent repeat events.

Called by APScheduler daily job. Must never crash the scheduler.
Daily sequence:
  1. compute_price_metrics()  →  store in model_metrics
  2. evaluate_degradation()   →  check thresholds, mark_model_degraded(), log event
  3. compute_disease_metrics() → store in model_metrics
  4. evaluate_degradation()   →  same
"""
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Tuple

import numpy as np
from sqlalchemy.orm import Session

from app.crud.crud_monitoring import get_logs_for_window, create_model_metric
from app.models.monitoring import PredictionLog, GroundTruthLog, ModelDegradationLog, ModelType
from app.services.monitoring.degradation_config import get_threshold, ALL_THRESHOLDS

logger = logging.getLogger("krishi_saathi.monitoring.metrics")

THIRTY_DAYS = timedelta(days=30)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _safe_float(value: str) -> float | None:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _has_degradation_log_in_window(
    db: Session,
    *,
    model_type: str,
    model_version: str,
    metric_name: str,
    window_start: datetime,
) -> bool:
    """
    Fast indexed dedup check: has this (type, version, metric) already been
    logged within the current 30-day computation window?
    Uses the composite index ix_degradation_logs_type_version_metric.
    """
    count = (
        db.query(ModelDegradationLog)
        .filter(
            ModelDegradationLog.model_type == ModelType(model_type),
            ModelDegradationLog.model_version == model_version,
            ModelDegradationLog.metric_name == metric_name,
            ModelDegradationLog.triggered_at >= window_start,
        )
        .limit(1)
        .count()
    )
    return count > 0


def _insert_degradation_log(
    db: Session,
    *,
    model_type: str,
    model_version: str,
    metric_name: str,
    metric_value: float,
    threshold: float,
) -> None:
    record = ModelDegradationLog(
        id=uuid.uuid4(),
        model_type=ModelType(model_type),
        model_version=model_version,
        metric_name=metric_name,
        metric_value=metric_value,
        threshold=threshold,
    )
    db.add(record)
    db.commit()
    logger.warning(
        f"DEGRADATION EVENT | type={model_type} | version={model_version} "
        f"| metric={metric_name} | value={metric_value:.4f} | threshold={threshold}"
    )


def _evaluate_and_mark_degraded(
    db: Session,
    *,
    model_type: str,
    model_version: str,
    metrics: dict[str, float],
    window_start: datetime,
) -> None:
    """
    Compare computed metrics against thresholds. For each breach:
      1. Dedup check (indexed query) — skip if already logged this window.
      2. mark_model_degraded() on the active registry entry.
      3. Insert degradation log event.
    Model stays 'active' — no auto-promotion. That is Phase 3.
    """
    from app.crud.crud_model_registry import get_active_model, mark_model_degraded

    for metric_name, metric_value in metrics.items():
        threshold_cfg = get_threshold(model_type, metric_name)
        if threshold_cfg is None:
            continue  # No threshold configured for this metric

        if not threshold_cfg.is_breached(metric_value):
            continue  # Within acceptable range

        logger.warning(
            f"Threshold breach | type={model_type} | metric={metric_name} "
            f"| value={metric_value:.4f} {'>' if threshold_cfg.direction == 'above' else '<'} "
            f"threshold={threshold_cfg.threshold}"
        )

        # Dedup: skip if we already logged this exact breach in this window
        if _has_degradation_log_in_window(
            db,
            model_type=model_type,
            model_version=model_version,
            metric_name=metric_name,
            window_start=window_start,
        ):
            logger.info(
                f"Dedup skip | degradation already logged for {model_type}/{metric_name} "
                f"this window."
            )
            continue

        # Mark the active registry entry as degraded (keeps model serving — retraining will promote a replacement)
        active = get_active_model(db, model_type=model_type)
        if active and active.model_version == model_version:
            try:
                mark_model_degraded(db, entry_id=active.id)
            except Exception as exc:
                logger.error(f"Failed to mark model degraded in registry: {exc}")

        # Persist the immutable degradation event
        _insert_degradation_log(
            db,
            model_type=model_type,
            model_version=model_version,
            metric_name=metric_name,
            metric_value=metric_value,
            threshold=threshold_cfg.threshold,
        )

        # Enqueue a retraining job (dedup: skip if one is already pending/running)
        from app.crud.crud_retraining import create_retraining_job, has_pending_or_running_job
        if not has_pending_or_running_job(db, model_type=model_type):
            create_retraining_job(
                db,
                model_type=model_type,
                old_model_version=model_version,
                triggered_by="degradation",
            )
            logger.info(
                f"Retraining job enqueued | type={model_type} | version={model_version}"
            )
        else:
            logger.info(
                f"Retraining job skipped (already queued) | type={model_type}"
            )
        # Only enqueue once per model_type per degradation run, even if multiple metrics breach
        break



# ─── Price Forecast Metrics ────────────────────────────────────────────────────

def compute_price_metrics(db: Session, model_version: str) -> dict[str, float]:
    """MAE, RMSE, MAPE over the last 30 days. Returns computed metric dict."""
    now = datetime.now(timezone.utc)
    window_start = now - THIRTY_DAYS

    rows: List[Tuple[PredictionLog, GroundTruthLog]] = get_logs_for_window(
        db, model_type="price_forecast", window_start=window_start, window_end=now,
    )

    if not rows:
        logger.info("No price prediction+ground_truth pairs in 30-day window. Skipping.")
        return {}

    actuals, preds = [], []
    for pred_log, gt_log in rows:
        p = _safe_float(pred_log.predicted_value)
        a = _safe_float(gt_log.actual_value)
        if p is not None and a is not None:
            preds.append(p)
            actuals.append(a)

    if not actuals:
        logger.warning("All price metric rows had non-numeric values. Skipping.")
        return {}

    preds_arr = np.array(preds)
    actuals_arr = np.array(actuals)
    mae = float(np.mean(np.abs(preds_arr - actuals_arr)))
    rmse = float(np.sqrt(np.mean((preds_arr - actuals_arr) ** 2)))
    nonzero = actuals_arr != 0
    mape = (
        float(np.mean(np.abs((preds_arr[nonzero] - actuals_arr[nonzero]) / actuals_arr[nonzero])) * 100)
        if nonzero.any() else 0.0
    )

    computed: dict[str, float] = {"MAE": mae, "RMSE": rmse, "MAPE": mape}
    logger.info(f"Price metrics [{model_version}] | MAE={mae:.2f} | RMSE={rmse:.2f} | MAPE={mape:.2f}%")

    for name, value in computed.items():
        create_model_metric(
            db, model_type="price_forecast", model_version=model_version,
            metric_name=name, metric_value=value, window_start=window_start, window_end=now,
        )

    return computed


# ─── Disease Detection Metrics ────────────────────────────────────────────────

def compute_disease_metrics(db: Session, model_version: str) -> dict[str, float]:
    """Accuracy and weighted F1 over the last 30 days. Returns computed metric dict."""
    from sklearn.metrics import accuracy_score, f1_score

    now = datetime.now(timezone.utc)
    window_start = now - THIRTY_DAYS

    rows: List[Tuple[PredictionLog, GroundTruthLog]] = get_logs_for_window(
        db, model_type="disease_detection", window_start=window_start, window_end=now,
    )

    if not rows:
        logger.info("No disease prediction+ground_truth pairs. Skipping.")
        return {}

    y_pred = [r[0].predicted_value.strip() for r in rows]
    y_true = [r[1].actual_value.strip() for r in rows]

    if not y_true:
        return {}

    accuracy = float(accuracy_score(y_true, y_pred))
    f1 = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))
    computed: dict[str, float] = {"Accuracy": accuracy, "F1": f1}

    logger.info(f"Disease metrics [{model_version}] | Accuracy={accuracy:.4f} | F1={f1:.4f}")

    now_ts = datetime.now(timezone.utc)
    window_start_ts = now_ts - THIRTY_DAYS
    for name, value in computed.items():
        create_model_metric(
            db, model_type="disease_detection", model_version=model_version,
            metric_name=name, metric_value=value, window_start=window_start_ts, window_end=now_ts,
        )

    return computed


# ─── Orchestrator ──────────────────────────────────────────────────────────────

def run_daily_metric_computation(db: Session, model_version: str) -> None:
    """
    Full daily pipeline (called by APScheduler):
      1. Compute price metrics
      2. Evaluate price degradation thresholds
      3. Compute disease metrics
      4. Evaluate disease degradation thresholds

    Each phase is exception-isolated — failure in one does not abort others.
    """
    now = datetime.now(timezone.utc)
    window_start = now - THIRTY_DAYS

    logger.info("=== Daily metric + degradation evaluation started ===")

    # ── Phase 1: Price ──────────────────────────────────────────────────────────
    try:
        price_metrics = compute_price_metrics(db, model_version=model_version)
    except Exception as exc:
        logger.error(f"Price metric computation failed: {exc}", exc_info=True)
        price_metrics = {}

    try:
        if price_metrics:
            _evaluate_and_mark_degraded(
                db,
                model_type="price_forecast",
                model_version=model_version,
                metrics=price_metrics,
                window_start=window_start,
            )
    except Exception as exc:
        logger.error(f"Price degradation evaluation failed: {exc}", exc_info=True)

    # ── Phase 2: Disease ────────────────────────────────────────────────────────
    try:
        disease_metrics = compute_disease_metrics(db, model_version=model_version)
    except Exception as exc:
        logger.error(f"Disease metric computation failed: {exc}", exc_info=True)
        disease_metrics = {}

    try:
        if disease_metrics:
            _evaluate_and_mark_degraded(
                db,
                model_type="disease_detection",
                model_version=model_version,
                metrics=disease_metrics,
                window_start=window_start,
            )
    except Exception as exc:
        logger.error(f"Disease degradation evaluation failed: {exc}", exc_info=True)

    logger.info("=== Daily metric + degradation evaluation complete ===")
