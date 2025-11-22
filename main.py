# main.py

import pygame

from settings.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GREY
from settings.game_constants import BULLET_COOLDOWN
from settings.spawn_config import STAGE_SPAWN_CONFIGS
from settings.boss_config import BOSS_STAGE_CONFIGS

from managers.resource_manager import ResourceManager
from managers.input_manager import InputManager
from managers.collision_manager import CollisionManager
from managers.spawn_manager import SpawnManager
from managers.sound_manager import SoundManager
from managers.ui_manager import UIManager

from nodes.hero_node import HeroNode
from nodes.enemy_node import EnemyNode
from nodes.meteor_node import MeteorNode
from nodes.bullet_node import BulletNode
from nodes.item_node import ItemNode
from nodes.boss_node import BossNode
from nodes.boss_bullet_node import BossBulletNode  # เผื่อ BossNode ใช้ภายใน
from nodes.laser_beam_node import LaserBeamNode


# Boss จะโผล่เมื่อเวลาผ่านไปกี่ % ของด่าน (0.7 = 70% ท้ายด่าน)
BOSS_APPEAR_RATIO = 0.7


def create_boss_for_stage(stage: int, hero: HeroNode, boss_bullets: pygame.sprite.Group) -> BossNode:
    """
    สร้าง BossNode ตามค่าที่กำหนดไว้ใน BOSS_STAGE_CONFIGS ของด่านนั้น ๆ
    - ถ้าไม่เจอ config ของด่านนั้น จะใช้ค่า default
    """
    cfg = BOSS_STAGE_CONFIGS.get(stage, {})

    max_hp = cfg.get("max_hp", 50)
    fire_interval = cfg.get("fire_interval", 5.0)
    bullet_pairs = cfg.get("bullet_pairs", 1)

    boss = BossNode(
        hero=hero,
        boss_bullet_group=boss_bullets,
        max_hp=max_hp,
        fire_interval=fire_interval,
        bullet_speed=250.0,
        bullet_pairs=bullet_pairs,
    )
    return boss


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
    # ฟอนต์ + UI Manager
    # --------------------------------------------------
    font_small = pygame.font.Font(None, 28)
    font_big = pygame.font.Font(None, 64)
    ui = UIManager(font_small, font_big)

    # --------------------------------------------------
    # กลุ่ม Sprite ต่าง ๆ
    # --------------------------------------------------
    heros = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bosses = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    boss_bullets = pygame.sprite.Group()
    meteors = pygame.sprite.Group()
    items = pygame.sprite.Group()
    drones = pygame.sprite.Group()
    shields = pygame.sprite.Group()
    explosions = pygame.sprite.Group()
    laser_beams = pygame.sprite.Group()   # ★ เลเซอร์ Beam

    # --------------------------------------------------
    # สร้าง Hero / Enemy เริ่มต้น
    # --------------------------------------------------
    hero = HeroNode()
    heros.add(hero)

    enemy = EnemyNode()
    enemies.add(enemy)

    # --------------------------------------------------
    # ตัวแปรเกม (ด่าน + เวลา)
    # --------------------------------------------------
    score = 0
    bullet_cooldown = 0.0

    current_stage = 1
    STAGE_DURATION = 30.0       # วินาทีต่อด่าน
    stage_timer = 0.0
    total_time = 0.0
    max_stage = len(STAGE_SPAWN_CONFIGS)

    GAME_STATE_PLAYING = "PLAYING"
    GAME_STATE_GAME_OVER = "GAME_OVER"
    GAME_STATE_WIN = "WIN"
    game_state = GAME_STATE_PLAYING

    # สำหรับด่านที่มีบอส
    boss_spawned = False

    # --------------------------------------------------
    # SpawnManager สำหรับด่านแรก
    # --------------------------------------------------
    spawn_manager = SpawnManager(STAGE_SPAWN_CONFIGS, initial_stage=current_stage)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # --------------------------------------------------
        # Event ปิดหน้าต่าง
        # --------------------------------------------------
        running = InputManager.handle_quit_events()
        if not running:
            break

        keys = pygame.key.get_pressed()

        # --------------------------------------------------
        # ปุ่มตอน Game Over / You Win: R = restart, Q = quit
        # --------------------------------------------------
        if game_state in (GAME_STATE_GAME_OVER, GAME_STATE_WIN):
            if keys[pygame.K_r]:
                return main()
            if keys[pygame.K_q]:
                running = False

        # --------------------------------------------------
        # เวลา + เปลี่ยนด่าน (แยกกรณีมีบอส / ไม่มีบอส)
        # --------------------------------------------------
        if game_state == GAME_STATE_PLAYING:
            stage_timer += dt
            total_time += dt

            # ----- กรณีด่านนี้ "มีบอส" -----
            if current_stage in BOSS_STAGE_CONFIGS:
                # 1) ให้บอสโผล่ช่วงท้ายด่าน (ตาม BOSS_APPEAR_RATIO) ถ้ายังไม่ spawn
                if (not boss_spawned) and stage_timer >= STAGE_DURATION * BOSS_APPEAR_RATIO:
                    bosses.add(create_boss_for_stage(current_stage, hero, boss_bullets))
                    boss_spawned = True

                # 2) เปลี่ยนด่านเมื่อบอสตาย
                if boss_spawned and len(bosses) == 0:
                    if current_stage < max_stage:
                        current_stage += 1
                        stage_timer = 0.0
                        boss_spawned = False
                        bosses.empty()
                        boss_bullets.empty()
                        spawn_manager.set_stage(current_stage)
                    else:
                        # บอด่านสุดท้ายตาย → ชนะเกม
                        game_state = GAME_STATE_WIN

            # ----- กรณีด่านนี้ "ไม่มีบอส" -----
            else:
                if stage_timer >= STAGE_DURATION:
                    if current_stage < max_stage:
                        stage_timer = 0.0
                        current_stage += 1
                        spawn_manager.set_stage(current_stage)

                        boss_spawned = False
                        bosses.empty()
                        boss_bullets.empty()
                    else:
                        # ด่านสุดท้าย + ไม่มีบอส → ชนะเกมเมื่อเวลาครบ
                        game_state = GAME_STATE_WIN

        # --------------------------------------------------
        # Input + ยิงกระสุน Hero
        # --------------------------------------------------
        if game_state == GAME_STATE_PLAYING:
            move_dir = InputManager.get_move_direction()

            bullet_cooldown -= dt
            # ยิงเฉพาะตอน weapon_mode == "normal"
            if (
                keys[pygame.K_SPACE]
                and bullet_cooldown <= 0
                and hero.alive()
                and getattr(hero, "weapon_mode", "normal") == "normal"
            ):
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
        # จัดการ LaserBeam ตาม weapon_mode ของ Hero
        # --------------------------------------------------
        if game_state == GAME_STATE_PLAYING and hero.alive():
            if getattr(hero, "weapon_mode", "normal") == "laser":
                if len(laser_beams) == 0:
                    beam = LaserBeamNode(hero)
                    laser_beams.add(beam)
            else:
                if len(laser_beams) > 0:
                    laser_beams.empty()
        else:
            if len(laser_beams) > 0:
                laser_beams.empty()

        # --------------------------------------------------
        # Spawn ต่าง ๆ (Meteor / Item)
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

            # -------- Boss (ตัว + กระสุน) --------
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

            # BossBullet vs Hero
            CollisionManager.handle_hero_bossbullet_collisions(
                heros, boss_bullets,
                explosions,
                explosion_frames, explosion_sound
            )

            # BossBullet vs Shield
            CollisionManager.handle_shield_bossbullet_collisions(
                shields, boss_bullets,
                explosions,
                explosion_frames, explosion_sound
            )

            # -------- LaserBeam vs Enemy/Meteor/Boss --------
            score = CollisionManager.handle_laser_enemy_collisions(
                laser_beams, enemies,
                explosions,
                explosion_frames, explosion_sound,
                score
            )

            score = CollisionManager.handle_laser_meteor_collisions(
                laser_beams, meteors,
                explosions,
                explosion_frames, explosion_sound,
                score
            )

            score = CollisionManager.handle_laser_boss_collisions(
                laser_beams, bosses,
                explosions,
                explosion_frames, explosion_sound,
                score
            )

        # --------------------------------------------------
        # Update Sprites
        # --------------------------------------------------
        if game_state == GAME_STATE_PLAYING:
            heros.update(dt, move_dir)
            enemies.update(dt)
            bosses.update(dt)
            drones.update(dt, bullets)
            bullets.update(dt)
            boss_bullets.update(dt)
            meteors.update(dt)
            items.update(dt)
            shields.update(dt)
            laser_beams.update(dt)

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
        boss_bullets.draw(screen)
        laser_beams.draw(screen)   # ★ วาดเลเซอร์
        explosions.draw(screen)

        # HUD + Boss HP + Game Over / Win
        ui.render(
            screen=screen,
            hero=hero,
            score=score,
            current_stage=current_stage,
            max_stage=max_stage,
            bosses=bosses,
            game_state=game_state,
            drones=drones,
            shields=shields,
        )

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
