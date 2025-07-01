import pygame

from engine.component.component import Component

class CircleRendererComponent(Component):
    def __init__(self, radius, color):
        super().__init__()
        self.radius = radius
        self.color = color

    def render(self, surface):
        pygame.draw.circle(surface, self.color, self.actor.transform.position, self.radius)