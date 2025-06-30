import pygame
from ..widget import Widget, WidgetState

class Slider(Widget):
    """
    Slider widget for value selection.
    """
    
    def __init__(self, rect: pygame.Rect, min_value: float = 0.0, 
                 max_value: float = 1.0, value: float = 0.5,
                 name: str = ""):
        super().__init__(rect, name)
        self.min_value = min_value
        self.max_value = max_value
        self._value = value
        
        # Visual properties
        self.track_color = pygame.Color(100, 100, 100)
        self.handle_color = pygame.Color(200, 200, 200)
        self.handle_size = 20
        
        # Interaction
        self.dragging = False
        
    @property
    def value(self) -> float:
        """Get the current value."""
        return self._value
        
    @value.setter
    def value(self, val: float) -> None:
        """Set the current value."""
        old_value = self._value
        self._value = max(self.min_value, min(self.max_value, val))
        if old_value != self._value:
            self.emit_event("value_changed", self._value)
            
    def get_handle_rect(self) -> pygame.Rect:
        """Get the handle rectangle."""
        world_rect = self.get_world_rect()
        
        # Calculate handle position
        range_val = self.max_value - self.min_value
        if range_val > 0:
            ratio = (self._value - self.min_value) / range_val
        else:
            ratio = 0
            
        handle_x = world_rect.x + ratio * (world_rect.width - self.handle_size)
        handle_y = world_rect.centery - self.handle_size // 2
        
        return pygame.Rect(handle_x, handle_y, self.handle_size, self.handle_size)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle slider-specific events."""
        if not self.visible or not self.enabled:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pygame.Vector2(event.pos)
                handle_rect = self.get_handle_rect()
                
                if handle_rect.collidepoint(int(mouse_pos.x), int(mouse_pos.y)):
                    self.dragging = True
                    return True
                elif self.contains_point(mouse_pos):
                    # Click on track - move handle to mouse position
                    self._update_value_from_mouse(mouse_pos)
                    self.dragging = True
                    return True
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging:
                self.dragging = False
                return True
                
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_pos = pygame.Vector2(event.pos)
                self._update_value_from_mouse(mouse_pos)
                return True
                
        return super().handle_event(event)
        
    def _update_value_from_mouse(self, mouse_pos: pygame.Vector2) -> None:
        """Update value based on mouse position."""
        world_rect = self.get_world_rect()
        
        # Calculate ratio
        ratio = (mouse_pos.x - world_rect.x) / world_rect.width
        ratio = max(0, min(1, ratio))
        
        # Update value
        new_value = self.min_value + ratio * (self.max_value - self.min_value)
        self.value = new_value
        
    def render(self, screen: pygame.Surface) -> None:
        """Render the slider."""
        if not self.visible:
            return
            
        world_rect = self.get_world_rect()
        
        # Draw track
        track_rect = pygame.Rect(
            world_rect.x, 
            world_rect.centery - 2,
            world_rect.width,
            4
        )
        pygame.draw.rect(screen, self.track_color, track_rect)
        
        # Draw handle
        handle_rect = self.get_handle_rect()
        handle_color = self.handle_color
        
        if self.state == WidgetState.HOVER or self.dragging:
            handle_color = pygame.Color(min(255, handle_color.r + 50),
                                      min(255, handle_color.g + 50),
                                      min(255, handle_color.b + 50))
        elif self.state == WidgetState.PRESSED:
            handle_color = pygame.Color(max(0, handle_color.r - 50),
                                      max(0, handle_color.g - 50),
                                      max(0, handle_color.b - 50))
            
        pygame.draw.circle(screen, handle_color, handle_rect.center, self.handle_size // 2)
        
        # Render children
        for child in self.children:
            child.render(screen)