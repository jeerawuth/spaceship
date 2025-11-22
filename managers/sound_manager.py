# managers/sound_manager.py

import pygame
import time


class SoundManager:
    """
    ระบบจัดการเสียงแบบ SoundPool + Recycle Channel
    - จำกัดจำนวนเสียงชนิดเดียวกันที่เล่นพร้อมกัน (max_simultaneous)
    - เลือก channel ที่ว่าง หรือ recycle channel ที่ priority ต่ำสุด / เก่าสุด
    """

    _initialized = False
    _channels: list[pygame.mixer.Channel] = []
    _channel_priority: list[int] = []
    _channel_sound: list[pygame.mixer.Sound | None] = []
    _last_play_time: list[float] = []

    @classmethod
    def init(cls, num_channels: int = 32):
        """
        เรียกครั้งเดียวหลังจาก pygame.mixer.init()
        """
        if cls._initialized:
            return

        pygame.mixer.set_num_channels(num_channels)
        cls._channels = [pygame.mixer.Channel(i) for i in range(num_channels)]
        cls._channel_priority = [0] * num_channels
        cls._channel_sound = [None] * num_channels
        cls._last_play_time = [0.0] * num_channels
        cls._initialized = True

    @classmethod
    def play(
        cls,
        sound: pygame.mixer.Sound | None,
        volume: float = 1.0,
        max_simultaneous: int | None = None,
        priority: int = 0,
    ):
        """
        เล่นเสียงโดยใช้ SoundPool
        - sound: pygame.mixer.Sound
        - volume: 0.0 - 1.0
        - max_simultaneous: จำกัดจำนวน instance ของเสียงนี้ที่เล่นพร้อมกัน (None = ไม่จำกัด)
        - priority: ค่ามาก = สำคัญกว่า เมื่อจำเป็นต้องแย่ง channel
        """
        if sound is None:
            return

        if not cls._initialized:
            cls.init()

        # จำกัดจำนวนเสียงชนิดเดียวกันที่เล่นพร้อมกัน
        if max_simultaneous is not None:
            same_count = 0
            for ch in cls._channels:
                if ch.get_busy() and ch.get_sound() is sound:
                    same_count += 1
            if same_count >= max_simultaneous:
                return

        now = time.time()

        # หาช่องว่างก่อน
        selected_index = None
        for idx, ch in enumerate(cls._channels):
            if not ch.get_busy():
                selected_index = idx
                break

        # ถ้าไม่มีช่องว่าง → เลือกช่องที่ priority ต่ำสุด และเก่าสุด
        if selected_index is None:
            lowest_pri = min(cls._channel_priority)
            candidates = [i for i, p in enumerate(cls._channel_priority) if p == lowest_pri]
            selected_index = min(candidates, key=lambda i: cls._last_play_time[i])

        ch = cls._channels[selected_index]
        ch.set_volume(volume)
        ch.play(sound)

        cls._channel_priority[selected_index] = priority
        cls._channel_sound[selected_index] = sound
        cls._last_play_time[selected_index] = now
