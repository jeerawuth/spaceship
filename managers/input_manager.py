# managers/input_manager.py

import pygame


class InputManager:
    @staticmethod
    def handle_quit_events():
        """คืนค่า False ถ้าผู้ใช้กดปิดหน้าต่าง, True ถ้ายังเล่นต่อ"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    @staticmethod
    def get_move_direction() -> pygame.math.Vector2:
        """
        อ่านปุ่มลูกศร / WASD แล้วคืนค่า Vector2 ทิศทางการเคลื่อนที่
        - ปกติใช้กับ Hero: hero.update(dt, move_dir)
        """
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        # ซ้าย-ขวา
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1

        # ขึ้น-ลง
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        vec = pygame.math.Vector2(dx, dy)
        if vec.length_squared() > 0:
            vec = vec.normalize()

        return vec

    @staticmethod
    def is_space_pressed() -> bool:
        """เช็คว่าปุ่ม Space ถูกกดอยู่หรือไม่"""
        keys = pygame.key.get_pressed()
        return keys[pygame.K_SPACE]
