import pygame
from engine.core.ui import UIElement

class Button(UIElement):
    def __init__(self, x, y, width, height, text, callback):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, 24)
        self.hovered = False

    def render(self, screen):
        super().render(screen)
        if self.visible:
            color = (200, 200, 200) if self.hovered else (255, 255, 255)
            text_surface = self.font.render(self.text, True, color)
            pygame.draw.rect(screen, (100, 100, 100) if self.hovered else (50, 50, 50), self.rect)
            screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()
