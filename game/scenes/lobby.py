from engine import Game, Scene
from engine.rendering.ui import UIManager, Button, Label, TextInput
from engine.networking.networking import get_network_manager, NetworkPriority, MessageType, NetworkMessage
from typing import Dict, Any
import pygame
import time

class LobbyScene(Scene):
    """Lobby scene where players can chat and prepare for the game."""

    def __init__(self):
        super().__init__("LobbyScene")
        self.ui_manager = None
        self.players = ["Player1"]  # List of connected players
        self.chat_messages = []
        self.current_message = ""
        self.is_host = False  # Will be set based on how we got here
        self.max_players = 4
        self.network_manager = None
        self.player_name = "Player1"  # Will be set from join lobby or default for host
        
    def on_enter(self) -> None:
        super().on_enter()
        
        # Setup UI
        screen_size = pygame.display.get_surface().get_size()
        self.ui_manager = UIManager(screen_size)
        
        # Get network manager and set up callbacks
        self.network_manager = get_network_manager()
        self.setup_network_callbacks()
        
        # Determine if we're the host (simplified logic)
        # In a real implementation, this would be determined by networking
        self.is_host = self.network_manager.is_server if self.network_manager else True
        
        # Initialize player list with self
        if self.is_host:
            # Host adds themselves to the list
            if self.player_name not in self.players:
                self.players = [self.player_name]
        else:
            # Client starts with empty list, will be populated by lobby_update
            self.players = []
        
        # Create lobby UI
        self.create_lobby_ui()
        
        # Add some sample chat messages
        self.add_chat_message("System", "Welcome to the lobby!")
        if self.is_host:
            self.add_chat_message("System", "You are the host. Click 'Start Game' when ready.")
            # Start hosting if not already hosting
            if not self.network_manager.is_connected:
                success = self.network_manager.host("localhost", 7777)
                if not success:
                    self.add_chat_message("System", "Failed to start server! Another host may be running.")
                    self.is_host = False
                else:
                    self.add_chat_message("System", "Server started successfully on port 7777.")
        else:
            self.add_chat_message("System", "Waiting for host to start the game...")
            # Request current lobby state and then announce our join
            if self.network_manager and self.network_manager.is_connected:
                # First request the current lobby state
                self.network_manager.send_custom_message(
                    "lobby_state_request",
                    {"player_name": self.player_name},
                    NetworkPriority.HIGH,
                    self.player_name
                )
                # Then send our join message
                self.network_manager.send_custom_message(
                    "player_join",
                    {"player_name": self.player_name},
                    NetworkPriority.HIGH,
                    self.player_name
                )
            
    def setup_network_callbacks(self):
        """Setup network event callbacks."""
        if self.network_manager:
            # Register handlers for specific custom message types
            self.network_manager.register_custom_handler("chat", self.on_network_chat_message)
            self.network_manager.register_custom_handler("player_join", self.on_network_player_joined)
            self.network_manager.register_custom_handler("player_leave", self.on_network_player_left)
            self.network_manager.register_custom_handler("lobby_update", self.on_network_lobby_update)
            self.network_manager.register_custom_handler("lobby_state_request", self.on_lobby_state_request)
            self.network_manager.register_custom_handler("lobby_shutdown", self.on_lobby_shutdown)
            self.network_manager.register_custom_handler("game_start", self.on_network_game_start)
            
            # Set up client connection/disconnection callbacks
            self.network_manager.on_client_connected = self.on_client_connected
            self.network_manager.on_client_disconnected = self.on_client_disconnected
            
    def on_network_chat_message(self, event_data: Dict[str, Any], sender_name: str, timestamp: float):
        """Handle incoming network chat messages."""
        message = event_data.get("message", "")
        if sender_name != self.player_name:  # Don't echo our own messages
            self.add_chat_message(sender_name, message)
            
    def on_network_player_joined(self, event_data: Dict[str, Any], sender_name: str, timestamp: float):
        """Handle player joining the lobby."""
        player_name = event_data.get("player_name", sender_name)
        
        # Only the host should manage the authoritative player list
        if self.is_host:
            if player_name not in self.players:
                self.players.append(player_name)
                self.update_players_list()
                self.add_chat_message("System", f"{player_name} joined the lobby")
                
                # Broadcast updated lobby state to all clients
                if self.network_manager:
                    self.network_manager.send_custom_message(
                        "lobby_update",
                        {
                            "players": self.players,
                            "max_players": self.max_players
                        },
                        NetworkPriority.HIGH,
                        "Server"
                    )
        # Clients don't handle player_join directly - they wait for lobby_update from server
            
    def on_network_player_left(self, event_data: Dict[str, Any], sender_name: str, timestamp: float):
        """Handle player leaving the lobby."""
        player_name = event_data.get("player_name", sender_name)
        
        # Only the host should manage the authoritative player list
        if self.is_host:
            if player_name in self.players:
                self.players.remove(player_name)
                self.update_players_list()
                self.add_chat_message("System", f"{player_name} left the lobby")
                
                # Broadcast updated lobby state to all clients
                if self.network_manager:
                    self.network_manager.send_custom_message(
                        "lobby_update",
                        {
                            "players": self.players,
                            "max_players": self.max_players
                        },
                        NetworkPriority.HIGH,
                        "Server"
                    )
        # Clients don't handle player_leave directly - they wait for lobby_update from server
            
    def on_network_lobby_update(self, event_data: Dict[str, Any], sender_name: str, timestamp: float):
        """Handle lobby information updates from the server."""
        # Only process lobby updates from the server
        if sender_name == "Server" and "players" in event_data:
            # Store previous player list to detect changes
            old_players = set(self.players)
            new_players = set(event_data["players"])
            
            # Update the lobby state
            self.players = event_data["players"]
            self.update_players_list()
            
            # Show join/leave messages for players who changed (but not for self)
            if not self.is_host:  # Host already shows these messages when processing join/leave
                joined_players = new_players - old_players
                left_players = old_players - new_players
                
                for player in joined_players:
                    if player != self.player_name:  # Don't show join message for ourselves
                        self.add_chat_message("System", f"{player} joined the lobby")
                        
                for player in left_players:
                    if player != self.player_name:  # Don't show leave message for ourselves
                        self.add_chat_message("System", f"{player} left the lobby")
            
        if "max_players" in event_data:
            self.max_players = event_data["max_players"]
            
    def on_lobby_state_request(self, event_data: Dict[str, Any], sender_name: str, timestamp: float):
        """Handle lobby state request from a new client."""
        # Only the host responds to lobby state requests
        if self.is_host and self.network_manager:
            # Send current lobby state to the requesting client
            self.network_manager.send_custom_message(
                "lobby_update",
                {
                    "players": self.players,
                    "max_players": self.max_players
                },
                NetworkPriority.HIGH,
                "Server"
            )
            
    def on_lobby_shutdown(self, event_data: Dict[str, Any], sender_name: str, timestamp: float):
        """Handle lobby shutdown notification from host."""
        if not self.is_host:  # Only clients should handle this
            reason = event_data.get("reason", "Unknown reason")
            self.add_chat_message("System", f"Lobby closed: {reason}")
            
            # Disconnect from the server
            if self.network_manager:
                self.network_manager.disconnect()
            
            # Go back to the main menu after a short delay
            import time
            time.sleep(1.0)  # Give user time to see the message
            
            if self.game:
                # Go back to multiplayer select
                self.game.pop_scene()
            
    def on_network_game_start(self, event_data: Dict[str, Any], sender_name: str, timestamp: float):
        """Handle game start notification."""
        self.add_chat_message("System", "Host is starting the game!")
        if self.game:
            self.game.load_scene("game")
            
    def on_client_connected(self, client_id: str):
        """Handle a new client connecting to the server (server only)."""
        if self.is_host:
            # Just log the connection, actual player join is handled by player_join message
            print(f"Client {client_id} connected to server")
                    
    def on_client_disconnected(self, client_id: str):
        """Handle a client disconnecting from the server (server only)."""
        if self.is_host:
            # When a client disconnects, we need to figure out which player left
            # In a real implementation, you'd maintain a client_id -> player_name mapping
            # For now, we'll rely on the player_leave message being sent before disconnect
            print(f"Client {client_id} disconnected from server")
            
    def check_network_connection(self):
        """Check if network connection is still active (for clients)."""
        if not self.is_host and self.network_manager:
            if not self.network_manager.is_connected:
                # Lost connection to host
                self.add_chat_message("System", "Lost connection to host")
                
                # Go back to multiplayer select after a delay
                import time
                time.sleep(1.0)
                
                if self.game:
                    self.game.pop_scene()
        
    def create_lobby_ui(self) -> None:
        """Create the lobby UI elements."""
        screen_size = pygame.display.get_surface().get_size()
        
        # Title label
        title_text = "Game Lobby (Host)" if self.is_host else "Game Lobby"
        title_label = Label(
            pygame.Rect((screen_size[0] - 200) // 2, 20, 200, 40),
            title_text,
            name="title_label"
        )
        self.ui_manager.add_widget(title_label)
        
        # Players section
        players_title = Label(
            pygame.Rect(50, 80, 200, 30),
            f"Players ({len(self.players)}/{self.max_players}):",
            name="players_title"
        )
        self.ui_manager.add_widget(players_title)
        
        # Players list (will be updated dynamically)
        self.update_players_list()
        
        # Chat section
        chat_title = Label(
            pygame.Rect(300, 80, 200, 30),
            "Chat:",
            name="chat_title"
        )
        self.ui_manager.add_widget(chat_title)
        
        # Chat input
        chat_input = TextInput(
            pygame.Rect(300, screen_size[1] - 150, 300, 30),
            "",
            name="chat_input"
        )
        chat_input.add_event_handler("text_changed", self.on_chat_changed)
        chat_input.add_event_handler("enter_pressed", self.on_chat_send)
        self.ui_manager.add_widget(chat_input)
        
        # Send button
        send_button = Button(
            pygame.Rect(610, screen_size[1] - 150, 70, 30),
            "Send",
            name="send_button"
        )
        send_button.add_event_handler("clicked", self.on_send_clicked)
        self.ui_manager.add_widget(send_button)
        
        # Control buttons
        if self.is_host:
            # Start game button (only for host)
            start_button = Button(
                pygame.Rect(screen_size[0] - 200, screen_size[1] - 100, 150, 50),
                "Start Game",
                name="start_button"
            )
            start_button.add_event_handler("clicked", self.on_start_clicked)
            self.ui_manager.add_widget(start_button)
        
        # Leave lobby button
        leave_button = Button(
            pygame.Rect(50, screen_size[1] - 100, 120, 50),
            "Leave Lobby",
            name="leave_button"
        )
        leave_button.add_event_handler("clicked", self.on_leave_clicked)
        self.ui_manager.add_widget(leave_button)
        
    def update_players_list(self) -> None:
        """Update the visual players list."""
        # Remove old player labels
        for i in range(10):  # Remove up to 10 old labels
            old_label = self.ui_manager.find_widget(f"player_{i}")
            if old_label:
                self.ui_manager.remove_widget(old_label)
        
        # Add current players
        for i, player in enumerate(self.players):
            player_label = Label(
                pygame.Rect(70, 120 + i * 25, 200, 20),
                f"> {player}",
                name=f"player_{i}"
            )
            self.ui_manager.add_widget(player_label)
            
        # Update players count
        players_title = self.ui_manager.find_widget("players_title")
        if players_title:
            players_title.set_text(f"Players ({len(self.players)}/{self.max_players}):")
    
    def add_chat_message(self, sender: str, message: str) -> None:
        """Add a message to the chat."""
        timestamp = time.strftime("%H:%M")
        self.chat_messages.append(f"[{timestamp}] {sender}: {message}")
        
        # Keep only last 20 messages
        if len(self.chat_messages) > 20:
            self.chat_messages = self.chat_messages[-20:]
    
    def on_chat_changed(self, event) -> None:
        """Handle chat input change."""
        self.current_message = event.data
        
    def on_chat_send(self, event) -> None:
        """Handle enter key in chat input."""
        self.send_chat_message()
        
    def on_send_clicked(self, event) -> None:
        """Handle send button click."""
        self.send_chat_message()
        
    def send_chat_message(self) -> None:
        """Send the current chat message via network."""
        if self.current_message.strip():
            # Add to local chat immediately for instant feedback
            self.add_chat_message(self.player_name, self.current_message)
            
            # Send via network with instant priority
            if self.network_manager and self.network_manager.is_connected:
                self.network_manager.send_chat_message(self.player_name, self.current_message)
            
            # Clear input
            chat_input = self.ui_manager.find_widget("chat_input")
            if chat_input:
                chat_input.set_text("")
            self.current_message = ""
            
    def on_start_clicked(self, event) -> None:
        """Handle start game button click (host only)."""
        if self.is_host:
            print("Host is starting the game!")
            self.add_chat_message("System", "Host is starting the game!")
            
            # Send game start notification via custom message
            if self.network_manager and self.network_manager.is_connected:
                self.network_manager.send_custom_message(
                    "game_start", 
                    {"scene": "game"}, 
                    NetworkPriority.HIGH
                )
            
            if self.game:
                self.game.load_scene("game")
                
    def on_leave_clicked(self, event) -> None:
        """Handle leave lobby button click."""
        print("Leaving lobby...")
        
        if self.is_host:
            # Host is leaving - shut down the entire lobby
            self.shutdown_lobby()
        else:
            # Client is leaving - announce and disconnect
            if self.network_manager and self.network_manager.is_connected:
                self.network_manager.send_custom_message(
                    "player_leave", 
                    {"player_name": self.player_name}, 
                    NetworkPriority.HIGH,
                    self.player_name
                )
                self.network_manager.disconnect()
        
        if self.game:
            self.game.pop_scene()  # Go back to multiplayer select
            
    def shutdown_lobby(self):
        """Shutdown the lobby when host leaves (host only)."""
        print("Host is shutting down the lobby...")
        
        if self.network_manager and self.network_manager.is_connected:
            # Notify all clients that the lobby is closing
            self.network_manager.send_custom_message(
                "lobby_shutdown",
                {"reason": "Host left the lobby"},
                NetworkPriority.INSTANT,
                "Server"
            )
            
            # Give a moment for the message to be sent
            import time
            time.sleep(0.1)
            
            # Disconnect all clients and shut down server
            self.network_manager.disconnect()
            
        self.add_chat_message("System", "Lobby closed by host")
            
    def simulate_player_join(self, player_name: str) -> None:
        """Simulate a player joining (for demo purposes)."""
        if len(self.players) < self.max_players and player_name not in self.players:
            self.players.append(player_name)
            self.update_players_list()
            self.add_chat_message("System", f"{player_name} joined the lobby")
            
    def simulate_player_leave(self, player_name: str) -> None:
        """Simulate a player leaving (for demo purposes)."""
        if player_name in self.players:
            self.players.remove(player_name)
            self.update_players_list()
            self.add_chat_message("System", f"{player_name} left the lobby")
            
    def update(self, dt: float) -> None:
        super().update(dt)
        
        # Update network manager for instant chat processing
        if self.network_manager:
            self.network_manager.update()
        
        # Check network connection status for clients
        if not self.is_host:
            self.check_network_connection()
        
        # Update UI
        if self.ui_manager:
            self.ui_manager.update(dt)
        
        # Demo activity simulation (remove in real implementation)
        if hasattr(self, '_demo_timer'):
            self._demo_timer += dt
        else:
            self._demo_timer = 0
            
        # Simulate players joining/leaving occasionally (only if not connected to real network)
        if not (self.network_manager and self.network_manager.is_connected):
            if self._demo_timer > 10.0 and len(self.players) < 3:
                self.simulate_player_join(f"Player{len(self.players) + 1}")
                self._demo_timer = 0
            
    def render(self, screen: pygame.Surface) -> None:
        # Clear screen with dark background
        self.background_color = pygame.Color(25, 35, 45)
        super().render(screen)
        
        # Render chat messages
        chat_font = Game.get_instance().asset_manager.get_default_font(14)
        chat_y = 120
        for i, message in enumerate(self.chat_messages[-15:]):  # Show last 15 messages
            if chat_y < screen.get_height() - 180:  # Don't overlap with input
                msg_text = chat_font.render(message, True, pygame.Color(200, 200, 200))
                screen.blit(msg_text, (300, chat_y + i * 18))
        
        # Render UI
        if self.ui_manager:
            self.ui_manager.render(screen)
            
    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        
        # Handle UI events
        if self.ui_manager:
            if self.ui_manager.handle_event(event):
                return
                
        # Handle keyboard shortcuts
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Leave lobby
                if self.game:
                    self.game.pop_scene()
            elif event.key == pygame.K_F1 and self.is_host:
                # Quick start for host
                if self.game:
                    self.game.load_scene("game")
                    
    def on_exit(self) -> None:
        """Clean up when exiting the lobby scene."""
        super().on_exit()
        
        # If we're still connected, properly disconnect
        if self.network_manager and self.network_manager.is_connected:
            if self.is_host:
                # Host shutting down - notify clients and disconnect
                self.shutdown_lobby()
            else:
                # Client leaving - send leave message if still connected
                try:
                    self.network_manager.send_custom_message(
                        "player_leave",
                        {"player_name": self.player_name},
                        NetworkPriority.HIGH,
                        self.player_name
                    )
                except:
                    pass  # Connection might already be lost
                
                self.network_manager.disconnect()
        
        # Clear network callbacks to avoid memory leaks
        if self.network_manager:
            self.network_manager.on_client_connected = None
            self.network_manager.on_client_disconnected = None