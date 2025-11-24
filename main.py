# main.py

import pygame
from game import Game  # ไฟล์ใหม่ที่เราจะสร้างด้านล่าง

def main():
    pygame.init()
    pygame.mixer.init()

    game = Game()
    game.run()          # วน loop ผ่าน SceneManager

    pygame.quit()


if __name__ == "__main__":
    main()
