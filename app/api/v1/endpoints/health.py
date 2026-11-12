from fastapi import APIRouter
from app.core.config import settings
router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok", "service": settings.app_name, "version": "1.0.0", "supabase_enabled": settings.supabase_enabled, "openrouter_configured": bool(settings.openrouter_api_key)}
