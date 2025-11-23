# managers/background_manager.py

import random
import pygame
from settings.config import SCREEN_WIDTH, SCREEN_HEIGHT
from managers.resource_manager import ResourceManager


# ============================================================
# CONFIG: ปรับจูนสำหรับดาวเคราะห์
# ============================================================

# ชั้นพื้นหลังแบบ tile (ไกลสุด → ใกล้สุด)
BACKGROUND_LAYERS = [
    {
        "name": "far_stars",
        "image_key": "bg_01",   
        "scale": 0.05,          
        "speed": 8.0,           
    },
    {
        "name": "near_stars",
        "image_key": "bg_02",   
        "scale": 0.5,
        "speed": 14.0,
    },
]

# ดาว / ดาวเคราะห์ใกล้สายตา
PLANET_CONFIG = {
    "image_keys": ["bg_03", "bg_04", "bg_05", "bg_06"],
    "base_scale": 0.25,          
    "min_speed": 40.0,           
    "max_speed": 60.0,           
    "scale_range": (0.9, 1.2),   
}


# ============================================================
# ชั้นพื้นหลังแบบ tile
# ============================================================

class TiledLayer:
    """
    พื้นหลังที่ใช้ภาพ 1 รูป แล้วปูกระเบื้องทั้งจอ
    เลื่อนลงตามแกน Y ด้วยความเร็วที่กำหนด
    """

    def __init__(self, image: pygame.Surface, speed: float):
        self.image = image
        self.speed = speed          # px/s
        self.offset_y = 0.0

    def update(self, dt: float):
        self.offset_y += self.speed * dt
        h = self.image.get_height()
        if h > 0:
            self.offset_y %= h

    def draw(self, surface: pygame.Surface):
        img_w, img_h = self.image.get_size()
        if img_w <= 0 or img_h <= 0:
            return

        surf_w, surf_h = surface.get_size()

        start_y = -self.offset_y
        y = start_y
        while y < surf_h:
            x = 0
            while x < surf_w:
                surface.blit(self.image, (x, y))
                x += img_w
            y += img_h


# ============================================================
# สไปรต์พาราแล็กซ์เดี่ยว ๆ (ใช้สำหรับ planet)
# ============================================================

class ParallaxSprite(pygame.sprite.Sprite):
    """
    สำหรับวัตถุที่ลอยลง (ดาว / ดาวเคราะห์ ใกล้สายตา)
    - มีความเร็วของตัวเอง
    """

    def __init__(
        self,
        image: pygame.Surface,
        min_speed: float,
        max_speed: float,
        scale_range=(0.5, 1.0),
        start_random_inside: bool = False,
    ):
        super().__init__()

        self.screen_w = SCREEN_WIDTH
        self.screen_h = SCREEN_HEIGHT

        # random scale รอบสุดท้าย
        scale = random.uniform(*scale_range)
        w = max(1, int(image.get_width() * scale))
        h = max(1, int(image.get_height() * scale))
        self.original_image = image
        self.image = pygame.transform.smoothscale(image, (w, h))
        self.rect = self.image.get_rect()

        self.speed = random.uniform(min_speed, max_speed)

        self.reset(start_random_inside=start_random_inside)

    def reset(self, start_random_inside: bool = False):
        """
        กำหนดตำแหน่งเริ่มต้นใหม่ (เหนือจอ)
        """
        self.rect.centerx = random.randint(
            self.rect.width // 2,
            self.screen_w - self.rect.width // 2
        )

        if start_random_inside:
            self.rect.y = random.randint(-self.screen_h, self.screen_h)
        else:
            # กำหนดตำแหน่งเริ่มต้นเหนือจอ
            y_offset = random.randint(20, 150) 
            self.rect.bottom = -y_offset 

    def update(self, dt: float):
        self.rect.y += self.speed * dt
        # ลบ self.reset() ออก (โค้ดถูกต้องแล้ว)


