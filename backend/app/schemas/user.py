from datetime import datetime
from pydantic import BaseModel, ConfigDict
import uuid

# Shared properties
class UserBase(BaseModel):
    phone_number: str
    full_name: str
    is_active: bool = True

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: str | None = None

class UserInDBBase(UserBase):
    id: uuid.UUID
    role_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Additional properties to return via API
class User(UserInDBBase):
    pass

# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str

class RoleBase(BaseModel):
    name: str
    description: str | None = None

class Role(RoleBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)
