# nodes/boss_node.py

import pygame
from settings.config import SCREEN_WIDTH
from managers.resource_manager import ResourceManager
from nodes.animation_node import AnimationNode


class BossNode(AnimationNode):
    """
    Boss ขนาดใหญ่ ใช้สปรายคนละชุดกับ Enemy ปกติ
    มี HP หลายหน่วย และเคลื่อนที่ซ้าย–ขวาด้านบนหน้าจอ
    """

    def __init__(self, max_hp: int = 50, speed_x: float = 150.0, y: int = 60):
        """
        max_hp : เลือกความถึกของ Boss
        speed_x: ความเร็วเคลื่อนที่แนวนอน
        y      : ตำแหน่งแกน Y ที่วาง Boss บริเวณด้านบนหน้าจอ
        """
        boss_frames = ResourceManager.get_boss_frames()
        if not boss_frames:
            raise ValueError("ResourceManager.get_boss_frames() must return at least 1 frame")

        states = {
            "default": {
                "frames": boss_frames,
                "frame_duration": 0.1,
                "loop": True,
                "kill_on_end": False,
            }
        }

        super().__init__(states, default_state="default", use_mask=True)

        self.max_hp = max_hp
        self.hp = max_hp

        self.rect = self.image.get_rect()
        self.rect.midtop = (SCREEN_WIDTH // 2, y)

        # การเคลื่อนที่แบบง่าย ๆ: วิ่งซ้าย-ขวา
        self.speed_x = speed_x
        self.direction = 1  # 1 = วิ่งไปขวา, -1 = วิ่งไปซ้าย

    # ------------------ โดนดาเมจจากกระสุน ------------------
    def take_damage(self, amount: int = 1) -> bool:
        """
        ทำดาเมจกับ Boss
        :return: True ถ้า Boss ตาย, False ถ้ายังไม่ตาย
        """
        self.hp -= amount
        if self.hp <= 0:
            self.kill()
            return True
        return False

    # ------------------ อัปเดตทุกเฟรม ------------------
    def update(self, dt: float):
        # เคลื่อนที่ซ้าย-ขวาด้านบนจอ
        self.rect.x += self.direction * self.speed_x * dt

        # เด้งกลับเมื่อชนขอบจอ
        if self.rect.left < 0:
            self.rect.left = 0
            self.direction = 1
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.direction = -1

        # อัปเดตแอนิเมชัน
        self.update_animation(dt)
