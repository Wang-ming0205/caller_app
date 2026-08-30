# # from datetime import datetime
# # from decimal import Decimal
# # from pydantic import BaseModel, Field

# # class TransactionItemCreate(BaseModel):
# #     item_name: str
# #     qty: int = Field(default=1, ge=1)
# #     unit_price: Decimal = Field(default=0, ge=0)

# # class TransactionCreate(BaseModel):
# #     customer_id: int
# #     stylist_user_id: int | None = None
# #     note: str | None = None
# #     record_date: datetime | None = None
# #     items: list[TransactionItemCreate]

# # class TransactionItemOut(BaseModel):
# #     id: int
# #     item_name: str
# #     qty: int
# #     unit_price: Decimal
# #     subtotal: Decimal

# #     class Config:
# #         from_attributes = True

# # class TransactionOut(BaseModel):
# #     id: int
# #     customer_id: int
# #     stylist_user_id: int | None = None
# #     total_amount: Decimal
# #     note: str | None = None
# #     record_date: datetime
# #     created_at: datetime
# #     items: list[TransactionItemOut]

# #     class Config:
# #         from_attributes = True

# #==============
# from datetime import datetime
# from decimal import Decimal

# from pydantic import BaseModel, Field


# class TransactionItemCreate(BaseModel):
#     item_name: str
#     qty: int = Field(default=1, ge=1)
#     unit_price: Decimal = Field(default=0, ge=0)


# class TransactionCreate(BaseModel):
#     customer_id: int | None = None
#     stylist_user_id: int | None = None
#     note: str | None = None
#     record_date: datetime | None = None
#     items: list[TransactionItemCreate]


# class TransactionItemOut(BaseModel):
#     id: int
#     item_name: str
#     qty: int
#     unit_price: Decimal
#     subtotal: Decimal

#     class Config:
#         from_attributes = True


# class TransactionOut(BaseModel):
#     id: int
#     customer_id: int | None = None
#     stylist_user_id: int | None = None
#     total_amount: Decimal
#     note: str | None = None
#     record_date: datetime
#     created_at: datetime
#     items: list[TransactionItemOut]

#     class Config:
#         from_attributes = True


#=================

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

class TransactionItemCreate(BaseModel):
    item_name: str
    qty: int = Field(default=1, ge=1)
    unit_price: Decimal = Field(default=0, ge=0)

class TransactionCreate(BaseModel):
    customer_id: int | None = None
    stylist_user_id: int | None = None
    note: str | None = None
    record_date: datetime | None = None
    items: list[TransactionItemCreate]

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
