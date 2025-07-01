import pygame
from .label import Label

class FPSDisplay(Label):
    """
    FPS display widget that automatically updates with current frame rate.
    """
    
    def __init__(self, x: int = 10, y: int = 10, width: int = 100, height: int = 30,
                 font: pygame.font.Font = None, name: str = "fps_display", 
                 update_interval: float = 0.5):
        # Create rect from position and size parameters
        rect = pygame.Rect(x, y, width, height)
        if font is None:
            try:
                from ... import Game
                game = Game._instance
                font = game.assetManager.getDefaultFont()
            except:
                font = pygame.font.Font(None, 24)
        super().__init__(rect, "FPS: --", font, name)
        
        # FPS tracking
        self.frame_times = []
        self.update_interval = update_interval  # How often to update FPS display
        self.last_update = 0
        self.current_fps = 0
        
        # Default styling for FPS display
        self.text_color = pygame.Color(255, 255, 0)  # Yellow text
        self.align_x = 'left'
        self.align_y = 'top'
        
    def update(self, dt: float) -> None:
        """Update FPS calculation and display."""
        super().update(dt)
        
        # Track frame time
        if dt > 0:
            self.frame_times.append(dt)
            
        # Keep only recent frame times (last 60 frames)
        if len(self.frame_times) > 60:
            self.frame_times.pop(0)
            
        # Update display periodically
        self.last_update += dt
        if self.last_update >= self.update_interval and self.frame_times:
            # Calculate average FPS
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            self.current_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
            
            # Update text
            self.set_text(f"FPS: {self.current_fps:.1f}")
            self.last_update = 0
            
    def get_fps(self) -> float:
        """Get the current FPS value."""
        return self.current_fps