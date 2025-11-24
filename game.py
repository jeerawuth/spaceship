# game.py

import pygame

from settings.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    GREY,
)
from settings.game_constants import (
    BULLET_COOLDOWN,
    GAME_STATE_PLAYING,
    GAME_STATE_GAME_OVER,
    GAME_STATE_WIN,
)

from settings.stage_config import (
    STAGE_CONFIGS,
    has_boss,
    get_boss_config,
    MAX_STAGE,
)

from managers.resource_manager import ResourceManager
    # ใช้ InputManager เฉพาะเช็ค quit ใน loop หลัก
from managers.input_manager import InputManager
from managers.collision_manager import CollisionManager
from managers.spawn_manager import SpawnManager
from managers.sound_manager import SoundManager
from managers.ui_manager import UIManager
from managers.background_manager import BackgroundManager
from managers.scene_manager import (
    SceneManager,
    MenuScene,
    GameScene,
    PauseScene,
    GameOverScene,
)

from nodes.hero_node import HeroNode
from nodes.bullet_node import BulletNode
from nodes.boss_node import BossNode
from nodes.laser_beam_node import LaserBeamNode


# Boss จะโผล่เมื่อเวลาผ่านไปกี่ % ของด่าน (0.7 = 70% ท้ายด่าน)
BOSS_APPEAR_RATIO = 0.7


def create_boss_for_stage(
    stage: int,
    hero: HeroNode,
    boss_bullets: pygame.sprite.Group,
) -> BossNode:
    """
    สร้าง BossNode ตามค่าที่กำหนดไว้ใน STAGE_CONFIGS ของด่านนั้น ๆ
    - ถ้าไม่เจอ config ของด่านนั้น จะใช้ค่า default
    """
    cfg = get_boss_config(stage)  # ถ้าไม่มี boss จะได้ {} กลับมา

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


