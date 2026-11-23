from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.models.appointment import Appointment
from app.models.user import User
from app.schemas.appointment import AppointmentAdminOut


router = APIRouter(prefix="/customer_reservation", tags=["customer reservations"])


@router.get("", response_model=list[AppointmentAdminOut])
def list_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "staff")),
):
    return list(
        db.execute(
            select(Appointment).order_by(Appointment.starts_at, Appointment.id)
        ).scalars().all()
    )
