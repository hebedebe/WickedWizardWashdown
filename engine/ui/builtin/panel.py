import pygame
from engine.ui.widget import Widget
from engine.ui.event import UIEvent

class Panel(Widget):
    """
    Basic panel widget for layout and grouping.
    """
    
    def __init__(self, rect: pygame.Rect, name: str = "", 
                 background_color: pygame.Color = None,
                 border_color: pygame.Color = None,
                 border_width: int = 0):
        super().__init__(rect, name)
        self.background_color = background_color or pygame.Color(100, 100, 100, 200)
        self.border_color = border_color or pygame.Color(200, 200, 200)
        self.border_width = border_width
        
    def render(self, screen: pygame.Surface) -> None:
        """Render the panel."""
        if not self.visible:
            return
            
        world_rect = self.get_world_rect()
        
        # Draw background
        if self.background_color.a > 0:
            if self.background_color.a < 255:
                # Create surface for alpha blending
                surf = pygame.Surface((world_rect.width, world_rect.height), pygame.SRCALPHA)
                surf.fill(self.background_color)
                screen.blit(surf, world_rect.topleft)
            else:
                pygame.draw.rect(screen, self.background_color, world_rect)
                
        # Draw border
        if self.border_width > 0:
            pygame.draw.rect(screen, self.border_color, world_rect, self.border_width)
            
        # Render children
        for child in self.children:
            child.render(screen)