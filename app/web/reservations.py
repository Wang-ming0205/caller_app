# from datetime import datetime, timezone

# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy import func, select ,update
# from sqlalchemy.orm import Session

# from app.core.database import get_db
# from app.models.appointment import Appointment
# from app.models.customer import Customer
# from app.models.user import User
# from app.schemas.appointment import (
#     GuestAppointmentCandidateOut,
#     GuestAppointmentCreate,
#     GuestAppointmentLast3Lookup,
#     GuestAppointmentLookup,
#     GuestAppointmentOut,
#     GuestAppointmentCancel,
#     GuestAppointmentCandidateSearch,
#     GuestAppointmentLast3Create,
# )
# from app.services.customer_service import lock_household_phone


# router = APIRouter(prefix="/reservation", tags=["customer reservations"])


# def validate_reservation_time(starts_at: datetime) -> None:
#     if starts_at.tzinfo is None:
#         raise HTTPException(
#             status_code=400,
#             detail="Appointment time must include a timezone",
#         )
#     if starts_at <= datetime.now(timezone.utc):
#         raise HTTPException(
#             status_code=400,
#             detail="Appointment time must be in the future",
#         )



# @router.post("/book", response_model=GuestAppointmentOut)
# def create_customer_reservation(
#     payload: GuestAppointmentCreate,
#     db: Session = Depends(get_db),
# ):
#     validate_reservation_time(payload.starts_at)

#     lock_household_phone(db, payload.phone_number)
#     # customer = db.execute(
#     #     select(Customer).where(
#     #         Customer.phone_number == payload.phone_number,
#     #         Customer.birthday == payload.birthday,
#     #     )
#     # ).scalar_one_or_none()
#     #############################以下新增的
#     # customer = None

#     # if payload.birthday is not None:
#     #     customer = db.execute(
#     #         select(Customer).where(
#     #             Customer.phone_number == payload.phone_number,
#     #             Customer.birthday == payload.birthday,
#     #         )
#     #     ).scalar_one_or_none()

#     #     if customer is None:
#     #         undated_matches = db.scalars(
#     #             select(Customer).where(
#     #                 Customer.phone_number == payload.phone_number,
#     #                 Customer.name == payload.name,
#     #                 Customer.birthday.is_(None),
#     #             )
#     #         ).all()

#     #         if len(undated_matches) > 1:
#     #             raise HTTPException(
#     #                 status_code=409,
#     #                 detail="同一手機有多位相同姓名且未登記生日的會員，請洽店家確認。",
#     #             )

#     #         if undated_matches:
#     #             customer = undated_matches[0]
#     #             customer.birthday = payload.birthday
#     # else:
#     #     name_matches = db.scalars(
#     #         select(Customer).where(
#     #             Customer.phone_number == payload.phone_number,
#     #             Customer.name == payload.name,
#     #         )
# #     #     ).all()
# #     customer = None

# #     if payload.birthday is not None:
# #         customer = db.execute(
# #             select(Customer).where(
# #                 Customer.phone_number == payload.phone_number,
# #                 Customer.birthday == payload.birthday,
# #             )
# #         ).scalar_one_or_none()

# #         if customer is None:
# #             undated_matches = db.scalars(
# #                 select(Customer).where(
# #                     Customer.phone_number == payload.phone_number,
# #                     Customer.name == payload.name,
# #                     Customer.birthday.is_(None),
# #                 )
# #             ).all()

# #             if len(undated_matches) > 1:
# #                 raise HTTPException(
# #                     status_code=409,
# #                     detail="同一手機有多位相同姓名且未登記生日的會員，請洽店家確認。",
# #                 )

# #             if undated_matches:
# #                 customer = undated_matches[0]
# #                 customer.birthday = payload.birthday

# #             else:
# #                 name_matches = db.scalars(
# #                     select(Customer).where(
# #                         Customer.phone_number == payload.phone_number,
# #                         Customer.name == payload.name,
# #                     )
# #                 ).all()

# #         if len(name_matches) > 1:
# #             raise HTTPException(
# #                 status_code=409,
# #                 detail="同一手機有多位相同姓名的會員，請洽店家補登生日。",
# #             )

