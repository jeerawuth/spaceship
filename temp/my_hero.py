import pygame
import os
import sys

pygame.init()

# ตั้งค่าหน้าจอเกม
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Frames Animation with Sprite Class")

WHITE = (255, 255, 255)
clock = pygame.time.Clock()
FPS = 60


# ---------------------------------------------------------
#  คลาส MyHero: Sprite พร้อมแอนิเมชันจาก Sprite Sheet
# ---------------------------------------------------------
class MyHero(pygame.sprite.Sprite):
    def __init__(self, image_path, columns, rows, scale=1.0):
        super().__init__()

        # โหลด sprite sheet
        sprite_sheet = pygame.image.load(image_path).convert_alpha()

        # ปรับสเกลของ sprite sheet
        sheet_width, sheet_height = sprite_sheet.get_size()
        sprite_sheet = pygame.transform.scale(
            sprite_sheet,
            (int(sheet_width * scale), int(sheet_height * scale))
        )

        self.sheet = sprite_sheet
        self.columns = columns
        self.rows = rows
        self.total_frames = columns * rows

        # คำนวณขนาดของเฟรม
        self.sheet_width, self.sheet_height = self.sheet.get_size()
        self.frame_width = self.sheet_width // self.columns
        self.frame_height = self.sheet_height // self.rows

        # เก็บเฟรมทั้งหมดลง list
        self.frames = []
        self.load_frames()

        # เฟรมปัจจุบัน
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()

        # ตัวแปรเวลาแอนิเมชัน
        self.frame_duration = 0.05     # วินาทีต่อเฟรม
        self.time_since_last_frame = 0

        # ความเร็ว hero
        self.velocity = 300            # pixel/s

    # -----------------------------------------------------
    # ตัดภาพออกเป็นเฟรม และเก็บใส่ list
    # -----------------------------------------------------
    def load_frames(self):
        for row in range(self.rows):
            for col in range(self.columns):
                frame_surface = self.sheet.subsurface(
                    pygame.Rect(
                        col * self.frame_width,
                        row * self.frame_height,
                        self.frame_width,
                        self.frame_height
                    )
                )
                self.frames.append(frame_surface)

    # -----------------------------------------------------
    # ตั้งตำแหน่งเริ่มต้น
    # -----------------------------------------------------
    def set_position(self, x, y):
        self.rect.topleft = (x, y)

    # -----------------------------------------------------
    # อัปเดตการเคลื่อนที่ + อัปเดตแอนิเมชัน
    # -----------------------------------------------------
    def update(self, dt):
        # ----- อัปเดตตำแหน่งแกน X (ให้วิ่งไปทางขวา) -----
        self.rect.x += int(self.velocity * dt)
        if self.rect.x > SCREEN_WIDTH:
            self.rect.x = -self.frame_width + 100

        # ----- อัปเดตแอนิเมชัน -----
        self.time_since_last_frame += dt

        if self.time_since_last_frame >= self.frame_duration:
            self.frame_index = (self.frame_index + 1) % self.total_frames
            self.image = self.frames[self.frame_index]
            self.time_since_last_frame = 0


# ---------------------------------------------------------
# สร้าง Hero จากคลาส MyHero
# ---------------------------------------------------------
image_path = os.path.join("images", "run_4x4.png")
hero = MyHero(image_path, columns=4, rows=4, scale=0.5)

# ตั้งตำแหน่งเริ่มต้น
hero.set_position(0, SCREEN_HEIGHT - hero.frame_height - 50)

# สร้าง sprite group
all_sprites = pygame.sprite.Group(hero)


# ---------------------------------------------------------
# Game Loop
# ---------------------------------------------------------
running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # อัปเดต sprite ทั้งหมด
    all_sprites.update(dt)

    # วาดภาพ
    screen.fill(WHITE)
    all_sprites.draw(screen)
    pygame.display.flip()


pygame.quit()
sys.exit()
