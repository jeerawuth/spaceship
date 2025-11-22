import pygame
import sys
import os

pygame.init()

SCREEN_WIDTH = 680
SCREEN_HEIGHT = 400

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Play Sound")

WHITE = (255, 255, 255)   # สีพื้นหลัง
clock = pygame.time.Clock()
FPS = 60

path = os.path.join("sounds", "beep.wav")   # พาธของไฟล์เสียง
beep_sound = pygame.mixer.Sound(path)       # โหลดเสียงบี๊บ

running = True
while running:
    dt = clock.tick(FPS) / 1000.0  # วินาที

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            # เมื่อผู้ใช้กดปุ่ม <Space>
            if event.key == pygame.K_SPACE:
                beep_sound.play()   # เล่นเสียงบี๊บ

    # วาดหน้าจอ
    screen.fill(WHITE)
    pygame.display.flip()

pygame.quit()
sys.exit()
