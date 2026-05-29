from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.config_schema import ConfigResponse, ConfigUpdate
from app.services.config_service import ConfigService

router = APIRouter(prefix="/config", tags=["Configuración"])


@router.get("", response_model=ConfigResponse)
def get_config(db: Session = Depends(get_db)):
    return ConfigService.get_or_create(db)


@router.put("", response_model=ConfigResponse)
def update_config(payload: ConfigUpdate, db: Session = Depends(get_db)):
    return ConfigService.update(db, payload)
