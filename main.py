# main.py

import pygame
import random

from settings.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GREY
from settings.game_constants import BULLET_COOLDOWN
from managers.resource_manager import ResourceManager
from managers.input_manager import InputManager
from managers.collision_manager import CollisionManager

from nodes.hero_node import HeroNode
from nodes.enemy_node import EnemyNode
from nodes.meteor_node import MeteorNode
from nodes.bullet_node import BulletNode
from nodes.item_node import ItemNode


# ถ้ายังไม่มีค่า spawn interval ใน game_constants ให้กำหนดใน main ไปก่อน
METEOR_SPAWN_INTERVAL = 1.0   # วินาทีต่อ 1 ลูก
ITEM_SPAWN_INTERVAL   = 5.0   # วินาทีต่อ 1 ไอเท็ม


def main():
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Spaceship (State-based Animation)")
    clock = pygame.time.Clock()

    # --------------------------------------------------
    # โหลด Resource ทั้งหมด
    # --------------------------------------------------
    ResourceManager.init()
    explosion_frames = ResourceManager.get_explosion_frames()
    explosion_sound = ResourceManager.get_sound("explosion")
    pickup_sound    = ResourceManager.get_sound("pickup")

    # --------------------------------------------------
    # กลุ่ม Sprite ต่าง ๆ
    # --------------------------------------------------
    heros         = pygame.sprite.Group()
    enemies       = pygame.sprite.Group()
    bullets       = pygame.sprite.Group()
    meteors       = pygame.sprite.Group()
    items         = pygame.sprite.Group()
    drones        = pygame.sprite.Group()
    shields       = pygame.sprite.Group()
    explosions    = pygame.sprite.Group()
    sound_effects = pygame.sprite.Group()

    # --------------------------------------------------
    # สร้าง Hero / Enemy เริ่มต้น
    # --------------------------------------------------
    hero = HeroNode()
    heros.add(hero)

    enemy = EnemyNode()
    enemies.add(enemy)

    # --------------------------------------------------
    # ตัวแปรเกม
    # --------------------------------------------------
    score = 0

    bullet_cooldown = 0.0
    meteor_spawn_timer = METEOR_SPAWN_INTERVAL
    item_spawn_timer   = ITEM_SPAWN_INTERVAL

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # --------------------------------------------------
        # จัดการ event ปิดหน้าต่าง
        # --------------------------------------------------
        running = InputManager.handle_quit_events()
        if not running:
            break

        # --------------------------------------------------
        # Input: ทิศทางการเคลื่อนที่ + ยิงกระสุน
        # --------------------------------------------------
        move_dir = InputManager.get_move_direction()  # Vector2

        keys = pygame.key.get_pressed()
        bullet_cooldown -= dt

        if keys[pygame.K_SPACE] and bullet_cooldown <= 0:
            # ยิงกระสุนจาก Hero
            if hero.alive():
                bullet_pos = hero.rect.midtop
                bullet = BulletNode(bullet_pos)
                bullets.add(bullet)

                bullet_cooldown = BULLET_COOLDOWN

                snd = ResourceManager.get_sound("bullet")
                if snd:
                    snd.play()

        # --------------------------------------------------
        # สุ่มเกิด Meteor / Item ตามเวลา
        # --------------------------------------------------
        meteor_spawn_timer -= dt
        if meteor_spawn_timer <= 0:
            meteor_spawn_timer = METEOR_SPAWN_INTERVAL
            meteors.add(MeteorNode())

        item_spawn_timer -= dt
        if item_spawn_timer <= 0:
            item_spawn_timer = ITEM_SPAWN_INTERVAL
            # สุ่มชนิดไอเท็ม: single / double / shield
            item_type = random.choice(["single", "double", "shield"])
            items.add(ItemNode(item_type))

        # --------------------------------------------------
        # ตรวจสอบการชนต่าง ๆ
        # --------------------------------------------------

        # 1) Bullet vs Enemy
        score = CollisionManager.handle_bullet_enemy_collisions(
            bullets, enemies,
            explosions, sound_effects,
            explosion_frames, explosion_sound,
            score
        )

        # 2) Hero vs Enemy
        CollisionManager.handle_hero_enemy_collisions(
            heros, enemies,
            explosions, sound_effects,
            explosion_frames, explosion_sound
        )

        # 3) Hero vs Meteor
        CollisionManager.handle_hero_meteor_collisions(
            heros, meteors,
            explosions, sound_effects,
            explosion_frames, explosion_sound
        )

        # 4) Bullet vs Meteor
        score = CollisionManager.handle_bullet_meteor_collisions(
            bullets, meteors,
            explosions, sound_effects,
            explosion_frames, explosion_sound,
            score
        )

        # 5) Hero เก็บ Item → สร้าง Drone / Shield
        CollisionManager.handle_hero_item_collisions(
            heros, items,
            drones, shields,
            sound_effects,
            pickup_sound
        )

        # 6) Shield vs Meteor
        CollisionManager.handle_shield_meteor_collisions(
            shields, meteors,
            explosions, sound_effects,
            explosion_frames, explosion_sound
        )

        # 7) Shield vs Enemy
        CollisionManager.handle_shield_enemy_collisions(
            shields, enemies,
            explosions, sound_effects,
            explosion_frames, explosion_sound
        )

        # --------------------------------------------------
        # อัปเดตทุกกลุ่ม
        # --------------------------------------------------
        # Hero รับ move_dir
        heros.update(dt, move_dir)

        # Drone ยิงอัตโนมัติ ต้องส่ง bullet_group ให้ด้วย
        drones.update(dt, bullets)

        bullets.update(dt)
        enemies.update(dt)
        meteors.update(dt)
        items.update(dt)
        shields.update(dt)
        explosions.update(dt)
        sound_effects.update(dt)

        # --------------------------------------------------
        # วาดทุกอย่าง
        # --------------------------------------------------
        screen.fill(GREY)

        # ลำดับการวาด (แล้วแต่ดีไซน์)
        meteors.draw(screen)
        enemies.draw(screen)
        items.draw(screen)
        heros.draw(screen)
        shields.draw(screen)
        drones.draw(screen)
        bullets.draw(screen)
        explosions.draw(screen)
        # sound_effects ไม่ต้อง draw (ไม่มีภาพ)

        # TODO: ถ้าต้องการแสดง score ให้เพิ่มส่วนวาดตัวหนังสือที่นี่

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
