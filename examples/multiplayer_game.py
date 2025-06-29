"""
Networked multiplayer game example.
Run with --server to start a server, or --client to connect as a client.
"""

import pygame
import sys
import argparse
from engine import *
from engine.networking import NetworkMessage, MessageType

class NetworkedPlayer(Component):
    """Networked player component that syncs position."""
    
    def __init__(self, is_local: bool = False, speed: float = 200.0):
        super().__init__()
        self.is_local = is_local
        self.speed = speed
        self.network_id = None
        self.last_sync_time = 0.0
        self.sync_interval = 1.0 / 30.0  # 30 FPS network updates
        
    def update(self, dt: float) -> None:
        if not self.actor:
            return
            
        if self.is_local:
            # Handle local input
            self.handle_input(dt)
            
            # Send position updates
            self.last_sync_time += dt
            if self.last_sync_time >= self.sync_interval:
                self.send_position_update()
                self.last_sync_time = 0.0
                
    def handle_input(self, dt: float) -> None:
        """Handle local player input."""
        keys = pygame.key.get_pressed()
        movement = pygame.Vector2(0, 0)
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            movement.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            movement.x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            movement.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            movement.y += 1
            
        if movement.length() > 0:
            movement = movement.normalize()
            self.actor.transform.local_position += movement * self.speed * dt
            
        # Keep on screen
        screen_size = pygame.display.get_surface().get_size()
        pos = self.actor.transform.local_position
        pos.x = max(16, min(screen_size[0] - 16, pos.x))
        pos.y = max(16, min(screen_size[1] - 16, pos.y))
        
    def send_position_update(self) -> None:
        """Send position update to server/clients."""
        if self.actor and hasattr(self.actor, 'scene') and self.actor.scene.game:
            network_manager = self.actor.scene.game.network_manager
            
            if network_manager.is_connected():
                pos = self.actor.transform.local_position
                data = {
                    'player_id': self.network_id,
                    'position': {'x': pos.x, 'y': pos.y},
                    'action': 'move'
                }
                
                message = NetworkMessage(MessageType.PLAYER_INPUT, data)
                
                if network_manager.mode == 'client':
                    network_manager.client.send_message(message)
                elif network_manager.mode == 'server':
                    network_manager.server.broadcast_message(message, exclude=[self.network_id])
                    
    def update_position(self, position: dict) -> None:
        """Update position from network."""
        if not self.is_local and self.actor:
            self.actor.transform.local_position = pygame.Vector2(position['x'], position['y'])

