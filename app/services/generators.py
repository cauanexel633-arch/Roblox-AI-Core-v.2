import time
from uuid import uuid4
from app.services.openrouter import openrouter_client
from app.services.prompts import WEAPON_SYSTEM, MAP_SYSTEM, EVENT_SYSTEM
from app.schemas.weapon import WeaponDefinition, WeaponGenerateRequest
from app.schemas.map import MapDefinition, MapGenerateRequest
from app.schemas.event import EventDefinition, EventGenerateRequest

async def generate_weapon(request: WeaponGenerateRequest):
    started = time.perf_counter()
    category_hint = f" Preferred category: {request.preferred_category}." if request.preferred_category else ""
    user_prompt = f"Create one balanced original weapon from this player request: {request.description}.{category_hint} Output a complete definition."
    weapon, model = await openrouter_client.generate_structured(system_prompt=WEAPON_SYSTEM, user_prompt=user_prompt, schema_model=WeaponDefinition, schema_name="parth_weapon")
    # Apply a deterministic category preference after schema validation.
    if request.preferred_category:
        weapon.category = request.preferred_category
    return {"id": str(uuid4()), "owner_user_id": request.player_id, "weapon": weapon, "model": model, "generation_ms": int((time.perf_counter()-started)*1000)}

async def generate_map(request: MapGenerateRequest):
    prompt = f"Create a buildable Roblox PvP map specification from this request: {request.description}."
    result, model = await openrouter_client.generate_structured(system_prompt=MAP_SYSTEM, user_prompt=prompt, schema_model=MapDefinition, schema_name="parth_map")
    return {"id": str(uuid4()), "map": result, "model": model}

async def generate_event(request: EventGenerateRequest):
    prompt = f"Create one balanced event for mode {request.mode}. Player request: {request.description}."
    result, model = await openrouter_client.generate_structured(system_prompt=EVENT_SYSTEM, user_prompt=prompt, schema_model=EventDefinition, schema_name="parth_event")
    return {"id": str(uuid4()), "event": result, "model": model}
