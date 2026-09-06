import re
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


TAIWAN_MOBILE_PATTERN = re.compile(r"09\d{8}")


def validate_taiwan_mobile(value: str) -> str:
    value = value.strip()

    if not TAIWAN_MOBILE_PATTERN.fullmatch(value):
        raise ValueError("Phone number must start with 09 and contain exactly 10 digits")

    return value


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
        return validate_taiwan_mobile(value)


class CustomerCreate(CustomerBase):
    birthday: date


class CustomerUpdate(BaseModel):
    name: str | None = None
    phone_number: str | None = None
    gender: str | None = None
    birthday: date | None = None
    note: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty")

        return value

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return validate_taiwan_mobile(value)


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