"""
services/monitoring/scheduler.py
---------------------------------
APScheduler setup with the full daily ML monitoring pipeline:
  Stage 0 — 01:30 UTC: Generate 7-day crop price forecasts
  Stage 1 — 02:00 UTC: Compute rolling metrics + evaluate degradation thresholds
  Stage 2 — 02:30 UTC: Process pending retraining jobs (runs after Stage 1)

All stages share a daily cron trigger. APScheduler runs
them sequentially within a single BackgroundScheduler thread pool, with
max_instances=1 to prevent overlap. Stage 2 tolerates Stage 1 failures.
"""
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.db.session import SessionLocal
from app.core.config import settings
from app.services.monitoring.metric_service import run_daily_metric_computation

logger = logging.getLogger("krishi_saathi.monitoring.scheduler")

_scheduler: BackgroundScheduler | None = None

def _run_forecast_generation() -> None:
    """
    Stage 0 — Run at 01:30 UTC.
    Pre-computes the 7-day crop price predictions for the top demo districts.
    """
    from app.services.forecasting.forecast_generator import generate_7_day_forecasts
    logger.info(f"[Stage 0] Forecast generation job started at {datetime.now(timezone.utc).isoformat()}")
    db = SessionLocal()
    try:
        count = generate_7_day_forecasts(db)
        logger.info(f"[Stage 0] Generated {count} individual forecast data points.")
    except Exception as exc:
        logger.error(f"[Stage 0] Forecast generation job failed: {exc}", exc_info=True)
    finally:
        db.close()
    logger.info("[Stage 0] Forecast generation job complete.")


def _run_metrics_and_degradation() -> None:
    """
    Stage 1 — Run at 02:00 UTC.
    Compute rolling 30-day metrics and evaluate degradation thresholds.
    Enqueues retraining jobs in the DB if any threshold is breached.
    """
    logger.info(f"[Stage 1] Metrics + degradation job started at {datetime.now(timezone.utc).isoformat()}")
    db = SessionLocal()
    try:
        run_daily_metric_computation(db, model_version=settings.MODEL_VERSION_TAG)
    except Exception as exc:
        logger.error(f"[Stage 1] Metrics job failed: {exc}", exc_info=True)
    finally:
        db.close()
    logger.info("[Stage 1] Metrics + degradation job complete.")


def _run_retraining_processor() -> None:
    """
    Stage 2 — Run at 02:30 UTC (30 minutes after Stage 1).
    Picks up any pending retraining jobs enqueued by Stage 1.
    Runs subprocess training, registers candidate, promotes if improved.
    Intentionally scheduled 30m after Stage 1 to guarantee Stage 1 finishes.
    """
    from app.services.retraining.retraining_service import process_pending_retraining_jobs

    logger.info(f"[Stage 2] Retraining processor started at {datetime.now(timezone.utc).isoformat()}")
    db = SessionLocal()
    try:
        process_pending_retraining_jobs(db)
    except Exception as exc:
        logger.error(f"[Stage 2] Retraining processor failed: {exc}", exc_info=True)
    finally:
        db.close()
    logger.info("[Stage 2] Retraining processor complete.")


def start_scheduler() -> None:
    """
    Start the APScheduler background scheduler with both daily jobs.
    Called once at application startup from main.py lifespan.
    """
    global _scheduler
    _scheduler = BackgroundScheduler(
        job_defaults={"coalesce": True, "max_instances": 1},
        timezone="UTC",
    )

    # Stage 0: Pre-compute Price Forecasts (01:30 UTC)
    _scheduler.add_job(
        _run_forecast_generation,
        trigger=CronTrigger(hour=1, minute=30),
        id="daily_forecast_generation",
        name="[Stage 0] Pre-compute Crop Price Forecasts",
        replace_existing=True,
    )

    # Stage 1: Metrics + degradation detection (02:00 UTC)
    _scheduler.add_job(
        _run_metrics_and_degradation,
        trigger=CronTrigger(hour=2, minute=0),
        id="daily_metrics_degradation",
        name="[Stage 1] Rolling Metrics + Degradation Detection",
        replace_existing=True,
    )

    # Stage 2: Retraining processor (02:30 UTC — runs after Stage 1 completes)
    _scheduler.add_job(
        _run_retraining_processor,
        trigger=CronTrigger(hour=2, minute=30),
        id="daily_retraining_processor",
        name="[Stage 2] Automated Retraining + Candidate Promotion",
        replace_existing=True,
    )

    _scheduler.start()
    logger.info(
        "Scheduler started. "
        "Stage 0 (forecast) @ 01:30 UTC | "
        "Stage 1 (metrics + degradation) @ 02:00 UTC | "
        "Stage 2 (retraining + promotion) @ 02:30 UTC"
    )


def shutdown_scheduler() -> None:
    """Gracefully shuts down the scheduler on application teardown."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down gracefully.")
