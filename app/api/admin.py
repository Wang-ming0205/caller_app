from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.core.security import verify_password
from app.models.user import User
from app.schemas.admin import ResetDataRequest, ResetDataResponse
from app.services.admin_service import reset_application_data


router = APIRouter(prefix="/admin", tags=["admin"])

RESET_CONFIRMATION_TEXT = "DELETE ALL DATA"


@router.post(
    "/reset-data",
    response_model=ResetDataResponse,
    status_code=status.HTTP_200_OK,
)
def reset_data(
    payload: ResetDataRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    """
    Admin 專用的系統資料重置 API。

    清除客戶、消費紀錄、消費項目、AuditLog
    與額外帳號，只保留 admin、manager、staff。
    """

    if payload.confirmation != RESET_CONFIRMATION_TEXT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'請輸入「{RESET_CONFIRMATION_TEXT}」確認重置',
        )

    if not verify_password(
        payload.password,
        current_user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="目前密碼錯誤",
        )

    try:
        return reset_application_data(db)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc