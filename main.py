# main.py

import pygame

from settings.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GREY
from settings.game_constants import BULLET_COOLDOWN
from managers.resource_manager import ResourceManager
from managers.input_manager import InputManager
from managers.collision_manager import CollisionManager
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

    # ด่านและเวลา
    current_stage = 1
    STAGE_DURATION = 30.0  # วินาทีต่อ 1 ด่าน
    stage_timer = 0.0
    total_time = 0.0

    max_stage = len(STAGE_SPAWN_CONFIGS)

    # สถานะเกม
    GAME_STATE_PLAYING = "PLAYING"
    GAME_STATE_GAME_OVER = "GAME_OVER"
    game_state = GAME_STATE_PLAYING

    # --------------------------------------------------
    # สร้าง SpawnManager สำหรับด่าน 1
    # --------------------------------------------------
    spawn_manager = SpawnManager(STAGE_SPAWN_CONFIGS, initial_stage=current_stage)

    # ถ้าด่านแรกคือด่านสุดท้ายด้วย → spawn Boss ทันที
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
        # อัปเดตเวลา และเปลี่ยนด่านตามเวลา
        # --------------------------------------------------
        if game_state == GAME_STATE_PLAYING:
            stage_timer += dt
            total_time += dt

            # เปลี่ยนด่านทุก 30 วินาที จนถึงด่านสุดท้าย
            if stage_timer >= STAGE_DURATION and current_stage < max_stage:
                stage_timer = 0.0
                current_stage += 1
                spawn_manager.set_stage(current_stage)

                # ถ้าด่านใหม่คือด่านสุดท้าย → spawn Boss
                if current_stage == max_stage and len(bosses) == 0:
                    bosses.add(BossNode(max_hp=50))

        # --------------------------------------------------
        # Input: ทิศทางการเคลื่อนที่ + ยิงกระสุน
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

                    snd = ResourceManager.get_sound("bullet")
                    if snd:
                        snd.play()
        else:
            move_dir = pygame.math.Vector2(0, 0)

        # --------------------------------------------------
        # Spawn Meteor / Item (เฉพาะตอนกำลังเล่น)
        # --------------------------------------------------
        if game_state == GAME_STATE_PLAYING:
            spawn_manager.update(dt, meteors, items)

        # --------------------------------------------------
        # ตรวจสอบการชนต่าง ๆ (เฉพาะตอนกำลังเล่น)
        # --------------------------------------------------
        if game_state == GAME_STATE_PLAYING:
            # Bullet vs Enemy
            score = CollisionManager.handle_bullet_enemy_collisions(
                bullets, enemies,
                explosions, sound_effects,
                explosion_frames, explosion_sound,
                score
            )

            # Hero vs Enemy
            CollisionManager.handle_hero_enemy_collisions(
                heros, enemies,
                explosions, sound_effects,
                explosion_frames, explosion_sound
            )

            # Hero vs Meteor
            CollisionManager.handle_hero_meteor_collisions(
                heros, meteors,
                explosions, sound_effects,
                explosion_frames, explosion_sound
            )

            # Bullet vs Meteor
            score = CollisionManager.handle_bullet_meteor_collisions(
                bullets, meteors,
                explosions, sound_effects,
                explosion_frames, explosion_sound,
                score
            )

            # Hero เก็บ Item → Drone / Shield
            CollisionManager.handle_hero_item_collisions(
                heros, items,
                drones, shields,
                sound_effects,
                pickup_sound
            )

            # Shield vs Meteor
            CollisionManager.handle_shield_meteor_collisions(
                shields, meteors,
                explosions, sound_effects,
                explosion_frames, explosion_sound
            )

            # Shield vs Enemy
            CollisionManager.handle_shield_enemy_collisions(
                shields, enemies,
                explosions, sound_effects,
                explosion_frames, explosion_sound
            )

            # --------- Collision ที่เกี่ยวกับ Boss ---------

            # Bullet vs Boss
            score = CollisionManager.handle_bullet_boss_collisions(
                bullets, bosses,
                explosions, sound_effects,
                explosion_frames, explosion_sound,
                score
            )

            # Hero vs Boss
            CollisionManager.handle_hero_boss_collisions(
                heros, bosses,
                explosions, sound_effects,
                explosion_frames, explosion_sound
            )

            # Shield vs Boss
            score = CollisionManager.handle_shield_boss_collisions(
                shields, bosses,
                explosions, sound_effects,
                explosion_frames, explosion_sound,
                score
            )

        # --------------------------------------------------
        # อัปเดตทุกกลุ่ม Sprite
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

            # Hero ตายเมื่อไหร่ → Game Over
            if not hero.alive():
                game_state = GAME_STATE_GAME_OVER

        explosions.update(dt)
        sound_effects.update(dt)

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
