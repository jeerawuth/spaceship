import pygame                 # นำเข้าไลบรารี pygame
import os                     # ใช้จัดการ path ของไฟล์ภาพ
import sys                    # ใช้สำหรับออกจากโปรแกรมแบบปลอดภัย

# สร้างคลาส PlayerSprite ซึ่งเป็น Sprite แบบง่าย
class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, image_path):
        # เรียก constructor ของคลาสแม่ (Sprite)
        super().__init__()                       
        # โหลดภาพและรักษาความโปร่งใส
        self.image = pygame.image.load(image_path).convert_alpha()  
        # สร้างกรอบ rect ของ sprite ใช้เพื่อกำหนดตำแหน่ง
        self.rect = self.image.get_rect()                      

    def set_position_center(self, SCREEN_WIDTH, SCREEN_HEIGHT):
        # ตั้งให้ sprite อยู่กลางหน้าจอ
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)  

# เริ่มต้นใช้งาน Pygame
pygame.init()                                                 # เริ่มระบบต่าง ๆ ของ pygame

SCREEN_WIDTH = 800            # ความกว้างของหน้าจอเกม
SCREEN_HEIGHT = 600           # ความสูงของหน้าจอเกม
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  
pygame.display.set_caption("Sprite Sheet Animation")         

WHITE = (255, 255, 255)                                       
clock = pygame.time.Clock()   # สร้างนาฬิกาสำหรับควบคุม FPS
FPS = 60                      # จำนวนเฟรมต่อวินาที (60 FPS ลื่นที่สุด)


# โหลดภาพ sprite และสร้างผู้เล่น
image_path = os.path.join("images", "hero.png")         # สร้าง path ไปยังไฟล์ hero.png
player = PlayerSprite(image_path)                       # สร้างออบเจ็กต์ PlayerSprite
player.set_position_center(SCREEN_WIDTH, SCREEN_HEIGHT) # กำหนดตำแหน่งให้อยู่กลางหน้าจอ

running = True                                                
while running:
    dt = clock.tick(FPS) / 1000.0                     

    for event in pygame.event.get():
        if event.type == pygame.QUIT:        # หากกดปิดหน้าต่าง ออกจากลูปเกม
            running = False                                  

    screen.fill(WHITE)                       # ลบภาพเฟรมเดิม และระบายพื้นหลังเป็นสีขาว
    screen.blit(player.image, player.rect)   # วาด sprite ลงบนหน้าจอที่ตำแหน่ง rect
    pygame.display.flip()                    # อัปเดตหน้าจอให้แสดงผลเฟรมล่าสุด

pygame.quit()                                # ปิดระบบ pygame
sys.exit()                                   # ออกจากโปรแกรม