# #         if name_matches:
# #             customer = name_matches[0]
# # #############################以上新增的
# #     if len(name_matches) > 1:
# #         raise HTTPException(
# #             status_code=409,
# #             detail="同一手機有多位相同姓名的會員，請洽店家補登生日。",
# #         )

# #     if name_matches:
# #         customer = name_matches[0]

# #     if customer is None:
# #         household_size = db.scalar(
# #             select(func.count(Customer.id)).where(
# #                 Customer.phone_number == payload.phone_number
# #             )
# #         ) or 0
# #         if household_size >= 6:
# #             raise HTTPException(
# #                 status_code=400,
# #                 detail="This phone number already has 6 family members",
# #             )

# #         owner_user_id = db.scalar(
# #             select(User.id)
# #             .where(User.role == "admin", User.is_active.is_(True))
# #             .order_by(User.id)
# #             .limit(1)
# #         )
# #         if owner_user_id is None:
# #             raise HTTPException(
# #                 status_code=503,
# #                 detail="The shop is not ready to accept reservations",
# #             )

# #         customer = Customer(
# #             name=payload.name,
# #             phone_number=payload.phone_number,
# #             birthday=payload.birthday,
# #             owner_user_id=owner_user_id,
# #         )
# #         db.add(customer)
# #         db.flush()

# #     return save_reservation(
# #         db, customer.id, payload.starts_at, payload.service_name
# #     )
#     customer = None

#     if payload.birthday is not None:
#         customer = db.execute(
#             select(Customer).where(
#                 Customer.phone_number == payload.phone_number,
#                 Customer.birthday == payload.birthday,
#             )
#         ).scalar_one_or_none()

#     #     if customer is None:
#     #         undated_matches = db.scalars(
#     #             select(Customer).where(
#     #                 Customer.phone_number == payload.phone_number,
#     #                 Customer.name == payload.name,
#     #                 Customer.birthday.is_(None),
#     #             )
#     #         ).all()

#     #         if len(undated_matches) > 1:
#     #             raise HTTPException(
#     #                 status_code=409,
#     #                 detail="同一手機有多位相同姓名且未登記生日的會員，請洽店家確認。",
#     #             )

#     #         if undated_matches:
#     #             customer = undated_matches[0]
#     #             customer.birthday = payload.birthday

#     # else:
#     #     name_matches = db.scalars(
#     #         select(Customer).where(
#     #             Customer.phone_number == payload.phone_number,
#     #             Customer.name == payload.name,
#     #         )
#     #     ).all()

#     #     if len(name_matches) > 1:
#     #         raise HTTPException(
#     #             status_code=409,
#     #             detail="同一手機有多位相同姓名的會員，請洽店家補登生日。",
#     #         )

#     #     if name_matches:
#     #         customer = name_matches[0]
#             if customer is None:
#         household_size = db.scalar(
#             select(func.count(Customer.id)).where(
#                 Customer.phone_number == payload.phone_number
#             )
#         ) or 0

#         if household_size >= 6:
#             raise HTTPException(
#                 status_code=400,
#                 detail="This phone number already has 6 family members",
#             )

#         if household_size > 0:
#             raise HTTPException(
#                 status_code=409,
#                 detail="這支手機已有會員資料，但姓名或生日未符合，請洽店家確認。",
#             )

#         owner_user_id = db.scalar(
#             select(User.id)
#             .where(User.role == "admin", User.is_active.is_(True))
#             .order_by(User.id)
#             .limit(1)
#         )
#         if owner_user_id is None:
#             raise HTTPException(
#                 status_code=503,
#                 detail="The shop is not ready to accept reservations",
#             )

#         customer = Customer(
#             name=payload.name,
#             phone_number=payload.phone_number,
#             birthday=payload.birthday,
#             owner_user_id=owner_user_id,
#         )
#         db.add(customer)
#         db.flush()

#     return save_reservation(
#         db, customer.id, payload.starts_at, payload.service_name
#     )


