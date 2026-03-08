from typing import Generator, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
import uuid

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_db() -> Generator[Session, None, None]:
    """Dependency injects a DB session into endpoints, auto-closing after requests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]

def get_current_user(
    db: SessionDep, token: TokenDep
) -> User:
    """Verifies JWT access token and fetches the current user from the database."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        # Security: Prevent refresh tokens from accessing standard API routes
        if payload.get("type") == "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh tokens cannot be used as access tokens"
            )
            
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    # Needs a raw CRUD call to fetch user via Token Subject (which is their phone or UUID)
    # Using raw SQLAlchemy query here to avoid circular imports with CRUD layer
    user = db.query(User).filter(User.id == token_data.sub).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_deleted:
        raise HTTPException(status_code=400, detail="User is dormant/deleted")
        
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]

def get_current_active_user(
    current_user: CurrentUser,
) -> User:
    """Ensures the authenticated user possesses an active status."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_admin(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Role Based Access Control: Admins only."""
    if current_user.role.name != "Admin":
        raise HTTPException(
            status_code=403, detail="Not enough privileges"
        )
    return current_user
