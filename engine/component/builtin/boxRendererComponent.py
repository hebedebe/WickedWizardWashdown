# engine/component/builtin/boxRendererComponent.py

from engine.component.component import Component
import pygame

class BoxRendererComponent(Component):
    def __init__(self, size=(50, 50), color=(255, 255, 255)):
        super().__init__()
        self.size = size
        self.color = color

    def render(self, screen, camera):
        if not self.actor or not self.actor.physics:
            return

        body = self.actor.physics.body
        pos = body.position
        angle = body.angle

        width, height = self.size
        center = (int(pos.x), int(pos.y))

        # Create and rotate rectangle surface
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        surf.fill(self.color)
        rotated = pygame.transform.rotate(surf, -angle * 57.2958)  # Radians to degrees
        rect = rotated.get_rect(center=center)

        screen.blit(rotated, rect.topleft)
