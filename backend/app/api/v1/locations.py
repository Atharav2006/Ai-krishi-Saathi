import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/states", response_model=List[schemas.State])
def read_states(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve overarching active states securely.
    """
    return crud.state.get_multi(db, skip=skip, limit=limit)

@router.get("/states/{state_id}/districts", response_model=List[schemas.District])
def read_districts_by_state(
    state_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve districts chained locally to a state, highly optimized for frontend dropdowns.
    """
    state_record = crud.state.get(db, id=state_id)
    if not state_record:
        raise HTTPException(status_code=404, detail="State not found")
        
    return crud.district.get_by_state(db, state_id=state_id, skip=skip, limit=limit)
