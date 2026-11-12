from fastapi import APIRouter
from app.api.v1.endpoints import health, weapons, maps, events, models

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(models.router, prefix="/v1", tags=["models"])
api_router.include_router(weapons.router, prefix="/v1/weapons", tags=["weapons"])
api_router.include_router(maps.router, prefix="/v1/maps", tags=["maps"])
api_router.include_router(events.router, prefix="/v1/events", tags=["events"])
