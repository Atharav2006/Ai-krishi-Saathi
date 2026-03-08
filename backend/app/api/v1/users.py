from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current localized user profile.
    """
    return current_user

@router.get("/", response_model=List[schemas.User], dependencies=[Depends(deps.get_current_admin)])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Admin only: Retrieve all users in the system securely.
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users
