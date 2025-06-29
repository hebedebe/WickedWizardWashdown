"""
Text rendering component for actors.
"""
import pygame
from engine.actor import Component


class TextComponent(Component):
    """Component for rendering text that can be animated."""
    
    def __init__(self, text: str = "", font: pygame.font.Font = None, 
                 color: pygame.Color = pygame.Color(255, 255, 255),
                 size: int = 24):
        super().__init__()
        self.text = text
        self.font = font
        self.color = color
        self.size = size
        self.surface = None
        self.rect = None
        self.alpha = 255
        self.offset = pygame.Vector2(0, 0)
        
        # Auto-create font if not provided
        if not self.font:
            try:
                # Try to use the game's default font
                from engine import Game
                self.font = Game.get_instance().asset_manager.get_default_font(self.size)
            except:
                # Fallback to pygame default
                self.font = pygame.font.Font(None, self.size)
        
        self._render_text()
        
    def set_text(self, text: str) -> None:
        """Update the text content."""
        self.text = text
        self._render_text()
        
    def set_font(self, font: pygame.font.Font) -> None:
        """Update the font."""
        self.font = font
        self._render_text()
        
    def set_color(self, color: pygame.Color) -> None:
        """Update the text color."""
        self.color = color
        self._render_text()
        
    def set_alpha(self, alpha: int) -> None:
        """Set text transparency (0-255)."""
        self.alpha = max(0, min(255, alpha))
        if self.surface:
            self.surface.set_alpha(self.alpha)
            
    def _render_text(self) -> None:
        """Render the text to a surface."""
        if self.font and self.text:
            self.surface = self.font.render(self.text, True, self.color)
            self.surface.set_alpha(self.alpha)
            self.rect = self.surface.get_rect()
            
    def update(self, dt: float) -> None:
        """Update text position from actor transform."""
        if self.actor and self.rect:
            pos = self.actor.transform.world_position + self.offset
            self.rect.center = (int(pos.x), int(pos.y))
            # Debug: print position updates
            # print(f"Text position: {pos}, Actor position: {self.actor.transform.position}")
            
    def render(self, screen: pygame.Surface) -> None:
        """Render the text to the screen."""
        if self.surface and self.rect:
            screen.blit(self.surface, self.rect)
