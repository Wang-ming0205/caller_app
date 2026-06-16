from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


def write_audit_log(
    db: Session,
    action: str,
    target_type: str,
    user_id: int | None = None,
    target_id: int | None = None,
    detail: dict | None = None,
):
    log = AuditLog(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail=detail,
    )

    db.add(log)
    db.commit()