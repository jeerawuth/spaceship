# managers/collision_manager.py

import pygame
from nodes.explosion_node import ExplosionNode
from nodes.drone_node import DroneNode
from nodes.shield_node import ShieldNode
from managers.sound_manager import SoundManager


class CollisionManager:

    # -------------------------------------------------
    # 1) Bullet vs Enemy
    # -------------------------------------------------
    @staticmethod
    def handle_bullet_enemy_collisions(
        bullets, enemies,
        explosions,
        explosion_frames, explosion_sound,
        score
    ):
        hits = pygame.sprite.groupcollide(
            bullets, enemies,
            True, True,
            pygame.sprite.collide_rect
        )

        for bullet, enemy_list in hits.items():
            for enemy in enemy_list:
                score += 1

                if explosion_frames:
                    expl = ExplosionNode(enemy.rect.center, explosion_frames)
                    explosions.add(expl)

                SoundManager.play(
                    explosion_sound,
                    volume=0.9,
                    max_simultaneous=8,
                    priority=5,
                )

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

                SoundManager.play(
                    explosion_sound,
                    volume=1.0,
                    max_simultaneous=8,
                    priority=10,
                )

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

                SoundManager.play(
                    explosion_sound,
                    volume=1.0,
                    max_simultaneous=8,
                    priority=10,
                )

    # -------------------------------------------------
    # 4) Bullet vs Meteor
    # -------------------------------------------------
    @staticmethod
    def handle_bullet_meteor_collisions(
        bullets, meteors,
        explosions,
        explosion_frames, explosion_sound,
        score
    ):
        hits = pygame.sprite.groupcollide(
            bullets, meteors,
            True, True,
            pygame.sprite.collide_rect
        )

        for bullet, meteor_list in hits.items():
            for meteor in meteor_list:
                score += 1

                if explosion_frames:
                    expl = ExplosionNode(meteor.rect.center, explosion_frames)
                    explosions.add(expl)

                SoundManager.play(
                    explosion_sound,
                    volume=0.8,
                    max_simultaneous=8,
                    priority=4,
                )

        return score

    # -------------------------------------------------
    # 5) Hero vs Item → Drone / Shield
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
                if item_type is None:
                    continue

                SoundManager.play(
                    pickup_sound,
                    volume=0.7,
                    max_simultaneous=4,
                    priority=6,
                )

                if item_type == "single":
                    drone_right = DroneNode(hero, side="right", weapon_type="single")
                    drones.add(drone_right)

                elif item_type == "double":
                    drone_left = DroneNode(hero, side="left", weapon_type="double")
                    drone_right = DroneNode(hero, side="right", weapon_type="double")
                    drones.add(drone_left, drone_right)

                elif item_type == "shield":
                    shield = ShieldNode(hero, max_hp=3)
                    shields.add(shield)

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

                SoundManager.play(
                    explosion_sound,
                    volume=0.7,
                    max_simultaneous=6,
                    priority=3,
                )

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

                SoundManager.play(
                    explosion_sound,
                    volume=0.7,
                    max_simultaneous=6,
                    priority=3,
                )

    # -------------------------------------------------
    # 8) Bullet vs Boss
    # -------------------------------------------------
    @staticmethod
    def handle_bullet_boss_collisions(
        bullets, bosses,
        explosions,
        explosion_frames, explosion_sound,
        score
    ):
        hits = pygame.sprite.groupcollide(
            bullets, bosses,
            True, False,
            pygame.sprite.collide_mask
        )

        for bullet, boss_list in hits.items():
            for boss in boss_list:
                died = False
                if hasattr(boss, "take_damage"):
                    died = boss.take_damage(1)

                if explosion_frames:
                    expl = ExplosionNode(boss.rect.center, explosion_frames)
                    explosions.add(expl)

                SoundManager.play(
                    explosion_sound,
                    volume=0.6,
                    max_simultaneous=3,
                    priority=2,
                )

                if died:
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
                cx = (hero.rect.centerx + boss.rect.centerx) // 2
                cy = (hero.rect.centery + boss.rect.centery) // 2

                if explosion_frames:
                    expl = ExplosionNode((cx, cy), explosion_frames)
                    explosions.add(expl)

                SoundManager.play(
                    explosion_sound,
                    volume=1.0,
                    max_simultaneous=5,
                    priority=10,
                )

    # -------------------------------------------------
    # 10) Shield vs Boss
    # -------------------------------------------------
    @staticmethod
    def handle_shield_boss_collisions(
        shields, bosses,
        explosions,
        explosion_frames, explosion_sound,
        score
    ):
        hits = pygame.sprite.groupcollide(
            shields, bosses,
            False, False,
            pygame.sprite.collide_circle
        )

        for shield, boss_list in hits.items():
            for boss in boss_list:
                shield.take_hit(1)

                died = False
                if hasattr(boss, "take_damage"):
                    died = boss.take_damage(1)

                if explosion_frames:
                    expl = ExplosionNode(boss.rect.center, explosion_frames)
                    explosions.add(expl)

                SoundManager.play(
                    explosion_sound,
                    volume=0.6,
                    max_simultaneous=3,
                    priority=2,
                )

                if died:
                    score += 50

        return score

    # -------------------------------------------------
    # 11) Hero vs BossBullet
    # -------------------------------------------------
    @staticmethod
    def handle_hero_bossbullet_collisions(
        heros, boss_bullets,
        explosions,
        explosion_frames, explosion_sound
    ):
        """
        กระสุน Boss ชน Hero:
        - ลบ Hero และกระสุน
        - ระเบิด
        - (Game Over จะถูกเช็คใน main ตามเดิม)
        """
        hits = pygame.sprite.groupcollide(
            heros, boss_bullets,
            True, True,
            pygame.sprite.collide_rect
        )

        for hero, bullet_list in hits.items():
            for bullet in bullet_list:
                cx = (hero.rect.centerx + bullet.rect.centerx) // 2
                cy = (hero.rect.centery + bullet.rect.centery) // 2

                if explosion_frames:
                    expl = ExplosionNode((cx, cy), explosion_frames)
                    explosions.add(expl)

                SoundManager.play(
                    explosion_sound,
                    volume=1.0,
                    max_simultaneous=5,
                    priority=10,
                )

    # -------------------------------------------------
    # 12) Shield vs BossBullet
    # -------------------------------------------------
    @staticmethod
    def handle_shield_bossbullet_collisions(
        shields, boss_bullets,
        explosions,
        explosion_frames, explosion_sound
    ):
        """
        กระสุน Boss ชน Shield:
        - ลบกระสุน
        - Shield เสีย HP
        """
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

                SoundManager.play(
                    explosion_sound,
                    volume=0.7,
                    max_simultaneous=5,
                    priority=4,
                )
