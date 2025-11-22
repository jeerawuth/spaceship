# nodes/sound_node.py

import pygame

class SoundNode(pygame.sprite.Sprite):
    def __init__(self, sound, volume=1.0):
        super().__init__()

        if isinstance(sound, str):
            self.sound = pygame.mixer.Sound(sound)
        else:
            self.sound = sound

        self.sound.set_volume(volume)
        self.channel = self.sound.play()

        self.image = pygame.Surface((0, 0), pygame.SRCALPHA)
        self.rect = self.image.get_rect()

    def update(self, dt):
        if not self.channel.get_busy():
            self.kill()