class MultiplayerGameScene(Scene):
    """Multiplayer game scene."""
    
    def __init__(self, is_server: bool = False):
        super().__init__("MultiplayerGame")
        self.is_server = is_server
        self.players = {}  # network_id -> actor
        self.local_player = None
        self.ui_manager = None
        self.connected_players = 0
        
    def on_enter(self) -> None:
        super().on_enter()
        
        # Setup networking handlers
        if self.game:
            network_manager = self.game.network_manager
            
            if self.is_server:
                network_manager.server.add_message_handler(
                    MessageType.CONNECT, self.on_client_connect
                )
                network_manager.server.add_message_handler(
                    MessageType.DISCONNECT, self.on_client_disconnect
                )
                network_manager.server.add_message_handler(
                    MessageType.PLAYER_INPUT, self.on_player_input
                )
            else:
                network_manager.client.add_message_handler(
                    MessageType.GAME_STATE, self.on_game_state
                )
                network_manager.client.add_message_handler(
                    MessageType.PLAYER_INPUT, self.on_player_input
                )
                
        # Create UI
        self.setup_ui()
        
        # Create local player
        self.create_local_player()
        
    def setup_ui(self) -> None:
        """Setup UI elements."""
        screen_size = pygame.display.get_surface().get_size()
        self.ui_manager = UIManager(screen_size)
        
        # Connection status
        status_text = "Server" if self.is_server else "Client"
        status_label = Label(
            pygame.Rect(10, 10, 200, 30),
            f"Mode: {status_text}",
            name="status_label"
        )
        status_label.text_color = pygame.Color(0, 255, 0)
        self.ui_manager.add_widget(status_label)
        
        # Player count
        count_label = Label(
            pygame.Rect(10, 50, 200, 30),
            f"Players: {self.connected_players}",
            name="count_label"
        )
        count_label.text_color = pygame.Color(255, 255, 0)
        self.ui_manager.add_widget(count_label)
        
        # Instructions
        instructions = Label(
            pygame.Rect(10, screen_size[1] - 80, 400, 60),
            "WASD/Arrow Keys: Move\nESC: Quit",
            name="instructions"
        )
        instructions.text_color = pygame.Color(255, 255, 255)
        self.ui_manager.add_widget(instructions)
        
    def create_local_player(self) -> None:
        """Create the local player."""
        screen_size = pygame.display.get_surface().get_size()
        
        # Get client ID for network identification
        network_id = "server_player" if self.is_server else None
        if not self.is_server and self.game and self.game.network_manager.client:
            network_id = self.game.network_manager.client.client_id
            
        self.local_player = self.create_actor("LocalPlayer", 
                                            pygame.Vector2(screen_size[0] // 2, screen_size[1] // 2))
        
        # Add sprite component (green for local player)
        sprite = SpriteComponent(color=pygame.Color(0, 255, 0), size=pygame.Vector2(32, 32))
        self.local_player.add_component(sprite)
        
        # Add networked player component
        networked_player = NetworkedPlayer(is_local=True, speed=250.0)
        networked_player.network_id = network_id
        self.local_player.add_component(networked_player)
        
        self.local_player.add_tag("player")
        self.players[network_id] = self.local_player
        
    def create_remote_player(self, network_id: str) -> Actor:
        """Create a remote player."""
        import random
        screen_size = pygame.display.get_surface().get_size()
        
        # Random starting position
        pos = pygame.Vector2(
            random.randint(50, screen_size[0] - 50),
            random.randint(50, screen_size[1] - 50)
        )
        
        player = self.create_actor(f"RemotePlayer_{network_id}", pos)
        
        # Add sprite component (blue for remote players)
        sprite = SpriteComponent(color=pygame.Color(0, 100, 255), size=pygame.Vector2(32, 32))
        player.add_component(sprite)
        
        # Add networked player component
        networked_player = NetworkedPlayer(is_local=False)
        networked_player.network_id = network_id
        player.add_component(networked_player)
        
        player.add_tag("player")
        self.players[network_id] = player
        
        return player
        
    def on_client_connect(self, client_id: str, message: NetworkMessage) -> None:
        """Handle client connection (server only)."""
        print(f"Client connected: {client_id}")
        
        # Create remote player for this client
        if client_id not in self.players:
            self.create_remote_player(client_id)
            
        self.update_player_count()
        
        # Send current game state to new client
        game_state = self.get_game_state()
        state_message = NetworkMessage(MessageType.GAME_STATE, game_state)
        if self.game and self.game.network_manager.server:
            self.game.network_manager.server.send_to_client(client_id, state_message)
            
    def on_client_disconnect(self, client_id: str, message: NetworkMessage) -> None:
        """Handle client disconnection."""
        print(f"Client disconnected: {client_id}")
        
        # Remove player
        if client_id in self.players:
            player = self.players[client_id]
            self.destroy_actor(player)
            del self.players[client_id]
            
        self.update_player_count()
        
    def on_player_input(self, *args) -> None:
        """Handle player input from network."""
        if self.is_server:
            client_id, message = args
        else:
            message = args[0]
            client_id = message.sender_id
            
        data = message.data
        if data.get('action') == 'move':
            player_id = data.get('player_id', client_id)
            position = data.get('position')
            
            if player_id in self.players and position:
                player = self.players[player_id]
                networked_comp = player.get_component(NetworkedPlayer)
                if networked_comp:
                    networked_comp.update_position(position)
                    
        # If server, broadcast to other clients
        if self.is_server and self.game and self.game.network_manager.server:
            self.game.network_manager.server.broadcast_message(message, exclude=[client_id])
            
    def on_game_state(self, message: NetworkMessage) -> None:
        """Handle game state update from server (client only)."""
        data = message.data
        
        # Update players from game state
        players_data = data.get('players', {})
        for player_id, player_data in players_data.items():
            if player_id != (self.game.network_manager.client.client_id if self.game.network_manager.client else None):
                if player_id not in self.players:
                    self.create_remote_player(player_id)
                    
                if player_id in self.players:
                    position = player_data.get('position')
                    if position:
                        networked_comp = self.players[player_id].get_component(NetworkedPlayer)
                        if networked_comp:
                            networked_comp.update_position(position)
                            
    def get_game_state(self) -> dict:
        """Get current game state for network sync."""
        players_data = {}
        
        for player_id, player in self.players.items():
            pos = player.transform.world_position
            players_data[player_id] = {
                'position': {'x': pos.x, 'y': pos.y}
            }
            
        return {
            'players': players_data,
            'timestamp': pygame.time.get_ticks()
        }
        
    def update_player_count(self) -> None:
        """Update the player count display."""
        self.connected_players = len(self.players)
        
        if self.ui_manager:
            count_label = self.ui_manager.find_widget("count_label")
            if count_label:
                count_label.set_text(f"Players: {self.connected_players}")
                
    def update(self, dt: float) -> None:
        super().update(dt)
        
        # Update UI
        if self.ui_manager:
            self.ui_manager.update(dt)
            
    def render(self, screen: pygame.Surface) -> None:
        # Set background
        self.background_color = pygame.Color(30, 30, 60)
        super().render(screen)
        
        # Render UI
        if self.ui_manager:
            self.ui_manager.render(screen)
            
    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        
        # Handle UI events
        if self.ui_manager:
            self.ui_manager.handle_event(event)
            
        # Handle game events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.game:
                    self.game.quit()

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Networked Multiplayer Game")
    parser.add_argument("--server", action="store_true", help="Run as server")
    parser.add_argument("--client", action="store_true", help="Run as client")
    parser.add_argument("--host", default="localhost", help="Server host (client mode)")
    parser.add_argument("--port", type=int, default=12345, help="Server port")
    
    args = parser.parse_args()
    
    if not args.server and not args.client:
        print("Please specify --server or --client")
        return
        
    # Create game
    title = "Multiplayer Game - Server" if args.server else "Multiplayer Game - Client"
    game = Game(800, 600, title)
    
    # Setup networking
    if args.server:
        if not game.network_manager.start_server(args.port):
            print("Failed to start server")
            return
        print(f"Server started on port {args.port}")
    else:
        if not game.network_manager.connect_to_server(args.host, args.port):
            print(f"Failed to connect to server at {args.host}:{args.port}")
            return
        print(f"Connected to server at {args.host}:{args.port}")
        
    # Create and add scene
    game_scene = MultiplayerGameScene(is_server=args.server)
    game.add_scene("multiplayer", game_scene)
    game.load_scene("multiplayer")
    
    # Run game
    try:
        game.run()
    finally:
        # Cleanup networking
        game.network_manager.cleanup()

if __name__ == "__main__":
    main()
