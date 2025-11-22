# nodes/explosion_node.py

from nodes.animation_node import AnimationNode

class ExplosionNode(AnimationNode):
    def __init__(self, pos, frames, frame_duration=0.05):
        states = {
            "default": {
                "frames": frames,
                "frame_duration": frame_duration,
                "loop": False,
                "kill_on_end": True,
            }
        }

        super().__init__(states, default_state="default", use_mask=True)
        self.rect.center = pos

    def update(self, dt):
        self.update_animation(dt)
