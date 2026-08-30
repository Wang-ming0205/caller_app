from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CatalogItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    default_price: Decimal = Field(default=0, ge=0)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Item name cannot be empty")
        return value


class CatalogItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    default_price: Decimal
    description: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime