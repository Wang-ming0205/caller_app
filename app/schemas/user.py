from datetime import datetime
from pydantic import BaseModel, Field

class UserOut(BaseModel):
    id: int
    username: str
    full_name: str | None = None
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6)
    full_name: str | None = None
    role: str = "staff"
    is_active: bool = True

class UserUpdate(BaseModel):
    password: str | None = Field(default=None, min_length=6)
    full_name: str | None = None
    role: str | None = None
    is_active: bool | None = None
