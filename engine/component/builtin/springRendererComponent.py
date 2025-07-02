import pygame
from .. import Component

class SpringRendererComponent(Component):
    def __init__(self, get_other_actor, get_spring):
        super().__init__()
        self.get_other_actor = get_other_actor  # function returning the other actor
        self.get_spring = get_spring  # function returning the spring constraint

    def render(self, surface):
        other = self.get_other_actor()
        spring = self.get_spring()
        if not other or not spring:
            return
        pos1 = self.actor.transform.position
        pos2 = other.transform.position
        # Calculate spring stress (stretch/compression)
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        dist = (dx*dx + dy*dy) ** 0.5
        rest_length = spring.constraint.rest_length
        # Stress: 0 = rest, >0 = stretched, <0 = compressed
        stress = dist - rest_length
        # Color: blue (compressed), green (rest), red (stretched)
        if abs(stress) < 2:
            color = (0, 255, 0)
        elif stress > 0:
            # interpolate green to red
            t = min(stress / rest_length, 1)
            color = (int(0 + 255 * t), int(255 * (1-t)), 0)
        else:
            # interpolate green to blue
            t = min(-stress / rest_length, 1)
            color = (0, int(255 * (1-t)), int(255 * t))
        pygame.draw.line(surface, color, pos1, pos2, 4)