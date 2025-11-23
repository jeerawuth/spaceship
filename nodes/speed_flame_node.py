# nodes/speed_flame_node.py

import pygame

from managers.resource_manager import ResourceManager
from settings.game_constants import SPEED_FLAME_LIFETIME

class SpeedFlameNode(pygame.sprite.Sprite):
    """
    เอฟเฟกต์ไอพ่นที่หางของ Hero
    - ไม่มี collision ใช้แค่แสดงผล
    - ติดตาม Hero ตลอดเวลา
    - หายไปเมื่อถูก kill() หรือ Hero ไม่อยู่ในโหมด speed
    """


    def __init__(self, hero):
        super().__init__()
        self.hero = hero

        # โหลดเฟรมเกราะจาก ResourceManager (shield_01.png - shield_04.png)
        self.frames = ResourceManager.get_speed_frames()
        
        if not self.frames:
            raise ValueError("No speed frames loaded")

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
        self.lifetime = SPEED_FLAME_LIFETIME

    def update_position(self):
        """
        ให้ไอพ่นไปอยู่ด้านท้ายของยาน
        สมมติยานหันหัวขึ้น: tail = midbottom ของ Hero
        เราจะให้หัวไอพ่นชิดท้ายยาน
        """
        # ให้จุดบนสุดของไอพ่นติดกับด้านล่างของ Hero ขยับขึ้นเล็กน้อย
        self.rect.midtop = self.hero.rect.midbottom

        # ถ้าอยากให้ไอพ่นเลื่อนขึ้นไปอีกหน่อยก็เพิ่ม offset ได้ เช่น:
        self.rect.y -= 30

    def update(self, dt):
        # ถ้า Hero ตายแล้วไม่ต้องอยู่ ก็หายไปด้วย
        if not self.hero.alive():
            self.kill()
            return

        # ไอพ่นต้องอยู่ที่ตำแหน่งเดียวกับ Hero ตลอด
        self.rect.midtop = self.hero.rect.midbottom
        self.rect.y -= 30

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

    def kill(self):
        super().kill()
