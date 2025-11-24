# managers/scene_manager.py

from __future__ import annotations

from typing import Optional, TYPE_CHECKING
import pygame

from settings.game_constants import (
    GAME_STATE_PLAYING,
    GAME_STATE_GAME_OVER,
    GAME_STATE_WIN,
    GAME_STATE_PAUSED,
)

if TYPE_CHECKING:
    from game import Game


class SceneBase:
    """Base class ของทุก Scene"""

    name: str = "BASE"

    def __init__(self, game: Game):
        self.game = game

    # 3 เมธอดหลักที่ SceneManager จะเรียก
    def handle_input(self) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        pass

    # hook เวลาเปลี่ยน Scene
    def on_enter(self, previous: Optional["SceneBase"]) -> None:
        pass

    def on_exit(self, next_scene: Optional["SceneBase"]) -> None:
        pass


class SceneManager:
    """
    จัดการ Scene ปัจจุบัน
    """

    def __init__(self, game: Game):
        self.game = game
        self.current_scene: Optional[SceneBase] = None

    def change_scene(self, scene: SceneBase):
        if self.current_scene is not None:
            self.current_scene.on_exit(scene)
        previous = self.current_scene
        self.current_scene = scene
        self.current_scene.on_enter(previous)

    def update(self, dt: float):
        if self.current_scene is None:
            return
        self.current_scene.handle_input()
        self.current_scene.update(dt)

    def render(self, screen: pygame.Surface):
        if self.current_scene is None:
            return
        self.current_scene.render(screen)

    @property
    def is_playing(self) -> bool:
        return isinstance(self.current_scene, GameScene)


# --------------------------------------------------
# 1) MenuScene – หน้ากดเริ่มเกม
# --------------------------------------------------

class MenuScene(SceneBase):
    name = "MENU"

    def __init__(self, game: Game):
        super().__init__(game)
        self.title_font = pygame.font.Font(None, 72)
        self.hint_font = pygame.font.Font(None, 32)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        # Enter หรือ Space → เริ่มเกมใหม่
        if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
            self.game.start_new_game()

    def update(self, dt: float):
        # ให้ background ขยับสวย ๆ
        self.game.background.update(dt)

    def render(self, screen: pygame.Surface):
        screen.fill((0, 0, 0))
        self.game.background.draw(screen)

        center_x = screen.get_rect().centerx
        center_y = screen.get_rect().centery

        title = self.title_font.render("SPACE SHOOTER", True, (255, 255, 255))
        hint1 = self.hint_font.render(
            "Press ENTER or SPACE to Start",
            True,
            (255, 255, 0),
        )

        screen.blit(title, title.get_rect(center=(center_x, center_y - 40)))
        screen.blit(hint1, hint1.get_rect(center=(center_x, center_y + 20)))


# --------------------------------------------------
# 2) GameScene – ขณะเล่นเกม
# --------------------------------------------------

class GameScene(SceneBase):
    name = "GAME"

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # P = Pause
        if keys[pygame.K_p]:
            self.game.game_state = GAME_STATE_PAUSED
            self.game.scene_manager.change_scene(PauseScene(self.game))

    def update(self, dt: float):
        # ถ้าเกมชนะแล้ว / Game Over แล้ว → เปลี่ยน Scene ตาม state
        if self.game.game_state == GAME_STATE_GAME_OVER:
            self.game.scene_manager.change_scene(GameOverScene(self.game))
            return

        if self.game.game_state == GAME_STATE_WIN:
            # ใช้ GameOverScene เดิมในการแสดง You Win ก็ได้
            self.game.scene_manager.change_scene(GameOverScene(self.game))
            return

        # Logic หลักตอนเล่นเกม
        self.game.update_world_playing(dt)

    def render(self, screen: pygame.Surface):
        # ขณะเล่นเกม → ให้ UIManager รู้ว่าเป็น PLAYING
        self.game.draw_world(GAME_STATE_PLAYING)


# --------------------------------------------------
# 3) PauseScene – หยุดเกมชั่วคราว
# --------------------------------------------------

class PauseScene(SceneBase):
    name = "PAUSE"

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # R = Resume
        if keys[pygame.K_r]:
            self.game.game_state = GAME_STATE_PLAYING
            self.game.scene_manager.change_scene(GameScene(self.game))

        # Q = Quit ทั้งเกม
        elif keys[pygame.K_q]:
            self.game.quit()

    def update(self, dt: float):
        # ให้ background ขยับต่อได้ (หรือจะไม่อัปเดตก็ได้)
        self.game.background.update(dt)

    def render(self, screen: pygame.Surface):
        # วาด world ปัจจุบัน + overlay PAUSED
        self.game.draw_world(GAME_STATE_PAUSED)


# --------------------------------------------------
# 4) GameOverScene – แพ้เกม (หรือชนะก็ใช้จอนี้)
# --------------------------------------------------

class GameOverScene(SceneBase):
    name = "GAME_OVER"

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # R = Restart → กลับไปเริ่มเกมใหม่
        if keys[pygame.K_r]:
            self.game.start_new_game()

        # Q = Quit
        elif keys[pygame.K_q]:
            self.game.quit()

    def update(self, dt: float):
        # ไม่อัปเดต world เพิ่มเติม (หรือจะให้ explosion ลอยต่อก็ได้ เพราะ game.update_world_playing ยังไม่ถูกเรียก)
        pass

    def render(self, screen: pygame.Surface):
        # ให้ UIManager แสดง Game Over / You Win ตาม self.game.game_state
        state_for_ui = (
            GAME_STATE_GAME_OVER
            if self.game.game_state != GAME_STATE_WIN
            else GAME_STATE_WIN
        )
        self.game.draw_world(state_for_ui)
