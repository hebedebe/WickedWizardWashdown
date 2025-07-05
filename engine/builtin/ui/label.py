import pygame
from engine.core.ui import UIElement

class Label(UIElement):
    def __init__(self, x, y, text, font=None, font_size=24, color=(255, 255, 255)):
        super().__init__(x, y, 0, 0)  # Width and height are dynamic based on text
        self.text = text
        self.font = pygame.font.Font(font, font_size) if font else pygame.font.Font(None, font_size)
        self.color = color

    def render(self, screen):
        if self.visible:
            text_surface = self.font.render(self.text, True, self.color)
            self.rect.width, self.rect.height = text_surface.get_size()
            screen.blit(text_surface, (self.rect.x, self.rect.y))

    def set_text(self, text):
        self.text = text
