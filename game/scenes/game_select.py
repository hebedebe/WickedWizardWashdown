from engine import Game, Scene
from engine.ui import UIManager, Button, Label
import pygame


class GameSelectScene(Scene):
    """Scene for selecting game mode (single player, multiplayer, etc.)."""
    
    def __init__(self):
        super().__init__("GameSelect")
        self.ui_manager = None
        
    def on_enter(self) -> None:
        super().on_enter()
        
        # Setup UI
        screen_size = pygame.display.get_surface().get_size()
        self.ui_manager = UIManager(screen_size)
        
        # Create title
        title_label = Label(
            pygame.Rect((screen_size[0] - 300) // 2, 100, 300, 50),
            "Select Game Mode",
            name="title_label"
        )
        self.ui_manager.add_widget(title_label)
        
        # Create game mode buttons
        self.create_game_mode_buttons()
        
    def create_game_mode_buttons(self) -> None:
        """Create buttons for different game modes."""
        screen_size = pygame.display.get_surface().get_size()
        button_width = 250
        button_height = 50
        button_spacing = 20
        start_y = screen_size[1] // 2 - 50
        
        # Single Player button
        single_player_button = Button(
            pygame.Rect((screen_size[0] - button_width) // 2, start_y, button_width, button_height),
            "Single Player",
            name="single_player_button"
        )
        single_player_button.add_event_handler("clicked", self.on_single_player_clicked)
        self.ui_manager.add_widget(single_player_button)
        
        # Multiplayer button
        multiplayer_button = Button(
            pygame.Rect((screen_size[0] - button_width) // 2, start_y + button_height + button_spacing, 
                       button_width, button_height),
            "Multiplayer",
            name="multiplayer_button"
        )
        multiplayer_button.add_event_handler("clicked", self.on_multiplayer_clicked)
        self.ui_manager.add_widget(multiplayer_button)
        
        # Back button
        back_button = Button(
            pygame.Rect((screen_size[0] - button_width) // 2, 
                       start_y + 2 * (button_height + button_spacing), 
                       button_width, button_height),
            "Back",
            name="back_button"
        )
        back_button.add_event_handler("clicked", self.on_back_clicked)
        self.ui_manager.add_widget(back_button)
        
    def on_single_player_clicked(self, event) -> None:
        """Handle single player button click."""
        if self.game:
            self.game.load_scene("game")
            
    def on_multiplayer_clicked(self, event) -> None:
        """Handle multiplayer button click."""
        if self.game:
            self.game.load_scene("lobby_select")
            
    def on_back_clicked(self, event) -> None:
        """Handle back button click."""
        if self.game:
            self.game.pop_scene()
            
    def update(self, dt: float) -> None:
        super().update(dt)
        
        if self.ui_manager:
            self.ui_manager.update(dt)
            
    def render(self, screen: pygame.Surface) -> None:
        # Dark blue background
        self.background_color = pygame.Color(20, 30, 50)
        super().render(screen)
        
        if self.ui_manager:
            self.ui_manager.render(screen)
            
    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        
        if self.ui_manager:
            if self.ui_manager.handle_event(event):
                return
                
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.game:
                    self.game.pop_scene()