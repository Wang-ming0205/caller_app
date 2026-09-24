from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

class TransactionItemCreate(BaseModel):
    item_name: str = Field(min_length=1, max_length=100)
    qty: int = Field(default=1, ge=1)
    unit_price: Decimal = Field(default=0, ge=0)

    @field_validator("item_name")
    @classmethod
    def validate_item_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Item name cannot be empty")
        return value

class TransactionCreate(BaseModel):
    customer_id: int
    stylist_user_id: int | None = None
    note: str | None = None
    record_date: datetime | None = None
    items: list[TransactionItemCreate]


# ===== 新增：修改消費紀錄使用的 payload =====
class TransactionUpdate(BaseModel):
    note: str | None = None
    record_date: datetime | None = None

    items: list[TransactionItemCreate] = Field(
        min_length=1,
    )


class TransactionItemOut(BaseModel):
    id: int
    item_name: str
    qty: int
    unit_price: Decimal
    subtotal: Decimal

    class Config:
        from_attributes = True

class TransactionOut(BaseModel):
    id: int
    customer_id: int | None = None
    stylist_user_id: int | None = None
    total_amount: Decimal
    note: str | None = None
    record_date: datetime
    created_at: datetime
    items: list[TransactionItemOut]

    class Config:
        from_attributes = True
