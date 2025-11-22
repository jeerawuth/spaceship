# nodes/boss_node.py

import pygame
from settings.config import SCREEN_WIDTH
from managers.resource_manager import ResourceManager
from nodes.animation_node import AnimationNode
from nodes.boss_bullet_node import BossBulletNode


class BossNode(AnimationNode):
    """
    Boss ขนาดใหญ่:
    - เคลื่อนที่ซ้าย–ขวาด้านบนหน้าจอ
    - มี HP หลายหน่วย
    - ยิงกระสุน BossBullet ไล่ตำแหน่ง Hero
      (ซ้าย+ขวาพร้อมกัน หลายคู่ ตาม bullet_pairs)
    """

    def __init__(
        self,
        hero,
        boss_bullet_group,
        max_hp: int = 50,
        speed_x: float = 150.0,
        y: int = 60,
        fire_interval: float = 5.0,
        bullet_speed: float = 250.0,
        bullet_pairs: int = 1,
    ):
        """
        hero              : HeroNode (ใช้ตำแหน่งสำหรับเล็งกระสุน)
        boss_bullet_group : pygame.sprite.Group สำหรับเก็บกระสุน Boss
        max_hp            : HP สูงสุดของ Boss
        speed_x           : ความเร็วเคลื่อนที่แนวนอน
        y                 : ตำแหน่งแกน Y ของ Boss
        fire_interval     : เวลาหน่วงระหว่างยิงแต่ละชุด (วินาที)
        bullet_speed      : ความเร็วกระสุน Boss
        bullet_pairs      : จำนวน "คู่กระสุน" ซ้าย+ขวา ต่อ 1 ชุดยิง
                            1 = 2 กระสุน, 2 = 4 กระสุน, 3 = 6, ...
        """
        self.hero = hero
        self.boss_bullet_group = boss_bullet_group

        boss_frames = ResourceManager.get_boss_frames()
        if not boss_frames:
            raise ValueError("ResourceManager.get_boss_frames() must return at least 1 frame")

        states = {
            "default": {
                "frames": boss_frames,
                "frame_duration": 0.1,
                "loop": True,
                "kill_on_end": False,
            }
        }

        super().__init__(states, default_state="default", use_mask=True)

        self.max_hp = max_hp
        self.hp = max_hp

        self.rect = self.image.get_rect()
        self.rect.midtop = (SCREEN_WIDTH // 2, y)

        # การเคลื่อนที่แนวนอน
        self.speed_x = speed_x
        self.direction = 1  # 1 = ไปขวา, -1 = ไปซ้าย

        # ระบบยิง
        self.fire_interval = fire_interval
        self.fire_cooldown = fire_interval
        self.bullet_speed = bullet_speed

        # จำนวนคู่กระสุนต่อ 1 ชุดยิง
        self.bullet_pairs = max(1, int(bullet_pairs))

        # ขนาดกระสุน (ใช้กำหนดระยะห่างขั้นต่ำ)
        bullet_frames = ResourceManager.get_boss_bullet_frames()
        if bullet_frames:
            w, h = bullet_frames[0].get_size()
            # อย่างน้อย 2 เท่าของขนาดใหญ่สุด (width/height)
            self.min_bullet_distance = 2 * max(w, h)
        else:
            self.min_bullet_distance = 40  # fallback

    # ------------------ โดนดาเมจจากกระสุน ------------------
    def take_damage(self, amount: int = 1) -> bool:
        """
        ทำดาเมจกับ Boss
        :return: True ถ้า Boss ตาย, False ถ้ายังไม่ตาย
        """
        self.hp -= amount
        if self.hp <= 0:
            self.kill()
            return True
        return False

    # ------------------ ยิงกระสุนใส่ Hero ------------------
    def _fire_at_hero(self):
        if not self.hero.alive():
            return

        hero_pos = pygame.Vector2(self.hero.rect.center)

        # จุดยิงพื้นฐานจากด้านซ้ายและขวาของ Boss
        left_base = pygame.Vector2(self.rect.midleft)
        right_base = pygame.Vector2(self.rect.midright)

        # ✔ ลอจิกแบบเกมชั้นนำ:
        # - กระจายกระสุนเป็นเส้นในแนวตั้ง
        # - ระยะห่างระหว่างคู่กระสุน = min_bullet_distance (หรือมากกว่า)
        # - ไม่มีการสุ่ม / ไม่มีการข้าม → ทุกลูกเกิดครบแน่นอน
        if self.bullet_pairs == 1:
            offsets = [0.0]
        else:
            spacing = self.min_bullet_distance
            total_span = spacing * (self.bullet_pairs - 1)
            start = -total_span / 2
            offsets = [start + i * spacing for i in range(self.bullet_pairs)]

        for offset_y in offsets:
            # ซ้าย
            spawn_left = left_base + pygame.Vector2(0, offset_y)
            dir_left = hero_pos - spawn_left
            if dir_left.length_squared() > 0:
                bullet_left = BossBulletNode(spawn_left, dir_left, self.bullet_speed)
                self.boss_bullet_group.add(bullet_left)

            # ขวา
            spawn_right = right_base + pygame.Vector2(0, offset_y)
            dir_right = hero_pos - spawn_right
            if dir_right.length_squared() > 0:
                bullet_right = BossBulletNode(spawn_right, dir_right, self.bullet_speed)
                self.boss_bullet_group.add(bullet_right)

    # ------------------ อัปเดตทุกเฟรม ------------------
    def update(self, dt: float):
        # เคลื่อนที่ซ้าย-ขวาด้านบนจอ
        self.rect.x += self.direction * self.speed_x * dt

        # เด้งกลับเมื่อชนขอบจอ
        if self.rect.left < 0:
            self.rect.left = 0
            self.direction = 1
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.direction = -1

        # ระบบยิง (นับถอยหลัง)
        self.fire_cooldown -= dt
        if self.fire_cooldown <= 0:
            self.fire_cooldown = self.fire_interval
            self._fire_at_hero()

        # อัปเดตแอนิเมชัน
        self.update_animation(dt)
