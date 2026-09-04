# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from app.core.config import settings
# from app.core.database import get_db
# from app.services.setup_service import seed_database

# router = APIRouter(prefix="/setup", tags=["setup"])


# @router.post("/seed")
# def seed_data(db: Session = Depends(get_db)):
#     if not settings.ENABLE_SEED:
#         raise HTTPException(status_code=403, detail="Seed endpoint is disabled")

#     return seed_database(db)

#new version
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.services.setup_service import seed_database

router = APIRouter(prefix="/setup", tags=["setup"])


@router.post("/seed")
def seed_data(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles("admin")),
):
    if not settings.ENABLE_SEED:
        raise HTTPException(status_code=403, detail="Seed endpoint is disabled")

    return seed_database(db)
