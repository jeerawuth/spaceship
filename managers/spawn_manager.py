# managers/spawn_manager.py

import random
from nodes.meteor_node import MeteorNode
from nodes.item_node import ItemNode
from nodes.speed_item_node import SpeedItemNode
from nodes.laser_item_node import LaserItemNode
from nodes.buckshot_item_node import BuckshotItemNode 


class SpawnManager:
    """
    จัดการการ Spawn ศัตรู/อ็อบเจกต์ต่าง ๆ ตาม config ของแต่ละด่าน

    รองรับสองแบบ:
    - แบบเดิม: stage_configs = STAGE_SPAWN_CONFIGS
        { stage: { "meteor_interval": ..., "item_interval": ..., "item_weights": {...} } }

    - แบบ Hybrid: stage_configs = STAGE_CONFIGS
        {
          stage: {
            "spawn": { "meteor_interval": ..., "item_interval": ..., "item_weights": {...} },
            "boss":  {...}  # (ไม่ใช้ใน SpawnManager)
          }
        }
    """

    def __init__(self, stage_configs: dict, initial_stage: int = 1):
        self.stage_configs = stage_configs
        self.current_stage = None

        # ตัวแปร timer ภายใน
        self.meteor_timer = 0.0
        self.item_timer   = 0.0

        self.set_stage(initial_stage)

    def set_stage(self, stage: int):
        """เปลี่ยนด่าน → โหลด config ใหม่ของด่านนั้น"""
        self.current_stage = stage
        cfg = self.stage_configs.get(stage, {})

        # Hybrid support:
        # ถ้า cfg ไม่มี key meteor_interval แต่มี key "spawn"
        # แปลว่าใช้โครงสร้าง STAGE_CONFIGS → ดึง cfg["spawn"] มาใช้แทน
        if "meteor_interval" not in cfg and "spawn" in cfg:
            cfg = cfg["spawn"]

        self.meteor_interval = cfg.get("meteor_interval", 1.0)
        self.item_interval   = cfg.get("item_interval", 5.0)
        self.item_weights    = cfg.get("item_weights", {"single": 1.0})

        # reset timer ให้เริ่มนับใหม่
        self.meteor_timer = 0.0
        self.item_timer   = 0.0

    def update(self, dt: float, meteors_group, items_group):
        """
        เรียกทุกเฟรมจาก main:
            spawn_manager.update(dt, meteors, items)
        """
        # ----------------- Meteor -------------------
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

            # แปลง item_type → instance จริง
            if item_type in ("single", "double", "shield"):
                item = ItemNode(item_type)
            elif item_type == "speed":
                item = SpeedItemNode()
            elif item_type == "laser":
                item = LaserItemNode()
            elif item_type == "buckshot":
                item = BuckshotItemNode()
            else:
                # กันพังกรณี config พิมพ์ผิด
                item = ItemNode("single")

            items_group.add(item)