# ============================================================
# BackgroundManager หลัก
# ============================================================

class BackgroundManager:

    def __init__(self):
        # ---------- สร้าง layer แบบ tile ----------
        self.layers: dict[str, TiledLayer] = {}

        for cfg in BACKGROUND_LAYERS:
            img = ResourceManager.get_image(cfg["image_key"])
            if img is None:
                continue

            scaled = self._scale(img, cfg.get("scale", 1.0))
            layer = TiledLayer(scaled, speed=cfg.get("speed", 10.0))
            self.layers[cfg["name"]] = layer

        # ---------- เตรียมภาพ planet ใกล้สายตา ----------
        self.planet_base_images: list[pygame.Surface] = []
        loaded_keys = [] 
        base_scale = PLANET_CONFIG.get("base_scale", 0.5)
        for key in PLANET_CONFIG.get("image_keys", []):
            img = ResourceManager.get_image(key)
            if img is not None:
                scaled_img = self._scale(img, base_scale)
                if scaled_img is not None:
                    self.planet_base_images.append(scaled_img)
                    loaded_keys.append(key) 
            
        num_loaded = len(self.planet_base_images)
        # ลบ Debug Prints ออกเพื่อให้โค้ดดูสะอาดขึ้น

        if num_loaded == 0:
            print("WARNING: No planet base images were loaded. Close planets will not appear.")

        self.planet_min_speed = PLANET_CONFIG.get("min_speed", 40.0) 
        self.planet_max_speed = PLANET_CONFIG.get("max_speed", 60.0) 
        self.planet_scale_range = PLANET_CONFIG.get("scale_range", (0.9, 1.2))

        self.close_planet: ParallaxSprite | None = None
        
        # ตัวแปรสำหรับวนซ้ำภาพ
        self.planet_index = 0

        self._spawn_close_planet()


    # ------------------------------------------------
    # Helper scale
    # ------------------------------------------------
    def _scale(self, img: pygame.Surface, factor: float) -> pygame.Surface | None:
        if img is None:
            return None
        w = max(1, int(img.get_width() * factor))
        h = max(1, int(img.get_height() * factor))
        return pygame.transform.smoothscale(img, (w, h))

    # ------------------------------------------------
    # API ให้ main เรียกใช้
    # ------------------------------------------------
    def update(self, dt: float):
        for layer in self.layers.values():
            layer.update(dt)

        self._update_close_planet(dt)

    def draw(self, screen: pygame.Surface):
        
        if self.close_planet is not None:
            screen.blit(self.close_planet.image, self.close_planet.rect)
            
        for cfg in BACKGROUND_LAYERS:
            name = cfg["name"]
            layer = self.layers.get(name)
            if layer is not None:
                layer.draw(screen)


    # ------------------------------------------------
    # ภายใน: Planet ใกล้สายตา 1 ดวง
    # ------------------------------------------------
    def _update_close_planet(self, dt: float):
        if not self.planet_base_images:
            return

        if self.close_planet is None:
            self._spawn_close_planet()
            return
        
        self.close_planet.update(dt)

        # ★★★ แก้ไข: ใช้ SCREEN_HEIGHT แทน self.screen_h ★★★
        if self.close_planet.rect.top > SCREEN_HEIGHT:
            self.close_planet = None 


    def _spawn_close_planet(self):
        if not self.planet_base_images:
            return
        
        # เลือกภาพตามดัชนีที่กำหนด
        img = self.planet_base_images[self.planet_index]
        
        # เลื่อนดัชนีไปภาพถัดไป และวนกลับไป 0 เมื่อถึงปลายลิสต์
        self.planet_index = (self.planet_index + 1) % len(self.planet_base_images)

        planet = ParallaxSprite(
            img,
            min_speed=self.planet_min_speed,
            max_speed=self.planet_max_speed,
            scale_range=self.planet_scale_range,
            start_random_inside=False, 
        )
        
        self.close_planet = planet