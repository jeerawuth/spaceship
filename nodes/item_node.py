# nodes/item_node.py

import pygame
import random
from settings.config import SCREEN_WIDTH, SCREEN_HEIGHT
from settings.game_constants import ITEM_FALL_SPEED
from managers.resource_manager import ResourceManager
from nodes.animation_node import AnimationNode

class ItemNode(AnimationNode):
    def __init__(self, item_type):
        """
        item_type: "single", "double", "shield" ฯลฯ
        """
        self.type = item_type

        frames = ResourceManager.get_item_frames(self.type)
        if not frames:
            raise ValueError(f"No item frames found for type='{self.type}'")

        states = {
            "default": {
                "frames": frames,
                "frame_duration": 0.12,
                "loop": True,
                "kill_on_end": False,
            }
        }

        super().__init__(states, default_state="default", use_mask=True)

        start_x = random.randint(0, SCREEN_WIDTH)
        self.rect = self.image.get_rect()
        self.rect.midbottom = (start_x, 0)

        self.pos = pygame.Vector2(self.rect.centerx, self.rect.centery)
        self.speed = ITEM_FALL_SPEED

    def update(self, dt):
        # แอนิเมชันเฟรม
        self.update_animation(dt)

        # เคลื่อนที่ลงล่าง
        self.pos.y += self.speed * dt
        self.rect.center = self.pos

        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
