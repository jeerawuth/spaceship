# settings/spawn_config.py 

STAGE_SPAWN_CONFIGS = {
    1: {  # ด่าน 1
        "meteor_interval": 1.0,   # วินาที / 1 ลูก
        "item_interval":   5.0,   # วินาที / 1 ไอเท็ม
        "item_weights": {         # โอกาสออกไอเท็มแต่ละแบบ
            "single": 0.6,
            "double": 0.3,
            "shield": 0.1,
        }
    },
    2: {  # ด่าน 2 ยากขึ้น: Meteor ถี่ขึ้น ไอเท็มน้อยลง
        "meteor_interval": 0.7,
        "item_interval":   7.0,
        "item_weights": {
            "single": 0.4,
            "double": 0.4,
            "shield": 0.2,
        }
    },
    # เพิ่มด่าน 3, 4, ... ได้ตามใจ
}
