# nodes/shield_node.py

import pygame
from managers.resource_manager import ResourceManager
from settings.game_constants import SHIELD_LIFETIME


class ShieldNode(pygame.sprite.Sprite):
    def __init__(self, hero, max_hp=3):
        """
        hero   : HeroNode ที่จะติดเกราะ
        max_hp : จำนวนครั้งที่กันดาเมจได้ ก่อนพัง
        """
        super().__init__()

        self.hero = hero
        self.max_hp = max_hp
        self.hp = max_hp

        # ชนิดอาวุธ (สำหรับ HUD)
        self.weapon_type = "shield"

        # โหลดเฟรมเกราะจาก ResourceManager (shield_01.png - shield_04.png)
        self.frames = ResourceManager.get_shield_frames()
        if not self.frames:
            raise ValueError("No shield frames loaded")

        self.index = 0
        self.image = self.frames[self.index]

        # ใช้ rect ปกติให้ศูนย์กลางตรงกับ Hero
        self.rect = self.image.get_rect(center=self.hero.rect.center)

        # ใช้ mask จากรูป เพื่อใช้กับ pygame.sprite.collide_mask
        self.mask = pygame.mask.from_surface(self.image)

        # เวลาเปลี่ยนเฟรมแอนิเมชัน
        self.frame_duration = 0.08
        self.time_since_last = 0.0

        # อายุการทำงาน (วินาที)
        self.lifetime = SHIELD_LIFETIME
        self.radius = max(self.rect.width, self.rect.height) // 2

        # เพิ่มจำนวน shield ใน Hero ตอนสร้าง
        if hasattr(self.hero, "weapon_counts") and "shield" in self.hero.weapon_counts:
            self.hero.weapon_counts["shield"] += 1

    # ------------------ โดนโจมตีหนึ่งครั้ง ------------------
    def take_hit(self, damage=1):
        self.hp -= damage
        if self.hp <= 0:
            # เกราะแตก หายไปจากเกม
            self.kill()

    def kill(self):
        """ลบ Shield ออกจากเกม และอัปเดตจำนวนใน Hero"""
        if hasattr(self.hero, "weapon_counts") and "shield" in self.hero.weapon_counts:
            if self.hero.weapon_counts["shield"] > 0:
                self.hero.weapon_counts["shield"] -= 1
        super().kill()

    # ------------------ อัปเดตเกราะทุกเฟรม ------------------
    def update(self, dt):
        # ถ้า Hero ตายแล้วไม่ต้องอยู่ ก็หายไปด้วย
        if not self.hero.alive():
            self.kill()
            return

        # เกราะต้องอยู่ที่ตำแหน่งเดียวกับ Hero ตลอด
        self.rect.center = self.hero.rect.center

        # อัปเดตแอนิเมชัน
        self.time_since_last += dt
        if self.time_since_last >= self.frame_duration:
            self.time_since_last = 0
            self.index = (self.index + 1) % len(self.frames)

            old_center = self.rect.center
            self.image = self.frames[self.index]
            self.rect = self.image.get_rect(center=old_center)

            # อัปเดต mask ด้วย (สำคัญถ้าเฟรมมีรูปร่างไม่เหมือนกัน)
            self.mask = pygame.mask.from_surface(self.image)

        # อายุการทำงานลดลง
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return
