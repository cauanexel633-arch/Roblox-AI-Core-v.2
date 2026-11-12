import logging
from fastapi import APIRouter, Depends, HTTPException
from app.core.security import require_api_key
from app.core.errors import AIProviderError
from app.schemas.map import MapGenerateRequest
from app.services.generators import generate_map
from app.services.repository import repository
from app.core.config import settings
logger = logging.getLogger(__name__)
router = APIRouter(dependencies=[Depends(require_api_key)])

@router.post("/generate")
async def create_map(payload: MapGenerateRequest):
    try:
        result = await generate_map(payload)
        await repository.insert(settings.supabase_maps_table, {"id": result["id"], "name": result["map"].name, "definition": result["map"].model_dump(mode="json")})
        return {"id": result["id"], "map": result["map"], "model": result["model"]}
    except AIProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)[:300]) from exc
    except Exception as exc:
        logger.exception("Map generation failed")
        raise HTTPException(status_code=500, detail="Map generation failed") from exc
