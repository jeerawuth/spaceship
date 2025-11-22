# nodes/meteor_node.py

import pygame
import random
from settings.config import SCREEN_WIDTH, SCREEN_HEIGHT
from settings.game_constants import METEOR_SPEED
from managers.resource_manager import ResourceManager
from nodes.animation_node import AnimationNode

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

        start_x = random.randint(0, SCREEN_WIDTH)
        self.rect = self.image.get_rect()
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
