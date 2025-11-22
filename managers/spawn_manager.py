# managers/spawn_manager.py

import random

from nodes.meteor_node import MeteorNode
from nodes.item_node import ItemNode


class SpawnManager:
    """
    จัดการการ Spawn ศัตรู/อ็อบเจกต์ต่าง ๆ ตาม config ของแต่ละด่าน
    คอนฟิกถูกส่งมาจาก settings.spawn_config.STAGE_SPAWN_CONFIGS
    ตัวอย่างโครงสร้าง config:

    STAGE_SPAWN_CONFIGS = {
        1: {
            "meteor_interval": 1.0,
            "item_interval": 5.0,
            "item_weights": {
                "single": 0.6,
                "double": 0.3,
                "shield": 0.1,
            },
        },
        2: { ... },
    }
    """

    def __init__(self, stage_configs: dict, initial_stage: int = 1):
        self.stage_configs = stage_configs
        self.current_stage = None

        # ตัวจับเวลา spawn
        self.meteor_timer = 0.0
        self.item_timer = 0.0

        self.meteor_interval = 1.0
        self.item_interval = 5.0
        self.item_weights = {"single": 1.0}

        self.set_stage(initial_stage)

    def set_stage(self, stage_id: int):
        """เปลี่ยนด่าน / โหลด config ด่านใหม่"""
        if stage_id not in self.stage_configs:
            raise ValueError(f"Stage {stage_id} not in stage_configs")

        self.current_stage = stage_id
        cfg = self.stage_configs[stage_id]

        self.meteor_interval = cfg.get("meteor_interval", 1.0)
        self.item_interval = cfg.get("item_interval", 5.0)
        self.item_weights = cfg.get("item_weights", {"single": 1.0})

        # reset timer
        self.meteor_timer = self.meteor_interval
        self.item_timer = self.item_interval

    def update(self, dt: float, meteors_group, items_group):
        """
        เรียกทุกเฟรมจาก main loop เพื่อเช็คว่าถึงเวลาต้อง spawn หรือยัง
        dt: วินาทีที่ผ่านไปในเฟรมนั้น
        """

        # ----------------- Meteor -----------------
        self.meteor_timer -= dt
        if self.meteor_timer <= 0:
            self.meteor_timer += self.meteor_interval
            meteors_group.add(MeteorNode())

        # ----------------- Item -------------------
        self.item_timer -= dt
        if self.item_timer <= 0:
            self.item_timer += self.item_interval

            # สุ่มชนิดไอเท็มตาม weights ของด่าน
            types = list(self.item_weights.keys())
            weights = list(self.item_weights.values())
            item_type = random.choices(types, weights=weights, k=1)[0]

            # สมมติว่า ItemNode รองรับพารามิเตอร์ชนิดไอเท็ม เช่น ItemNode("single")
            items_group.add(ItemNode(item_type))
