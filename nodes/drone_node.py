# nodes/drone_node.py

import pygame
from settings.game_constants import (
    DRONE_FIRE_INTERVAL,
    DRONE_LIFETIME,
    DRONE_X_OFFSET,
    DRONE_Y_OFFSET,
)
from managers.resource_manager import ResourceManager
from nodes.animation_node import AnimationNode
from nodes.bullet_node import BulletNode  # หรือส่งคลาสจากข้างนอกก็ได้


class DroneNode(AnimationNode):
    def __init__(self, hero, side="right", weapon_type="single"):
        """
        hero       : HeroNode ที่ drone จะติดตาม
        side       : "right" หรือ "left"
        weapon_type: "single" หรือ "double" (ใช้บอก HUD)
        """
        self.hero = hero
        self.side = side
        self.weapon_type = weapon_type

        frames = ResourceManager.get_drone_frames()
        if not frames:
            raise ValueError("No drone frames loaded")

        states = {
            "default": {
                "frames": frames,
                "frame_duration": 0.08,
                "loop": True,
                "kill_on_end": False,
            }
        }

        super().__init__(states, default_state="default", use_mask=True)

        self.pos = pygame.Vector2(self.hero.rect.centerx, self.hero.rect.centery)
        self.rect.center = self.pos

        self.fire_cooldown = DRONE_FIRE_INTERVAL
        self.lifetime = DRONE_LIFETIME

        # นับจำนวนอาวุธที่ Hero มีอยู่ตอนนี้
        if hasattr(self.hero, "weapon_counts") and self.weapon_type in self.hero.weapon_counts:
            self.hero.weapon_counts[self.weapon_type] += 1

    def _update_position(self):
        base_x = self.hero.rect.centerx
        base_y = self.hero.rect.centery + DRONE_Y_OFFSET

        if self.side == "right":
            self.pos.x = base_x + DRONE_X_OFFSET
        elif self.side == "left":
            self.pos.x = base_x - DRONE_X_OFFSET
        else:
            self.pos.x = base_x

        self.pos.y = base_y
        self.rect.center = self.pos

    def _try_fire(self, dt, bullet_group):
        self.fire_cooldown -= dt
        if self.fire_cooldown <= 0:
            self.fire_cooldown = DRONE_FIRE_INTERVAL
            bullet_pos = self.rect.midtop
            bullet = BulletNode(bullet_pos)
            bullet_group.add(bullet)

    def kill(self):
        """ลบ Drone ออกจากเกม และอัปเดตจำนวนใน Hero"""
        if hasattr(self.hero, "weapon_counts"):
            wt = getattr(self, "weapon_type", None)
            if wt in self.hero.weapon_counts and self.hero.weapon_counts[wt] > 0:
                self.hero.weapon_counts[wt] -= 1
        super().kill()

    def update(self, dt, bullet_group=None):
        # อายุการทำงานลดลง
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return

        # ถ้า Hero หายไป Drone ก็หาย
        if not self.hero.alive():
            self.kill()
            return

        # ติดตาม Hero
        self._update_position()

        # ยิงกระสุนอัตโนมัติ
        if bullet_group is not None:
            self._try_fire(dt, bullet_group)

        # แอนิเมชัน
        self.update_animation(dt)
