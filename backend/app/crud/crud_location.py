from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.location import State, District
from app.schemas.location import StateBase, DistrictBase
import uuid

class CRUDState(CRUDBase[State, StateBase, StateBase]):
    def get_by_name(self, db: Session, *, name: str) -> State | None:
        return db.query(State).filter(State.name == name).first()

class CRUDDistrict(CRUDBase[District, DistrictBase, DistrictBase]):
    def get_by_state(
        self, db: Session, *, state_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[District]:
        return (
            db.query(District)
            .filter(District.state_id == state_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

state = CRUDState(State)
district = CRUDDistrict(District)
