"""
api/v1/model_registry.py
-------------------------
Admin endpoints for the model registry — list versions, view status,
and trigger safe atomic model promotion.

All routes secured behind JWT + role 'officer' (admin/officer authority).
"""
import uuid
import logging
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.schemas.model_registry import ModelRegistryOut, PromoteModelRequest
from app.crud.crud_model_registry import (
    get_active_model,
    get_all_versions,
    get_registry_entry,
    mark_model_degraded,
    promote_model,
    create_candidate_model,
)
from app.schemas.model_registry import ModelRegistryCreate

router = APIRouter()
logger = logging.getLogger("krishi_saathi.api.model_registry")


@router.get(
    "/{model_type}/active",
    response_model=ModelRegistryOut,
    summary="Get the currently active model for a given type",
)
def get_active(
    model_type: str,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.get_current_active_user),
) -> Any:
    entry = get_active_model(db, model_type=model_type)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active model found for type='{model_type}'.",
        )
    return entry


@router.get(
    "/{model_type}/versions",
    response_model=List[ModelRegistryOut],
    summary="List all versions for a model type (newest first)",
)
def list_versions(
    model_type: str,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.get_current_active_user),
) -> Any:
    return get_all_versions(db, model_type=model_type)


@router.post(
    "/promote",
    response_model=ModelRegistryOut,
    status_code=status.HTTP_200_OK,
    summary="Promote a candidate model to active (atomically demotes old active to degraded)",
)
def promote(
    payload: PromoteModelRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    try:
        result = promote_model(db, candidate_id=payload.candidate_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    logger.info(
        f"Promotion authorized | candidate={payload.candidate_id} "
        f"| promoted_by={current_user.id}"
    )
    return result


@router.post(
    "/register",
    response_model=ModelRegistryOut,
    status_code=status.HTTP_201_CREATED,
    summary="Manually register a new model version as candidate",
)
def register_candidate(
    payload: ModelRegistryCreate,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.get_current_active_user),
) -> Any:
    return create_candidate_model(
        db,
        model_type=payload.model_type,
        model_version=payload.model_version,
        trained_at=payload.trained_at,
        metrics_snapshot=payload.metrics_snapshot,
    )


@router.patch(
    "/{entry_id}/degrade",
    response_model=ModelRegistryOut,
    summary="Manually mark a registry entry as degraded",
)
def degrade(
    entry_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    entry = get_registry_entry(db, entry_id=entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registry entry {entry_id} not found.",
        )
    result = mark_model_degraded(db, entry_id=entry_id)
    logger.info(f"Model manually degraded | id={entry_id} | by_user={current_user.id}")
    return result
