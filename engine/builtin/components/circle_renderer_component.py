import pygame

from engine.core.component import Component

class CircleRendererComponent(Component):
    def __init__(self, radius=25, color=(255,255,255,255)):
        super().__init__()
        self.radius = radius
        self.color = color

    def render(self, surface):
        pygame.draw.circle(surface, self.color, self.actor.screenPosition, self.radius)