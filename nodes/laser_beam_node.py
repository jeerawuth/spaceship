# nodes/laser_beam_node.py

import pygame
from settings.config import SCREEN_HEIGHT


class LaserBeamNode(pygame.sprite.Sprite):
    """
    ลำแสงเลเซอร์ยาวแบบ Beam
    - ยิงจาก Hero ขึ้นไปด้านบนจอ
    - ติดตามตำแหน่ง Hero ตลอดเวลา
    """

    def __init__(self, hero, width: int = 16):
        super().__init__()
        self.hero = hero

        # สร้าง Surface โปร่งแสงแทนลำแสง (ถ้าคุณมีภาพจริงค่อยเปลี่ยนทีหลังได้)
        height = SCREEN_HEIGHT  # ให้สูงครอบคลุมทั้งจอ
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        # สีฟ้าโปร่งแสง ๆ หน่อย
        self.image.fill((0, 255, 255, 160))

        self.rect = self.image.get_rect()
        self.update_position()

    def update_position(self):
        # ให้ midbottom ของเลเซอร์ติดกับ midtop ของ Hero
        self.rect.midbottom = self.hero.rect.midtop

    def update(self, dt: float):
        # ถ้า Hero ตาย → เลเซอร์หายตาม
        if not self.hero.alive():
            self.kill()
            return

        self.update_position()
