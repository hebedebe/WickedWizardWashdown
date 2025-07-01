import pygame
from ..widget import Widget, WidgetState

class Button(Widget):
    """
    Clickable button widget.
    """
    
    def __init__(self, rect: pygame.Rect, text: str = "",
                 font: pygame.font.Font = None,
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
        
        # State-based colors
        self.colors = {
            WidgetState.NORMAL: {
                'background': pygame.Color(100, 100, 100),
                'text': pygame.Color(255, 255, 255),
                'border': pygame.Color(150, 150, 150)
            },
            WidgetState.HOVER: {
                'background': pygame.Color(120, 120, 120),
                'text': pygame.Color(255, 255, 255),
                'border': pygame.Color(200, 200, 200)
            },
            WidgetState.PRESSED: {
                'background': pygame.Color(80, 80, 80),
                'text': pygame.Color(255, 255, 255),
                'border': pygame.Color(100, 100, 100)
            },
            WidgetState.DISABLED: {
                'background': pygame.Color(60, 60, 60),
                'text': pygame.Color(100, 100, 100),
                'border': pygame.Color(80, 80, 80)
            }
        }
        
        self.border_width = 2
        
    def set_text(self, text: str) -> None:
        """Set button text."""
        self.text = text
        
    def render(self, screen: pygame.Surface) -> None:
        """Render the button."""
        if not self.visible:
            return
            
        world_rect = self.get_world_rect()
        state = WidgetState.DISABLED if not self.enabled else self.state
        colors = self.colors[state]
        
        # Draw background
        pygame.draw.rect(screen, colors['background'], world_rect)
        
        # Draw border
        if self.border_width > 0:
            pygame.draw.rect(screen, colors['border'], world_rect, self.border_width)
            
        # Draw text
        if self.text:
            text_surface = self.font.render(self.text, True, colors['text'])
            text_rect = text_surface.get_rect()
            text_rect.center = world_rect.center
            screen.blit(text_surface, text_rect)
            
        # Render children
        for child in self.children:
            child.render(screen)