from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles, get_current_user
from app.core.database import get_db
from app.core.security import hash_password , verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserUpdate , PasswordChange

router = APIRouter(prefix="/users", tags=["users"])

VALID_ROLES = {"admin", "manager", "staff"}

@router.get("", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    stmt = select(User).order_by(User.id.asc())
    return list(db.execute(stmt).scalars().all())

@router.post("", response_model=UserOut)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    if payload.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")
    exists = db.execute(select(User).where(User.username == payload.username)).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        is_active=payload.is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/me", response_model=UserOut)
def current_user_profile(current_user: User = Depends(get_current_user)):
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


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = payload.model_dump(exclude_unset=True)
    if "role" in data and data["role"] is not None and data["role"] not in VALID_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")
    if "password" in data and data["password"]:
        user.password_hash = hash_password(data.pop("password"))
    for key, value in data.items():
        if key != "password":
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

