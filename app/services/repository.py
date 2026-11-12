import logging
from typing import Any
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

class SupabaseRepository:
    """Small PostgREST repository. If Supabase is not configured, persistence is disabled (local dev only)."""
    async def insert(self, table: str, row: dict[str, Any]) -> None:
        if not settings.supabase_enabled:
            logger.info("Supabase disabled; skipped insert into %s", table)
            return
        url = f"{settings.supabase_url.rstrip('/')}/rest/v1/{table}"
        headers = {
            "apikey": settings.supabase_service_role_key,
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(url, headers=headers, json=row)
            if response.status_code >= 400:
                logger.error("Supabase insert failed (%s): %s", response.status_code, response.text[:300])
                response.raise_for_status()

    async def get_by_id(self, table: str, record_id: str) -> dict[str, Any] | None:
        if not settings.supabase_enabled:
            return None
        url = f"{settings.supabase_url.rstrip('/')}/rest/v1/{table}"
        headers = {"apikey": settings.supabase_service_role_key, "Authorization": f"Bearer {settings.supabase_service_role_key}"}
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, headers=headers, params={"id": f"eq.{record_id}", "select": "*", "limit": "1"})
            response.raise_for_status()
            rows = response.json()
            return rows[0] if rows else None

repository = SupabaseRepository()
