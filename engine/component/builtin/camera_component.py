import pygame
from ..component import Component

class CameraComponent(Component):
    """Camera component"""
    def __init__(self, interpolate=False, smoothing=10):
        super().__init__()
        self.position = pygame.Vector2()
        self.interpolate = interpolate
        self.smoothing = smoothing

    def lateUpdate(self, delta_time):
        if self.interpolate:
            self.position = pygame.Vector2.lerp(self.position, self.actor.transform.position, self.smoothing * delta_time)
        else:
            self.position = self.actor.transform.position
            
        self.getScene.worldOffset = self.position - pygame.Vector2(self.getGame.width//2, self.getGame.height//2) # type: ignore
        return super().lateUpdate(delta_time)