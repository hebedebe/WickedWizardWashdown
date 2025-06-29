from engine import Game, Scene
from engine.ui import UIManager, Button, Label, TextInput
import pygame

class JoinLobbyScene(Scene):
    """Scene where players can enter lobby details to join."""

    def __init__(self):
        super().__init__("JoinLobbyScene")
        self.ui_manager = None
        self.host_address = "localhost"
        self.port = "7777"
        self.player_name = "Player1"
        
    def on_enter(self) -> None:
        super().on_enter()
        
        # Setup UI
        screen_size = pygame.display.get_surface().get_size()
        self.ui_manager = UIManager(screen_size)
        
        # Create join lobby UI
        self.create_join_ui()
        
    def create_join_ui(self) -> None:
        """Create the join lobby UI elements."""
        screen_size = pygame.display.get_surface().get_size()
        
        # Title label
        title_label = Label(
            pygame.Rect((screen_size[0] - 250) // 2, 80, 250, 50),
            "Join Game Lobby",
            name="title_label"
        )
        self.ui_manager.add_widget(title_label)
        
        # Player name input
        name_label = Label(
            pygame.Rect(150, 180, 150, 30),
            "Player Name:",
            name="name_label"
        )
        self.ui_manager.add_widget(name_label)
        
        name_input = TextInput(
            pygame.Rect(320, 180, 200, 30),
            self.player_name,
            name="name_input"
        )
        name_input.add_event_handler("text_changed", self.on_name_changed)
        self.ui_manager.add_widget(name_input)
        
        # Host address input
        host_label = Label(
            pygame.Rect(150, 230, 150, 30),
            "Host Address:",
            name="host_label"
        )
        self.ui_manager.add_widget(host_label)
        
        host_input = TextInput(
            pygame.Rect(320, 230, 200, 30),
            self.host_address,
            name="host_input"
        )
        host_input.add_event_handler("text_changed", self.on_host_changed)
        self.ui_manager.add_widget(host_input)
        
        # Port input
        port_label = Label(
            pygame.Rect(150, 280, 150, 30),
            "Port:",
            name="port_label"
        )
        self.ui_manager.add_widget(port_label)
        
        port_input = TextInput(
            pygame.Rect(320, 280, 200, 30),
            self.port,
            name="port_input"
        )
        port_input.add_event_handler("text_changed", self.on_port_changed)
        self.ui_manager.add_widget(port_input)
        
        # Connect button
        connect_button = Button(
            pygame.Rect((screen_size[0] - 150) // 2, 360, 150, 50),
            "Connect",
            name="connect_button"
        )
        connect_button.add_event_handler("clicked", self.on_connect_clicked)
        self.ui_manager.add_widget(connect_button)
        
        # Status label for connection feedback
        status_label = Label(
            pygame.Rect((screen_size[0] - 300) // 2, 430, 300, 30),
            "Enter server details and click Connect",
            name="status_label"
        )
        self.ui_manager.add_widget(status_label)
        
        # Back button
        back_button = Button(
            pygame.Rect(50, screen_size[1] - 80, 100, 50),
            "Back",
            name="back_button"
        )
        back_button.add_event_handler("clicked", self.on_back_clicked)
        self.ui_manager.add_widget(back_button)
        
    def on_name_changed(self, event) -> None:
        """Handle player name input change."""
        self.player_name = event.data
        print(f"Player name changed to: {self.player_name}")
        
    def on_host_changed(self, event) -> None:
        """Handle host address input change."""
        self.host_address = event.data
        print(f"Host address changed to: {self.host_address}")
        
    def on_port_changed(self, event) -> None:
        """Handle port input change."""
        self.port = event.data
        print(f"Port changed to: {self.port}")
        
    def on_connect_clicked(self, event) -> None:
        """Handle connect button click."""
        print(f"Attempting to connect to {self.host_address}:{self.port} as {self.player_name}")
        
        # Update status
        status_label = self.ui_manager.find_widget("status_label")
        if status_label:
            status_label.set_text(f"Connecting to {self.host_address}:{self.port}...")
        
        # Get network manager and attempt connection
        from engine.networking import get_network_manager
        network_manager = get_network_manager()
        
        try:
            port_num = int(self.port)
            success = network_manager.connect(self.host_address, port_num)
            
            if success:
                # Set player name in lobby scene
                if self.game:
                    lobby_scene = self.game.scenes.get("lobby")
                    if lobby_scene:
                        lobby_scene.player_name = self.player_name
                        lobby_scene.is_host = False
                    
                    # Go to lobby
                    self.game.push_scene("lobby")
            else:
                if status_label:
                    status_label.set_text("Failed to connect to server")
                    
        except ValueError:
            if status_label:
                status_label.set_text("Invalid port number")
        except Exception as e:
            print(f"Connection error: {e}")
            if status_label:
                status_label.set_text(f"Connection failed: {str(e)}")
                
        # Note: Removed the artificial delay and demo connection
            
    def on_back_clicked(self, event) -> None:
        """Handle back button click."""
        if self.game:
            self.game.pop_scene()
            
    def update(self, dt: float) -> None:
        super().update(dt)
        
        # Update UI
        if self.ui_manager:
            self.ui_manager.update(dt)
            
    def render(self, screen: pygame.Surface) -> None:
        # Clear screen with dark background
        self.background_color = pygame.Color(20, 30, 40)
        super().render(screen)
        
        # Add instructions
        instruction_font = Game.get_instance().asset_manager.get_default_font(14)
        instructions = [
            "Enter the host's IP address or 'localhost' for local play",
            "Default port is 7777 unless the host specifies otherwise",
            "Choose a unique player name for identification"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_text = instruction_font.render(instruction, True, pygame.Color(160, 160, 160))
            inst_rect = inst_text.get_rect(center=(screen.get_width() // 2, 140 + i * 20))
            screen.blit(inst_text, inst_rect)
        
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