from engine import Game, Scene
from engine.rendering.ui import UIManager, Button, Label
import pygame

class MultiplayerSelectScene(Scene):
    """Multiplayer selection scene where players can join or create lobbies."""

    def __init__(self):
        super().__init__("MultiplayerSelectScene")
        self.ui_manager = None
        
    def on_enter(self) -> None:
        super().on_enter()
        
        # Setup UI
        screen_size = pygame.display.get_surface().get_size()
        self.ui_manager = UIManager(screen_size)
        
        # Create multiplayer selection UI
        self.create_multiplayer_ui()
        
    def create_multiplayer_ui(self) -> None:
        """Create the multiplayer selection UI elements."""
        screen_size = pygame.display.get_surface().get_size()
        
        # Title label
        title_label = Label(
            pygame.Rect((screen_size[0] - 300) // 2, 100, 300, 50),
            "Choose Game Mode",
            name="title_label"
        )
        self.ui_manager.add_widget(title_label)
        
        button_width = 250
        button_height = 60
        button_spacing = 30
        start_y = screen_size[1] // 2 - 50
        
        # Host Game button
        host_button = Button(
            pygame.Rect((screen_size[0] - button_width) // 2, start_y, button_width, button_height),
            "Host Game",
            name="host_button"
        )
        host_button.add_event_handler("clicked", self.on_host_clicked)
        host_button.add_event_handler("mouse_enter", self.on_button_hover)
        host_button.add_event_handler("mouse_leave", self.on_button_leave)
        self.ui_manager.add_widget(host_button)
        
        # Join Game button
        join_button = Button(
            pygame.Rect((screen_size[0] - button_width) // 2, start_y + button_height + button_spacing, button_width, button_height),
            "Join Game",
            name="join_button"
        )
        join_button.add_event_handler("clicked", self.on_join_clicked)
        join_button.add_event_handler("mouse_enter", self.on_button_hover)
        join_button.add_event_handler("mouse_leave", self.on_button_leave)
        self.ui_manager.add_widget(join_button)
        
        # Single Player button (local game)
        single_button = Button(
            pygame.Rect((screen_size[0] - button_width) // 2, start_y + 2 * (button_height + button_spacing), button_width, button_height),
            "Single Player",
            name="single_button"
        )
        single_button.add_event_handler("clicked", self.on_single_clicked)
        single_button.add_event_handler("mouse_enter", self.on_button_hover)
        single_button.add_event_handler("mouse_leave", self.on_button_leave)
        self.ui_manager.add_widget(single_button)
        
        # Back button
        back_button = Button(
            pygame.Rect(50, screen_size[1] - 80, 100, 50),
            "Back",
            name="back_button"
        )
        back_button.add_event_handler("clicked", self.on_back_clicked)
        self.ui_manager.add_widget(back_button)
        
        # Status label for showing errors/messages
        status_label = Label(
            pygame.Rect((screen_size[0] - 400) // 2, screen_size[1] - 150, 400, 30),
            "",
            name="status_label"
        )
        self.ui_manager.add_widget(status_label)
        
    def on_host_clicked(self, event) -> None:
        """Handle host game button click."""
        print("Starting as host...")
        
        # Get network manager and attempt to host
        from engine.networking.networking import get_network_manager
        network_manager = get_network_manager()
        
        # Try to start hosting before going to lobby
        success = network_manager.host("localhost", 7777)
        
        if success:
            print("Successfully started hosting on port 7777")
            if self.game:
                # Set lobby scene as host
                lobby_scene = self.game.scenes.get("lobby")
                if lobby_scene:
                    lobby_scene.is_host = True
                    lobby_scene.player_name = "Host"
                
                # Go to lobby as host
                self.game.push_scene("lobby")
        else:
            print("Failed to start hosting - another server may be running")
            # Show error message to user
            status_label = self.ui_manager.find_widget("status_label")
            if status_label:
                status_label.set_text("Error: Cannot host - port already in use!")
        
    def on_join_clicked(self, event) -> None:
        """Handle join game button click."""
        print("Looking to join a game...")
        if self.game:
            # Go to join lobby scene
            self.game.push_scene("join_lobby")
            
    def on_single_clicked(self, event) -> None:
        """Handle single player button click."""
        print("Starting single player game...")
        if self.game:
            # Go directly to game scene
            self.game.push_scene("game")
            
    def on_back_clicked(self, event) -> None:
        """Handle back button click."""
        if self.game:
            self.game.pop_scene()
            
    def on_button_hover(self, event) -> None:
        """Handle button mouse enter."""
        pass
        
    def on_button_leave(self, event) -> None:
        """Handle button mouse leave."""
        pass
        
    def update(self, dt: float) -> None:
        super().update(dt)
        
        # Update UI
        if self.ui_manager:
            self.ui_manager.update(dt)
            
    def render(self, screen: pygame.Surface) -> None:
        # Clear screen with dark background
        self.background_color = pygame.Color(25, 35, 45)
        super().render(screen)
        
        # Add descriptive text
        description_font = Game.get_instance().asset_manager.get_default_font(16)
        descriptions = [
            "Host Game: Create a new multiplayer session",
            "Join Game: Connect to an existing session",
            "Single Player: Play offline by yourself"
        ]
        
        for i, desc in enumerate(descriptions):
            desc_text = description_font.render(desc, True, pygame.Color(180, 180, 180))
            desc_rect = desc_text.get_rect(center=(screen.get_width() // 2, 200 + i * 25))
            screen.blit(desc_text, desc_rect)
        
        # Render UI
        if self.ui_manager:
            self.ui_manager.render(screen)
            
    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        
        # Handle UI events
        if self.ui_manager:
            if self.ui_manager.handle_event(event):
                return
                
        # Handle escape key to go back
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.game:
                    self.game.pop_scene()