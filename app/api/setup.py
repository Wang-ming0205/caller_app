from datetime import datetime, timezone
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import hash_password
from app.models.user import User
from app.models.customer import Customer
from app.models.transaction import Transaction, TransactionItem

router = APIRouter(prefix="/setup", tags=["setup"])

@router.post("/seed")
def seed_data(db: Session = Depends(get_db)):
    if not settings.ENABLE_SEED:
        raise HTTPException(status_code=403, detail="Seed endpoint is disabled")

    existing_admin = db.execute(select(User).where(User.username == "admin")).scalar_one_or_none()
    if existing_admin:
        return {"message": "Seed already exists"}

    admin = User(username="admin", password_hash=hash_password("admin123"), full_name="System Admin", role="admin")
    manager = User(username="manager", password_hash=hash_password("manager123"), full_name="Store Manager", role="manager")
    staff = User(username="staff", password_hash=hash_password("staff123"), full_name="Front Desk", role="staff")
    db.add_all([admin, manager, staff])
    db.flush()

    c1 = Customer(name="王小明", phone_number="0912345678", note="喜歡剪短", owner_user_id=manager.id)
    c2 = Customer(name="陳小美", phone_number="0987654321", note="固定染髮", owner_user_id=staff.id)
    db.add_all([c1, c2])
    db.flush()

    tx1 = Transaction(
        customer_id=c1.id,
        stylist_user_id=manager.id,
        total_amount=Decimal("700"),
        note="剪髮+洗髮",
        record_date=datetime.now(timezone.utc),
        items=[
            TransactionItem(item_name="剪髮", qty=1, unit_price=Decimal("500"), subtotal=Decimal("500")),
            TransactionItem(item_name="洗髮", qty=1, unit_price=Decimal("200"), subtotal=Decimal("200")),
        ],
    )
    tx2 = Transaction(
        customer_id=c1.id,
        stylist_user_id=staff.id,
        total_amount=Decimal("1200"),
        note="染髮",
        record_date=datetime.now(timezone.utc),
        items=[TransactionItem(item_name="染髮", qty=1, unit_price=Decimal("1200"), subtotal=Decimal("1200"))],
    )

    db.add_all([tx1, tx2])
    db.commit()

    return {
        "message": "Seed created",
        "accounts": [
            {"username": "admin", "password": "admin123"},
            {"username": "manager", "password": "manager123"},
            {"username": "staff", "password": "staff123"},
        ],
    }
