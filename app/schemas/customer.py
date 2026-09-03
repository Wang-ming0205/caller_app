from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1)
    phone_number: str = Field(..., min_length=1, max_length=20)
    gender: str | None = None
    birthday: date | None = None
    note: str | None = None
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Name cannot be empty")

        return value

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Phone number cannot be empty")

        return value

class CustomerCreate(CustomerBase):
    birthday: date

class CustomerUpdate(BaseModel):
    name: str | None = None
    phone_number: str | None = None
    gender: str | None = None
    birthday: date | None = None
    note: str | None = None

    @field_validator("name", "phone_number")
    @classmethod
    def validate_required_text(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()
        if not value:
            raise ValueError("Value cannot be empty")

        return value

class CustomerOut(CustomerBase):
    id: int
    owner_user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CustomerSummaryOut(BaseModel):
    customer_id: int
    name: str
    phone_number: str
    last_record: str | None = None
    last_items: str | None = None
    total_amount: Decimal
    last_day: datetime | None = None
