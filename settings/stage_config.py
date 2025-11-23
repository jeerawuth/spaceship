# settings/stage_config.py

from .spawn_config import STAGE_SPAWN_CONFIGS
from .boss_config import BOSS_STAGE_CONFIGS

# Hybrid: รวม config ต่อด่านไว้ที่เดียว
#
# โครงสร้าง STAGE_CONFIGS:
# {
#   1: {
#       "spawn": {... เหมือนใน STAGE_SPAWN_CONFIGS[1] ...},
#       "boss":  {... เหมือนใน BOSS_STAGE_CONFIGS[1] ...} หรือไม่มี key นี้ถ้าไม่มีบอส
#   },
#   2: {...},
#   ...
# }

STAGE_CONFIGS: dict[int, dict] = {}


# เอา config การ spawn ใส่เข้าไปก่อน
for stage, spawn_cfg in STAGE_SPAWN_CONFIGS.items():
    STAGE_CONFIGS.setdefault(stage, {})
    STAGE_CONFIGS[stage]["spawn"] = spawn_cfg

# แล้วค่อยเอา config บอสมาเติม
for stage, boss_cfg in BOSS_STAGE_CONFIGS.items():
    STAGE_CONFIGS.setdefault(stage, {})
    STAGE_CONFIGS[stage]["boss"] = boss_cfg

MAX_STAGE: int = max(STAGE_CONFIGS.keys()) if STAGE_CONFIGS else 0


def has_boss(stage: int) -> bool:
    """เช็คว่าด่านนี้มีบอสไหม"""
    return "boss" in STAGE_CONFIGS.get(stage, {})


def get_spawn_config(stage: int) -> dict:
    """ดึง config spawn ของด่าน (ถ้าไม่มีคืน dict ว่าง ๆ)"""
    return STAGE_CONFIGS.get(stage, {}).get("spawn", {})


def get_boss_config(stage: int) -> dict:
    """ดึง config boss ของด่าน (ถ้าไม่มีคืน dict ว่าง ๆ)"""
    return STAGE_CONFIGS.get(stage, {}).get("boss", {})
