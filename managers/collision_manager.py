# managers/collision_manager.py

import pygame
from nodes.explosion_node import ExplosionNode
from nodes.sound_node import SoundNode
from nodes.drone_node import DroneNode
from nodes.shield_node import ShieldNode


class CollisionManager:

    # -------------------------------------------------
    # 1) Bullet vs Enemy
    # -------------------------------------------------
    @staticmethod
    def handle_bullet_enemy_collisions(
        bullets, enemies,
        explosions, sound_effects,
        explosion_frames, explosion_sound,
        score
    ):
        """
        กระสุนชนศัตรู:
        - ลบ bullet และ enemy ที่ชนกัน
        - สร้าง ExplosionNode
        - เล่นเสียงระเบิด
        - เพิ่ม score
        """
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

                if explosion_sound is not None:
                    snd = SoundNode(explosion_sound)
                    sound_effects.add(snd)

        return score

    # -------------------------------------------------
    # 2) Hero vs Enemy
    # -------------------------------------------------
    @staticmethod
    def handle_hero_enemy_collisions(
        heros, enemies,
        explosions, sound_effects,
        explosion_frames, explosion_sound
    ):
        """
        ฮีโร่ชนศัตรูปกติ:
        - ลบ Hero และ Enemy ที่ชนกัน
        - สร้างระเบิดกลางระหว่างสองตัว
        """
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
                    snd = SoundNode(explosion_sound)
                    sound_effects.add(snd)

    # -------------------------------------------------
    # 3) Hero vs Meteor
    # -------------------------------------------------
    @staticmethod
    def handle_hero_meteor_collisions(
        heros, meteors,
        explosions, sound_effects,
        explosion_frames, explosion_sound
    ):
        """
        ฮีโร่ชนอุกกาบาต:
        - ลบ Hero และ Meteor
        """
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
                    snd = SoundNode(explosion_sound)
                    sound_effects.add(snd)

    # -------------------------------------------------
    # 4) Bullet vs Meteor
    # -------------------------------------------------
    @staticmethod
    def handle_bullet_meteor_collisions(
        bullets, meteors,
        explosions, sound_effects,
        explosion_frames, explosion_sound,
        score
    ):
        """
        กระสุนชนอุกกาบาต:
        - ลบ bullet และ meteor
        - เพิ่มคะแนน
        """
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

                if explosion_sound is not None:
                    snd = SoundNode(explosion_sound)
                    sound_effects.add(snd)

        return score

    # -------------------------------------------------
    # 5) Hero vs Item  → Drone / Shield
    # -------------------------------------------------
    @staticmethod
    def handle_hero_item_collisions(
        heros, items,
        drones, shields,
        sound_effects,
        pickup_sound
    ):
        """
        ฮีโร่เก็บไอเท็ม:
        - Hero ไม่หาย, Item หาย
        - item.type == "single" → Drone ขวา weapon_type="single"
        - item.type == "double" → Drone ซ้าย+ขวา weapon_type="double"
        - item.type == "shield" → ShieldNode รอบ Hero
        """
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

                if pickup_sound is not None:
                    snd = SoundNode(pickup_sound)
                    sound_effects.add(snd)

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
        shields, meteors, explosions, sound_effects,
        explosion_frames, explosion_sound
    ):
        """
        Meteor ชน Shield:
        - ลบ Meteor
        - Shield เสีย HP
        """
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
                    snd = SoundNode(explosion_sound)
                    sound_effects.add(snd)

    # -------------------------------------------------
    # 7) Shield vs Enemy
    # -------------------------------------------------
    @staticmethod
    def handle_shield_enemy_collisions(
        shields, enemies, explosions, sound_effects,
        explosion_frames, explosion_sound
    ):
        """
        Enemy ชน Shield:
        - ลบ Enemy
        - Shield เสีย HP
        """
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
                    snd = SoundNode(explosion_sound)
                    sound_effects.add(snd)

    # -------------------------------------------------
    # 8) Bullet vs Boss
    # -------------------------------------------------
    @staticmethod
    def handle_bullet_boss_collisions(
        bullets, bosses,
        explosions, sound_effects,
        explosion_frames, explosion_sound,
        score
    ):
        """
        กระสุนชน Boss:
        - ลบ bullet
        - Boss โดนดาเมจ (ใช้ boss.take_damage())
        - ถ้า Boss ตายให้เพิ่มคะแนนพิเศษ
        """
        hits = pygame.sprite.groupcollide(
            bullets, bosses,
            True, False,                  # bullet หาย, boss ยังอยู่
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

                if explosion_sound is not None:
                    snd = SoundNode(explosion_sound)
                    sound_effects.add(snd)

                if died:
                    score += 50  # โบนัสตอนล้ม Boss

        return score

    # -------------------------------------------------
    # 9) Hero vs Boss
    # -------------------------------------------------
    @staticmethod
    def handle_hero_boss_collisions(
        heros, bosses,
        explosions, sound_effects,
        explosion_frames, explosion_sound
    ):
        """
        ฮีโร่ชน Boss:
        - Hero ตายทันที
        - Boss ไม่ตาย (ตามปกติ Boss ไม่ควรหายด้วยการชน)
        """
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

                if explosion_sound is not None:
                    snd = SoundNode(explosion_sound)
                    sound_effects.add(snd)

    # -------------------------------------------------
    # 10) Shield vs Boss
    # -------------------------------------------------
    @staticmethod
    def handle_shield_boss_collisions(
        shields, bosses,
        explosions, sound_effects,
        explosion_frames, explosion_sound,
        score
    ):
        """
        Shield ชน Boss:
        - Boss โดนดาเมจ (เหมือนโดนกระสุน)
        - Shield เสีย HP
        """
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

                if explosion_sound is not None:
                    snd = SoundNode(explosion_sound)
                    sound_effects.add(snd)

                if died:
                    score += 50

        return score
