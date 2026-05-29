from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health():
    settings = get_settings()
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}
