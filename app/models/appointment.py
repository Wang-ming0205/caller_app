from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.core.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(
        Integer,
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    starts_at = Column(DateTime(timezone=True), nullable=False, index=True)
    service_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default="booked")
    internal_note = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )