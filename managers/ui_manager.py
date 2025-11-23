# managers/ui_manager.py

import pygame
from settings.config import SCREEN_WIDTH


class UIManager:
    """
    จัดการการวาด UI ทั้งหมด:
    - HUD (Stage, Score, Active Item Counts)
    - Boss HP Bar
    - Game Over Screen
    - You Win Screen
    """

    def __init__(self, font_small: pygame.font.Font, font_big: pygame.font.Font):
        self.font_small = font_small
        self.font_big = font_big

    # ----------------- Public API -----------------

    def render(
        self,
        screen: pygame.surface.Surface,
        hero,
        score: int,
        current_stage: int,
        max_stage: int,
        bosses: pygame.sprite.Group,
        game_state: str,
        drones=None,
        shields=None,
    ):
        """
        ฟังก์ชันหลัก เรียกจาก main เพื่อวาด HUD, Boss HP, GameOver / Win
        """
        self._draw_hud(screen, hero, score, current_stage, drones, shields)
        self._draw_boss_hp_bar(screen, bosses)

        if game_state == "GAME_OVER":
            self._draw_game_over(screen, score, current_stage)
        elif game_state == "WIN":
            self._draw_game_win(screen, score, current_stage)
        elif game_state == "PAUSED":
            self._draw_pause(screen)
        elif game_state == "CONFIRM_QUIT":
            self._draw_confirm_quit(screen)


    # ----------------- Internal helpers -----------------

    def _draw_hud(self, screen, hero, score: int, current_stage: int, drones, shields):
        """
        วาด Stage, Score, และ 'จำนวนไอเท็มที่กำลังทำงานอยู่ในปัจจุบัน'
        เช่น จำนวน Drone, จำนวน Shield, Speed / Laser ที่ Active อยู่
        """
        if drones is None:
            drones = []
        if shields is None:
            shields = []

        hud_y = 10

        # Stage
        text_stage = self.font_small.render(
            f"Stage: {current_stage}", True, (255, 255, 255)
        )
        screen.blit(text_stage, (10, hud_y))

        # Score
        hud_y += 25
        text_score = self.font_small.render(
            f"Score: {score}", True, (255, 255, 255)
        )
        screen.blit(text_score, (10, hud_y))

        # ---------- นับสถานะปัจจุบันของไอเท็ม ----------

        # 1) นับ Drone ที่เป็นของ Hero นี้
        drone_count = 0
        for d in drones:
            owner = getattr(d, "hero", None)
            if owner is hero and d.alive():
                drone_count += 1

        # เดโม่ logic:
        # - single_count = จำนวน Drone ทั้งหมด (ยิงช่วยกี่กระบอก)
        # - double_count = 1 ถ้ามี Drone >= 2 (ซ้าย+ขวาครบ) ไม่งั้น 0
        single_count = drone_count
        double_count = 1 if drone_count >= 2 else 0

        # 2) Shield: จำนวน ShieldNode ที่ล้อม Hero
        shield_count = 0
        for s in shields:
            owner = getattr(s, "hero", None)
            if owner is hero and s.alive():
                shield_count += 1

        # 3) Speed: ใช้ speed_boost_time / speed_multiplier
        speed_boost_time = getattr(hero, "speed_boost_time", 0.0)
        speed_multiplier = getattr(hero, "speed_multiplier", 1.0)
        speed_active = (speed_boost_time > 0.0) or (speed_multiplier > 1.0)
        speed_count = 1 if speed_active else 0

        # 4) Laser: weapon_mode == "laser"
        weapon_mode = getattr(hero, "weapon_mode", "normal")
        laser_active = (weapon_mode == "laser")
        laser_count = 1 if laser_active else 0

        # ---------- วาด HUD แสดงตัวเลข ----------

        hud_y += 25
        # บรรทัดแรก: อาวุธยิง + Shield
        text_weapons_1 = self.font_small.render(
            f"Single: {single_count}  "
            f"Double: {double_count}  "
            f"Shield: {shield_count}",
            True,
            (255, 255, 255),
        )
        screen.blit(text_weapons_1, (10, hud_y))

        # บรรทัดสอง: Buff / Mode พิเศษ
        hud_y += 22
        text_weapons_2 = self.font_small.render(
            f"Speed: {speed_count}  "
            f"Laser: {laser_count}",
            True,
            (255, 255, 255),
        )
        screen.blit(text_weapons_2, (10, hud_y))

    def _draw_boss_hp_bar(
        self,
        screen,
        bosses: pygame.sprite.Group,
    ):
        """
        แสดงแถบพลัง Boss:
        - ถ้ามี Boss อย่างน้อย 1 ตัวใน group → แสดง
        - ถ้าไม่มี Boss → ไม่แสดง
        """
        if len(bosses) == 0:
            return

        boss = next(iter(bosses))

        if not hasattr(boss, "hp") or not hasattr(boss, "max_hp"):
            return
        if boss.max_hp <= 0:
            return

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
        bar_y = 10  # อยู่ด้านบนสุดของหน้าจอ

        # พื้นหลังแถบ (เทาเข้ม)
        pygame.draw.rect(
            screen,
            (40, 40, 40),
            (bar_x, bar_y, bar_width, bar_height),
        )

        # แถบพลังจริง
        pygame.draw.rect(
            screen,
            bar_color,
            (bar_x, bar_y, int(bar_width * ratio), bar_height),
        )

        # กรอบเส้นขาว
        pygame.draw.rect(
            screen,
            (255, 255, 255),
            (bar_x, bar_y, bar_width, bar_height),
            2,
        )

        # ข้อความ Boss HP ตรงกลางแถบ
        hp_text = self.font_small.render(
            f"Boss HP: {boss.hp}/{boss.max_hp}",
            True,
            (255, 255, 255),
        )
        hp_rect = hp_text.get_rect(
            center=(SCREEN_WIDTH // 2, bar_y + bar_height // 2)
        )
        screen.blit(hp_text, hp_rect)

    def _draw_game_over(self, screen, score: int, current_stage: int):
        """วาดหน้าจอ Game Over กลางจอ"""
        game_over_text = self.font_big.render(
            "GAME OVER", True, (255, 50, 50)
        )
        score_text = self.font_small.render(
            f"Final Score: {score}", True, (255, 255, 255)
        )
        stage_text = self.font_small.render(
            f"Reached Stage: {current_stage}", True, (255, 255, 255)
        )
        hint_text = self.font_small.render(
            "Press R to Restart  |  Q to Quit",
            True,
            (255, 255, 0),
        )

        screen_rect = screen.get_rect()
        center_x = screen_rect.centerx
        center_y = screen_rect.centery

        rect_game_over = game_over_text.get_rect(
            center=(center_x, center_y - 40)
        )
        rect_score = score_text.get_rect(center=(center_x, center_y))
        rect_stage = stage_text.get_rect(center=(center_x, center_y + 30))
        rect_hint = hint_text.get_rect(center=(center_x, center_y + 70))

        screen.blit(game_over_text, rect_game_over)
        screen.blit(score_text, rect_score)
        screen.blit(stage_text, rect_stage)
        screen.blit(hint_text, rect_hint)

    def _draw_game_win(self, screen, score: int, current_stage: int):
        """วาดหน้าจอ You Win กลางจอ"""
        win_text = self.font_big.render(
            "YOU WIN!", True, (80, 255, 80)
        )
        score_text = self.font_small.render(
            f"Final Score: {score}", True, (255, 255, 255)
        )
        stage_text = self.font_small.render(
            f"All Stages Cleared ({current_stage})", True, (255, 255, 255)
        )
        hint_text = self.font_small.render(
            "Press R to Play Again  |  Q to Quit",
            True,
            (255, 255, 0),
        )

        screen_rect = screen.get_rect()
        center_x = screen_rect.centerx
        center_y = screen_rect.centery

        rect_win = win_text.get_rect(
            center=(center_x, center_y - 40)
        )
        rect_score = score_text.get_rect(center=(center_x, center_y))
        rect_stage = stage_text.get_rect(center=(center_x, center_y + 30))
        rect_hint = hint_text.get_rect(center=(center_x, center_y + 70))

        screen.blit(win_text, rect_win)
        screen.blit(score_text, rect_score)
        screen.blit(stage_text, rect_stage)
        screen.blit(hint_text, rect_hint)


    def _draw_pause(self, screen):
        """วาดหน้าจอ Pause กลางจอ"""
        pause_text = self.font_big.render(
            "PAUSED", True, (255, 255, 0)
        )
        hint_text1 = self.font_small.render(
            "Press R to Resume", True, (255, 255, 255)
        )
        hint_text2 = self.font_small.render(
            "Press Q to Quit Game", True, (255, 255, 255)
        )

        screen_rect = screen.get_rect()
        center_x = screen_rect.centerx
        center_y = screen_rect.centery

        rect_pause = pause_text.get_rect(center=(center_x, center_y - 40))
        rect_hint1 = hint_text1.get_rect(center=(center_x, center_y))
        rect_hint2 = hint_text2.get_rect(center=(center_x, center_y + 30))

        screen.blit(pause_text, rect_pause)
        screen.blit(hint_text1, rect_hint1)
        screen.blit(hint_text2, rect_hint2)

    def _draw_confirm_quit(self, screen):
        """วาดหน้าจอถามยืนยันออกจากเกม"""
        confirm_text = self.font_big.render(
            "QUIT GAME?", True, (255, 80, 80)
        )
        hint_text1 = self.font_small.render(
            "Press Y to Confirm", True, (255, 255, 255)
        )
        hint_text2 = self.font_small.render(
            "Press N to Cancel", True, (255, 255, 255)
        )

        screen_rect = screen.get_rect()
        center_x = screen_rect.centerx
        center_y = screen_rect.centery

        rect_confirm = confirm_text.get_rect(center=(center_x, center_y - 40))
        rect_hint1 = hint_text1.get_rect(center=(center_x, center_y))
        rect_hint2 = hint_text2.get_rect(center=(center_x, center_y + 30))

        screen.blit(confirm_text, rect_confirm)
        screen.blit(hint_text1, rect_hint1)
        screen.blit(hint_text2, rect_hint2)
