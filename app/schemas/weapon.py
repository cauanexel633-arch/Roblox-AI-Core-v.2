from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator
import re
from app.schemas.common import GenerationMeta

Rarity = Literal["common", "uncommon", "rare", "epic", "legendary", "mythic"]
Category = Literal["pistol", "rifle", "smg", "shotgun", "sniper", "special"]
FireMode = Literal["semi", "automatic", "burst"]

def _safe_catalog_key(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,48}", value):
        raise ValueError("Catalog identifiers may contain only letters, numbers, _ and -")
    return value

class WeaponVisual(BaseModel):
    model_config = ConfigDict(extra="forbid")
    template: str = "BasicRifle"
    primary_color: str = "#315BFF"
    secondary_color: str = "#202438"
    material: Literal["Plastic", "Metal", "Neon", "SmoothPlastic"] = "Metal"
    components: list[str] = Field(default_factory=list, max_length=12)
    skin_id: str = "default"

    @field_validator("template", "skin_id")
    @classmethod
    def safe_visual_ids(cls, value: str) -> str:
        return _safe_catalog_key(value)

    @field_validator("components")
    @classmethod
    def safe_components(cls, values: list[str]) -> list[str]:
        return [_safe_catalog_key(value) for value in values]

    @field_validator("primary_color", "secondary_color")
    @classmethod
    def valid_hex(cls, value: str) -> str:
        if len(value) != 7 or not value.startswith("#"):
            raise ValueError("Color must be #RRGGBB")
        int(value[1:], 16)
        return value.upper()

class WeaponCombat(BaseModel):
    model_config = ConfigDict(extra="forbid")
    damage: float = Field(ge=1, le=100)
    fire_rate: float = Field(ge=0.08, le=2.0, description="Seconds between shots")
    range: float = Field(ge=10, le=1000)
    magazine_size: int = Field(ge=1, le=200)
    reserve_ammo: int = Field(ge=0, le=1000)
    reload_time: float = Field(ge=0.5, le=15)
    fire_mode: FireMode
    spread: float = Field(ge=0, le=30)
    recoil: float = Field(ge=0, le=10)

class WeaponAbility(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["piercing_shot", "explosive_shot", "ricochet_shot", "chain_lightning", "plasma_shot", "freeze_shot", "teleport_shot", "gravity_shot"]
    enabled: bool = True
    cooldown: float = Field(default=8, ge=1, le=120)

class WeaponEffects(BaseModel):
    model_config = ConfigDict(extra="forbid")
    muzzle: str = "default_muzzle"
    impact: str = "default_impact"
    tracer: str = "default_tracer"

    @field_validator("muzzle", "impact", "tracer")
    @classmethod
    def safe_effect_ids(cls, value: str) -> str:
        return _safe_catalog_key(value)

class WeaponAnimations(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fire: str = "DefaultFire"
    reload: str = "DefaultReload"
    equip: str = "DefaultEquip"
    inspect: str = "DefaultInspect"

    @field_validator("fire", "reload", "equip", "inspect")
    @classmethod
    def safe_animation_ids(cls, value: str) -> str:
        return _safe_catalog_key(value)

class WeaponDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"] = "1.0"
    name: str = Field(min_length=2, max_length=32)
    description: str = Field(min_length=3, max_length=180)
    category: Category
    rarity: Rarity
    visual: WeaponVisual
    combat: WeaponCombat
    abilities: list[WeaponAbility] = Field(default_factory=list, max_length=2)
    effects: WeaponEffects = Field(default_factory=WeaponEffects)
    animations: WeaponAnimations = Field(default_factory=WeaponAnimations)

class WeaponGenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    description: str = Field(min_length=5, max_length=240)
    player_id: str = Field(min_length=1, max_length=32)
    request_id: str | None = Field(default=None, max_length=80)
    preferred_category: Category | None = None

class WeaponGenerateResponse(BaseModel):
    id: str
    owner_user_id: str
    weapon: WeaponDefinition
    meta: GenerationMeta
