import pytest
from pydantic import ValidationError
from app.schemas.weapon import WeaponDefinition

def valid_weapon():
    return {
        "schema_version": "1.0", "name": "TEST-X", "description": "Rifle de teste",
        "category": "rifle", "rarity": "rare",
        "visual": {"template": "BasicRifle", "primary_color": "#1122AA", "secondary_color": "#223344", "material": "Metal", "components": [], "skin_id": "default"},
        "combat": {"damage": 25, "fire_rate": 0.2, "range": 300, "magazine_size": 30, "reserve_ammo": 90, "reload_time": 2.5, "fire_mode": "automatic", "spread": 1, "recoil": 1},
        "abilities": [], "effects": {"muzzle": "default_muzzle", "impact": "default_impact", "tracer": "default_tracer"},
        "animations": {"fire": "DefaultFire", "reload": "DefaultReload", "equip": "DefaultEquip", "inspect": "DefaultInspect"}
    }

def test_valid_weapon_schema():
    weapon = WeaponDefinition.model_validate(valid_weapon())
    assert weapon.name == "TEST-X"

def test_rejects_out_of_range_damage():
    data = valid_weapon()
    data["combat"]["damage"] = 1000
    with pytest.raises(ValidationError):
        WeaponDefinition.model_validate(data)
