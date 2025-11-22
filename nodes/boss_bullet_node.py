# nodes/boss_bullet_node.py

import pygame
from managers.resource_manager import ResourceManager
from settings.config import SCREEN_WIDTH, SCREEN_HEIGHT


class BossBulletNode(pygame.sprite.Sprite):
    """
    กระสุนของ Boss:
    - ใช้เฟรมแยกจากกระสุน Hero (boss_bullet_xx.png)
    - เคลื่อนที่ตามทิศทางที่ล็อกไว้ตอนยิง
    - มีแอนิเมชันหมุน/วิบวับได้ ถ้ามีหลายเฟรม
    """

    def __init__(self, start_pos, direction: pygame.Vector2, speed: float = 250.0):
        super().__init__()

        frames = ResourceManager.get_boss_bullet_frames()
        if not frames:
            # fallback: ใช้สี่เหลี่ยมแดงเล็ก ๆ ถ้าไม่มี asset
            fallback = pygame.Surface((10, 20), pygame.SRCALPHA)
            fallback.fill((255, 80, 80))
            frames = [fallback]

        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=start_pos)

        # mask สำหรับ collide_mask (ถ้าต้องการใช้)
        self.mask = pygame.mask.from_surface(self.image)

        self.pos = pygame.Vector2(start_pos)

        self.direction = pygame.Vector2(direction)
        if self.direction.length_squared() > 0:
            self.direction = self.direction.normalize()
        else:
            self.direction = pygame.Vector2(0, 1)

        self.speed = speed

        # แอนิเมชัน
        self.frame_duration = 0.06  # วินาทีต่อเฟรม
        self.time_since_last = 0.0

    def _update_animation(self, dt: float):
        if len(self.frames) <= 1:
            return

        self.time_since_last += dt
        if self.time_since_last >= self.frame_duration:
            self.time_since_last = 0.0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            center = self.rect.center
            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect(center=center)
            self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt: float):
        # อัปเดตตำแหน่ง
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos

        # อัปเดตแอนิเมชัน
        self._update_animation(dt)

        # ถ้าหลุดจอให้ลบทิ้ง
        if (
            self.rect.right < 0
            or self.rect.left > SCREEN_WIDTH
            or self.rect.bottom < 0
            or self.rect.top > SCREEN_HEIGHT
        ):
            self.kill()