class Game:
    """
    คลาสหลักของเกม
    - เก็บ screen, clock, resource, sprite groups, stage state
    - มี SceneManager คอยจัดการ Scene ต่าง ๆ
    """

    def __init__(self):
        # ---------- Pygame Window ----------
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Spaceship (State-based Animation)")
        self.clock = pygame.time.Clock()

        # ---------- Audio ----------
        SoundManager.init(num_channels=32)

        # ---------- Resource ----------
        ResourceManager.init()
        self.explosion_frames = ResourceManager.get_explosion_frames()
        self.explosion_sound = ResourceManager.get_sound("explosion")
        self.pickup_sound = ResourceManager.get_sound("pickup")
        self.laser_sound = ResourceManager.get_sound("laser")

        # ---------- Background ----------
        self.background = BackgroundManager()

        # ---------- Fonts + UI ----------
        self.font_small = pygame.font.Font(None, 28)
        self.font_big = pygame.font.Font(None, 64)
        self.ui = UIManager(self.font_small, self.font_big)

        # ---------- Sprite Groups ----------
        self.heros = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bosses = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.boss_bullets = pygame.sprite.Group()
        self.meteors = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.drones = pygame.sprite.Group()
        self.shields = pygame.sprite.Group()
        self.speeds = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.laser_beams = pygame.sprite.Group()

        # ---------- Game Variables ----------
        self.hero: HeroNode | None = None
        self.score = 0
        self.bullet_cooldown = 0.0

        self.current_stage = 1
        self.STAGE_DURATION = 30.0
        self.stage_timer = 0.0
        self.total_time = 0.0
        self.max_stage = MAX_STAGE
        self.boss_spawned = False

        self.game_state = GAME_STATE_PLAYING  # ใช้สำหรับ UIManager / สถานะภายใน
        self.spawn_manager: SpawnManager | None = None

        # ---------- Running flag ----------
        self.running = True

        # ---------- SceneManager ----------
        self.scene_manager = SceneManager(self)
        # เริ่มจากหน้าเมนู
        self.scene_manager.change_scene(MenuScene(self))

    # --------------------------------------------------
    # API ให้ Scene เรียกใช้งาน
    # --------------------------------------------------

    def start_new_game(self):
        """เริ่มเกมใหม่ (ใช้จาก MenuScene / GameOverScene)"""
        # เคลียร์ group ต่าง ๆ
        self.heros.empty()
        self.enemies.empty()
        self.bosses.empty()
        self.bullets.empty()
        self.boss_bullets.empty()
        self.meteors.empty()
        self.items.empty()
        self.drones.empty()
        self.shields.empty()
        self.speeds.empty()
        self.explosions.empty()
        self.laser_beams.empty()

        # Hero ใหม่
        self.hero = HeroNode()
        self.heros.add(self.hero)

        # รีเซ็ตตัวแปรเกม
        self.score = 0
        self.bullet_cooldown = 0.0

        self.current_stage = 1
        self.stage_timer = 0.0
        self.total_time = 0.0
        self.max_stage = MAX_STAGE
        self.boss_spawned = False

        self.game_state = GAME_STATE_PLAYING

        # SpawnManager สำหรับด่านแรก
        self.spawn_manager = SpawnManager(STAGE_CONFIGS, initial_stage=self.current_stage)

        # เข้าสู่ GameScene
        self.scene_manager.change_scene(GameScene(self))

    def quit(self):
        """ใช้จาก Scene เพื่อออกเกม"""
        self.running = False

    # --------------------------------------------------
    # Logic หลักตอน "กำลังเล่นเกม" (ใช้ใน GameScene)
    # --------------------------------------------------

    def handle_playing_input_and_weapons(self, dt: float):
        """ส่วนเดิม: Input + ยิงกระสุน + จัดการเลเซอร์"""
        keys = pygame.key.get_pressed()

        if self.game_state == GAME_STATE_PLAYING and self.hero and self.hero.alive():
            move_dir = InputManager.get_move_direction()

            # -------------------------------
            # จัดการ cooldown ร่วมกันทั้ง normal / buckshot
            # -------------------------------
            self.bullet_cooldown -= dt
            if self.bullet_cooldown < 0:
                self.bullet_cooldown = 0

            # กด SPACE แล้วค่อยดูว่าจะยิงแบบไหน
            if keys[pygame.K_SPACE] and self.bullet_cooldown <= 0:
                weapon_mode = getattr(self.hero, "weapon_mode", "normal")

                # -------------------------------
                # โหมด BUCKSHOT: ยิงกระจาย 5 นัด
                # -------------------------------
                if weapon_mode == "buckshot":
                    # แนวคิดแบบเกมชั้นนำ: ยิงเป็นพัดกว้างด้านหน้า
                    # ที่นี่ทำแบบ "กระจายแนวนอน" โดยใช้ BulletNode เดิม
                    offsets = [-40, -20, 0, 20, 40]  # px จาก center ของยาน
                    for dx in offsets:
                        bullet_pos = (self.hero.rect.centerx + dx, self.hero.rect.top)
                        bullet = BulletNode(bullet_pos)
                        self.bullets.add(bullet)

                    # ให้คูลดาวน์ 1 นัด / BULLET_COOLDOWN วินาที
                    self.bullet_cooldown = BULLET_COOLDOWN

                    bullet_sound = ResourceManager.get_sound("bullet")
                    SoundManager.play(
                        bullet_sound,
                        volume=0.8,
                        max_simultaneous=8,
                        priority=7,
                    )

                # -------------------------------
                # โหมดปกติ: ยิงกระสุนเดี่ยว
                # -------------------------------
                elif weapon_mode == "normal":
                    bullet_pos = self.hero.rect.midtop
                    bullet = BulletNode(bullet_pos)
                    self.bullets.add(bullet)

                    self.bullet_cooldown = BULLET_COOLDOWN

                    bullet_sound = ResourceManager.get_sound("bullet")
                    SoundManager.play(
                        bullet_sound,
                        volume=0.5,
                        max_simultaneous=8,
                        priority=7,
                    )

                # ถ้าเป็น laser ก็ไม่ยิง BulletNode
        else:
            move_dir = pygame.math.Vector2(0, 0)

        # ---------- LaserBeam ----------
        if self.game_state == GAME_STATE_PLAYING and self.hero and self.hero.alive():
            if getattr(self.hero, "weapon_mode", "normal") == "laser":
                if len(self.laser_beams) == 0:
                    beam = LaserBeamNode(self.hero, self.laser_sound)
                    self.laser_beams.add(beam)
            else:
                for beam in self.laser_beams.sprites():
                    beam.kill()
        else:
            for beam in self.laser_beams.sprites():
                beam.kill()

        return move_dir


    def update_stage_and_boss(self, dt: float):
        """ส่วนเดิม: เวลา + เปลี่ยนด่าน + spawn boss"""
        if self.game_state != GAME_STATE_PLAYING or not self.spawn_manager:
            return

        self.stage_timer += dt
        self.total_time += dt

        # มีบอสในด่านนี้ไหม
        if has_boss(self.current_stage):
            # ให้บอสโผล่ช่วงท้ายด่าน
            if (not self.boss_spawned) and self.stage_timer >= self.STAGE_DURATION * BOSS_APPEAR_RATIO:
                self.bosses.add(
                    create_boss_for_stage(self.current_stage, self.hero, self.boss_bullets)
                )
                self.boss_spawned = True

            # เปลี่ยนด่านเมื่อบอสตาย
            if self.boss_spawned and len(self.bosses) == 0:
                if self.current_stage < self.max_stage:
                    self.current_stage += 1
                    self.stage_timer = 0.0
                    self.boss_spawned = False
                    self.bosses.empty()
                    self.boss_bullets.empty()
                    self.spawn_manager.set_stage(self.current_stage)
                else:
                    # บอด่านสุดท้ายตาย → ชนะเกม
                    self.game_state = GAME_STATE_WIN
        else:
            # ด่านไม่มีบอส → เปลี่ยนด่านตามเวลา
            if self.stage_timer >= self.STAGE_DURATION:
                if self.current_stage < self.max_stage:
                    self.stage_timer = 0.0
                    self.current_stage += 1
                    self.spawn_manager.set_stage(self.current_stage)

                    self.boss_spawned = False
                    self.bosses.empty()
                    self.boss_bullets.empty()
                else:
                    # ด่านสุดท้าย + ไม่มีบอส → ชนะเกมเมื่อเวลาครบ
                    self.game_state = GAME_STATE_WIN

    def update_world_playing(self, dt: float):
        """
        รวม logic หลักตอน PLAYING:
        - เวลา + เปลี่ยนด่าน
        - Input + อาวุธ
        - spawn meteor/item
        - collision
        - update sprites
        """
        if not self.hero:
            return

        # เวลา + ด่าน + บอส
        self.update_stage_and_boss(dt)

        # Input + weapon
        move_dir = self.handle_playing_input_and_weapons(dt)

        # Spawn
        if self.game_state == GAME_STATE_PLAYING and self.spawn_manager:
            self.spawn_manager.update(dt, self.meteors, self.items)

        # Collision
        if self.game_state == GAME_STATE_PLAYING:
            # Bullet vs Enemy
            self.score = CollisionManager.handle_bullet_enemy_collisions(
                self.bullets,
                self.enemies,
                self.explosions,
                self.explosion_frames,
                self.explosion_sound,
                self.score,
            )

            # Hero vs Enemy
            CollisionManager.handle_hero_enemy_collisions(
                self.heros,
                self.enemies,
                self.explosions,
                self.explosion_frames,
                self.explosion_sound,
            )

            # Hero vs Meteor
            CollisionManager.handle_hero_meteor_collisions(
                self.heros,
                self.meteors,
                self.explosions,
                self.explosion_frames,
                self.explosion_sound,
            )

            # Bullet vs Meteor
            self.score = CollisionManager.handle_bullet_meteor_collisions(
                self.bullets,
                self.meteors,
                self.explosions,
                self.explosion_frames,
                self.explosion_sound,
                self.score,
            )

            # Hero เก็บ Item
            CollisionManager.handle_hero_item_collisions(
                self.heros,
                self.items,
                self.drones,
                self.shields,
                self.speeds,
                self.pickup_sound,
            )

            # Shield vs Meteor
            CollisionManager.handle_shield_meteor_collisions(
                self.shields,
                self.meteors,
                self.explosions,
                self.explosion_frames,
                self.explosion_sound,
            )

            # Shield vs Enemy
            CollisionManager.handle_shield_enemy_collisions(
                self.shields,
                self.enemies,
                self.explosions,
                self.explosion_frames,
                self.explosion_sound,
            )

            # -------- Boss (ตัว + กระสุน) --------
            self.score = CollisionManager.handle_bullet_boss_collisions(
                self.bullets,
                self.bosses,
                self.explosions,
                self.explosion_frames,
                self.explosion_sound,
                self.score,
            )

            CollisionManager.handle_hero_boss_collisions(
                self.heros,
                self.bosses,
                self.explosions,
                self.explosion_frames,
                self.explosion_sound,
            )

            self.score = CollisionManager.handle_shield_boss_collisions(
                self.shields,
                self.bosses,
                self.explosions,
                self.explosion_frames,
                self.explosion_sound,
                self.score,
            )

            # BossBullet vs Hero
            CollisionManager.handle_hero_bossbullet_collisions(
                self.heros,
                self.boss_bullets,
                self.explosions,
                self.explosion_frames,
                self.explosion_sound,
            )

            # BossBullet vs Shield
            CollisionManager.handle_shield_bossbullet_collisions(
                self.shields,
                self.boss_bullets,
                self.explosions,
                self.explosion_frames,
                self.explosion_sound,
            )

            # -------- LaserBeam vs Enemy/Meteor/Boss --------
            self.score = CollisionManager.handle_laser_enemy_collisions(
                self.laser_beams,
                self.enemies,
                self.explosions,
                self.explosion_frames,
                self.explosion_sound,
                self.score,
            )

            self.score = CollisionManager.handle_laser_meteor_collisions(
                self.laser_beams,
                self.meteors,
                self.explosions,
                self.explosion_frames,
                self.explosion_sound,
                self.score,
            )

            self.score = CollisionManager.handle_laser_boss_collisions(
                self.laser_beams,
                self.bosses,
                self.explosions,
                self.explosion_frames,
                self.explosion_sound,
                self.score,
            )

        # Update Sprites
        if self.game_state == GAME_STATE_PLAYING:
            self.background.update(dt)
            self.heros.update(dt, move_dir)
            self.enemies.update(dt)
            self.bosses.update(dt)
            self.drones.update(dt, self.bullets)
            self.bullets.update(dt)
            self.boss_bullets.update(dt)
            self.meteors.update(dt)
            self.items.update(dt)
            self.shields.update(dt)
            self.speeds.update(dt)
            self.laser_beams.update(dt)

            if not self.hero.alive():
                self.game_state = GAME_STATE_GAME_OVER

        # ระเบิดทำงานต่อในทุก state
        self.explosions.update(dt)

    def draw_world(self, game_state_for_ui: str):
        """วาดทุกอย่าง + UI"""
        self.screen.fill(GREY)
        self.background.draw(self.screen)
        self.meteors.draw(self.screen)
        self.enemies.draw(self.screen)
        self.bosses.draw(self.screen)
        self.items.draw(self.screen)
        self.heros.draw(self.screen)
        self.speeds.draw(self.screen)
        self.shields.draw(self.screen)
        self.drones.draw(self.screen)
        self.bullets.draw(self.screen)
        self.boss_bullets.draw(self.screen)
        self.laser_beams.draw(self.screen)
        self.explosions.draw(self.screen)

        hero_for_ui = self.hero if self.hero else None

        self.ui.render(
            screen=self.screen,
            hero=hero_for_ui,
            score=self.score,
            current_stage=self.current_stage,
            max_stage=self.max_stage,
            bosses=self.bosses,
            game_state=game_state_for_ui,
            drones=self.drones,
            shields=self.shields,
        )

    # --------------------------------------------------
    # Game Loop หลัก
    # --------------------------------------------------

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            # ปิดหน้าต่าง
            if not InputManager.handle_quit_events():
                break

            # ให้ SceneManager จัดการ input + update + render
            self.scene_manager.update(dt)
            self.scene_manager.render(self.screen)

            pygame.display.flip()
