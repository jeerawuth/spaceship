# managers/input_manager.py

# import pygame

# class InputManager:
#     @staticmethod
#     def handle_quit_events():
#         """คืนค่า False ถ้าผู้ใช้กดปิดหน้าต่าง"""
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 return False
#         return True

#     @staticmethod
#     def is_space_pressed():
#         keys = pygame.key.get_pressed()
#         return keys[pygame.K_SPACE]

#     @staticmethod
#     def get_horizontal_axis():
#         """ใช้สำหรับขยับ hero ซ้ายขวา"""
#         keys = pygame.key.get_pressed()
#         axis = 0
#         if keys[pygame.K_LEFT] or keys[pygame.K_a]:
#             axis -= 1
#         if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
#             axis += 1
#         return axis



# managers/input_manager.py

import pygame

class InputManager:
    @staticmethod
    def handle_quit_events():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    @staticmethod
    def get_move_direction():
        """คืนค่าทิศทางเป็น Vector2 เช่น (-1, 0), (0, 1), (1, -1)"""
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(0, 0)

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            direction.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction.x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            direction.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            direction.y += 1

        # ทำให้การกดทแยงไม่เร็วกว่า 1 ทิศทาง
        if direction.length_squared() > 0:
            direction = direction.normalize()

        return direction
