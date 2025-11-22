# nodes/sound_node.py

import pygame


class SoundNode(pygame.sprite.Sprite):
    """
    เล่นเสียงแบบ Sprite: ทำงานเองแล้ว kill ตัวเองเมื่อเสียงจบ
    ปลอดภัยแม้ sound.play() จะคืนค่า None
    """

    def __init__(self, sound: pygame.mixer.Sound):
        super().__init__()

        self.sound = sound
        self.channel = None

        # พยายามเล่นเสียง แต่ถ้าไม่สำเร็จ channel จะเป็น None
        try:
            self.channel = self.sound.play()
        except:
            self.channel = None

    def update(self, dt):
        """
        ถ้า channel ไม่มี หรือเล่นจบแล้ว ให้ kill ตัวเอง
        """

        # ป้องกัน error: channel ไม่มี
        if self.channel is None:
            self.kill()
            return

        # ถ้า channel ไม่มีเสียงแล้ว → kill ตัวเอง
        try:
            if not self.channel.get_busy():
                self.kill()
        except:
            # ถ้า channel เสียหรือใช้งานไม่ได้ → ลบตัวเองทันที
            self.kill()
