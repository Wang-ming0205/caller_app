from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.catalog_item import CatalogItem
from app.models.customer import Customer
from app.models.transaction import Transaction, TransactionItem
from app.models.user import User


PRESERVED_USERNAMES = (
    "admin",
    "manager",
    "staff",
)


def reset_application_data(db: Session) -> dict:
    """
    清除系統中的業務資料，只保留三個基本帳號。

    整個刪除流程使用同一個 database transaction。
    任何一步失敗時會 rollback，不會只刪除一半。
    """

    existing_users = set(
        db.execute(
            select(User.username).where(
                User.username.in_(PRESERVED_USERNAMES)
            )
        ).scalars().all()
    )

    missing_users = sorted(
        set(PRESERVED_USERNAMES) - existing_users
    )

    if missing_users:
        raise ValueError(
            "缺少必要的基本帳號："
            + ", ".join(missing_users)
        )

    deleted = {}

    try:
        # 必須依照 Foreign Key 關聯順序刪除。
        result = db.execute(delete(TransactionItem))
        deleted["transaction_items"] = result.rowcount or 0

        result = db.execute(delete(Transaction))
        deleted["transactions"] = result.rowcount or 0

        result = db.execute(delete(Customer))
        deleted["customers"] = result.rowcount or 0

        result = db.execute(delete(CatalogItem))
        deleted["catalog_items"] = result.rowcount or 0

        # AuditLog 可能參照額外建立的 User，
        # 因此必須在刪除 User 之前清除。
        result = db.execute(delete(AuditLog))
        deleted["audit_logs"] = result.rowcount or 0

        result = db.execute(
            delete(User).where(
                ~User.username.in_(PRESERVED_USERNAMES)
            )
        )
        deleted["users"] = result.rowcount or 0

        db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "message": "Application data reset successfully",
        "deleted": deleted,
        "preserved_users": list(PRESERVED_USERNAMES),
    }