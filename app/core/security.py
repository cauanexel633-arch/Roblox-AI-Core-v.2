import secrets
from fastapi import Header, HTTPException, status
from app.core.config import settings

async def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    configured = settings.parth_api_key
    if not configured or configured == "change-me-in-production":
        if settings.environment.lower() == "production":
            raise HTTPException(status_code=503, detail="API authentication is not configured")
    if not x_api_key or not secrets.compare_digest(x_api_key, configured):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")
