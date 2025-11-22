# nodes/animation_node.py

import pygame

class AnimationNode(pygame.sprite.Sprite):
    def __init__(self, states, default_state="default", use_mask=True):
        """
        states: dict รูปแบบ
            {
                "state_name": {
                    "frames": [Surface, ...],
                    "frame_duration": 0.1,
                    "loop": True/False,
                    "kill_on_end": True/False,
                },
                ...
            }
        default_state: ชื่อ state เริ่มต้น เช่น "default"
        use_mask: ถ้า True จะสร้าง mask จากภาพ (ใช้กับ collide_mask)
        """
        super().__init__()

        if default_state not in states:
            raise ValueError(f"default_state '{default_state}' not in states")

        self.states = states
        self.current_state = default_state
        self.use_mask = use_mask

        self._apply_state(self.current_state, reset_frame=True)

    def _apply_state(self, state_name, reset_frame=False):
        data = self.states[state_name]
        self.frames = data["frames"]
        self.frame_duration = data.get("frame_duration", 0.1)
        self.loop = data.get("loop", True)
        self.kill_on_end = data.get("kill_on_end", False)

        if not self.frames:
            raise ValueError(f"State '{state_name}' has no frames")

        if reset_frame or not hasattr(self, "index"):
            self.index = 0

        # เซ็ตภาพเริ่มต้น รักษา center ถ้าเคยมี rect แล้ว
        if hasattr(self, "rect"):
            old_center = self.rect.center
            self.image = self.frames[self.index]
            self.rect = self.image.get_rect(center=old_center)
        else:
            self.image = self.frames[self.index]
            self.rect = self.image.get_rect()

        self.time_since_last_frame = 0.0
        self.finished = False

        if self.use_mask:
            self.mask = pygame.mask.from_surface(self.image)
        else:
            self.mask = None

    def set_state(self, state_name, reset_frame=True):
        """เปลี่ยน state ปัจจุบัน"""
        if state_name == self.current_state and not reset_frame:
            return

        if state_name not in self.states:
            raise ValueError(f"Unknown state '{state_name}'")

        self.current_state = state_name
        self._apply_state(state_name, reset_frame=reset_frame)

    def add_state(self, name, frames, frame_duration=0.1, loop=True, kill_on_end=False):
        self.states[name] = {
            "frames": frames,
            "frame_duration": frame_duration,
            "loop": loop,
            "kill_on_end": kill_on_end,
        }

    def update_animation(self, dt):
        """อัปเดตเฟรมของ state ปัจจุบัน (ให้คลาสลูกเรียกใน update())"""
        if getattr(self, "finished", False):
            return

        self.time_since_last_frame += dt
        if self.time_since_last_frame < self.frame_duration:
            return

        self.time_since_last_frame = 0.0
        self.index += 1

        if self.index >= len(self.frames):
            if self.loop:
                self.index = 0
            else:
                self.finished = True
                if self.kill_on_end:
                    self.kill()
                return

        old_center = self.rect.center
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=old_center)

        if self.use_mask:
            self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt, *args, **kwargs):
        """default behavior: แอนิเมชันอย่างเดียว (คลาสลูก override เองได้)"""
        self.update_animation(dt)
