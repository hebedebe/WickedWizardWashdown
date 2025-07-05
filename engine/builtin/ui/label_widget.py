import pygame
from engine.core.ui import UIElement

class Label(UIElement):
    def __init__(self, x, y, text):
        self.text = text
        self.font = pygame.font.Font(None, 24)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        self.rect = text_surface.get_rect(topleft=(x, y))
        self.visible = True

    def render(self, screen):
        if self.visible:
            text_surface = self.font.render(self.text, True, (255, 255, 255))
            screen.blit(text_surface, self.rect.topleft)