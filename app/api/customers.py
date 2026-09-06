from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

#新增匯出csv
import csv
from io import StringIO
from fastapi.responses import StreamingResponse

from app.api.deps import get_current_user, require_roles, require_customer_access
from app.core.database import get_db
from app.models.customer import Customer
from app.models.transaction import Transaction, TransactionItem
from app.models.user import User
from app.schemas.customer import CustomerCreate, CustomerOut, CustomerSummaryOut, CustomerUpdate
from app.services import customer_service
from app.api.audit import write_audit_log

router = APIRouter(prefix="/customers", tags=["customers"])


PHONE_ALREADY_EXISTS = "Phone number already exists"


@router.post("", response_model=CustomerOut)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "staff")),
):
    owner_user_id = current_user.id
    exists = db.execute(
        select(Customer).where(
            Customer.phone_number == payload.phone_number,
        )
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=400, detail=PHONE_ALREADY_EXISTS)

    customer = Customer(**payload.model_dump(), owner_user_id=owner_user_id)
    db.add(customer)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail=PHONE_ALREADY_EXISTS
    )
    db.refresh(customer)

    write_audit_log(
        db=db,
        action="CREATE_CUSTOMER",
        target_type="customer",
        user_id=current_user.id,
        target_id=customer.id,
        detail={
            "name": customer.name,
            "phone_number": customer.phone_number,
        },
    )
    return customer


@router.get("/search/list", response_model=list[CustomerOut])
def search_customers(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Customer).where(
        (Customer.name.ilike(f"%{q}%")) |
        (Customer.phone_number.ilike(f"%{q}%"))
    )
    stmt = stmt.order_by(Customer.id.desc()).limit(20)
    return list(db.execute(stmt).scalars().all())


#新增curd.py
@router.get("/debug/test")
def test():
    return {"message":"curd loaded"}

@router.get("/", response_model=list[CustomerOut])
def list_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Customer)
    stmt = stmt.order_by(Customer.id.desc()).limit(5)
    return list(db.execute(stmt).scalars().all())



@router.get("/by-phone/{phone_number}", response_model=CustomerOut)
def get_customer_by_phone(
    phone_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Customer).where(Customer.phone_number == phone_number)
    customer = db.execute(stmt).scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

#這個是?新增的匯出csv#
@router.get("/export/csv")
def export_customers_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "staff")),
):
    stmt = select(Customer)
    customers = db.execute(stmt).scalars().all()

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "id",
        "name",
        "phone",
        "note",
        "owner_user_id",
    ])

    for c in customers:
        writer.writerow([
            c.id,
            c.name,
            c.phone_number,
            c.note or "",
            c.owner_user_id,
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=customers.csv"
        },
    )

@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "staff")),
):
    customer = db.get(Customer, customer_id)
    customer = require_customer_access(customer, current_user)

    detail = {
        "name":customer.name,
        "phone_number":customer.phone_number,
    }

    db.delete(customer)
    db.commit()

    write_audit_log(
        db=db,
        action="DELETE_CUSTOMER",
        target_type="customer",
        user_id=current_user.id,
        target_id=customer_id,
        detail=detail,
)
    
    return {"message": "Customer deleted", "id": customer_id}

@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.get(Customer, customer_id)
    return require_customer_access(customer, current_user)


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "staff")),
):
    customer = db.get(Customer, customer_id)
    customer = require_customer_access(customer, current_user)

    data = payload.model_dump(exclude_unset=True)

    new_phone_number = data.get("phone_number")
    if new_phone_number is not None:
        exists = db.execute(
            select(Customer).where(
                Customer.phone_number == new_phone_number,
                Customer.id != customer_id,
            )
        ).scalar_one_or_none()
        if exists:
            raise HTTPException(status_code=400, detail=PHONE_ALREADY_EXISTS)

    for key, value in data.items():
        setattr(customer, key, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail=PHONE_ALREADY_EXISTS
    )
    db.refresh(customer)

    write_audit_log(
        db=db,
        action="UPDATE_CUSTOMER",
        target_type="customer",
        user_id=current_user.id,
        target_id=customer.id,
        detail={
            "name": customer.name,
            "phone_number": customer.phone_number,
        },
    )
    return customer


@router.get("/{customer_id}/summary", response_model=CustomerSummaryOut)
def get_customer_summary(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = db.get(Customer, customer_id)
    customer = require_customer_access(customer, current_user)

    last_tx = db.execute(
        select(Transaction)
        .where(Transaction.customer_id == customer_id)
        .order_by(Transaction.record_date.desc(), Transaction.id.desc())
        .limit(1)
    ).scalar_one_or_none()

    total_amount = db.execute(
        select(func.coalesce(func.sum(Transaction.total_amount), 0))
        .where(Transaction.customer_id == customer_id)
    ).scalar_one()

    last_items = None
    last_record = None
    last_day = None

    if last_tx:
        items = db.execute(
            select(TransactionItem.item_name)
            .where(TransactionItem.transaction_id == last_tx.id)
        ).scalars().all()
        last_items = ", ".join(items) if items else None
        last_record = last_tx.note
        last_day = last_tx.record_date

    return CustomerSummaryOut(
        customer_id=customer.id,
        name=customer.name,
        phone_number=customer.phone_number,
        last_record=last_record,
        last_items=last_items,
        total_amount=Decimal(total_amount),
        last_day=last_day,
    )
