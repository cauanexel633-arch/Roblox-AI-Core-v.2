from fastapi import APIRouter, Depends
from app.core.security import require_api_key
from app.core.config import settings
router = APIRouter()

@router.get("/models", dependencies=[Depends(require_api_key)])
async def models():
    return {"provider": "openrouter", "primary_model": settings.openrouter_model, "fallback_models": settings.fallback_models, "structured_output": "attempt-json-schema-then-json-mode-and-local-validation"}
