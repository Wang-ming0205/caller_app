from decimal import Decimal

from sqlalchemy import or_, select , func
from sqlalchemy.orm import Session ,selectinload
from app.models.customer import Customer
from app.models.transaction import Transaction
from app.schemas.customer import CustomerCreate, CustomerUpdate , CustomerSummaryOut


def get_latest_customers(db: Session, limit: int = 5):
    stmt = (
        select(Customer)
        .order_by(Customer.id.desc())
        .limit(limit)
    )

    return list(
        db.execute(stmt)
        .scalars()
        .all()
    )


def search_customers(db: Session, keyword: str,limit: int = 20,):
    keyword = keyword.strip()

    if not keyword:
        return []

    conditions = []

    if keyword.isdigit():
        # 數字永遠先比對唯一的客戶 ID
        conditions.append(
            Customer.id == int(keyword)
        )

        # 至少三碼，才搜尋手機尾碼
        if len(keyword) >= 3:
            conditions.append(
                Customer.phone_number.endswith(keyword)
            )
    else:
        # 姓名可輸入一個字或部分姓名
        conditions.append(
            Customer.name.icontains(
                keyword,
                autoescape=True,
            )
        )

    stmt = (
        select(Customer)
        .where(or_(*conditions))
        .order_by(Customer.id.desc())
        .limit(limit)
    )

    return list(
        db.execute(stmt)
        .scalars()
        .all()
    )



def get_customer_by_id(db: Session, customer_id: int):
    stmt = select(Customer).where(
        Customer.id == customer_id
    )

    return (
        db.execute(stmt)
        .scalar_one_or_none()
    )


def create_customer(db: Session, data: CustomerCreate, owner_user_id: int):
    customer = Customer(
        name=data.name,
        phone_number=data.phone_number,
        owner_user_id=owner_user_id,
        gender=data.gender,
        birthday=data.birthday,
        note=data.note,
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


def update_customer(db: Session, customer_id: int, data: CustomerUpdate):
    customer = get_customer_by_id(db, customer_id)

    if customer is None:
        return None

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(customer, key, value)

    db.commit()
    db.refresh(customer)

    return customer


def delete_customer(db: Session, customer_id: int):
    customer = get_customer_by_id(db, customer_id)

    if customer is None:
        return None

    db.delete(customer)
    db.commit()

    return customer

def get_customer_summary(
    db: Session,
    customer: Customer,
    limit: int = 5,
) -> CustomerSummaryOut:
    transaction_count, total_amount = db.execute(
        select(
            func.count(Transaction.id),
            func.coalesce(
                func.sum(Transaction.total_amount),
                0,
            ),
        ).where(
            Transaction.customer_id == customer.id
        )
    ).one()

    transaction_count = int(
        transaction_count or 0
    )

    transactions = list(
        db.execute(
            select(Transaction)
            .options(
                selectinload(Transaction.items)
            )
            .where(
                Transaction.customer_id == customer.id
            )
            .order_by(
                Transaction.record_date.desc(),
                Transaction.id.desc(),
            )
            .limit(limit)
        )
        .scalars()
        .all()
    )

    recent_transactions = []

    for index, transaction in enumerate(
        transactions
    ):
        visit_number = transaction_count - index

        items = []

        for item in transaction.items:
            qty = int(item.qty or 0)
            unit_price = Decimal(
                item.unit_price or 0
            )

            subtotal = Decimal(
                item.subtotal
                if item.subtotal is not None
                else qty * unit_price
            )

            items.append({
                "id": item.id,
                "item_name": item.item_name,
                "qty": qty,
                "unit_price": unit_price,
                "subtotal": subtotal,
            })

        recent_transactions.append({
            "id": transaction.id,
            "visit_number": visit_number,
            "total_amount": Decimal(
                transaction.total_amount or 0
            ),
            "note": transaction.note,
            "record_date": transaction.record_date,
            "items": items,
        })

    last_transaction = (
        transactions[0]
        if transactions
        else None
    )

    last_items = None

    if last_transaction:
        item_names = [
            item.item_name
            for item in last_transaction.items
        ]

        if item_names:
            last_items = ", ".join(item_names)

    return CustomerSummaryOut(
        customer_id=customer.id,
        name=customer.name,
        phone_number=customer.phone_number,
        transaction_count=transaction_count,
        total_amount=Decimal(total_amount or 0),
        last_record=(
            last_transaction.note
            if last_transaction
            else None
        ),
        last_items=last_items,
        last_day=(
            last_transaction.record_date
            if last_transaction
            else None
        ),
        recent_transactions=recent_transactions,
    )