# @router.post("/book-by-last3", response_model=GuestAppointmentOut)
# def create_customer_reservation_by_last3(
#     payload: GuestAppointmentLast3Create,
#     db: Session = Depends(get_db),
# ):
#     validate_reservation_time(payload.starts_at)

#     customer_id = db.scalar(
#         select(Customer.id).where(
#             Customer.id == payload.customer_id,
#             Customer.phone_number.endswith(payload.phone_last3),
#             Customer.birthday == payload.birthday,
#         )
#     )
#     if customer_id is None:
#         raise HTTPException(
#             status_code=404,
#             detail="找不到符合資料的會員，請確認手機末三碼和生日。",
#         )

#     return save_reservation(
#         db, customer_id, payload.starts_at, payload.service_name
#     )


# def save_reservation(
#     db: Session,
#     customer_id: int,
#     starts_at: datetime,
#     service_name: str,
# ) -> Appointment:
#     appointment = Appointment(
#         customer_id=customer_id,
#         starts_at=starts_at,
#         service_name=service_name,
#     )
#     db.add(appointment)
#     db.commit()
#     db.refresh(appointment)
#     return appointment


# @router.post("/lookup", response_model=list[GuestAppointmentOut])
# def lookup_customer_reservations(
#     payload: GuestAppointmentLookup,
#     db: Session = Depends(get_db),
# ):
#     customer = db.execute(
#         select(Customer).where(
#             Customer.phone_number == payload.phone_number,
#             Customer.birthday == payload.birthday,
#         )
#     ).scalar_one_or_none()
#     if customer is None:
#         return []

#     return list(
#         db.execute(
#             select(Appointment)
#             .where(
#                 Appointment.customer_id == customer.id,
#                 Appointment.starts_at >= datetime.now(timezone.utc),
#             )
#             .order_by(Appointment.starts_at, Appointment.id)
#         ).scalars().all()
#     )

# @router.post("/lookup-candidates", response_model=list[GuestAppointmentCandidateOut])
# def lookup_reservation_candidates(
#     payload: GuestAppointmentCandidateSearch,
#     db: Session = Depends(get_db),
# ):
#     customers = db.execute(
#         select(Customer.id, Customer.name)
#         .where(
#             Customer.phone_number.endswith(payload.phone_last3),
#             Customer.birthday == payload.birthday,
#         )
#         .order_by(Customer.name, Customer.id)
#     ).all()

#     candidates = []
#     for customer_id, name in customers:
#         if len(name) <= 1:
#             masked_name = "○"
#         elif len(name) == 2:
#             masked_name = f"{name[0]}○"
#         else:
#             masked_name = name[0] + "○" * (len(name) - 2) + name[-1]

#         candidates.append(
#             GuestAppointmentCandidateOut(
#                 customer_id=customer_id,
#                 masked_name=masked_name,
#             )
#         )

#     return candidates

# @router.post("/lookup-by-last3", response_model=list[GuestAppointmentOut])
# def lookup_customer_reservations_by_last3(
#     payload: GuestAppointmentLast3Lookup,
#     db: Session = Depends(get_db),
# ):
#     return db.scalars(
#         select(Appointment)
#         .join(Customer, Customer.id == Appointment.customer_id)
#         .where(
#             Customer.id == payload.customer_id,
#             Customer.phone_number.endswith(payload.phone_last3),
#             Customer.birthday == payload.birthday,
#             Appointment.starts_at >= datetime.now(timezone.utc),
#         )
#         .order_by(Appointment.starts_at, Appointment.id)
#     ).all()


# @router.post("/cancel")
# def cancel_customer_reservation(
#     payload: GuestAppointmentCancel,
#     db: Session = Depends(get_db),
# ):
#     customer_ids = select(Customer.id).where(
#         Customer.phone_number == payload.phone_number,
#         Customer.birthday == payload.birthday,
#     )

#     result = db.execute(
#         update(Appointment)
#         .where(
#             Appointment.id == payload.appointment_id,
#             Appointment.customer_id.in_(customer_ids),
#             Appointment.starts_at > datetime.now(timezone.utc),
#             Appointment.status == "booked",
#         )
#         .values(status="cancelled")
#         .execution_options(synchronize_session=False)
#     )

