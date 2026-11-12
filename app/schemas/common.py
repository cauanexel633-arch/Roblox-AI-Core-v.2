from datetime import datetime, timezone
from uuid import uuid4
from pydantic import BaseModel, Field

class ErrorResponse(BaseModel):
    detail: str

class GenerationMeta(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model: str | None = None
    generation_ms: int | None = None
