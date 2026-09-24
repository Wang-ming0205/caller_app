# ======================    
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from datetime import datetime, timezone

from app.api.deps import get_current_user, require_roles, require_customer_access
from app.core.database import get_db
from app.models.customer import Customer
from app.models.transaction import Transaction, TransactionItem
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas.transaction import TransactionCreate, TransactionOut,TransactionUpdate

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionOut)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "staff")),
):
    customer = db.get(Customer, payload.customer_id)
    require_customer_access(customer, current_user)

    if not payload.items:
        raise HTTPException(status_code=400, detail="Transaction items required")

    total_amount = Decimal("0")
    tx_items = []
    for item in payload.items:
        subtotal = Decimal(item.qty) * Decimal(item.unit_price)
        total_amount += subtotal
        tx_items.append(
            TransactionItem(
                item_name=item.item_name,
                qty=item.qty,
                unit_price=item.unit_price,
                subtotal=subtotal,
            )
        )

    tx = Transaction(
        customer_id=payload.customer_id,
        stylist_user_id=payload.stylist_user_id or current_user.id,
        total_amount=total_amount,
        note=payload.note,
        record_date=payload.record_date or datetime.now(timezone.utc),
        items=tx_items,
    )
    db.add(tx)
    db.flush()

    db.add(
        AuditLog(
            user_id=current_user.id,
            action="create_transaction",
            target_type="transaction",
            target_id=tx.id,
            detail={
                "customer_id": payload.customer_id,
                "total_amount": str(total_amount),
            },
        )
    )

    db.commit()

    stmt = (
        select(Transaction)
        .options(selectinload(Transaction.items))
        .where(Transaction.id == tx.id)
    )
    created_tx = db.execute(stmt).scalar_one()
    return created_tx


@router.get("/customer/{customer_id}", response_model=list[TransactionOut])
def list_transactions_by_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.get(Customer, customer_id)
    require_customer_access(customer, current_user)

    stmt = (
        select(Transaction)
        .options(selectinload(Transaction.items))
        .where(Transaction.customer_id == customer_id)
        .order_by(Transaction.record_date.desc(), Transaction.id.desc())
    )
    return list(db.execute(stmt).scalars().unique().all())

# ===== 新增：修改一筆既有消費紀錄 =====
@router.put(
    "/{transaction_id}",
    response_model=TransactionOut,
)
def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "admin",
            "manager",
            "staff",
        )
    ),
):
    # 先把消費紀錄和項目一起查出來
    stmt = (
        select(Transaction)
        .options(
            selectinload(Transaction.items)
        )
        .where(
            Transaction.id == transaction_id
        )
    )

    transaction = (
        db.execute(stmt)
        .scalar_one_or_none()
    )

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found",
        )

    # 確認目前登入者能操作這位客戶
    customer = db.get(
        Customer,
        transaction.customer_id,
    )

    require_customer_access(
        customer,
        current_user,
    )

    # 再次保護：消費項目不能是空陣列
    if not payload.items:
        raise HTTPException(
            status_code=400,
            detail="Transaction items required",
        )

    # 重新計算總金額
    total_amount = Decimal("0")

    new_items = []

    for item in payload.items:
        subtotal = (
            Decimal(item.qty)
            * Decimal(item.unit_price)
        )

        total_amount += subtotal

        new_items.append(
            TransactionItem(
                transaction_id=transaction.id,
                item_name=item.item_name,
                qty=item.qty,
                unit_price=item.unit_price,
                subtotal=subtotal,
            )
        )

    # 修改備註
    transaction.note = payload.note

    # 有傳消費日期才修改
    if payload.record_date is not None:
        record_date = payload.record_date

        # 如果前端傳來的日期沒有時區，
        # 暫時視為 UTC，避免資料庫日期格式不一致
        if record_date.tzinfo is None:
            record_date = record_date.replace(
                tzinfo=timezone.utc,
            )

        transaction.record_date = record_date

    # 更新總金額
    transaction.total_amount = total_amount

    # 刪除原本的消費項目
    for old_item in list(transaction.items):
        db.delete(old_item)

    # 先執行刪除，避免新舊項目混在一起
    db.flush()

    # 加入新的消費項目
    for new_item in new_items:
        db.add(new_item)

    # 寫入操作紀錄
    db.add(
        AuditLog(
            user_id=current_user.id,
            action="update_transaction",
            target_type="transaction",
            target_id=transaction.id,
            detail={
                "customer_id":
                    transaction.customer_id,

                "total_amount":
                    str(total_amount),
            },
        )
    )

    db.commit()

    # 重新查詢，確保回傳最新的 items
    updated_stmt = (
        select(Transaction)
        .options(
            selectinload(Transaction.items)
        )
        .where(
            Transaction.id == transaction.id
        )
    )

    updated_transaction = (
        db.execute(updated_stmt)
        .scalar_one()
    )

    return updated_transaction