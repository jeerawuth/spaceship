# main.py

import pygame

from settings.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GREY
from settings.game_constants import BULLET_COOLDOWN
from managers.resource_manager import ResourceManager
from managers.input_manager import InputManager
from managers.collision_manager import CollisionManager
from managers.sound_manager import SoundManager
from settings.spawn_config import STAGE_SPAWN_CONFIGS
from managers.spawn_manager import SpawnManager

from nodes.hero_node import HeroNode
from nodes.enemy_node import EnemyNode
from nodes.meteor_node import MeteorNode
from nodes.bullet_node import BulletNode
from nodes.item_node import ItemNode
from nodes.boss_node import BossNode


def main():
    pygame.init()
    pygame.mixer.init()

    # 🔊 ตั้งค่า SoundPool
    SoundManager.init(num_channels=32)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Spaceship (State-based Animation)")
    clock = pygame.time.Clock()

    # --------------------------------------------------
    # โหลด Resource ทั้งหมด
    # --------------------------------------------------
    ResourceManager.init()
    explosion_frames = ResourceManager.get_explosion_frames()
    explosion_sound = ResourceManager.get_sound("explosion")
    pickup_sound = ResourceManager.get_sound("pickup")

    # --------------------------------------------------
    # ฟอนต์สำหรับ HUD และ Game Over
    # --------------------------------------------------
    font_small = pygame.font.Font(None, 28)
    font_big = pygame.font.Font(None, 64)

    # --------------------------------------------------
    # กลุ่ม Sprite ต่าง ๆ
    # --------------------------------------------------
    heros = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bosses = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    meteors = pygame.sprite.Group()
    items = pygame.sprite.Group()
    drones = pygame.sprite.Group()
    shields = pygame.sprite.Group()
    explosions = pygame.sprite.Group()

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

    # ด่านและเวลา
    current_stage = 1
    STAGE_DURATION = 30.0  # วินาทีต่อด่าน
    stage_timer = 0.0
    total_time = 0.0
    max_stage = len(STAGE_SPAWN_CONFIGS)  # ด่านสุดท้าย = Boss stage

    GAME_STATE_PLAYING = "PLAYING"
    GAME_STATE_GAME_OVER = "GAME_OVER"
    game_state = GAME_STATE_PLAYING

    # --------------------------------------------------
    # สร้าง SpawnManager สำหรับด่าน 1
    # --------------------------------------------------
    spawn_manager = SpawnManager(STAGE_SPAWN_CONFIGS, initial_stage=current_stage)

    # ถ้าด่านแรกเป็นด่านสุดท้ายด้วย → spawn Boss ทันที
    if current_stage == max_stage:
        bosses.add(BossNode(max_hp=50))

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # --------------------------------------------------
        # จัดการ event ปิดหน้าต่าง
        # --------------------------------------------------
        running = InputManager.handle_quit_events()
        if not running:
            break

        keys = pygame.key.get_pressed()

        # --------------------------------------------------
        # ปุ่มตอน Game Over: R = restart, Q = quit
        # --------------------------------------------------
        if game_state == GAME_STATE_GAME_OVER:
            if keys[pygame.K_r]:
                return main()
            if keys[pygame.K_q]:
                running = False

        # --------------------------------------------------
        # อัปเดตเวลา + เปลี่ยนด่าน
        # --------------------------------------------------
        if game_state == GAME_STATE_PLAYING:
            stage_timer += dt
            total_time += dt

            # เปลี่ยนด่านทุก 30 วินาที จนถึงด่านสุดท้าย
            if stage_timer >= STAGE_DURATION and current_stage < max_stage:
                stage_timer = 0.0
                current_stage += 1
                spawn_manager.set_stage(current_stage)

                # ถ้าเข้าด่านสุดท้าย → spawn Boss
                if current_stage == max_stage and len(bosses) == 0:
                    bosses.add(BossNode(max_hp=50))

        # --------------------------------------------------
        # Input: การเคลื่อนที่ + ยิงกระสุน
        # --------------------------------------------------
        if game_state == GAME_STATE_PLAYING:
            move_dir = InputManager.get_move_direction()

            bullet_cooldown -= dt
            if keys[pygame.K_SPACE] and bullet_cooldown <= 0:
                if hero.alive():
                    bullet_pos = hero.rect.midtop
                    bullet = BulletNode(bullet_pos)
                    bullets.add(bullet)

                    bullet_cooldown = BULLET_COOLDOWN

                    bullet_sound = ResourceManager.get_sound("bullet")
                    SoundManager.play(
                        bullet_sound,
                        volume=0.8,
                        max_simultaneous=8,
                        priority=7,
                    )
        else:
            move_dir = pygame.math.Vector2(0, 0)

        # --------------------------------------------------
        # Spawn Meteor / Item
        # --------------------------------------------------
        if game_state == GAME_STATE_PLAYING:
            spawn_manager.update(dt, meteors, items)

        # --------------------------------------------------
        # Collision ต่าง ๆ
        # --------------------------------------------------
        if game_state == GAME_STATE_PLAYING:
            # Bullet vs Enemy
            score = CollisionManager.handle_bullet_enemy_collisions(
                bullets, enemies,
                explosions,
                explosion_frames, explosion_sound,
                score
            )

            # Hero vs Enemy
            CollisionManager.handle_hero_enemy_collisions(
                heros, enemies,
                explosions,
                explosion_frames, explosion_sound
            )

            # Hero vs Meteor
            CollisionManager.handle_hero_meteor_collisions(
                heros, meteors,
                explosions,
                explosion_frames, explosion_sound
            )

            # Bullet vs Meteor
            score = CollisionManager.handle_bullet_meteor_collisions(
                bullets, meteors,
                explosions,
                explosion_frames, explosion_sound,
                score
            )

            # Hero เก็บ Item
            CollisionManager.handle_hero_item_collisions(
                heros, items,
                drones, shields,
                pickup_sound
            )

            # Shield vs Meteor
            CollisionManager.handle_shield_meteor_collisions(
                shields, meteors,
                explosions,
                explosion_frames, explosion_sound
            )

            # Shield vs Enemy
            CollisionManager.handle_shield_enemy_collisions(
                shields, enemies,
                explosions,
                explosion_frames, explosion_sound
            )

            # -------- Collision ที่เกี่ยวกับ Boss --------
            score = CollisionManager.handle_bullet_boss_collisions(
                bullets, bosses,
                explosions,
                explosion_frames, explosion_sound,
                score
            )

            CollisionManager.handle_hero_boss_collisions(
                heros, bosses,
                explosions,
                explosion_frames, explosion_sound
            )

            score = CollisionManager.handle_shield_boss_collisions(
                shields, bosses,
                explosions,
                explosion_frames, explosion_sound,
                score
            )

        # --------------------------------------------------
        # Update sprites
        # --------------------------------------------------
        if game_state == GAME_STATE_PLAYING:
            heros.update(dt, move_dir)
            enemies.update(dt)
            bosses.update(dt)
            drones.update(dt, bullets)
            bullets.update(dt)
            meteors.update(dt)
            items.update(dt)
            shields.update(dt)

            # ถ้า Hero ตาย → Game Over
            if not hero.alive():
                game_state = GAME_STATE_GAME_OVER

        explosions.update(dt)

        # --------------------------------------------------
        # วาดทุกอย่าง
        # --------------------------------------------------
        screen.fill(GREY)

        meteors.draw(screen)
        enemies.draw(screen)
        bosses.draw(screen)
        items.draw(screen)
        heros.draw(screen)
        shields.draw(screen)
        drones.draw(screen)
        bullets.draw(screen)
        explosions.draw(screen)

        # ---------------- HUD: Stage, Score, Weapons ----------------
        hud_y = 10
        text_stage = font_small.render(f"Stage: {current_stage}", True, (255, 255, 255))
        screen.blit(text_stage, (10, hud_y))

        hud_y += 25
        text_score = font_small.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(text_score, (10, hud_y))

        wc = getattr(hero, "weapon_counts", {})
        current_single = wc.get("single", 0)
        current_double = wc.get("double", 0)
        current_shield = wc.get("shield", 0)

        hud_y += 25
        text_weapons = font_small.render(
            f"Single: {current_single}  "
            f"Double: {current_double}  "
            f"Shield: {current_shield}",
            True, (255, 255, 255)
        )
        screen.blit(text_weapons, (10, hud_y))

        # ---------------- Boss HP Bar (เฉพาะด่าน Boss) ----------------
        if current_stage == max_stage and len(bosses) > 0:
            boss = next(iter(bosses))  # ดึง Boss ตัวแรกจาก group

            if hasattr(boss, "hp") and hasattr(boss, "max_hp") and boss.max_hp > 0:
                ratio = max(boss.hp, 0) / boss.max_hp  # 0.0 - 1.0

                # เลือกสีตามเปอร์เซ็นต์ HP
                if ratio > 0.6:
                    bar_color = (0, 200, 0)       # เขียว
                elif ratio > 0.3:
                    bar_color = (230, 200, 0)     # เหลือง
                else:
                    bar_color = (200, 0, 0)       # แดง

                bar_width = 300
                bar_height = 22
                bar_x = (SCREEN_WIDTH - bar_width) // 2
                bar_y = 10  # ให้อยู่ด้านบนสุด เหนือ HUD เล็กน้อย

                # พื้นหลัง (เทาเข้ม)
                pygame.draw.rect(
                    screen,
                    (40, 40, 40),
                    (bar_x, bar_y, bar_width, bar_height)
                )

                # แถบพลังจริง
                pygame.draw.rect(
                    screen,
                    bar_color,
                    (bar_x, bar_y, int(bar_width * ratio), bar_height)
                )

                # กรอบเส้นขาว
                pygame.draw.rect(
                    screen,
                    (255, 255, 255),
                    (bar_x, bar_y, bar_width, bar_height),
                    2
                )

                # ข้อความ Boss HP ตรงกลางแถบ
                hp_text = font_small.render(
                    f"Boss HP: {boss.hp}/{boss.max_hp}",
                    True,
                    (255, 255, 255)
                )
                hp_rect = hp_text.get_rect(center=(SCREEN_WIDTH // 2, bar_y + bar_height // 2))
                screen.blit(hp_text, hp_rect)

        # ---------------- Game Over Text ----------------
        if game_state == GAME_STATE_GAME_OVER:
            game_over_text = font_big.render("GAME OVER", True, (255, 50, 50))
            score_text = font_small.render(f"Final Score: {score}", True, (255, 255, 255))
            stage_text = font_small.render(f"Reached Stage: {current_stage}", True, (255, 255, 255))
            hint_text = font_small.render("Press R to Restart  |  Q to Quit", True, (255, 255, 0))

            center_x = SCREEN_WIDTH // 2
            center_y = SCREEN_HEIGHT // 2

            rect_game_over = game_over_text.get_rect(center=(center_x, center_y - 40))
            rect_score = score_text.get_rect(center=(center_x, center_y))
            rect_stage = stage_text.get_rect(center=(center_x, center_y + 30))
            rect_hint = hint_text.get_rect(center=(center_x, center_y + 70))

            screen.blit(game_over_text, rect_game_over)
            screen.blit(score_text, rect_score)
            screen.blit(stage_text, rect_stage)
            screen.blit(hint_text, rect_hint)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
