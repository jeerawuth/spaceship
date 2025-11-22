# nodes/hero_node.py

import pygame
from settings.config import SCREEN_WIDTH, SCREEN_HEIGHT
from managers.resource_manager import ResourceManager
from nodes.animation_node import AnimationNode


class HeroNode(AnimationNode):
    def __init__(self):
        # โหลดเฟรมทั้งหมดของ Hero (อนาคตจะเพิ่ม state ได้)
        hero_frames = ResourceManager.get_hero_frames()
        states = {
            "default": {
                "frames": hero_frames,
                "frame_duration": 0.08,
                "loop": True,
                "kill_on_end": False,
            }
        }

        super().__init__(states, default_state="default", use_mask=True)

        # ใช้ Vector2 เก็บตำแหน่งจริง
        self.pos = pygame.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)
        self.rect.center = self.pos

        # ---------- ฟิสิกส์พื้นฐาน ----------
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = 1200        # px/s²
        self.drag = 900                 # px/s²
        self.max_speed = 500            # px/s

        # ---------- Buff / Weapon Mode / Counter ----------
        # speed buff
        self.speed_multiplier = 1.0
        self.speed_boost_time = 0.0

        # weapon mode: "normal" หรือ "laser"
        self.weapon_mode = "normal"
        self.weapon_timer = 0.0

        # นับจำนวนไอเท็มแต่ละชนิดที่เคยเก็บ
        self.weapon_counts = {
            "single": 0,
            "double": 0,
            "shield": 0,
            "speed":  0,
            "laser":  0,
        }

    # -------------------------------------------------
    # ใช้จาก CollisionManager ตอนเก็บไอเท็ม
    # -------------------------------------------------
    def start_speed_boost(self, duration: float, multiplier: float):
        """เริ่ม buff ความเร็วชั่วคราว"""
        self.speed_multiplier = max(multiplier, 0.1)
        # ถ้ามี buff เดิมอยู่แล้วให้ใช้เวลายาวสุด
        self.speed_boost_time = max(self.speed_boost_time, duration)

    def activate_laser(self, duration: float):
        """เปิดโหมดอาวุธเลเซอร์ชั่วคราว"""
        self.weapon_mode = "laser"
        self.weapon_timer = max(self.weapon_timer, duration)

    def add_item_count(self, item_type: str):
        """เพิ่มตัวนับจำนวนไอเท็มที่เก็บ"""
        if not isinstance(getattr(self, "weapon_counts", None), dict):
            self.weapon_counts = {}
        self.weapon_counts[item_type] = self.weapon_counts.get(item_type, 0) + 1

    # -------------------------------------------------
    # ฟิสิกส์พื้นฐาน
    # -------------------------------------------------
    def apply_drag(self, dt):
        speed = self.velocity.length()
        if speed == 0:
            return

        decel = self.drag * dt
        new_speed = max(0, speed - decel)

        if new_speed == 0:
            self.velocity.update(0, 0)
        else:
            self.velocity.scale_to_length(new_speed)

    def clamp_speed(self):
        speed = self.velocity.length()
        # ใช้ max_speed * speed_multiplier เพื่อรองรับ buff ความเร็ว
        max_speed = self.max_speed * self.speed_multiplier
        if speed > max_speed:
            self.velocity.scale_to_length(max_speed)

    def update(self, dt, direction):
        """
        direction: pygame.Vector2 จาก InputManager.get_move_direction()
        """

        # ---------- อัปเดต buff / weapon timer ----------
        if self.speed_boost_time > 0:
            self.speed_boost_time -= dt
            if self.speed_boost_time <= 0:
                self.speed_multiplier = 1.0

        if self.weapon_mode == "laser" and self.weapon_timer > 0:
            self.weapon_timer -= dt
            if self.weapon_timer <= 0:
                self.weapon_mode = "normal"

        # ---------- ฟิสิกส์ ----------
        if direction.length_squared() > 0:
            self.velocity += direction * self.acceleration * dt
        else:
            self.apply_drag(dt)

        self.clamp_speed()
        self.pos += self.velocity * dt
        self.rect.center = self.pos

        # กันไม่ให้ออกนอกจอ
        if self.rect.left < 0:
            self.rect.left = 0
            self.pos.x = self.rect.centerx
            self.velocity.x = 0

        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.pos.x = self.rect.centerx
            self.velocity.x = 0

        if self.rect.top < 0:
            self.rect.top = 0
            self.pos.y = self.rect.centery
            self.velocity.y = 0

        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.pos.y = self.rect.centery
            self.velocity.y = 0

        # ---- แอนิเมชัน ----
        self.update_animation(dt)
