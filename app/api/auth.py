from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, create_access_token,hash_password
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserMe , PasswordChange
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    stmt = select(User).where(User.username == payload.username)
    user = db.execute(stmt).scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or password incorrect",
        )

    token = create_access_token(subject=str(user.id))
    return TokenResponse(
        access_token=token,
        user=UserMe.model_validate(user),
    )

@router.get("/me", response_model=UserMe)
def me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me/password")
def change_my_password(
    payload: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    current_user.password_hash = hash_password(payload.new_password)

    db.commit()
    return {"message": "Password changed successfully"}

