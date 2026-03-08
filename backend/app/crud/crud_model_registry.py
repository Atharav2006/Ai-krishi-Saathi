"""
crud/crud_model_registry.py
----------------------------
Database access layer for the model_registry table.

promote_model() is the critical path:
  - Wrapped in a single DB transaction
  - Sets exactly one record to 'active' per type
  - Demotes the previous active to 'degraded'
  - Raises on any constraint violation (prevents race conditions)
"""
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, Any

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.model_registry import ModelRegistry, ModelTypeEnum, ModelStatusEnum

logger = logging.getLogger("krishi_saathi.crud.model_registry")


# ─── Create ──────────────────────────────────────────────────────────────────

def create_model_entry(
    db: Session,
    *,
    model_type: str,
    model_version: str,
    status: str = "candidate",
    trained_at: Optional[datetime] = None,
    metrics_snapshot: Optional[dict[str, Any]] = None,
) -> ModelRegistry:
    """Insert a new registry entry. Default status is 'candidate'."""
    record = ModelRegistry(
        id=uuid.uuid4(),
        model_type=ModelTypeEnum(model_type),
        model_version=model_version,
        status=ModelStatusEnum(status),
        trained_at=trained_at,
        metrics_snapshot=metrics_snapshot,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info(f"Model registered | type={model_type} | version={model_version} | status={status}")
    return record


# ─── Read ─────────────────────────────────────────────────────────────────────

def get_active_model(db: Session, *, model_type: str) -> Optional[ModelRegistry]:
    """Return the single active entry for a model type, or None."""
    return (
        db.query(ModelRegistry)
        .filter(
            ModelRegistry.model_type == ModelTypeEnum(model_type),
            ModelRegistry.status == ModelStatusEnum.active,
        )
        .first()
    )


def get_registry_entry(db: Session, *, entry_id: uuid.UUID) -> Optional[ModelRegistry]:
    return db.query(ModelRegistry).filter(ModelRegistry.id == entry_id).first()


def get_all_versions(db: Session, *, model_type: str) -> list[ModelRegistry]:
    return (
        db.query(ModelRegistry)
        .filter(ModelRegistry.model_type == ModelTypeEnum(model_type))
        .order_by(ModelRegistry.created_at.desc())
        .all()
    )


# ─── Status Mutations ─────────────────────────────────────────────────────────

def mark_model_degraded(db: Session, *, entry_id: uuid.UUID) -> ModelRegistry:
    """
    Demote a specific registry entry to 'degraded'.
    Does NOT automatically promote a candidate — caller must handle promotion
    separately to maintain explicit control over the promotion workflow.
    """
    record = get_registry_entry(db, entry_id=entry_id)
    if not record:
        raise ValueError(f"No registry entry found for id={entry_id}")
    record.status = ModelStatusEnum.degraded
    db.commit()
    db.refresh(record)
    logger.info(f"Model degraded | id={entry_id} | type={record.model_type} | version={record.model_version}")
    return record


def create_candidate_model(
    db: Session,
    *,
    model_type: str,
    model_version: str,
    trained_at: Optional[datetime] = None,
    metrics_snapshot: Optional[dict[str, Any]] = None,
) -> ModelRegistry:
    """Convenience wrapper that explicitly sets status=candidate."""
    return create_model_entry(
        db,
        model_type=model_type,
        model_version=model_version,
        status="candidate",
        trained_at=trained_at,
        metrics_snapshot=metrics_snapshot,
    )


def promote_model(db: Session, *, candidate_id: uuid.UUID) -> ModelRegistry:
    """
    Atomically promote a candidate to active:
      1. LOCK the candidate row — ensures no concurrent promotion races.
      2. Validate it is still a candidate.
      3. Find current active (if any) and demote it to degraded.
      4. Set candidate → active.
      5. Commit once — both changes land together or neither does.

    Raises:
        ValueError: if candidate_id not found or not in candidate status.
        IntegrityError: if the partial unique index is violated (two active models).
    """
    # Step 1 — Fetch with row-level lock to prevent concurrent promotion races
    candidate = (
        db.query(ModelRegistry)
        .filter(ModelRegistry.id == candidate_id)
        .with_for_update()
        .first()
    )

    if not candidate:
        raise ValueError(f"No registry entry found for candidate_id={candidate_id}")
    if candidate.status != ModelStatusEnum.candidate:
        raise ValueError(
            f"Entry {candidate_id} has status='{candidate.status.value}', not 'candidate'. "
            "Only candidates can be promoted."
        )

    # Step 2 — Demote existing active (if present)
    current_active = get_active_model(db, model_type=candidate.model_type.value)
    if current_active:
        current_active.status = ModelStatusEnum.degraded
        logger.info(
            f"Demoting active model | id={current_active.id} | version={current_active.model_version}"
        )
        db.add(current_active)

    # Step 3 — Promote candidate
    candidate.status = ModelStatusEnum.active
    db.add(candidate)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        logger.error(f"Promotion failed (integrity error): {exc}")
        raise

    db.refresh(candidate)
    logger.info(
        f"Model promoted to ACTIVE | type={candidate.model_type.value} "
        f"| version={candidate.model_version} | id={candidate.id}"
    )
    return candidate