#     if result.rowcount != 1:
#         db.rollback()
#         raise HTTPException(status_code=404, detail="Cancellable appointment not found")

#     db.commit()
#     return {"status": "cancelled"}


from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.appointment import Appointment
from app.models.customer import Customer
from app.models.user import User
from app.schemas.appointment import (
    GuestAppointmentCandidateOut,
    GuestAppointmentCandidateSearch,
    GuestAppointmentCancel,
    GuestAppointmentCreate,
    GuestAppointmentLast3Create,
    GuestAppointmentLast3Lookup,
    GuestAppointmentLookup,
    GuestAppointmentOut,
)
from app.services.customer_service import lock_household_phone


router = APIRouter(prefix="/reservation", tags=["customer reservations"])


def validate_reservation_time(starts_at: datetime) -> None:
    if starts_at.tzinfo is None:
        raise HTTPException(
            status_code=400,
            detail="Appointment time must include a timezone",
        )
    if starts_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=400,
            detail="Appointment time must be in the future",
        )


@router.post("/book", response_model=GuestAppointmentOut)
def create_customer_reservation(
    payload: GuestAppointmentCreate,
    db: Session = Depends(get_db),
):
    validate_reservation_time(payload.starts_at)
    lock_household_phone(db, payload.phone_number)

    customer = None

    if payload.birthday is not None:
        customer = db.execute(
            select(Customer).where(
                Customer.phone_number == payload.phone_number,
                Customer.birthday == payload.birthday,
            )
        ).scalar_one_or_none()

        if customer is None:
            undated_matches = db.scalars(
                select(Customer).where(
                    Customer.phone_number == payload.phone_number,
                    Customer.name == payload.name,
                    Customer.birthday.is_(None),
                )
            ).all()

            if len(undated_matches) > 1:
                raise HTTPException(
                    status_code=409,
                    detail="同一手機有多位相同姓名且未登記生日的會員，請洽店家確認。",
                )

            if undated_matches:
                customer = undated_matches[0]
                customer.birthday = payload.birthday

    else:
        name_matches = db.scalars(
            select(Customer).where(
                Customer.phone_number == payload.phone_number,
                Customer.name == payload.name,
            )
        ).all()

        if len(name_matches) > 1:
            raise HTTPException(
                status_code=409,
                detail="同一手機有多位相同姓名的會員，請洽店家補登生日。",
            )

        if name_matches:
            customer = name_matches[0]

    if customer is None:
        household_size = db.scalar(
            select(func.count(Customer.id)).where(
                Customer.phone_number == payload.phone_number
            )
        ) or 0

        if household_size >= 6:
            raise HTTPException(
                status_code=400,
                detail="This phone number already has 6 family members",
            )

        if household_size > 0:
            raise HTTPException(
                status_code=409,
                detail="這支手機已有會員資料，但姓名或生日未符合，請洽店家確認。",
            )

        owner_user_id = db.scalar(
            select(User.id)
            .where(User.role == "admin", User.is_active.is_(True))
            .order_by(User.id)
            .limit(1)
        )
        if owner_user_id is None:
            raise HTTPException(
                status_code=503,
                detail="The shop is not ready to accept reservations",
            )

        customer = Customer(
            name=payload.name,
            phone_number=payload.phone_number,
            birthday=payload.birthday,
            owner_user_id=owner_user_id,
        )
        db.add(customer)
        db.flush()

    return save_reservation(
        db,
        customer.id,
        payload.starts_at,
        payload.service_name,
    )


@router.post("/book-by-last3", response_model=GuestAppointmentOut)
def create_customer_reservation_by_last3(
    payload: GuestAppointmentLast3Create,
    db: Session = Depends(get_db),
):
    validate_reservation_time(payload.starts_at)

    customer_id = db.scalar(
        select(Customer.id).where(
            Customer.id == payload.customer_id,
            Customer.phone_number.endswith(payload.phone_last3),
            Customer.birthday == payload.birthday,
        )
    )
    if customer_id is None:
        raise HTTPException(
            status_code=404,
            detail="找不到符合資料的會員，請確認手機末三碼和生日。",
        )

    return save_reservation(
        db,
        customer_id,
        payload.starts_at,
        payload.service_name,
    )


