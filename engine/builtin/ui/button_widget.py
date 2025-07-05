import pygame
from engine.core.ui import UIElement
from engine.core.asset_manager import AssetManager

class Button(UIElement):
    def __init__(self, x, y, width, height, text, font=None, font_size=24, on_click_callback=None, on_start_hover_callback=None, on_stop_hover_callback=None):
        super().__init__(x, y, width, height)
        self.text = text
        self.on_click_callback = on_click_callback
        self.on_start_hover_callback = on_start_hover_callback
        self.on_stop_hover_callback = on_stop_hover_callback
        self.font = AssetManager().getFont(font, font_size) if font is not None else AssetManager().getDefaultFont(size=font_size)
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
            self.on_click_callback() if self.on_click_callback else None
