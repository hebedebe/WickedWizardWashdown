from engine import Game, Scene
from engine.ui import UIManager, Button, Label, TextInput
import pygame


class JoinLobbyScene(Scene):
    """Scene for entering IP and port to join a lobby."""
    
    def __init__(self):
        super().__init__("JoinLobby")
        self.ui_manager = None
        self.ip_input = None
        self.port_input = None
        
    def on_enter(self) -> None:
        super().on_enter()
        
        # Setup UI
        screen_size = pygame.display.get_surface().get_size()
        self.ui_manager = UIManager(screen_size)
        
        # Create title
        title_label = Label(
            pygame.Rect((screen_size[0] - 300) // 2, 80, 300, 50),
            "Join Lobby",
            name="title_label"
        )
        self.ui_manager.add_widget(title_label)
        
        # Create subtitle
        subtitle_label = Label(
            pygame.Rect((screen_size[0] - 400) // 2, 130, 400, 30),
            "Enter server details to connect",
            name="subtitle_label"
        )
        self.ui_manager.add_widget(subtitle_label)
        
        # Create input fields
        self.create_input_fields()
        
    def create_input_fields(self) -> None:
        """Create input fields for IP and port."""
        screen_size = pygame.display.get_surface().get_size()
        input_width = 250
        input_height = 45
        label_height = 30
        spacing = 20
        start_y = screen_size[1] // 2 - 80
        
        # IP Address Label
        ip_label = Label(
            pygame.Rect((screen_size[0] - input_width) // 2, start_y, input_width, label_height),
            "Server IP Address:",
            name="ip_label"
        )
        self.ui_manager.add_widget(ip_label)
        
        # IP Address Input
        self.ip_input = TextInput(
            pygame.Rect((screen_size[0] - input_width) // 2, start_y + label_height + 5, 
                       input_width, input_height),
            initial_text="localhost",
            placeholder="Enter IP address (e.g., 192.168.1.100)",
            name="ip_input"
        )
        self.ip_input.add_event_handler("enter_pressed", self.on_connect_pressed)
        self.ui_manager.add_widget(self.ip_input)
        
        # Port Label
        port_label_y = start_y + label_height + input_height + spacing + 5
        port_label = Label(
            pygame.Rect((screen_size[0] - input_width) // 2, port_label_y, input_width, label_height),
            "Port:",
            name="port_label"
        )
        self.ui_manager.add_widget(port_label)
        
        # Port Input
        self.port_input = TextInput(
            pygame.Rect((screen_size[0] - input_width) // 2, port_label_y + label_height + 5, 
                       input_width, input_height),
            initial_text="12345",
            placeholder="Enter port number (1-65535)",
            name="port_input"
        )
        self.port_input.add_event_handler("enter_pressed", self.on_connect_pressed)
        # Only allow numbers for port
        self.port_input.allowed_chars = set("0123456789")
        self.port_input.max_length = 5
        self.ui_manager.add_widget(self.port_input)
        
        # Create buttons
        self.create_buttons(port_label_y + label_height + input_height + spacing + 15)
        
    def create_buttons(self, start_y: int) -> None:
        """Create action buttons."""
        screen_size = pygame.display.get_surface().get_size()
        button_width = 120
        button_height = 45
        button_spacing = 20
        
        # Calculate button positions for centering
        total_width = 2 * button_width + button_spacing
        start_x = (screen_size[0] - total_width) // 2
        
        # Connect Button
        connect_button = Button(
            pygame.Rect(start_x, start_y, button_width, button_height),
            "Connect",
            name="connect_button"
        )
        connect_button.add_event_handler("clicked", self.on_connect_pressed)
        self.ui_manager.add_widget(connect_button)
        
        # Back Button
        back_button = Button(
            pygame.Rect(start_x + button_width + button_spacing, start_y, 
                       button_width, button_height),
            "Back",
            name="back_button"
        )
        back_button.add_event_handler("clicked", self.on_back_clicked)
        self.ui_manager.add_widget(back_button)
        
        # Status label for connection feedback
        status_label = Label(
            pygame.Rect((screen_size[0] - 400) // 2, start_y + button_height + 20, 400, 30),
            "",
            name="status_label"
        )
        self.ui_manager.add_widget(status_label)
        
    def on_connect_pressed(self, event=None) -> None:
        """Handle connect button click or enter key in input fields."""
        if not self.ip_input or not self.port_input:
            return
            
        ip_address = self.ip_input.get_text().strip()
        port_text = self.port_input.get_text().strip()
        
        # Validate inputs
        if not ip_address:
            self.show_status("Please enter an IP address", error=True)
            return
            
        if not port_text:
            self.show_status("Please enter a port number", error=True)
            return
            
        try:
            port = int(port_text)
            if port < 1 or port > 65535:
                self.show_status("Port must be between 1 and 65535", error=True)
                return
        except ValueError:
            self.show_status("Port must be a valid number", error=True)
            return
        
        # Attempt to connect
        self.show_status(f"Connecting to {ip_address}:{port}...")
        
        if self.game and self.game.network_manager:
            # Try to connect to the server
            success = self.game.network_manager.connect_to_server(ip_address, port, "player")
            
            if success:
                self.show_status("Connected successfully!")
                # Small delay to show success message
                pygame.time.wait(500)
                self.game.load_scene("lobby")
            else:
                self.show_status(f"Failed to connect to {ip_address}:{port}", error=True)
        else:
            # For testing when network manager is not available
            self.show_status("Network manager not available, proceeding to lobby for testing")
            pygame.time.wait(500)
            if self.game:
                self.game.load_scene("lobby")
                
    def on_back_clicked(self, event) -> None:
        """Handle back button click."""
        if self.game:
            self.game.pop_scene()
            
    def show_status(self, message: str, error: bool = False) -> None:
        """Show a status message to the user."""
        status_label = self.ui_manager.find_widget("status_label")
        if status_label:
            status_label.set_text(message)
            # Change color based on message type
            if error:
                status_label.text_color = pygame.Color(255, 100, 100)  # Light red
            else:
                status_label.text_color = pygame.Color(100, 255, 100)  # Light green
                
    def update(self, dt: float) -> None:
        super().update(dt)
        
        if self.ui_manager:
            self.ui_manager.update(dt)
            
    def render(self, screen: pygame.Surface) -> None:
        # Dark blue background
        self.background_color = pygame.Color(20, 30, 60)
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
