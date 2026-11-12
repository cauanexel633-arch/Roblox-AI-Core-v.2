from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

class EventGenerateRequest(BaseModel):
    description: str = Field(min_length=5, max_length=240)
    mode: Literal["chaos", "crazy", "infinity"] = "crazy"
    player_id: str = Field(min_length=1, max_length=32)

class EventDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"] = "1.0"
    name: str = Field(min_length=2, max_length=40)
    description: str = Field(min_length=5, max_length=160)
    duration_seconds: int = Field(ge=5, le=180)
    event_type: Literal["gravity", "movement", "weapon", "environment", "arena", "survival"]
    intensity: int = Field(ge=1, le=5)
    effect_id: Literal["low_gravity", "high_gravity", "speed_boost", "random_weapon", "infinite_ammo", "meteor_shower", "electric_floor", "shrinking_zone", "double_damage"]
    parameters: dict[str, float | int | bool | str] = Field(default_factory=dict, max_length=12)

class EventGenerateResponse(BaseModel):
    id: str
    event: EventDefinition
    model: str
