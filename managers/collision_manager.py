# managers/collision_manager.py

import pygame
from nodes.explosion_node import ExplosionNode
from nodes.drone_node import DroneNode
from nodes.shield_node import ShieldNode


class CollisionManager:

    # -------------------------------------------------
    # 1) Bullet vs Enemy
    # -------------------------------------------------
    @staticmethod
    def handle_bullet_enemy_collisions(
        bullets, enemies,
        explosions,
        explosion_frames, explosion_sound,
        score: int
    ) -> int:
        hits = pygame.sprite.groupcollide(
            bullets, enemies,
            True, True,
            pygame.sprite.collide_mask
        )

        for bullet, enemy_list in hits.items():
            for enemy in enemy_list:
                if explosion_frames:
                    expl = ExplosionNode(enemy.rect.center, explosion_frames)
                    explosions.add(expl)

                if explosion_sound is not None:
                    explosion_sound.play()

                score += 10  # ปรับคะแนนตามที่ต้องการได้

        return score

    # -------------------------------------------------
    # 2) Hero vs Enemy
    # -------------------------------------------------
    @staticmethod
    def handle_hero_enemy_collisions(
        heros, enemies,
        explosions,
        explosion_frames, explosion_sound
    ):
        hits = pygame.sprite.groupcollide(
            heros, enemies,
            True, True,
            pygame.sprite.collide_mask
        )

        for hero, enemy_list in hits.items():
            for enemy in enemy_list:
                cx = (hero.rect.centerx + enemy.rect.centerx) // 2
                cy = (hero.rect.centery + enemy.rect.centery) // 2

                if explosion_frames:
                    expl = ExplosionNode((cx, cy), explosion_frames)
                    explosions.add(expl)

                if explosion_sound is not None:
                    explosion_sound.play()

    # -------------------------------------------------
    # 3) Hero vs Meteor
    # -------------------------------------------------
    @staticmethod
    def handle_hero_meteor_collisions(
        heros, meteors,
        explosions,
        explosion_frames, explosion_sound
    ):
        hits = pygame.sprite.groupcollide(
            heros, meteors,
            True, True,
            pygame.sprite.collide_mask
        )

        for hero, meteor_list in hits.items():
            for meteor in meteor_list:
                cx = (hero.rect.centerx + meteor.rect.centerx) // 2
                cy = (hero.rect.centery + meteor.rect.centery) // 2

                if explosion_frames:
                    expl = ExplosionNode((cx, cy), explosion_frames)
                    explosions.add(expl)

                if explosion_sound is not None:
                    explosion_sound.play()

    # -------------------------------------------------
    # 4) Bullet vs Meteor
    # -------------------------------------------------
    @staticmethod
    def handle_bullet_meteor_collisions(
        bullets, meteors,
        explosions,
        explosion_frames, explosion_sound,
        score: int
    ) -> int:
        hits = pygame.sprite.groupcollide(
            bullets, meteors,
            True, True,
            pygame.sprite.collide_mask
        )

        for bullet, meteor_list in hits.items():
            for meteor in meteor_list:
                if explosion_frames:
                    expl = ExplosionNode(meteor.rect.center, explosion_frames)
                    explosions.add(expl)

                if explosion_sound is not None:
                    explosion_sound.play()

                score += 5

        return score

    # -------------------------------------------------
    # 5) Hero vs Item (Drone / Shield / Speed / Laser)
    # -------------------------------------------------
    @staticmethod
    def handle_hero_item_collisions(
        heros, items,
        drones, shields,
        pickup_sound
    ):
        hits = pygame.sprite.groupcollide(
            heros, items,
            False, True,
            pygame.sprite.collide_mask
        )

        for hero, item_list in hits.items():
            for item in item_list:
                item_type = getattr(item, "type", None)

                # เล่นเสียงเก็บ item
                if pickup_sound is not None:
                    try:
                        pickup_sound.play()
                    except Exception:
                        pass

                # single / double / shield เดิม
                if item_type == "single":
                    drone_right = DroneNode(hero, side="right")
                    drones.add(drone_right)

                elif item_type == "double":
                    drone_left = DroneNode(hero, side="left")
                    drone_right = DroneNode(hero, side="right")
                    drones.add(drone_left, drone_right)

                elif item_type == "shield":
                    shield = ShieldNode(hero, max_hp=3)
                    shields.add(shield)

                # ของใหม่: speed / laser
                elif item_type == "speed":
                    if hasattr(hero, "start_speed_boost"):
                        hero.start_speed_boost(duration=5.0, multiplier=1.5)

                elif item_type == "laser":
                    if hasattr(hero, "activate_laser"):
                        hero.activate_laser(duration=5.0)

    # -------------------------------------------------
    # 6) Shield vs Meteor
    # -------------------------------------------------
    @staticmethod
    def handle_shield_meteor_collisions(
        shields, meteors,
        explosions,
        explosion_frames, explosion_sound
    ):
        hits = pygame.sprite.groupcollide(
            shields, meteors,
            False, True,
            pygame.sprite.collide_circle
        )

        for shield, meteor_list in hits.items():
            for meteor in meteor_list:
                shield.take_hit(1)

                if explosion_frames:
                    expl = ExplosionNode(meteor.rect.center, explosion_frames)
                    explosions.add(expl)

                if explosion_sound is not None:
                    explosion_sound.play()

    # -------------------------------------------------
    # 7) Shield vs Enemy
    # -------------------------------------------------
    @staticmethod
    def handle_shield_enemy_collisions(
        shields, enemies,
        explosions,
        explosion_frames, explosion_sound
    ):
        hits = pygame.sprite.groupcollide(
            shields, enemies,
            False, True,
            pygame.sprite.collide_circle
        )

        for shield, enemy_list in hits.items():
            for enemy in enemy_list:
                shield.take_hit(1)

                if explosion_frames:
                    expl = ExplosionNode(enemy.rect.center, explosion_frames)
                    explosions.add(expl)

                if explosion_sound is not None:
                    explosion_sound.play()

    # -------------------------------------------------
    # 8) Bullet vs Boss
    # -------------------------------------------------
    @staticmethod
    def handle_bullet_boss_collisions(
        bullets, bosses,
        explosions,
        explosion_frames, explosion_sound,
        score: int
    ) -> int:
        hits = pygame.sprite.groupcollide(
            bullets, bosses,
            True, False,
            pygame.sprite.collide_mask
        )

        for bullet, boss_list in hits.items():
            for boss in boss_list:
                died = boss.take_damage(1)

                if explosion_frames:
                    expl = ExplosionNode(bullet.rect.center, explosion_frames)
                    explosions.add(expl)

                if explosion_sound is not None:
                    explosion_sound.play()

                score += 15
                if died:
                    # บอสตายแล้ว อาจให้โบนัสเพิ่มพิเศษได้
                    score += 50

        return score

    # -------------------------------------------------
    # 9) Hero vs Boss
    # -------------------------------------------------
    @staticmethod
    def handle_hero_boss_collisions(
        heros, bosses,
        explosions,
        explosion_frames, explosion_sound
    ):
        hits = pygame.sprite.groupcollide(
            heros, bosses,
            True, False,
            pygame.sprite.collide_mask
        )

        for hero, boss_list in hits.items():
            for boss in boss_list:
                # Hero หาย, Boss ยังอยู่ (อาจลด HP ถ้าต้องการ)
                if explosion_frames:
                    expl = ExplosionNode(hero.rect.center, explosion_frames)
                    explosions.add(expl)

                if explosion_sound is not None:
                    explosion_sound.play()

    # -------------------------------------------------
    # 10) Shield vs Boss
    # -------------------------------------------------
    @staticmethod
    def handle_shield_boss_collisions(
        shields, bosses,
        explosions,
        explosion_frames, explosion_sound,
        score: int
    ) -> int:
        hits = pygame.sprite.groupcollide(
            shields, bosses,
            False, False,
            pygame.sprite.collide_circle
        )

        for shield, boss_list in hits.items():
            for boss in boss_list:
                shield.take_hit(1)
                died = boss.take_damage(1)

                if explosion_frames:
                    expl = ExplosionNode(boss.rect.center, explosion_frames)
                    explosions.add(expl)

                if explosion_sound is not None:
                    explosion_sound.play()

                score += 10
                if died:
                    score += 50

        return score

    # -------------------------------------------------
    # 11) Hero vs Boss Bullets
    # -------------------------------------------------
    @staticmethod
    def handle_hero_bossbullet_collisions(
        heros, boss_bullets,
        explosions,
        explosion_frames, explosion_sound
    ):
        hits = pygame.sprite.groupcollide(
            heros, boss_bullets,
            True, True,
            pygame.sprite.collide_mask
        )

        for hero, bullet_list in hits.items():
            for bullet in bullet_list:
                if explosion_frames:
                    expl = ExplosionNode(hero.rect.center, explosion_frames)
                    explosions.add(expl)

                if explosion_sound is not None:
                    explosion_sound.play()

    # -------------------------------------------------
    # 12) Shield vs Boss Bullets
    # -------------------------------------------------
    @staticmethod
    def handle_shield_bossbullet_collisions(
        shields, boss_bullets,
        explosions,
        explosion_frames, explosion_sound
    ):
        hits = pygame.sprite.groupcollide(
            shields, boss_bullets,
            False, True,
            pygame.sprite.collide_circle
        )

        for shield, bullet_list in hits.items():
            for bullet in bullet_list:
                shield.take_hit(1)

                if explosion_frames:
                    expl = ExplosionNode(bullet.rect.center, explosion_frames)
                    explosions.add(expl)

                if explosion_sound is not None:
                    explosion_sound.play()

    # -------------------------------------------------
    # 13) LaserBeam vs Enemy
    # -------------------------------------------------
    @staticmethod
    def handle_laser_enemy_collisions(
        lasers, enemies,
        explosions,
        explosion_frames, explosion_sound,
        score: int
    ) -> int:
        # laser ไม่หาย, enemy หาย
        hits = pygame.sprite.groupcollide(
            lasers, enemies,
            False, True,
            pygame.sprite.collide_rect
        )

        for laser, enemy_list in hits.items():
            for enemy in enemy_list:
                if explosion_frames:
                    expl = ExplosionNode(enemy.rect.center, explosion_frames)
                    explosions.add(expl)

                if explosion_sound is not None:
                    explosion_sound.play()

                score += 10

        return score

    # -------------------------------------------------
    # 14) LaserBeam vs Meteor
    # -------------------------------------------------
    @staticmethod
    def handle_laser_meteor_collisions(
        lasers, meteors,
        explosions,
        explosion_frames, explosion_sound,
        score: int
    ) -> int:
        hits = pygame.sprite.groupcollide(
            lasers, meteors,
            False, True,
            pygame.sprite.collide_rect
        )

        for laser, meteor_list in hits.items():
            for meteor in meteor_list:
                if explosion_frames:
                    expl = ExplosionNode(meteor.rect.center, explosion_frames)
                    explosions.add(expl)

                if explosion_sound is not None:
                    explosion_sound.play()

                score += 5

        return score

    # -------------------------------------------------
    # 15) LaserBeam vs Boss
    # -------------------------------------------------
    @staticmethod
    def handle_laser_boss_collisions(
        lasers, bosses,
        explosions,
        explosion_frames, explosion_sound,
        score: int
    ) -> int:
        hits = pygame.sprite.groupcollide(
            lasers, bosses,
            False, False,
            pygame.sprite.collide_rect
        )

        for laser, boss_list in hits.items():
            for boss in boss_list:
                died = boss.take_damage(1)

                if explosion_frames:
                    expl = ExplosionNode(boss.rect.center, explosion_frames)
                    explosions.add(expl)

                if explosion_sound is not None:
                    explosion_sound.play()

                score += 15
                if died:
                    score += 50

        return score
