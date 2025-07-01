import pygame
from typing import Dict, List, Optional, Callable, Any, Tuple

from engine.ui.widget import Widget

class Label(Widget):
    """
    Text label widget.
    """
    
    def __init__(self, rect: pygame.Rect, text: str = "", 
                 font: pygame.font.Font = None,
                 text_color: pygame.Color = None,
                 background_color: pygame.Color = None,
                 name: str = ""):
        super().__init__(rect, name)
        self.text = text
        
        # Use default font if none provided
        if font is None:
            try:
                from ... import Game
                game = Game.get_instance()
                font = game.assetManager.getDefaultFont()
            except:
                font = pygame.font.Font(None, 24)
                
        self.font = font
        self.text_color = text_color or pygame.Color(255, 255, 255)
        self.background_color = background_color or pygame.Color(0, 0, 0, 0)
        
        # Text alignment
        self.align_x = 'center'  # 'left', 'center', 'right'
        self.align_y = 'center'  # 'top', 'center', 'bottom'
        
        # Cached rendered text
        self._rendered_text: Optional[pygame.Surface] = None
        self._last_text = ""
        
    def set_text(self, text: str) -> None:
        """Set the label text."""
        if text != self.text:
            self.text = text
            self._rendered_text = None  # Invalidate cache
            
    def _render_text(self) -> pygame.Surface:
        """Render the text surface."""
        if self._rendered_text is None or self._last_text != self.text:
            self._rendered_text = self.font.render(self.text, True, self.text_color)
            self._last_text = self.text
        return self._rendered_text
        
    def render(self, screen: pygame.Surface) -> None:
        """Render the label."""
        if not self.visible:
            return
            
        world_rect = self.get_world_rect()
        
        # Draw background
        if self.background_color.a > 0:
            if self.background_color.a < 255:
                surf = pygame.Surface((world_rect.width, world_rect.height), pygame.SRCALPHA)
                surf.fill(self.background_color)
                screen.blit(surf, world_rect.topleft)
            else:
                pygame.draw.rect(screen, self.background_color, world_rect)
                
        # Draw text
        if self.text:
            text_surface = self._render_text()
            text_rect = text_surface.get_rect()
            
            # Align horizontally
            if self.align_x == 'left':
                text_rect.left = world_rect.left + self.padding.left
            elif self.align_x == 'right':
                text_rect.right = world_rect.right - self.padding.right
            else:  # center
                text_rect.centerx = world_rect.centerx
                
            # Align vertically
            if self.align_y == 'top':
                text_rect.top = world_rect.top + self.padding.top
            elif self.align_y == 'bottom':
                text_rect.bottom = world_rect.bottom - self.padding.bottom
            else:  # center
                text_rect.centery = world_rect.centery
                
            screen.blit(text_surface, text_rect)
            
        # Render children
        for child in self.children:
            child.render(screen)