from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.services.setup_service import seed_database

router = APIRouter(prefix="/setup", tags=["setup"])


@router.post("/seed")
def seed_data(db: Session = Depends(get_db)):
    if not settings.ENABLE_SEED:
        raise HTTPException(status_code=403, detail="Seed endpoint is disabled")

    return seed_database(db)