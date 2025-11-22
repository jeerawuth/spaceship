import pygame

class SoundNode(pygame.sprite.Sprite):
    def __init__(self, sound_path, volume=1.0):
        super().__init__()

        # โหลดเสียง
        self.sound = pygame.mixer.Sound(sound_path)
        self.sound.set_volume(volume)      # ตั้งค่าความดัง (0.0 - 1.0)

        # เริ่มเล่นเสียงทันที
        self.channel = self.sound.play()

        # สร้าง image/rect เปล่า เพราะ SoundNode ไม่มีกราฟิก
        # แต่จำเป็นต่อระบบ Sprite
        self.image = pygame.Surface((0, 0))
        self.rect = self.image.get_rect()

    def update(self, dt):
        """
        ตรวจว่าเสียงเล่นจบหรือยัง
        ถ้าเล่นจบแล้วให้ kill() ตัวเองออกจากทุกกลุ่ม
        """
        if not self.channel.get_busy():
            self.kill()    # ลบตัวเองเมื่อเสียงเล่นเสร็จ
