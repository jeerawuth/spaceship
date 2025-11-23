# nodes/meteor_node.py

import pygame
import random
from settings.config import SCREEN_WIDTH, SCREEN_HEIGHT
from settings.game_constants import METEOR_SPEED
from managers.resource_manager import ResourceManager
from nodes.animation_node import AnimationNode


# ระยะห่างจากขอบจอซ้าย/ขวา (ปรับได้ตามที่ชอบ)
METEOR_SPAWN_MARGIN_X = 60


class MeteorNode(AnimationNode):
    def __init__(self):
        meteor_frames = ResourceManager.get_meteor_frames()
        states = {
            "default": {
                "frames": meteor_frames,
                "frame_duration": 0.08,
                "loop": True,
                "kill_on_end": False,
            }
        }

        super().__init__(states, default_state="default", use_mask=True)

        # ให้รู้ขนาดตัว sprite ก่อน แล้วค่อยสุ่ม x แบบเว้นขอบจอ
        self.rect = self.image.get_rect()

        # คำนวณช่วง x ที่อนุญาต (เว้น margin + ครึ่งหนึ่งของความกว้าง sprite)
        min_x = METEOR_SPAWN_MARGIN_X + self.rect.width // 2
        max_x = SCREEN_WIDTH - METEOR_SPAWN_MARGIN_X - self.rect.width // 2

        # กันกรณีจอเล็กมาก ๆ จน margin ทำให้ min_x >= max_x
        if min_x >= max_x:
            start_x = SCREEN_WIDTH // 2
        else:
            start_x = random.randint(min_x, max_x)

        self.rect.midbottom = (start_x, 0)

        self.pos = pygame.Vector2(self.rect.centerx, self.rect.centery)
        self.speed = METEOR_SPEED

    def update(self, dt):
        # เคลื่อนที่ลงล่าง
        self.pos.y += self.speed * dt
        self.rect.center = self.pos

        # ถ้าพ้นขอบล่างลบทิ้ง
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
            return

        self.update_animation(dt)
