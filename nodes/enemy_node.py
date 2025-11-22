# nodes/enemy_node.py

import pygame
from settings.config import SCREEN_WIDTH
from settings.game_constants import ENEMY_Y
from managers.resource_manager import ResourceManager
from nodes.animation_node import AnimationNode

class EnemyNode(AnimationNode):
    def __init__(self):
        enemy_frames = ResourceManager.get_enemy_frames()
        states = {
            "default": {
                "frames": enemy_frames,
                "frame_duration": 0.1,
                "loop": True,
                "kill_on_end": False,
            }
        }

        super().__init__(states, default_state="default", use_mask=True)

        self.rect = self.image.get_rect()
        self.rect.midtop = (SCREEN_WIDTH // 2, ENEMY_Y)

    def update(self, dt):
        # ศัตรูนิ่งในตัวอย่างนี้ (ถ้าจะให้เคลื่อนที่เพิ่มทีหลังได้)
        self.update_animation(dt)
