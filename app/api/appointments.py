from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, time, timedelta, timezone
from app.api.deps import require_roles
from app.core.database import get_db
from app.models.appointment import Appointment
from app.models.user import User
# add Customer -- 261124 
from app.models.customer import Customer
from app.schemas.appointment import AppointmentAdminOut


router = APIRouter(prefix="/customer_reservation", tags=["customer reservations"])
TAIPEI_TIMEZONE = timezone(timedelta(hours=8), "Asia/Taipei")
#以上一行新增的

@router.get("", response_model=list[AppointmentAdminOut])
def list_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "staff")),
):
    # return list(
    #     db.execute(
    #         select(Appointment).order_by(Appointment.starts_at, Appointment.id)
    #     ).scalars().all()
    # )
    #以下新增的
    today = datetime.now(TAIPEI_TIMEZONE).date()
    start_of_day = datetime.combine(
        today, time.min, tzinfo=TAIPEI_TIMEZONE
    ).astimezone(timezone.utc)
    start_of_next_day = datetime.combine(
        today + timedelta(days=1),
        time.min,
        tzinfo=TAIPEI_TIMEZONE,
    ).astimezone(timezone.utc)

    statement = (
        select(
            Appointment.id,
            Appointment.customer_id,
            Customer.name.label("customer_name"),
            Appointment.starts_at,
            Appointment.service_name,
            Appointment.status,
            Appointment.internal_note,
        )
        .join(Customer, Customer.id == Appointment.customer_id)
        .where(
            Appointment.status == "booked",
            Appointment.starts_at >= start_of_day,
            Appointment.starts_at < start_of_next_day,
        )
        .order_by(Appointment.starts_at, Appointment.id)
    )
    return db.execute(statement).mappings().all()
