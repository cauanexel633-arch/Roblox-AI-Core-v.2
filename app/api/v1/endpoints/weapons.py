import logging
from fastapi import APIRouter, Depends, HTTPException
from app.core.security import require_api_key
from app.core.errors import AIProviderError
from app.schemas.weapon import WeaponGenerateRequest, WeaponGenerateResponse
from app.services.generators import generate_weapon
from app.services.repository import repository
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(dependencies=[Depends(require_api_key)])

@router.post("/generate", response_model=WeaponGenerateResponse)
async def create_weapon(payload: WeaponGenerateRequest):
    if len(payload.description.strip()) < 5 or len(payload.description) > settings.max_description_length:
        raise HTTPException(status_code=422, detail="Description length is outside configured limits")
    try:
        result = await generate_weapon(payload)
        weapon = result["weapon"]
        await repository.insert(settings.supabase_weapons_table, {
            "id": result["id"], "owner_user_id": int(payload.player_id) if payload.player_id.isdigit() else 0,
            "name": weapon.name, "category": weapon.category, "rarity": weapon.rarity,
            "definition": weapon.model_dump(mode="json"), "asset_version": "catalog-v1"
        })
        await repository.insert(settings.supabase_requests_table, {
            "id": payload.request_id or result["id"],
            "player_user_id": int(payload.player_id) if payload.player_id.isdigit() else 0,
            "description": payload.description, "status": "completed"
        })
        return WeaponGenerateResponse(id=result["id"], owner_user_id=result["owner_user_id"], weapon=weapon, meta={"request_id": payload.request_id or result["id"], "model": result["model"], "generation_ms": result["generation_ms"]})
    except AIProviderError as exc:
        logger.exception("Weapon generation failed")
        raise HTTPException(status_code=502, detail=str(exc)[:300]) from exc
    except Exception as exc:
        logger.exception("Unexpected weapon generation error")
        raise HTTPException(status_code=500, detail="Weapon generation failed") from exc

@router.get("/{weapon_id}")
async def get_weapon(weapon_id: str):
    record = await repository.get_by_id(settings.supabase_weapons_table, weapon_id)
    if not record:
        raise HTTPException(status_code=404, detail="Weapon not found or persistence is not configured")
    return record
