from engine import Game, Scene, Actor, Component, InputManager, AssetManager, NetworkManager
from engine.ui import UIManager, FPSDisplay
from engine.particles import create_fire_emitter
import pygame

class MainGameScene(Scene):
    """Main game scene with FPS display."""
    
    def __init__(self):
        super().__init__("MainGame")
        self.ui_manager = None
        self.fps_display = None
        
        # Fire particle effect for magical ambiance
        self.fire_emitter = None
        
    def on_enter(self) -> None:
        super().on_enter()
        
        # Set the default font for the application
        Game.get_instance().asset_manager.set_default_font("alagard", 24)
        
        # Setup UI
        screen_size = pygame.display.get_surface().get_size()
        self.ui_manager = UIManager(screen_size)
        
        # Create FPS display - now uses the default font automatically!
        self.fps_display = FPSDisplay(
            pygame.Rect(10, 10, 100, 25),  # x, y, width, height
            name="fps_counter",
            update_interval=0.25  # Update 4 times per second
        )
        self.ui_manager.add_widget(self.fps_display)
        
        # Create fire particle effect that follows the mouse
        self.setup_fire_effects()
        
    def setup_fire_effects(self) -> None:
        """Setup fire particle effect that follows the mouse cursor."""
        # Start with fire emitter at screen center, it will follow mouse position
        mouse_pos = pygame.mouse.get_pos()
        self.fire_emitter = create_fire_emitter(pygame.Vector2(mouse_pos))
        
    def update(self, dt: float) -> None:
        super().update(dt)
        
        # Update UI
        if self.ui_manager:
            self.ui_manager.update(dt)
            
        # Update fire emitter to follow mouse position
        if self.fire_emitter:
            mouse_pos = pygame.mouse.get_pos()
            self.fire_emitter.position = pygame.Vector2(mouse_pos)
            self.fire_emitter.update(dt)
            
    def render(self, screen: pygame.Surface) -> None:
        # Clear screen with a nice background
        self.background_color = pygame.Color(20, 30, 40)
        super().render(screen)
        
        # Render fire effect first (behind text and UI)
        if self.fire_emitter:
            self.fire_emitter.render(screen)
        
        # Add some sample content using default font
        title_font = Game.get_instance().asset_manager.get_default_font(48)
        title_text = title_font.render("Wicked Wizard Washdown", True, pygame.Color(255, 255, 255))
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(title_text, title_rect)
        
        # Instructions using smaller default font
        instruction_font = Game.get_instance().asset_manager.get_default_font(18)
        instructions = instruction_font.render("Press ESC to quit", True, pygame.Color(200, 200, 200))
        inst_rect = instructions.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 60))
        screen.blit(instructions, inst_rect)
        
        # Render UI on top (including FPS display)
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