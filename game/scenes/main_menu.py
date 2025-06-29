from engine import Game, Scene
from engine.ui import UIManager, FPSDisplay, Button
from engine.particles import create_fire_emitter
import pygame
import math
import time

class MainMenuScene(Scene):
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
        
        # Create menu buttons
        self.create_menu_buttons()

        # Create fire particle effect that follows the mouse
        self.setup_fire_effects()
        
    def create_menu_buttons(self) -> None:
        """Create the main menu buttons."""
        screen_size = pygame.display.get_surface().get_size()
        button_width = 200
        button_height = 50
        button_spacing = 20
        start_y = screen_size[1] // 2 + 100
        
        # Play button
        play_button = Button(
            pygame.Rect((screen_size[0] - button_width) // 2, start_y, button_width, button_height),
            "Play",
            name="play_button"
        )
        play_button.add_event_handler("clicked", self.on_play_clicked)
        play_button.add_event_handler("mouse_enter", self.on_button_hover)
        play_button.add_event_handler("mouse_leave", self.on_button_leave)
        self.ui_manager.add_widget(play_button)
        
        # Settings button
        settings_button = Button(
            pygame.Rect((screen_size[0] - button_width) // 2, start_y + button_height + button_spacing, button_width, button_height),
            "Settings",
            name="settings_button"
        )
        settings_button.add_event_handler("clicked", self.on_settings_clicked)
        settings_button.add_event_handler("mouse_enter", self.on_button_hover)
        settings_button.add_event_handler("mouse_leave", self.on_button_leave)
        self.ui_manager.add_widget(settings_button)
        
        # Quit button
        quit_button = Button(
            pygame.Rect((screen_size[0] - button_width) // 2, start_y + 2 * (button_height + button_spacing), button_width, button_height),
            "Quit",
            name="quit_button"
        )
        quit_button.add_event_handler("clicked", self.on_quit_clicked)
        quit_button.add_event_handler("mouse_enter", self.on_button_hover)
        quit_button.add_event_handler("mouse_leave", self.on_button_leave)
        self.ui_manager.add_widget(quit_button)
        
    def on_play_clicked(self, event) -> None:
        """Handle play button click."""
        if self.game:
            self.game.push_scene("game_select")
        
    def on_settings_clicked(self, event) -> None:
        """Handle settings button click."""
        if self.game:
            self.game.push_scene("settings")
            
    def on_quit_clicked(self, event) -> None:
        """Handle quit button click."""
        if self.game:
            self.game.quit()
            
    def on_button_hover(self, event) -> None:
        """Handle button mouse enter - change to hand cursor."""
        
    def on_button_leave(self, event) -> None:
        """Handle button mouse leave - restore wizard cursor."""
        
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
        
        
        # Add some sample content using default font
        title_font = Game.get_instance().asset_manager.get_default_font(48)
        title_text = title_font.render("Wicked Wizard Washdown", True, pygame.Color(255, 255, 255))
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 100 - math.sin(time.time() * 1) * 10))
        screen.blit(title_text, title_rect)
        
        # Instructions using smaller default font
        instruction_font = Game.get_instance().asset_manager.get_default_font(18)
        instructions = instruction_font.render("Press ESC to quit", True, pygame.Color(200, 200, 200))
        inst_rect = instructions.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 60))
        screen.blit(instructions, inst_rect)
        
        # Render UI
        if self.ui_manager:
            self.ui_manager.render(screen)
            
        # Render fire effect
        if self.fire_emitter:
            self.fire_emitter.render(screen)

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