# from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric
# from sqlalchemy.sql import func
# from sqlalchemy.orm import relationship
# from app.core.database import Base

# class Transaction(Base):
#     __tablename__ = "transactions"

#     id = Column(Integer, primary_key=True, index=True)
#     customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
#     stylist_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
#     total_amount = Column(Numeric(10, 2), nullable=False, default=0)
#     note = Column(Text, nullable=True)
#     record_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
#     created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

#     items = relationship("TransactionItem", back_populates="transaction", cascade="all, delete-orphan")

# class TransactionItem(Base):
#     __tablename__ = "transaction_items"

#     id = Column(Integer, primary_key=True, index=True)
#     transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True)
#     item_name = Column(String(100), nullable=False)
#     qty = Column(Integer, nullable=False, default=1)
#     unit_price = Column(Numeric(10, 2), nullable=False, default=0)
#     subtotal = Column(Numeric(10, 2), nullable=False, default=0)

#     transaction = relationship("Transaction", back_populates="items")


#==============================
# from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func

# from app.core.database import Base


# class Transaction(Base):
#     __tablename__ = "transactions"

#     id = Column(Integer, primary_key=True, index=True)
#     customer_id = Column(
#         Integer,
#         ForeignKey("customers.id", ondelete="CASCADE"),
#         nullable=True,
#         index=True,
#     )
#     stylist_user_id = Column(
#         Integer,
#         ForeignKey("users.id"),
#         nullable=True,
#         index=True,
#     )
#     total_amount = Column(Numeric(10, 2), nullable=False, default=0)
#     note = Column(Text, nullable=True)
#     record_date = Column(
#         DateTime(timezone=True),
#         nullable=False,
#         server_default=func.now(),
#         index=True,
#     )
#     created_at = Column(
#         DateTime(timezone=True),
#         nullable=False,
#         server_default=func.now(),
#     )

#     items = relationship(
#         "TransactionItem",
#         back_populates="transaction",
#         cascade="all, delete-orphan",
#     )


# class TransactionItem(Base):
#     __tablename__ = "transaction_items"

#     id = Column(Integer, primary_key=True, index=True)
#     transaction_id = Column(
#         Integer,
#         ForeignKey("transactions.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )
#     item_name = Column(String(100), nullable=False)
#     qty = Column(Integer, nullable=False, default=1)
#     unit_price = Column(Numeric(10, 2), nullable=False, default=0)
#     subtotal = Column(Numeric(10, 2), nullable=False, default=0)

#     transaction = relationship("Transaction", back_populates="items")



#================
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True)
    stylist_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0)
    note = Column(Text, nullable=True)
    record_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    items = relationship("TransactionItem", back_populates="transaction", cascade="all, delete-orphan")

class TransactionItem(Base):
    __tablename__ = "transaction_items"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(100), nullable=False)
    qty = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False, default=0)
    subtotal = Column(Numeric(10, 2), nullable=False, default=0)

    transaction = relationship("Transaction", back_populates="items")


