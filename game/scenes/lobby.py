from engine import Game, Scene
from engine.ui import UIManager, Button, Label
import pygame
import socket


class LobbyScene(Scene):
    """Scene for multiplayer lobby where players wait before starting a game."""
    
    def __init__(self):
        super().__init__("Lobby")
        self.ui_manager = None
        self.is_host = False
        self.connected_players = []
        self.host_ip = "Unknown"
        self.host_port = 12345
        self.ip_hidden = False
        
        # UI elements that need to be updated
        self.host_info_label = None
        self.ip_label = None
        self.players_count_label = None
        self.players_list_labels = []
        
    def on_enter(self) -> None:
        super().on_enter()
        
        # Determine if we're the host
        if self.game and hasattr(self.game, 'network_manager') and self.game.network_manager:
            self.is_host = (self.game.network_manager.mode == 'server')
            if self.is_host:
                self.host_ip = self.get_local_ip()
                self.connected_players = ["Host (You)"]
                # Get network info for more details
                network_info = self.game.network_manager.get_network_info()
                if 'port' in network_info:
                    self.host_port = network_info['port']
            else:
                # For clients, add themselves to the player list
                self.connected_players = ["You"]
                # Set up scene change handler for clients
                self.setup_scene_change_handler()
        else:
            # Fallback for testing without network
            self.is_host = True
            self.host_ip = self.get_local_ip()
            self.connected_players = ["Host (You)"]
        
        # Setup UI
        screen_size = pygame.display.get_surface().get_size()
        self.ui_manager = UIManager(screen_size)
        
        self.create_lobby_ui()
    
    def setup_scene_change_handler(self) -> None:
        """Set up handler for scene change messages from server."""
        if self.game and self.game.network_manager:
            self.game.network_manager.add_scene_change_handler(self._handle_scene_change)
    
    def _handle_scene_change(self, scene_name: str) -> None:
        """Handle scene change message from server."""
        print(f"Received scene change command: {scene_name}")
        if self.game:
            self.game.load_scene(scene_name)
        
    def get_local_ip(self) -> str:
        """Get the local IP address."""
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def create_lobby_ui(self) -> None:
        """Create the lobby UI elements."""
        screen_size = pygame.display.get_surface().get_size()
        
        # Title
        title_label = Label(
            pygame.Rect((screen_size[0] - 200) // 2, 30, 200, 40),
            "Game Lobby",
            name="title_label"
        )
        self.ui_manager.add_widget(title_label)
        
        # Host information
        host_status = "Host" if self.is_host else "Client"
        self.host_info_label = Label(
            pygame.Rect(50, 80, 300, 30),
            f"Status: {host_status}",
            name="host_info_label"
        )
        self.ui_manager.add_widget(self.host_info_label)
        
        # IP Address information (only show for host)
        if self.is_host:
            ip_text = f"Server IP: {self.host_ip}:{self.host_port}"
            if self.ip_hidden:
                ip_text = f"Server IP: ***.***.***.**:{self.host_port}"
            
            self.ip_label = Label(
                pygame.Rect(50, 110, 400, 30),
                ip_text,
                name="ip_label"
            )
            self.ui_manager.add_widget(self.ip_label)
            
            # Hide/Show IP button
            toggle_ip_button = Button(
                pygame.Rect(450, 110, 100, 30),
                "Hide IP" if not self.ip_hidden else "Show IP",
                name="toggle_ip_button"
            )
            toggle_ip_button.add_event_handler("clicked", self.on_toggle_ip_clicked)
            self.ui_manager.add_widget(toggle_ip_button)
        
        # Players section
        self.players_count_label = Label(
            pygame.Rect(50, 160, 300, 30),
            f"Connected Players ({len(self.connected_players)}):",
            name="players_count_label"
        )
        self.ui_manager.add_widget(self.players_count_label)
        
        # Update player list display
        self.update_player_list_display()
        
        # Action buttons
        self.create_action_buttons()
        
    def create_action_buttons(self) -> None:
        """Create action buttons for the lobby."""
        screen_size = pygame.display.get_surface().get_size()
        button_width = 200
        button_height = 40
        
        # Start Game button (only for host)
        if self.is_host:
            start_game_button = Button(
                pygame.Rect((screen_size[0] - button_width) // 2, 
                           screen_size[1] - 120, button_width, button_height),
                "Start Game",
                name="start_game_button"
            )
            start_game_button.add_event_handler("clicked", self.on_start_game_clicked)
            self.ui_manager.add_widget(start_game_button)
        
        # Leave Lobby button
        leave_button = Button(
            pygame.Rect((screen_size[0] - button_width) // 2, 
                       screen_size[1] - 70, button_width, button_height),
            "Leave Lobby",
            name="leave_button"
        )
        leave_button.add_event_handler("clicked", self.on_leave_lobby_clicked)
        self.ui_manager.add_widget(leave_button)
    
    def update_player_list_display(self) -> None:
        """Update the visual display of connected players."""
        # Remove old player list labels
        for label in self.players_list_labels:
            self.ui_manager.remove_widget(label)
        self.players_list_labels.clear()
        
        # Create new player list labels
        for i, player in enumerate(self.connected_players):
            player_label = Label(
                pygame.Rect(70, 200 + i * 25, 400, 25),
                f"• {player}",
                name=f"player_{i}_label"
            )
            self.ui_manager.add_widget(player_label)
            self.players_list_labels.append(player_label)
        
        # Update player count
        if self.players_count_label:
            self.players_count_label.set_text(f"Connected Players ({len(self.connected_players)}):")
    
    def on_toggle_ip_clicked(self, event) -> None:
        """Toggle IP address visibility."""
        self.ip_hidden = not self.ip_hidden
        
        # Update IP label text
        if self.ip_label:
            if self.ip_hidden:
                ip_text = f"Server IP: ***.***.***.**:{self.host_port}"
            else:
                ip_text = f"Server IP: {self.host_ip}:{self.host_port}"
            self.ip_label.set_text(ip_text)
        
        # Update button text
        toggle_button = self.ui_manager.find_widget("toggle_ip_button")
        if toggle_button:
            toggle_button.text = "Show IP" if self.ip_hidden else "Hide IP"
    
    def on_start_game_clicked(self, event) -> None:
        """Handle start game button click."""
        if self.game and self.is_host:
            if hasattr(self.game, 'network_manager') and self.game.network_manager:
                # Send scene change to all clients
                game_data = {
                    'started_by': 'host',
                    'timestamp': pygame.time.get_ticks()
                }
                self.game.network_manager.send_scene_change("game", game_data)
                print("Starting game for all players...")
            
            # Start the game for the host as well
            self.game.load_scene("game")
    
    def on_leave_lobby_clicked(self, event) -> None:
        """Handle leave lobby button click with proper cleanup."""
        if self.game and hasattr(self.game, 'network_manager') and self.game.network_manager:
            print("Cleaning up network connection...")
            self.game.network_manager.cleanup()
        
        if self.game:
            self.game.pop_scene()
    
    def add_player(self, player_name: str) -> None:
        """Add a player to the lobby."""
        if player_name not in self.connected_players:
            self.connected_players.append(player_name)
            self.update_player_list_display()
            print(f"Player {player_name} joined the lobby")
    
    def remove_player(self, player_name: str) -> None:
        """Remove a player from the lobby."""
        if player_name in self.connected_players:
            self.connected_players.remove(player_name)
            self.update_player_list_display()
            print(f"Player {player_name} left the lobby")
    
    def update(self, dt: float) -> None:
        super().update(dt)
        
        if self.ui_manager:
            self.ui_manager.update(dt)
        
        # Update player list from network manager
        self.update_network_info()
    
    def update_network_info(self) -> None:
        """Update lobby information from network manager."""
        if self.game and hasattr(self.game, 'network_manager') and self.game.network_manager:
            network_info = self.game.network_manager.get_network_info()
            
            if self.is_host and 'clients' in network_info:
                # Update connected players list for host
                new_players = ["Host (You)"]
                for client_id in network_info['clients']:
                    new_players.append(f"Player ({client_id})")
                
                # Only update if the list changed
                if new_players != self.connected_players:
                    self.connected_players = new_players
                    self.update_player_list_display()
    
    def render(self, screen: pygame.Surface) -> None:
        # Dark green background
        self.background_color = pygame.Color(20, 40, 30)
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
                # Same cleanup as leave lobby
                self.on_leave_lobby_clicked(None)