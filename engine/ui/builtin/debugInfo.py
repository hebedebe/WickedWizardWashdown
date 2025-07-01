import pygame
from .label import Label

class DebugInfo(Label):
    def __init__(self, scene, balls, x=10, y=40, width=300, height=60, font=None, name="debug_info"):
        rect = pygame.Rect(x, y, width, height)
        super().__init__(rect, "", font, name)
        self.scene = scene
        self.balls = balls
        self.text_color = pygame.Color(255, 255, 255)
        self.align_x = 'left'
        self.align_y = 'top'

    def update(self, dt: float) -> None:
        super().update(dt)
        mouse_pos = pygame.mouse.get_pos()
        self.set_text(f"Balls: {len(self.balls)}\nMouse: {mouse_pos}")
