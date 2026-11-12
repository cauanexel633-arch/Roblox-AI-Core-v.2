from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "PARTH AI Server"
    environment: str = "development"
    parth_api_key: str = "change-me-in-production"
    openrouter_api_key: str = ""
    openrouter_model: str = "openrouter/free"
    openrouter_fallback_models: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_site_url: str = "https://parth-ai.vercel.app"
    openrouter_app_name: str = "PARTH AI"
    request_timeout: float = Field(default=45.0, ge=5, le=120)
    max_retries: int = Field(default=2, ge=0, le=4)
    max_description_length: int = Field(default=240, ge=20, le=2000)
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_weapons_table: str = "weapons"
    supabase_requests_table: str = "weapon_requests"
    supabase_maps_table: str = "generated_maps"
    supabase_events_table: str = "generated_events"
    cors_origins_raw: str = ""
    log_level: str = "INFO"

    @property
    def cors_origins(self) -> list[str]:
        return [x.strip() for x in self.cors_origins_raw.split(",") if x.strip()]

    @property
    def fallback_models(self) -> list[str]:
        return [x.strip() for x in self.openrouter_fallback_models.split(",") if x.strip()]

    @property
    def supabase_enabled(self) -> bool:
        return bool(self.supabase_url and self.supabase_service_role_key)

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
