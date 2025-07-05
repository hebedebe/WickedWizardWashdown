import pygame
from engine.core.ui import UIElement

class Button(UIElement):
    def __init__(self, x, y, width, height, text, callback):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, 24)

    def render(self, screen):
        super().render(screen)
        if self.visible:
            text_surface = self.font.render(self.text, True, (255, 255, 255))
            screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()
