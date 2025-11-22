import pygame                 
import sys                    
import os                     # ใช้จัดการ path ของไฟล์ภาพ
import itertools              # ใช้สร้างตัววนซ้ำ (cycle) สำหรับแอนิเมชัน

pygame.init()                 # เริ่มต้นระบบ pygame

# -----------------------------
# ตั้งค่าหน้าจอเกม
# -----------------------------
SCREEN_WIDTH = 800            # ความกว้างหน้าจอ
SCREEN_HEIGHT = 600           # ความสูงหน้าจอ
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) 
pygame.display.set_caption("Spaceship Animation")                

WHITE = (255, 255, 255)      
clock = pygame.time.Clock()   # ใช้ควบคุม FPS 
FPS = 60                      # จำนวนเฟรมต่อวินาที

# คลาสสร้างยานอวกาศแบบ Sprite
class MySpaceShip(pygame.sprite.Sprite):
    def __init__(self, default_image):
        super().__init__()        # เรียก constructor ของคลาสแม่ (Sprite)

        # โหลดรูปภาพเริ่มต้นของยาน
        image_path = os.path.join("images", default_image)   
        self.image = pygame.image.load(image_path).convert_alpha()  
        self.default_image = self.image       # เก็บรูปเริ่มต้นไว้ เพื่อใช้ตอนหยุดแอนิเมชัน
        self.rect = self.image.get_rect()     # สร้างกรอบ (rect) เพื่อตำแหน่งของรูป

        # เวลาใช้กำหนดความเร็วการเปลี่ยนเฟรม
        self.frame_duration = 0.1             # แสดงแต่ละเฟรม 0.1 วินาที
        self.time_since_last_frame = 0        # เวลาสะสมจนกว่าจะครบเวลาเปลี่ยนเฟรม

        # โหลดเฟรมแอนิเมชันทั้งหมดลงในลิสต์
        self.animated_frames = [
            pygame.image.load("./images/ship_01.png"),       # เฟรม 1
            pygame.image.load("./images/ship_02.png"),       # เฟรม 2
            pygame.image.load("./images/ship_03.png"),       # เฟรม 3
            pygame.image.load("./images/ship_04.png"),       # เฟรม 4
        ]

        # สร้างตัววนซ้ำเพื่อให้เฟรมเล่นวนไปเรื่อย ๆ
        self.animation_iterator = itertools.cycle(self.animated_frames)

        # ตัวแปรสถานะว่าแอนิเมชันกำลังเล่นอยู่หรือไม่
        self.is_animating = False

        # เฟรมปัจจุบันที่จะแสดง
        self.current_frame = self.image

    # ฟังก์ชันเริ่มต้นแอนิเมชัน
    def start_animation(self):
        self.is_animating = True

    # ฟังก์ชันหยุดแอนิเมชัน และคืนสู่รูปเดิม
    def stop_animation(self):
        self.is_animating = False
        # แสดงเป็นรูป default เมื่อหยุด
        self.image = self.default_image   

    # ฟังก์ชันตั้งตำแหน่งยานในจอ
    def set_postion(self, x, y):
        # กำหนดตำแหน่งบนหน้าจอตามค่าที่ส่งเข้ามา
        self.rect.center = (x, y)        

    # ฟังก์ชันอัปเดตแอนิเมชันในทุกเฟรมของเกม
    def update(self, dt):
        if self.is_animating:            # ทำงานเฉพาะตอนเปิดใช้แอนิเมชัน
            self.time_since_last_frame += dt  # เพิ่มเวลาสะสมตามเวลาจริง

            # หากเวลาสะสมถึงเวลาที่กำหนดให้เปลี่ยนเฟรม
            if self.time_since_last_frame >= self.frame_duration:
                # เปลี่ยนไปเฟรมถัดไป
                self.current_frame = next(self.animation_iterator)  
                # อัพเดตรูปที่จะแสดง
                self.image = self.current_frame                     
                self.time_since_last_frame = 0        # รีเซ็ตตัวนับเวลา

# สร้างยานอวกาศ (Hero)
hero = MySpaceShip("ship_00.png")     # โหลดรูปเริ่มต้นของยาน
 
running = True                        # ตัวควบคุมลูปหลักของเกม
while running:
    dt = clock.tick(FPS) / 1000.0     # คำนวณ delta time (วินาที/เฟรม)

    for event in pygame.event.get():  # เช็ก event ทุกชนิด เช่น กดปิดหน้าต่าง
        if event.type == pygame.QUIT:    
            running = False             

        # ตรวจจับการกดปุ่มคีย์บอร์ด
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:   # กด Space เพื่อเริ่มแอนิเมชัน
                hero.start_animation()
            if event.key == pygame.K_ESCAPE:  # กด ESC เพื่อหยุดแอนิเมชัน
                hero.stop_animation()

    screen.fill(WHITE)                        # เคลียร์หน้าจอด้วยสีขาว
    hero.set_postion(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)  # ตั้งตำแหน่งยานตรงกลาง
    hero.update(dt)                           # อัปเดตแอนิเมชันตามเวลา
    screen.blit(hero.image, hero.rect)        # วาดรูปยานด้วยเฟรมปัจจุบัน
    pygame.display.flip()                     # อัปเดตหน้าจอ

pygame.quit()    
sys.exit()       
