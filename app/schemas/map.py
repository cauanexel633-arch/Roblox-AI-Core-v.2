from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator
import re

class MapGenerateRequest(BaseModel):
    description: str = Field(min_length=5, max_length=240)
    player_id: str = Field(min_length=1, max_length=32)
    request_id: str | None = None

class MapDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"] = "1.0"
    name: str = Field(min_length=2, max_length=40)
    theme: str = Field(min_length=2, max_length=80)
    size: Literal["small", "medium", "large"]
    recommended_mode: Literal["classic", "teams", "chaos", "crazy", "infinity"]
    zones: list[str] = Field(min_length=2, max_length=12)
    structures: list[str] = Field(max_length=20)
    spawn_points: int = Field(ge=2, le=32)
    lighting: str = Field(max_length=80)
    gameplay_notes: list[str] = Field(max_length=8)

    @field_validator("structures")
    @classmethod
    def safe_structure_ids(cls, values: list[str]) -> list[str]:
        for value in values:
            if not re.fullmatch(r"[A-Za-z0-9_-]{1,48}", value):
                raise ValueError("Structure IDs must be safe catalog identifiers")
        return values

class MapGenerateResponse(BaseModel):
    id: str
    map: MapDefinition
    model: str
