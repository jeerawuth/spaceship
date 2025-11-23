# settings/boss_config.py

BOSS_STAGE_CONFIGS = {
    1: {
        "max_hp": 40,
        "fire_interval": 5.0,   # ยิงทุก 5 วินาที
        "bullet_pairs": 1,      # 1 คู่ = ยิงซ้าย+ขวา 2 นัด
    },
    2: {
        "max_hp": 60,
        "fire_interval": 4.0,   # ยิงถี่ขึ้น
        "bullet_pairs": 2,      # ยิงซ้าย+ขวา 2 คู่ = 4 นัด
    },
    3: {
        "max_hp": 80,
        "fire_interval": 3.0,
        "bullet_pairs": 3,
    },
    4: {
        "max_hp": 100,
        "fire_interval": 2.0,   
        "bullet_pairs": 3,      
    },
    5: {
        "max_hp": 200,
        "fire_interval": 2.0,
        "bullet_pairs": 3,
    },
    6: {
        "max_hp": 300,
        "fire_interval": 2.0,   
        "bullet_pairs": 4,   
    },
}

