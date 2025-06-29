"""
Example showing different FPS display configurations.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
from engine import *
from engine.ui import *

class FPSDemo(Scene):
    """Scene demonstrating different FPS display configurations."""
    
    def __init__(self):
        super().__init__("FPSDemo")
        self.ui_manager = None
        
    def on_enter(self) -> None:
        super().on_enter()
        
        # Setup UI
        screen_size = pygame.display.get_surface().get_size()
        self.ui_manager = UIManager(screen_size)
        
        # Top-left FPS display (default yellow)
        fps_topleft = FPSDisplay(
            pygame.Rect(10, 10, 120, 25),
            name="fps_topleft",
            update_interval=0.1  # Update 10 times per second for smooth updates
        )
        self.ui_manager.add_widget(fps_topleft)
        
        # Top-right FPS display (green, custom styled)
        fps_topright = FPSDisplay(
            pygame.Rect(screen_size[0] - 130, 10, 120, 25),
            name="fps_topright",
            update_interval=0.5  # Update 2 times per second
        )
        fps_topright.text_color = pygame.Color(0, 255, 0)  # Green
        fps_topright.align_x = 'right'
        self.ui_manager.add_widget(fps_topright)
        
        # Bottom-left detailed FPS display
        fps_detailed = FPSDisplay(
            pygame.Rect(10, screen_size[1] - 35, 200, 25),
            name="fps_detailed",
            update_interval=0.25
        )
        fps_detailed.text_color = pygame.Color(255, 100, 255)  # Magenta
        self.ui_manager.add_widget(fps_detailed)
        
        # Custom styling for detailed display
        def update_detailed_fps():
            if fps_detailed.current_fps > 0:
                frame_time_ms = (1.0 / fps_detailed.current_fps) * 1000
                fps_detailed.set_text(f"FPS: {fps_detailed.current_fps:.1f} ({frame_time_ms:.1f}ms)")
        
        # Override the update method to show frame time
        original_update = fps_detailed.update
        def detailed_update(dt):
            original_update(dt)
            if fps_detailed.current_fps > 0:
                frame_time_ms = (1.0 / fps_detailed.current_fps) * 1000
                fps_detailed.set_text(f"FPS: {fps_detailed.current_fps:.1f} ({frame_time_ms:.1f}ms)")
        fps_detailed.update = detailed_update
        
        # Performance indicator
        self.perf_indicator = Label(
            pygame.Rect(screen_size[0] - 150, screen_size[1] - 35, 140, 25),
            "Performance: Good",
            name="perf_indicator"
        )
        self.perf_indicator.text_color = pygame.Color(0, 255, 0)
        self.perf_indicator.align_x = 'right'
        self.ui_manager.add_widget(self.perf_indicator)
        
    def update(self, dt: float) -> None:
        super().update(dt)
        
        # Update UI
        if self.ui_manager:
            self.ui_manager.update(dt)
            
        # Update performance indicator based on FPS
        fps_topleft = self.ui_manager.find_widget("fps_topleft")
        if fps_topleft and fps_topleft.current_fps > 0:
            fps = fps_topleft.current_fps
            if fps >= 55:
                self.perf_indicator.set_text("Performance: Excellent")
                self.perf_indicator.text_color = pygame.Color(0, 255, 0)  # Green
            elif fps >= 45:
                self.perf_indicator.set_text("Performance: Good")
                self.perf_indicator.text_color = pygame.Color(255, 255, 0)  # Yellow
            elif fps >= 25:
                self.perf_indicator.set_text("Performance: Fair")
                self.perf_indicator.text_color = pygame.Color(255, 165, 0)  # Orange
            else:
                self.perf_indicator.set_text("Performance: Poor")
                self.perf_indicator.text_color = pygame.Color(255, 0, 0)  # Red
            
    def render(self, screen: pygame.Surface) -> None:
        # Gradient background
        self.background_color = pygame.Color(20, 25, 35)
        super().render(screen)
        
        # Add some content
        font = pygame.font.Font(None, 36)
        title = font.render("FPS Display Demo", True, pygame.Color(255, 255, 255))
        title_rect = title.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(title, title_rect)
        
        # Instructions
        small_font = pygame.font.Font(None, 24)
        instructions = [
            "Multiple FPS displays with different update rates and styles",
            "Top-left: Fast updates (10/sec)",
            "Top-right: Slow updates (2/sec)",  
            "Bottom-left: Detailed with frame time",
            "Bottom-right: Performance indicator",
            "",
            "Press ESC to quit"
        ]
        
        y_offset = 150
        for instruction in instructions:
            if instruction:  # Skip empty lines
                text = small_font.render(instruction, True, pygame.Color(200, 200, 200))
                text_rect = text.get_rect(center=(screen.get_width() // 2, y_offset))
                screen.blit(text, text_rect)
            y_offset += 30
            
        # Render UI
        if self.ui_manager:
            self.ui_manager.render(screen)
            
    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        
        # Handle UI events
        if self.ui_manager:
            if self.ui_manager.handle_event(event):
                return
                
        # Handle other events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.game:
                    self.game.quit()

def main():
    """Main function to run the FPS demo."""
    # Create game
    game = Game(800, 600, "FPS Display Demo")
    
    # Create and add the demo scene
    demo_scene = FPSDemo()
    game.add_scene("fps_demo", demo_scene)
    game.load_scene("fps_demo")
    
    # Run the game
    game.run()

if __name__ == "__main__":
    main()
