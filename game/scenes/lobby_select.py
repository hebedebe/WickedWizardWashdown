from engine import Game, Scene
from engine.ui import UIManager, Button, Label
import pygame


class LobbySelectScene(Scene):
    """Scene for selecting or creating lobbies for multiplayer games."""
    
    def __init__(self):
        super().__init__("LobbySelect")
        self.ui_manager = None
        
    def on_enter(self) -> None:
        super().on_enter()
        
        # Setup UI
        screen_size = pygame.display.get_surface().get_size()
        self.ui_manager = UIManager(screen_size)
        
        # Create title
        title_label = Label(
            pygame.Rect((screen_size[0] - 300) // 2, 100, 300, 50),
            "Multiplayer Lobbies",
            name="title_label"
        )
        self.ui_manager.add_widget(title_label)
        
        # Create lobby buttons
        self.create_lobby_buttons()
        
    def create_lobby_buttons(self) -> None:
        """Create buttons for lobby actions."""
        screen_size = pygame.display.get_surface().get_size()
        button_width = 250
        button_height = 50
        button_spacing = 20
        start_y = screen_size[1] // 2 - 50
        
        # Create Lobby button
        create_lobby_button = Button(
            pygame.Rect((screen_size[0] - button_width) // 2, start_y, button_width, button_height),
            "Create Lobby",
            name="create_lobby_button"
        )
        create_lobby_button.add_event_handler("clicked", self.on_create_lobby_clicked)
        self.ui_manager.add_widget(create_lobby_button)
        
        # Join Lobby button
        join_lobby_button = Button(
            pygame.Rect((screen_size[0] - button_width) // 2, start_y + button_height + button_spacing, 
                       button_width, button_height),
            "Join Lobby",
            name="join_lobby_button"
        )
        join_lobby_button.add_event_handler("clicked", self.on_join_lobby_clicked)
        self.ui_manager.add_widget(join_lobby_button)
        
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
        
    def on_create_lobby_clicked(self, event) -> None:
        """Handle create lobby button click."""
        if self.game:
            # For now, just go to lobby scene as host
            self.game.load_scene("lobby")
            
    def on_join_lobby_clicked(self, event) -> None:
        """Handle join lobby button click."""
        if self.game:
            # For now, just go to lobby scene as client
            self.game.load_scene("lobby")
            
    def on_back_clicked(self, event) -> None:
        """Handle back button click."""
        if self.game:
            self.game.pop_scene()
            
    def update(self, dt: float) -> None:
        super().update(dt)
        
        if self.ui_manager:
            self.ui_manager.update(dt)
            
    def render(self, screen: pygame.Surface) -> None:
        # Dark purple background
        self.background_color = pygame.Color(30, 20, 50)
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