from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.health import HealthRead

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthRead)
async def health() -> HealthRead:
    return HealthRead(status="ok", service=get_settings().app_name)
