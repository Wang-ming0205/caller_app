from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


def get_latest_customers(db: Session, limit: int = 5):
    return (
        db.query(Customer)
        .order_by(Customer.id.desc())
        .limit(limit)
        .all()
    )


def search_customers(db: Session, keyword: str):
    return (
        db.query(Customer)
        .filter(
            (Customer.name.contains(keyword)) |
            (Customer.phone_number.contains(keyword))
        )
        .all()
    )


def get_customer_by_id(db: Session, customer_id: int):
    return (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
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