def save_reservation(
    db: Session,
    customer_id: int,
    starts_at: datetime,
    service_name: str,
) -> Appointment:
    appointment = Appointment(
        customer_id=customer_id,
        starts_at=starts_at.astimezone(timezone.utc),
        service_name=service_name,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.post("/lookup", response_model=list[GuestAppointmentOut])
def lookup_customer_reservations(
    payload: GuestAppointmentLookup,
    db: Session = Depends(get_db),
):
    identity_query = select(Customer).where(
        Customer.phone_number == payload.phone_number
    )

    if payload.birthday is not None:
        identity_query = identity_query.where(
            Customer.birthday == payload.birthday
        )
    else:
        identity_query = identity_query.where(
            Customer.name == payload.name
        )

    customers = db.scalars(identity_query).all()

    if not customers:
        return []

    if len(customers) > 1:
        raise HTTPException(
            status_code=409,
            detail="找到多位符合資料的會員，請使用生日查詢或洽店家協助。",
        )

    customer = customers[0]

    return list(
        db.scalars(
            select(Appointment)
            .where(
                Appointment.customer_id == customer.id,
                Appointment.starts_at >= datetime.now(timezone.utc),
            )
            .order_by(Appointment.starts_at, Appointment.id)
        ).all()
    )


@router.post(
    "/lookup-candidates",
    response_model=list[GuestAppointmentCandidateOut],
)
def lookup_reservation_candidates(
    payload: GuestAppointmentCandidateSearch,
    db: Session = Depends(get_db),
):
    customers = db.execute(
        select(Customer.id, Customer.name)
        .where(
            Customer.phone_number.endswith(payload.phone_last3),
            Customer.birthday == payload.birthday,
        )
        .order_by(Customer.name, Customer.id)
    ).all()

    candidates = []

    for customer_id, name in customers:
        if len(name) <= 1:
            masked_name = "○"
        elif len(name) == 2:
            masked_name = f"{name[0]}○"
        else:
            masked_name = name[0] + "○" * (len(name) - 2) + name[-1]

        candidates.append(
            GuestAppointmentCandidateOut(
                customer_id=customer_id,
                masked_name=masked_name,
            )
        )

    return candidates


@router.post(
    "/lookup-by-last3",
    response_model=list[GuestAppointmentOut],
)
def lookup_customer_reservations_by_last3(
    payload: GuestAppointmentLast3Lookup,
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(Appointment)
        .join(Customer, Customer.id == Appointment.customer_id)
        .where(
            Customer.id == payload.customer_id,
            Customer.phone_number.endswith(payload.phone_last3),
            Customer.birthday == payload.birthday,
            Appointment.starts_at >= datetime.now(timezone.utc),
        )
        .order_by(Appointment.starts_at, Appointment.id)
    ).all()


@router.post("/cancel")
def cancel_customer_reservation(
    payload: GuestAppointmentCancel,
    db: Session = Depends(get_db),
):
    identity_query = select(Customer.id).where(
        Customer.phone_number == payload.phone_number
    )

    if payload.birthday is not None:
        identity_query = identity_query.where(
            Customer.birthday == payload.birthday
        )
    else:
        identity_query = identity_query.where(
            Customer.name == payload.name
        )

    customer_ids = db.scalars(identity_query).all()

    if len(customer_ids) > 1:
        raise HTTPException(
            status_code=409,
            detail="找到多位符合資料的會員，請洽店家協助取消。",
        )

    if not customer_ids:
        raise HTTPException(
            status_code=404,
            detail="Cancellable appointment not found",
        )

    result = db.execute(
        update(Appointment)
        .where(
            Appointment.id == payload.appointment_id,
            Appointment.customer_id == customer_ids[0],
            Appointment.starts_at > datetime.now(timezone.utc),
            Appointment.status == "booked",
        )
        .values(status="cancelled")
        .execution_options(synchronize_session=False)
    )

    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(
            status_code=404,
            detail="Cancellable appointment not found",
        )

    db.commit()
    return {"status": "cancelled"}