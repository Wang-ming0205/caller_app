from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    Query,
    UploadFile,
    File,
    )
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

#新增匯出csv
import csv
from io import StringIO 
from fastapi.responses import StreamingResponse

from app.api.deps import get_current_user, require_roles, require_customer_access
from app.core.database import get_db
from app.models.customer import Customer
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


@router.get(
    "/search/list",
    response_model=list[CustomerOut],
)
def search_customers(
    q: str = Query(
        ...,
        min_length=1,
        max_length=100,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return customer_service.search_customers(
        db=db,
        keyword=q,
        limit=20
    )

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

@router.post("/import/excel")
def import_customers_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "manager", "staff")
    ),
):
    try:
        filename = file.filename or ""

        if not filename.lower().endswith((".xlsx",".csv")):
            raise HTTPException(
                status_code=400,
                detail="請上傳 .xlsx 檔案 或 .csv檔案",
            )

        max_size = 5 * 1024 * 1024
        content = file.file.read(max_size + 1)

        if not content:
            raise HTTPException(
                status_code=400,
                detail="檔案不可為空",
            )

        if len(content) > max_size:
            raise HTTPException(
                status_code=413,
                detail="檔案不可超過 5 MB",
            )

        try:
            result = customer_service.import_customers(
                db=db,
                file_content=content,
                owner_user_id=current_user.id,
                filename = filename,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=str(exc),
            ) from exc

        write_audit_log(
            db=db,
            action="IMPORT_CUSTOMERS",
            target_type="customer",
            user_id=current_user.id,
            target_id=None,
            detail={
                "created": result["created"],
                "skipped": result["skipped"],
                "failed": result["failed"],
            },
        )

        return result

    finally:
        file.file.close()

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
    # customer = db.get(Customer, customer_id)
    # customer = require_customer_access(customer, current_user)
    customer = customer_service.get_customer_by_id(
        db=db,
        customer_id=customer_id,
    )
    
    # last_tx = db.execute(
    #     select(Transaction)
    #     .where(Transaction.customer_id == customer_id)
    #     .order_by(Transaction.record_date.desc(), Transaction.id.desc())
    #     .limit(1)
    # ).scalar_one_or_none()
    customer = require_customer_access(
        customer,
        current_user,
    )
    return customer_service.get_customer_summary(
        db=db,
        customer=customer,
        limit=5,
    )