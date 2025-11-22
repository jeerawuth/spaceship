# managers/resource_manager.py

import pygame
import os

# -----------------------------------------
#  ค่า scale สำหรับ asset ต่าง ๆ
#  ปรับค่าตัวเลข 0.5 = 50% / 2.0 = 200%
# -----------------------------------------
HERO_SCALE      = 0.12
ENEMY_SCALE     = 0.20
METEOR_SCALE    = 0.08
BULLET_SCALE    = 0.10
ITEM_SCALE      = 0.10
EXPLOSION_SCALE = 0.20
DRONE_SCALE     = 0.10
SHIELD_SCALE    = 0.4


def scale_image(image: pygame.Surface, scale_factor: float) -> pygame.Surface:
    """Scale ภาพ 1 รูปตาม scale_factor"""
    if scale_factor == 1.0:
        return image

    w, h = image.get_size()
    new_size = (int(w * scale_factor), int(h * scale_factor))
    return pygame.transform.smoothscale(image, new_size)


def scale_frames(frames, scale_factor: float):
    """Scale เฟรมหลายภาพ (ลิสต์ของ Surface)"""
    if scale_factor == 1.0:
        return frames

    scaled = []
    for img in frames:
        scaled.append(scale_image(img, scale_factor))
    return scaled


class ResourceManager:
    """
    ตัวจัดการ resource ทั้งหมดของเกม:
    - รูปภาพ (images / frames)
    - เสียง (sounds)
    """

    _images = {}
    _sounds = {}
    _explosion_frames = None

    @classmethod
    def init(cls):
        """เรียกครั้งเดียวหลัง pygame.init() / pygame.mixer.init()"""
        base_dir = os.path.dirname(os.path.dirname(__file__))
        assets_dir = os.path.join(base_dir, "assets")

        # --------------------------------------------------
        # HERO: hero_01.png - hero_04.png
        # --------------------------------------------------
        hero_dir = os.path.join(assets_dir, "images", "hero")
        hero_frames = []

        for i in range(1, 5):
            filename = f"hero_0{i}.png"
            path = os.path.join(hero_dir, filename)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                hero_frames.append(img)

        hero_frames = scale_frames(hero_frames, HERO_SCALE)
        cls._images["hero_frames"] = hero_frames
        cls._images["hero"] = hero_frames[0] if hero_frames else None

        # --------------------------------------------------
        # ENEMY: enemy_01.png - enemy_04.png
        # --------------------------------------------------
        enemy_dir = os.path.join(assets_dir, "images", "enemy")
        enemy_frames = []

        for i in range(1, 5):
            filename = f"enemy_0{i}.png"
            path = os.path.join(enemy_dir, filename)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                enemy_frames.append(img)

        enemy_frames = scale_frames(enemy_frames, ENEMY_SCALE)
        cls._images["enemy_frames"] = enemy_frames
        cls._images["enemy"] = enemy_frames[0] if enemy_frames else None

        # --------------------------------------------------
        # METEOR: meteor_01.png - meteor_04.png
        # --------------------------------------------------
        meteor_dir = os.path.join(assets_dir, "images", "meteor")
        meteor_frames = []

        for i in range(1, 5):
            filename = f"meteor_0{i}.png"
            path = os.path.join(meteor_dir, filename)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                meteor_frames.append(img)

        meteor_frames = scale_frames(meteor_frames, METEOR_SCALE)
        cls._images["meteor_frames"] = meteor_frames

        # --------------------------------------------------
        # DRONE: drone_01.png - drone_04.png
        # --------------------------------------------------
        drone_dir = os.path.join(assets_dir, "images", "drone")
        drone_frames = []

        for i in range(1, 5):
            filename = f"drone_0{i}.png"
            path = os.path.join(drone_dir, filename)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                drone_frames.append(img)

        drone_frames = scale_frames(drone_frames, DRONE_SCALE)
        cls._images["drone_frames"] = drone_frames

        # --------------------------------------------------
        # BULLET: bullet_01.png (ภาพเดียว)
        # --------------------------------------------------
        bullet_path = os.path.join(assets_dir, "images", "bullet", "bullet_01.png")
        if os.path.exists(bullet_path):
            bullet_img = pygame.image.load(bullet_path).convert_alpha()
            cls._images["bullet"] = scale_image(bullet_img, BULLET_SCALE)
        else:
            cls._images["bullet"] = None

        # --------------------------------------------------
        # ITEM: ชนิดต่าง ๆ (single / double / shield)
        #   ชื่อไฟล์:
        #   item_single_01.png - item_single_04.png
        #   item_double_01.png - item_double_04.png
        #   item_shield_01.png - item_shield_04.png
        # --------------------------------------------------
        item_dir = os.path.join(assets_dir, "images", "item")
        cls._images["item_frames"] = {}

        item_patterns = {
            "single": "item_single_0{}.png",
            "double": "item_double_0{}.png",
            "shield": "item_shield_0{}.png",
        }

        for item_type, pattern in item_patterns.items():
            frames = []
            for i in range(1, 5):
                filename = pattern.format(i)
                path = os.path.join(item_dir, filename)
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    frames.append(img)

            frames = scale_frames(frames, ITEM_SCALE)
            cls._images["item_frames"][item_type] = frames

        # --------------------------------------------------
        # SHIELD: shield_01.png - shield_04.png (เกราะรอบ Hero)
        # --------------------------------------------------
        shield_dir = os.path.join(assets_dir, "images", "shield")
        shield_frames = []

        for i in range(1, 5):
            filename = f"shield_0{i}.png"
            path = os.path.join(shield_dir, filename)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                shield_frames.append(img)

        shield_frames = scale_frames(shield_frames, SHIELD_SCALE)
        cls._images["shield_frames"] = shield_frames

        # --------------------------------------------------
        # EXPLOSION: explosion_01.png - explosion_04.png
        # --------------------------------------------------
        explosion_dir = os.path.join(assets_dir, "images", "explosion")
        explosion_frames = []

        for i in range(1, 5):
            filename = f"explosion_0{i}.png"
            path = os.path.join(explosion_dir, filename)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                explosion_frames.append(img)

        explosion_frames = scale_frames(explosion_frames, EXPLOSION_SCALE)
        cls._explosion_frames = explosion_frames
        cls._images["explosion_frames"] = explosion_frames

        # --------------------------------------------------
        # โหลดเสียงต่าง ๆ
        # --------------------------------------------------
        sounds_dir = os.path.join(assets_dir, "sounds")

        def load_sound(name):
            path = os.path.join(sounds_dir, name)
            if os.path.exists(path):
                return pygame.mixer.Sound(path)
            return None

        cls._sounds["explosion"] = load_sound("explosion.wav")
        cls._sounds["hit"]       = load_sound("hit.wav")
        cls._sounds["bullet"]    = load_sound("bullet.wav")
        cls._sounds["pickup"]    = load_sound("pickup.wav")  # เผื่อใช้เก็บไอเท็ม

    # ------------------------------------------------------
    #  Getter ต่าง ๆ
    # ------------------------------------------------------
    @classmethod
    def get_image(cls, key):
        """ใช้กับภาพเดี่ยว เช่น 'hero', 'enemy', 'bullet'"""
        return cls._images.get(key)

    @classmethod
    def get_hero_frames(cls):
        return cls._images.get("hero_frames", [])

    @classmethod
    def get_enemy_frames(cls):
        return cls._images.get("enemy_frames", [])

    @classmethod
    def get_meteor_frames(cls):
        return cls._images.get("meteor_frames", [])

    @classmethod
    def get_drone_frames(cls):
        return cls._images.get("drone_frames", [])

    @classmethod
    def get_item_frames(cls, item_type):
        """
        item_type: "single", "double", "shield", ...
        """
        return cls._images.get("item_frames", {}).get(item_type, [])

    @classmethod
    def get_shield_frames(cls):
        return cls._images.get("shield_frames", [])

    @classmethod
    def get_explosion_frames(cls):
        return cls._explosion_frames

    @classmethod
    def get_sound(cls, key):
        """key เช่น 'explosion', 'hit', 'bullet', 'pickup'"""
        return cls._sounds.get(key)
