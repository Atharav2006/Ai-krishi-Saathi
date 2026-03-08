from typing import Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.user import User, Role
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_phone(self, db: Session, *, phone_number: str) -> Optional[User]:
        return db.query(User).filter(User.phone_number == phone_number, User.is_deleted == False).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            phone_number=obj_in.phone_number,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_active=obj_in.is_active,
        )
        # Default assignment logic (assume Farmer if none provided)
        role = db.query(Role).filter(Role.name == "Farmer").first()
        if role:
            db_obj.role_id = role.id

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(
        self, db: Session, *, phone_number: str, password: str
    ) -> Optional[User]:
        user = self.get_by_phone(db, phone_number=phone_number)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

user = CRUDUser(User)
