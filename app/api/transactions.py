# # from decimal import Decimal
# # from fastapi import APIRouter, Depends, HTTPException
# # from sqlalchemy import select
# # from sqlalchemy.orm import Session, selectinload
# # from datetime import datetime, timezone

# # from app.api.deps import get_current_user, require_roles, require_customer_access
# # from app.core.database import get_db
# # from app.models.customer import Customer
# # from app.models.transaction import Transaction, TransactionItem
# # from app.models.user import User
# # from app.models.audit_log import AuditLog
# # from app.schemas.transaction import TransactionCreate, TransactionOut

# # router = APIRouter(prefix="/transactions", tags=["transactions"])


# # @router.post("", response_model=TransactionOut)
# # def create_transaction(
# #     payload: TransactionCreate,
# #     db: Session = Depends(get_db),
# #     current_user: User = Depends(require_roles("admin", "manager", "staff")),
# # ):
# #     customer = db.get(Customer, payload.customer_id)
# #     customer = require_customer_access(customer, current_user)

# #     if not payload.items:
# #         raise HTTPException(status_code=400, detail="Transaction items required")

# #     total_amount = Decimal("0")
# #     tx_items = []
# #     for item in payload.items:
# #         subtotal = Decimal(item.qty) * Decimal(item.unit_price)
# #         total_amount += subtotal
# #         tx_items.append(
# #             TransactionItem(
# #                 item_name=item.item_name,
# #                 qty=item.qty,
# #                 unit_price=item.unit_price,
# #                 subtotal=subtotal,
# #             )
# #         )

# #     tx = Transaction(
# #         customer_id=payload.customer_id,
# #         stylist_user_id=payload.stylist_user_id or current_user.id,
# #         total_amount=total_amount,
# #         note=payload.note,
# #         record_date=payload.record_date or datetime.now(timezone.utc),
# #         items=tx_items,
# #     )
# #     db.add(tx)
# #     db.flush()

# #     db.add(
# #         AuditLog(
# #             user_id=current_user.id,
# #             action="create_transaction",
# #             target_type="transaction",
# #             target_id=tx.id,
# #             detail={
# #                 "customer_id": payload.customer_id,
# #                 "total_amount": str(total_amount),
# #             },
# #         )
# #     )

# #     db.commit()

# #     stmt = (
# #         select(Transaction)
# #         .options(selectinload(Transaction.items))
# #         .where(Transaction.id == tx.id)
# #     )
# #     created_tx = db.execute(stmt).scalar_one()
# #     return created_tx


# # @router.get("/customer/{customer_id}", response_model=list[TransactionOut])
# # def list_transactions_by_customer(
# #     customer_id: int,
# #     db: Session = Depends(get_db),
# #     current_user: User = Depends(get_current_user),
# # ):
# #     customer = db.get(Customer, customer_id)
# #     require_customer_access(customer, current_user)

# #     stmt = (
# #         select(Transaction)
# #         .options(selectinload(Transaction.items))
# #         .where(Transaction.customer_id == customer_id)
# #         .order_by(Transaction.record_date.desc(), Transaction.id.desc())
# #     )
# #     return list(db.execute(stmt).scalars().unique().all())


# #=======================
# from datetime import datetime, timezone
# from decimal import Decimal

# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy import select
# from sqlalchemy.orm import Session, selectinload

# from app.api.deps import get_current_user, require_customer_access, require_roles
# from app.core.database import get_db
# from app.models.audit_log import AuditLog
# from app.models.customer import Customer
# from app.models.transaction import Transaction, TransactionItem
# from app.models.user import User
# from app.schemas.transaction import TransactionCreate, TransactionOut

# router = APIRouter(prefix="/transactions", tags=["transactions"])


# @router.post("", response_model=TransactionOut)
# def create_transaction(
#     payload: TransactionCreate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(
#         require_roles("admin", "manager", "staff")
#     ),
# ):
#     # 有指定客戶時才檢查客戶是否存在，以及目前使用者是否有權限。
#     # customer_id=None 代表散客消費。
#     if payload.customer_id is not None:
#         customer = db.get(Customer, payload.customer_id)
#         require_customer_access(customer, current_user)

#     if not payload.items:
#         raise HTTPException(
#             status_code=400,
#             detail="Transaction items required",
#         )

#     total_amount = Decimal("0")
#     tx_items = []

#     for item in payload.items:
#         subtotal = Decimal(item.qty) * Decimal(item.unit_price)
#         total_amount += subtotal
#         tx_items.append(
#             TransactionItem(
#                 item_name=item.item_name,
#                 qty=item.qty,
#                 unit_price=item.unit_price,
#                 subtotal=subtotal,
#             )
#         )

#     tx = Transaction(
#         customer_id=payload.customer_id,
#         stylist_user_id=payload.stylist_user_id or current_user.id,
#         total_amount=total_amount,
#         note=payload.note,
#         record_date=payload.record_date or datetime.now(timezone.utc),
#         items=tx_items,
#     )
#     db.add(tx)
#     db.flush()

#     db.add(
#         AuditLog(
#             user_id=current_user.id,
#             action="create_transaction",
#             target_type="transaction",
#             target_id=tx.id,
#             detail={
#                 "customer_id": payload.customer_id,
#                 "total_amount": str(total_amount),
#             },
#         )
#     )

#     db.commit()

#     stmt = (
#         select(Transaction)
#         .options(selectinload(Transaction.items))
#         .where(Transaction.id == tx.id)
#     )
#     created_tx = db.execute(stmt).scalar_one()
#     return created_tx


# @router.get(
#     "/customer/{customer_id}",
#     response_model=list[TransactionOut],
# )
# def list_transactions_by_customer(
#     customer_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     customer = db.get(Customer, customer_id)
#     require_customer_access(customer, current_user)

#     stmt = (
#         select(Transaction)
#         .options(selectinload(Transaction.items))
#         .where(Transaction.customer_id == customer_id)
#         .order_by(Transaction.record_date.desc(), Transaction.id.desc())
#     )
#     return list(db.execute(stmt).scalars().unique().all())


#==================
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
from app.schemas.transaction import TransactionCreate, TransactionOut

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionOut)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "staff")),
):
    if payload.customer_id is not None:
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
    