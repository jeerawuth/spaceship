import pygame
import sys
import random

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Random Meteors")

BLACK = (0, 0, 0)
GREY = (199, 199, 199)

clock = pygame.time.Clock()
FPS = 60

# คลาสสร้าง Sprite อุกาบาต
class Meteor(pygame.sprite.Sprite):
    def __init__(self, x, y, size, speed):
        super().__init__()

        # สร้าง Surface แบบโปร่งใสสำหรับวาดอุกาบาต
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        # วาดวงกลมเป็นอุกาบาต
        pygame.draw.circle(self.image, GREY, (size // 2, size // 2), size // 2)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)  # ตั้งตำแหน่งจากจุดกึ่งกลาง

        self.speed = speed  # ความเร็วตกลงด้านล่าง (px ต่อเฟรม)

    def update(self):
        # เลื่อนลงล่าง
        self.rect.y += self.speed

        # ถ้าเลยจอล่าง ให้ลบตัวเองออกจากทุกกลุ่ม
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# ฟังก์ชันสร้างอุกาบาตแบบสุ่ม (ไม่ซ้อนกัน)
def create_meteors(num_meteors):
    meteors = pygame.sprite.Group()
    meteor_list = []        # เก็บ rect ทั้งหมดไว้ตรวจสอบการซ้อนกัน
    max_attempts = 3000     # กันไว้เผื่อวนซ้ำไม่จบ
    attempts = 0

    while len(meteor_list) < num_meteors and attempts < max_attempts:
        attempts += 1
        # สุ่มขนาด (กว้าง = สูง = size)
        size = random.randint(30, 80)
        # สุ่มตำแหน่งจุดกึ่งกลาง (x, y) ต้องไม่ให้เลยขอบด้านซ้าย/ขวา/บน
        x = random.randint(size // 2, SCREEN_WIDTH - size // 2)
        y = random.randint(size // 2, SCREEN_HEIGHT // 3)  # บริเวณด้านบนของจอ
        # สร้าง rect ชั่วคราวเพื่อตรวจสอบการซ้อนกัน
        temp_rect = pygame.Rect(0, 0, size, size)
        temp_rect.center = (x, y)
        # ตรวจว่าไม่ซ้อนกับอุกาบาตตัวอื่น
        overlapped = False
        for item in meteor_list:
            if temp_rect.colliderect(item.rect):
                overlapped = True
                break

        if overlapped:
            continue  # ออกจากลูปเพื่อลองสุ่มใหม่

        # สุ่มความเร็วของอุกาบาต
        speed = random.randint(2, 5)

        # ถ้าไม่ซ้อนกัน ให้สร้าง Meteor จริง ๆ
        meteor = Meteor(x, y, size, speed)
        meteors.add(meteor)
        meteor_list.append(meteor)

    return meteors



class Hero(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

class Laser(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

hero = Hero()                       # สร้างฮีโร่


lasers = pygame.sprite.Group()      # สร้างกลุ่มลำแสงเลเซอร์
enemies = pygame.sprite.Group()     # สร้างกลุ่มศัตรู

for _ in range(0, 5):               # วนลูป 5 รอบ
    laser = Laser()                 # สร้างลำแสงเลเซอร์
    lasers.add(laser)               # เพิ่มเลเซอร์ลงในกลุ่ม

for _ in range(0, 10):              # วนลูป 10 รอบ
    enemy = Enemy()                 # สร้างศัตรู
    enemies.add(enemy)              # เพิ่มศัตรูลงในกลุ่ม

score = 0

hits = {
    "laser_1": [enemy_1, enemy_2],
    "laser_2": [enemy_4, enemy_8, enemy_9],
}

running = True
while running:
    dt = clock.tick(FPS) / 1000.0  

    # เมื่อแสงเลเซอร์โดนกับศัตรูใด ๆ
    hits = pygame.sprite.groupcollide(lasers, enemies, False, True)
    
    for laser, enemy_list in hits.items():
        for enemy in enemy_list:
            score += 1          # ยิงศัตรูได้ +1 คะแนน

    # อัปเดตหน้าจอ
    pygame.display.flip()


# สร้างกลุ่มอุกาบาต 10 ก้อน ใส่ไว้ในกลุ่ม meteors
meteors = create_meteors(10)

running = True
while running:
    dt = clock.tick(FPS) / 1000.0  



    hits = pygame.sprite.spritecollide(hero, bullets, False)

    for enemy in hits:
        print("ชนศัตรู!")


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # อัปเดตอุกาบาตทั้งหมดในกลุ่ม
    meteors.update()
    # วาดรูป
    screen.fill(BLACK)      # วาดพื้นหลัง
    meteors.draw(screen)    # วาดอุกาบาตทั้งหมด
    # อัปเดตหน้าจอ
    pygame.display.flip()

pygame.quit()
sys.exit()
