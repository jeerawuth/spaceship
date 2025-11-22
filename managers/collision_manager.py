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
            True, True,                 # ลบทั้งกระสุนและศัตรู
            pygame.sprite.collide_rect  # ใช้ rect พอ (ถ้าอยากใช้ mask ต้องแน่ใจว่ามี .mask ทุกตัว)
        )

        for bullet, enemy_list in hits.items():
            for enemy in enemy_list:
                score += 1

                # สร้างเอฟเฟ็กต์ระเบิด (ถ้ามีเฟรม)
                if explosion_frames:
                    expl = ExplosionNode(enemy.rect.center, explosion_frames)
                    explosions.add(expl)

                # เล่นเสียงระเบิดถ้ามี
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
        ฮีโร่ชนศัตรู:
        - ลบ Hero และ Enemy ที่ชน
        - สร้าง ExplosionNode กลางระหว่าง Hero กับ Enemy
        - เล่นเสียงระเบิด
        """
        hits = pygame.sprite.groupcollide(
            heros, enemies,
            True, True,
            pygame.sprite.collide_mask   # ใช้ mask เพราะ Hero / Enemy มาจาก AnimationNode
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

        # ไม่ยุ่งกับ score เพราะส่วนใหญ่คือ game over

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
        ฮีโร่ชนอุกาบาต:
        - ลบ Hero และ Meteor ที่ชน
        - สร้างระเบิด
        - เล่นเสียงระเบิด
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
        กระสุนชนอุกาบาต:
        - ลบ bullet และ meteor ที่ชน
        - สร้างระเบิด
        - เล่นเสียงระเบิด
        - เพิ่มคะแนน
        """
        hits = pygame.sprite.groupcollide(
            bullets, meteors,
            True, True,
            pygame.sprite.collide_rect   # ใช้ rect เหมือน bullet-enemy
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
    # 5) Hero vs Item  → ตรวจ item.type แล้วสร้าง Drone / Shield
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
        - ถ้า item.type == "single" → สร้าง Drone ด้านขวา
        - ถ้า item.type == "double" → สร้าง Drone ซ้าย+ขวา
        - ถ้า item.type == "shield" → สร้าง ShieldNode รอบ Hero
        - เล่นเสียง pickup ถ้ามี
        """
        hits = pygame.sprite.groupcollide(
            heros, items,
            False, True,
            pygame.sprite.collide_mask
        )

        for hero, item_list in hits.items():
            for item in item_list:
                # เล่นเสียงเก็บไอเท็ม (ถ้ามีเสียง)
                if pickup_sound is not None:
                    snd = SoundNode(pickup_sound)
                    sound_effects.add(snd)

                # ตัดสินตามชนิดไอเท็ม
                if item.type == "single":
                    # single → drone ขวา 1 ตัว
                    drone_right = DroneNode(hero, side="right", weapon_type="single")
                    drones.add(drone_right)

                elif item.type == "double":
                    # double → drone ซ้าย + ขวา (นับเป็น double ทั้งคู่)
                    drone_left = DroneNode(hero, side="left", weapon_type="double")
                    drone_right = DroneNode(hero, side="right", weapon_type="double")
                    drones.add(drone_left, drone_right)

                elif item.type == "shield":
                    shield = ShieldNode(hero, max_hp=3)
                    shields.add(shield)

                # ถ้ามีชนิดอื่นในอนาคต เช่น heal, power-up ฯลฯ
                # สามารถเพิ่ม elif เพิ่มได้ที่นี่

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
        - สร้างระเบิด + เสียง
        """
        hits = pygame.sprite.groupcollide(
            shields, meteors,
            False, True,                    # Shield ยังอยู่, Meteor หาย
            pygame.sprite.collide_circle    # ใช้ circle แทน mask
        )

        for shield, meteor_list in hits.items():
            for meteor in meteor_list:
                shield.take_hit(1)

                # เอฟเฟ็กต์ระเบิด
                if explosion_frames:
                    expl = ExplosionNode(meteor.rect.center, explosion_frames)
                    explosions.add(expl)

                # เสียงเอฟเฟ็กต์
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
        - สร้างระเบิด + เสียง
        """
        hits = pygame.sprite.groupcollide(
            shields, enemies,
            False, True,
            pygame.sprite.collide_circle    # ใช้ circle แทน mask
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


