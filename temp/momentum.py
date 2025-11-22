import pygame
import sys

# เริ่มต้น Pygame
pygame.init()

# กำหนดหน้าจอ
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Balls Collision")

# อัตราการแสดงผล
FPS = 60

# กำหนดสี
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# กำหนดค่าต่างๆ สำหรับวงกลม โดยใช้ Vector2 สำหรับตำแหน่งและความเร็ว
circle1 = { 
    "radius": 25, 
    "position": pygame.Vector2(50, 50), 
    "color": RED, 
    "velocity": pygame.Vector2(200, 200), 
    "mass": 1 
}
circle2 = { 
    "radius": 50, 
    "position": pygame.Vector2(400, 240), 
    "color": BLUE, 
    "velocity": pygame.Vector2(0, 0), 
    "mass": 4 
}

# ฟังก์ชันตรวจสอบการชนกับขอบจอทั้ง 4 ด้าน
def check_boundary_collision(circle, SCREEN_WIDTH, SCREEN_HEIGHT):
    # ตรวจสอบการชนกับขอบซ้ายและขอบขวา
    if circle["position"].x - circle["radius"] <= 0 or circle["position"].x + circle["radius"] >= SCREEN_WIDTH:
        circle["velocity"].x *= -1  # เปลี่ยนทิศทางแกน x

    # ตรวจสอบการชนกับขอบบนและขอบล่าง
    if circle["position"].y - circle["radius"] <= 0 or circle["position"].y + circle["radius"] >= SCREEN_HEIGHT:
        circle["velocity"].y *= -1  # เปลี่ยนทิศทางแกน y

# ฟังก์ชันตรวจสอบการชนกันระหว่างลูกบอลสองลูก
def check_collision(circle_a, circle_b):
    # ตรวจสอบว่าชนกัน โดยระยะห่างต้องน้อยกว่ารัศมีของทั้งสองวงกลมมาบวกกัน
    if circle_a["position"].distance_to(circle_b["position"]) <= circle_a["radius"] + circle_b["radius"]:
        # คำนวณการชน
        delta = circle_a["position"] - circle_b["position"]
        direction = delta.normalize()

        # ความเร็วของวงกลมในทิศทางที่วงกลมเคลื่อนที่
        v1 = circle_a["velocity"].dot(direction)
        v2 = circle_b["velocity"].dot(direction)

        # คำนวณความเร็วหลังชนตามกฎการอนุรักษ์โมเมนตัม
        v1_after = (v1 * (circle_a["mass"] - circle_b["mass"]) + 2 * circle_b["mass"] * v2) / (circle_a["mass"] + circle_b["mass"])
        v2_after = (v2 * (circle_b["mass"] - circle_a["mass"]) + 2 * circle_a["mass"] * v1) / (circle_a["mass"] + circle_b["mass"])

        # ปรับความเร็วใหม่หลังการชน
        circle_a["velocity"] += (v1_after - v1) * direction
        circle_b["velocity"] += (v2_after - v2) * direction

# Loop หลักของเกม
clock = pygame.time.Clock()
running = True
while running:

    # เติมสีพื้นหลังเป็นสีขาว
    screen.fill(WHITE)

    # คำนวณเวลาของแต่ละเฟรม (delta time)
    dt = clock.tick(FPS) / 1000.0

    # อัปเดตตำแหน่งของวงกลมโดยใช้ delta time
    circle1["position"] += circle1["velocity"] * dt
    circle2["position"] += circle2["velocity"] * dt

    # ตรวจสอบการชนกันระหว่างลูกบอลทั้งสองลูก
    check_collision(circle1, circle2)

    # ตรวจสอบการชนกันระหว่างลูกบอลกับขอบหน้าต่าง
    check_boundary_collision(circle1, SCREEN_WIDTH, SCREEN_HEIGHT)
    check_boundary_collision(circle2, SCREEN_WIDTH, SCREEN_HEIGHT)

    # วาดวงกลม
    pygame.draw.circle(
        screen, 
        circle1["color"], 
        (int(circle1["position"].x), int(circle1["position"].y)), 
        circle1["radius"]
    )
    pygame.draw.circle(
        screen, 
        circle2["color"], 
        (int(circle2["position"].x), int(circle2["position"].y)),
        circle2["radius"]
    )

    # อัปเดตหน้าจอ
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
sys.exit()
