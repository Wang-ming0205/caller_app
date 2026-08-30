from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.audit import write_audit_log
from app.api.deps import get_current_user, require_roles
from app.core.database import get_db
from app.models.catalog_item import CatalogItem
from app.models.user import User
from app.schemas.catalog_item import CatalogItemCreate, CatalogItemOut

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[CatalogItemOut])
def list_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(CatalogItem)
        .where(CatalogItem.is_active.is_(True))
        .order_by(CatalogItem.id.desc())
    )
    return list(db.execute(stmt).scalars().all())


@router.post("", response_model=CatalogItemOut, status_code=status.HTTP_201_CREATED)
def create_item(
    payload: CatalogItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "staff")),
):
    exists = db.execute(
        select(CatalogItem).where(
            func.lower(CatalogItem.name) == payload.name.lower()
        )
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=400, detail="Item name already exists")

    item = CatalogItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)

    write_audit_log(
        db=db,
        action="CREATE_ITEM",
        target_type="catalog_item",
        user_id=current_user.id,
        target_id=item.id,
        detail={
            "name": item.name,
            "default_price": str(item.default_price),
        },
    )
    return item