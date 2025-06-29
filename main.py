from engine import Game, Scene, Actor, Component, InputManager, AssetManager, NetworkManager
from engine.ui import UIManager, FPSDisplay
import pygame

class MainGameScene(Scene):
    """Main game scene with FPS display."""
    
    def __init__(self):
        super().__init__("MainGame")
        self.ui_manager = None
        self.fps_display = None
        
    def on_enter(self) -> None:
        super().on_enter()
        
        # Setup UI
        screen_size = pygame.display.get_surface().get_size()
        self.ui_manager = UIManager(screen_size)
        
        # Create FPS display in top-left corner
        self.fps_display = FPSDisplay(
            pygame.Rect(10, 10, 100, 25),  # x, y, width, height
            name="fps_counter",
            update_interval=0.25  # Update 4 times per second
        )
        self.ui_manager.add_widget(self.fps_display)
        
    def update(self, dt: float) -> None:
        super().update(dt)
        
        # Update UI
        if self.ui_manager:
            self.ui_manager.update(dt)
            
    def render(self, screen: pygame.Surface) -> None:
        # Clear screen with a nice background
        self.background_color = pygame.Color(20, 30, 40)
        super().render(screen)
        
        # Add some sample content
        font = pygame.font.Font(None, 48)
        title_text = font.render("Wicked Wizard Washdown", True, pygame.Color(255, 255, 255))
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(title_text, title_rect)
        
        # Instructions
        small_font = pygame.font.Font(None, 24)
        instructions = small_font.render("Press ESC to quit", True, pygame.Color(200, 200, 200))
        inst_rect = instructions.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 60))
        screen.blit(instructions, inst_rect)
        
        # Render UI (including FPS display)
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

if __name__ == "__main__":
    game = Game(800, 600, "Wicked Wizard Washdown")
    
    # Create and add the main scene
    main_scene = MainGameScene()
    game.add_scene("main", main_scene)
    game.load_scene("main")
    
    game.run()