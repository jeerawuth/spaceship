# nodes/bullet_node.py

import pygame
from settings.game_constants import BULLET_SPEED
from managers.resource_manager import ResourceManager

class BulletNode(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = ResourceManager.get_image("bullet")
        self.rect = self.image.get_rect(center=pos)
        self.speed = BULLET_SPEED

    def update(self, dt):
        self.rect.y -= self.speed * dt
        if self.rect.bottom < 0:
            self.kill()
