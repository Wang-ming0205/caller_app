import re
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator


TAIWAN_MOBILE_PATTERN = re.compile(r"09\d{8}")

# 姓名允許：
# 中文、英文、空格、連字號、單引號、中間點
CUSTOMER_NAME_PATTERN = re.compile(
    r"^[A-Za-z\u4e00-\u9fff·・' \-]+$"
)

# 姓名至少要真的包含一個中文字或英文字
CUSTOMER_NAME_CONTENT_PATTERN = re.compile(
    r"[A-Za-z\u4e00-\u9fff]"
)

def validate_taiwan_mobile(value: str) -> str:
    value = value.strip()

    if not TAIWAN_MOBILE_PATTERN.fullmatch(value):
        raise ValueError("Phone number must start with 09 and contain exactly 10 digits")

    return value

def validate_customer_name(value: str) -> str:
    value = value.strip()

    if not value:
        raise ValueError("Name cannot be empty")

    if not CUSTOMER_NAME_PATTERN.fullmatch(value):
        raise ValueError(
            "Name can only contain Chinese, English letters, "
            "spaces, hyphens or middle dots"
        )

    if not CUSTOMER_NAME_CONTENT_PATTERN.search(value):
        raise ValueError(
            "Name must contain at least one Chinese or English letter"
        )

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
        return validate_customer_name(value)

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

        return validate_customer_name(value)

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


class TransactionItemSummaryOut(BaseModel):
    id: int
    item_name: str
    qty: int
    unit_price: Decimal
    subtotal: Decimal


class TransactionHistorySummaryOut(BaseModel):
    id: int
    visit_number: int
    total_amount: Decimal
    note: str | None = None
    record_date: datetime
    items: list[TransactionItemSummaryOut] = Field(
        default_factory=list
    )


class CustomerSummaryOut(BaseModel):
    customer_id: int
    name: str
    phone_number: str

    transaction_count: int
    total_amount: Decimal

    # 保留舊欄位，避免原本測試或其他前端壞掉
    last_record: str | None = None
    last_items: str | None = None
    last_day: datetime | None = None

    recent_transactions: list[
        TransactionHistorySummaryOut
    ] = Field(default_factory=list)

