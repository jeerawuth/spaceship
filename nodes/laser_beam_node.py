# nodes/laser_beam_node.py

import pygame
from settings.config import SCREEN_HEIGHT


class LaserBeamNode(pygame.sprite.Sprite):
    """
    ลำแสงเลเซอร์ยาวแบบ Beam
    - ผูกกับ Hero
    - เล่นเสียง laser แบบ loop ขณะอยู่ในโหมดเลเซอร์
    - หยุดเสียงอัตโนมัติเมื่อ:
        * Hero ตาย
        * Hero หลุดจากโหมดเลเซอร์ (weapon_mode != 'laser')
        * เลเซอร์ถูก kill() ด้วยเหตุผลอื่น
    """

    def __init__(self, hero, laser_sound: pygame.mixer.Sound, width: int = 16):
        super().__init__()
        self.hero = hero
        self.laser_sound = laser_sound
        self.channel: pygame.mixer.Channel | None = None

        # ทำความสูงเต็มจอ
        height = SCREEN_HEIGHT
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill((0, 255, 255, 160))

        self.rect = self.image.get_rect()
        self.update_position()

        # ★ เริ่มเล่นเสียงแบบ loop
        if self.laser_sound is not None:
            try:
                # -1 = loop ไม่จำกัดจนกว่าจะ stop()
                self.channel = self.laser_sound.play(-1)
            except Exception:
                self.channel = None

    def update_position(self):
        # ให้ midbottom ของเลเซอร์ติดกับ midtop ของ Hero
        self.rect.midbottom = self.hero.rect.midtop

    def update(self, dt: float):
        """
        เรียกทุกเฟรมจาก group.update(dt)
        """
        # 1) ถ้า Hero ตาย → ปิดเลเซอร์ + หยุดเสียง
        if not self.hero.alive():
            self.kill()
            return

        # 2) ถ้า Hero หลุดจากโหมดเลเซอร์ → ปิดเลเซอร์ + หยุดเสียง
        weapon_mode = getattr(self.hero, "weapon_mode", "normal")
        if weapon_mode != "laser":
            self.kill()
            return

        # 3) ปกติ → อัปเดตตำแหน่งให้ตาม Hero
        self.update_position()

    def kill(self):
        """
        เรียกตอนลบเลเซอร์ออกจากเกม
        - หยุดเสียงถ้ายังเล่นอยู่
        """
        if self.channel is not None:
            try:
                self.channel.stop()
            except Exception:
                pass
            self.channel = None

        super().kill()
