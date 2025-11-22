# settings/game_constants.py

# ความเร็วต่าง ๆ
HERO_SPEED = 300          # px/s (ถ้าอยากให้ยานขยับซ้ายขวา)
BULLET_SPEED = 500        # px/s
ENEMY_Y = 100             # ตำแหน่งแนวตั้งของศัตรูด้านบน

# ค่าคงที่อื่น ๆ
BULLET_COOLDOWN = 0.3     # ยิงได้ทุก ๆ 0.3 วินาที
METEOR_SPEED = 150    # ความเร็วตกของอุกาบาต (px/s)
ITEM_FALL_SPEED = 120      # ความเร็วไอเท็มที่ตกลงมา (px/s)
ITEM_SPAWN_INTERVAL = 5.0  # ความถี่การเกิดไอเท็ม (วินาที)
METEO_SPAWN_INTERVAL = 1.0  # ความถี่การเกิดอุกาบาต (วินาที)

DRONE_FIRE_INTERVAL = 0.4   # ยิงทุก 0.4 วินาที
DRONE_LIFETIME = 8.0        # อยู่ได้ 8 วินาทีแล้วหายไป
DRONE_X_OFFSET = 80         # ห่างจาก Hero ตามแกน x
DRONE_Y_OFFSET = -10        # ขยับขึ้น/ลงจาก Hero ตามแกน y

SHIELD_LIFETIME = 10.0      # อยู่ได้ 10 วินาทีแล้วหายไป
