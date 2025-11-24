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

        # ความเร็วพื้นฐาน
        self.base_max_speed = 500       # px/s
        self.max_speed = self.base_max_speed

        # ---------- SPEED BUFF ----------
        self.speed_boost_time = 0.0     # เวลาที่เหลือของบัฟความเร็ว
        self.speed_multiplier = 1.0     # คูณความเร็วเคลื่อนที่
        self.is_speed_active = False    # ให้ SpeedFlameNode ใช้เช็ค
        self.speed_flame = None         # reference ไปยัง SpeedFlameNode ปัจจุบัน

        # ---------- WEAPON MODE (สำหรับ Laser ฯลฯ) ----------
        # "normal" หรือ "laser"
        self.weapon_mode = "normal"
        self.weapon_timer = 0.0         # เวลาที่เหลือของโหมดอาวุธพิเศษ

    # -------------------------------------------------
    # Helper: ปรับ max_speed ตาม speed_multiplier
    # -------------------------------------------------
    def _update_max_speed(self):
        self.max_speed = self.base_max_speed * self.speed_multiplier

    # -------------------------------------------------
    # เรียกตอนเก็บไอเท็ม SPEED
    # -------------------------------------------------
    def start_speed_boost(self, duration: float = 5.0, multiplier: float = 1.5):
        """
        เพิ่มความเร็วเคลื่อนที่ชั่วคราว + แสดงไอพ่นที่หางยาน
        """
        from nodes.speed_flame_node import SpeedFlameNode

        # ต่อเวลาเดิม ถ้ามี buff อยู่แล้ว ให้ใช้เวลายาวสุด
        self.speed_boost_time = max(self.speed_boost_time, duration)
        # ถ้ามี multiplier เดิมอยู่ อาจเอาค่าสูงสุด
        self.speed_multiplier = max(self.speed_multiplier, multiplier)
        self.is_speed_active = True
        self._update_max_speed()

        # ถ้ายังไม่มีไอพ่น หรืออันเดิมตายแล้ว → สร้างใหม่
        if self.speed_flame is None or not self.speed_flame.alive():
            self.speed_flame = SpeedFlameNode(self)

    # -------------------------------------------------
    # เรียกตอนเก็บไอเท็ม Laser
    # -------------------------------------------------
    def activate_laser(self, duration: float = 5.0):
        """
        เปิดโหมดอาวุธเลเซอร์ชั่วคราว (ใช้ร่วมกับ LaserBeamNode ใน main)
        """
        self.weapon_mode = "laser"
        self.weapon_timer = max(self.weapon_timer, duration)
    
    # -------------------------------------------------
    # เรียกตอนเก็บไอเท็ม Buckshot
    # -------------------------------------------------
    def activate_buckshot(self, duration: float = 5.0):
        """
        เปิดโหมดยิงกระสุนกระจาย (buckshot) ชั่วคราว
        ใช้ร่วมกับการยิง BulletNode ใน main.py
        """
        self.weapon_mode = "buckshot"
        # ถ้ามีเวลาโหมดพิเศษอยู่แล้ว ให้ต่อเวลาใช้ค่ามากสุด
        self.weapon_timer = max(self.weapon_timer, duration)


    # -------------------------------------------------
    # ฟิสิกส์พื้นฐาน
    # -------------------------------------------------
    def apply_drag(self, dt: float):
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
        if speed > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)

    # -------------------------------------------------
    # อัปเดต Hero ทุกเฟรม
    # -------------------------------------------------
    def update(self, dt: float, direction: pygame.math.Vector2):
        """
        direction: pygame.Vector2 จาก InputManager.get_move_direction()
        """

        # ---------- อัปเดตสถานะ SPEED BUFF ----------
        if self.speed_boost_time > 0:
            self.speed_boost_time -= dt
            if self.speed_boost_time <= 0:
                # หมดเวลา buff
                self.speed_boost_time = 0.0
                self.speed_multiplier = 1.0
                self.is_speed_active = False
                self._update_max_speed()

                # ปิดไอพ่น
                if self.speed_flame is not None and self.speed_flame.alive():
                    self.speed_flame.kill()
                self.speed_flame = None
            else:
                # ยังมี buff อยู่
                self.is_speed_active = True
                self._update_max_speed()
        else:
            # ไม่มี buff ความเร็ว
            self.speed_boost_time = 0.0
            self.is_speed_active = False
            self.speed_multiplier = 1.0
            self._update_max_speed()

        # ---------- อัปเดต WEAPON MODE TIMER ----------
        if self.weapon_mode in ("laser", "buckshot"):
            self.weapon_timer -= dt
            if self.weapon_timer <= 0:
                self.weapon_mode = "normal"
                self.weapon_timer = 0.0


        # ---------- ฟิสิกส์การเคลื่อนที่ ----------
        if direction.length_squared() > 0:
            self.velocity += direction * self.acceleration * dt
        else:
            self.apply_drag(dt)

        self.clamp_speed()
        self.pos += self.velocity * dt
        self.rect.center = self.pos

        # ---------- กันไม่ให้ออกนอกจอ ----------
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
