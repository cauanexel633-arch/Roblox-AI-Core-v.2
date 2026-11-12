import logging
from fastapi import APIRouter, Depends, HTTPException
from app.core.security import require_api_key
from app.core.errors import AIProviderError
from app.schemas.event import EventGenerateRequest
from app.services.generators import generate_event
from app.services.repository import repository
from app.core.config import settings
logger = logging.getLogger(__name__)
router = APIRouter(dependencies=[Depends(require_api_key)])

@router.post("/generate")
async def create_event(payload: EventGenerateRequest):
    try:
        result = await generate_event(payload)
        await repository.insert(settings.supabase_events_table, {"id": result["id"], "name": result["event"].name, "definition": result["event"].model_dump(mode="json")})
        return {"id": result["id"], "event": result["event"], "model": result["model"]}
    except AIProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)[:300]) from exc
    except Exception as exc:
        logger.exception("Event generation failed")
        raise HTTPException(status_code=500, detail="Event generation failed") from exc
