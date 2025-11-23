# settings/background_config.py

# กำหนดชื่อ KEY ของภาพพื้นหลังสำหรับแต่ละด่าน (Stage)
# ชื่อ Key (far, medium, near) ต้องตรงกับที่ใช้ใน BackgroundNode
# ชื่อ Value (เช่น 'far_stars_1') ต้องตรงกับที่ใช้ใน ResourceManager
STAGE_BACKGROUND_KEYS = {
    # Stage 1: ใช้ชุดดวงดาวเริ่มต้น (จากภาพที่อัปโหลดมา)
    1: {
        "far":    "far_stars_1",    # เช่น ผูกกับ bg_01.jpg
        "medium": "medium_planet_1",  # เช่น ผูกกับ jupiter.jpg
        "near":   "near_stars_1",   # เช่น ผูกกับ bg_02.png
    },
    
    # Stage 2: ตัวอย่างการเปลี่ยนไปใช้ชุดใหม่
    # เมื่อคุณมีภาพใหม่: เช่น far_stars_2.png, medium_planet_2.png
    2: {
        "far":    "far_stars_2",
        "medium": "medium_planet_2",
        "near":   "near_stars_2",
    },

    # 3: { ... }
    # ... และด่านอื่น ๆ
}