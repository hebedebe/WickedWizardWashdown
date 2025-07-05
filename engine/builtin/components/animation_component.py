import pygame
from ...core.world.component import Component
from ...animation.animation import Frame, Animation

class AnimationComponent(Component):
    def __init__(self, frames):
        super().__init__()
        self.animation = Animation(frames)
        self.timer = 0
        self.frame_index = 0
    
    def update(self, delta_time):
        super().update(delta_time)
        self.timer += delta_time
        self.frame_index = int(self.timer // self.animation.frame_time)%self.animation.numFrames

    @property
    def currentFrame(self):
        return self.animation.frames[self.frame_index].surface

    def render(self, surface: pygame.Surface):
        super().render(surface)
        surface.blit(self.currentFrame, self.actor.screenPosition)
