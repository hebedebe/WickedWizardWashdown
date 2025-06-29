from engine import Game, Scene, Actor, SpriteComponent, StaticBodyComponent
from engine.networking import MessageType
import pygame
from game.actors.player import Player


class GameScene(Scene):
    """Main gameplay scene."""
    
    def __init__(self):
        super().__init__("Game")
        self.spawned_players = {}  # Track spawned players by ID
        # Better spawn positions that avoid the top left and are spread out
        self.spawn_positions = [
            (150, 350),   # Player 1
            (250, 350),   # Player 2  
            (350, 350),   # Player 3
            (450, 350),   # Player 4
            (550, 350),   # Player 5 (if more than 4)
            (650, 350),   # Player 6
        ]
        self.next_spawn_index = 0
        
    def on_enter(self):
        super().on_enter()
        
        # Set background color
        self.background_color = pygame.Color(135, 206, 235)  # Sky blue
        
        # Create ground
        self.create_ground()
        
        # Handle player spawning based on network state
        self.setup_players()
        
    def create_ground(self):
        """Create ground objects for the game world."""
        screen_size = pygame.display.get_surface().get_size()
        
        # Main ground platform
        ground = Actor("Ground")
        ground.transform.local_position = pygame.Vector2(screen_size[0] // 2, screen_size[1] - 50)
        
        # Add visual component (green rectangle)
        sprite = SpriteComponent(
            color=pygame.Color(34, 139, 34),  # Forest green
            size=pygame.Vector2(screen_size[0], 100)
        )
        ground.add_component(sprite)
        
        # Add physics component for collision
        physics = StaticBodyComponent(
            shape_type="box",
            size=(screen_size[0], 100)
        )
        physics.friction = 0.8
        ground.add_component(physics)
        
        self.add_actor(ground)
        
        # Add some platforms
        self.create_platform(200, 300, 150, 20)
        self.create_platform(450, 250, 150, 20)
        self.create_platform(650, 200, 150, 20)
    
    def create_platform(self, x: float, y: float, width: float, height: float):
        """Create a platform at the specified position."""
        platform = Actor(f"Platform_{x}_{y}")
        platform.transform.local_position = pygame.Vector2(x, y)
        
        # Visual component
        sprite = SpriteComponent(
            color=pygame.Color(139, 69, 19),  # Saddle brown
            size=pygame.Vector2(width, height)
        )
        platform.add_component(sprite)
        
        # Physics component
        physics = StaticBodyComponent(
            shape_type="box",
            size=(width, height)
        )
        physics.friction = 0.8
        platform.add_component(physics)
        
        self.add_actor(platform)
    
    def setup_players(self):
        """Set up players based on network state."""
        if self.game and hasattr(self.game, 'network_manager') and self.game.network_manager:
            network_manager = self.game.network_manager
            
            if network_manager.mode == 'server':
                # Server: spawn players for all connected clients + host
                self.setup_server_players(network_manager)
            elif network_manager.mode == 'client':
                # Client: set up handlers for player spawn/despawn
                self.setup_client_handlers(network_manager)
                # Spawn local player
                self.spawn_local_player()
        else:
            # Single player or testing mode
            self.spawn_local_player()
    
    def _handle_new_player_connect(self, client_id: str, message):
        """Handle when a new player connects to the game scene."""
        if client_id not in self.spawned_players:
            spawn_pos = self.get_next_spawn_position()
            self.spawn_player(client_id, spawn_pos, is_owner=False)
            
            # Broadcast to all clients about the new player
            if self.game and hasattr(self.game, 'network_manager') and self.game.network_manager:
                self.game.network_manager.send_player_spawn(client_id, spawn_pos)
    
    def setup_server_players(self, network_manager):
        """Set up players on the server and broadcast spawn info."""
        # Get connected clients
        network_info = network_manager.get_network_info()
        clients = network_info.get('clients', [])
        
        # Spawn host player (server is always the host)
        host_spawn_pos = self.get_next_spawn_position()
        host_player = self.spawn_player("host", host_spawn_pos, is_owner=True)
        
        # Broadcast host spawn to clients
        network_manager.send_player_spawn("host", host_spawn_pos)
        
        # Spawn players for each connected client
        for client_id in clients:
            if client_id not in self.spawned_players:
                spawn_pos = self.get_next_spawn_position()
                # Server spawns all players but only owns the host
                self.spawn_player(client_id, spawn_pos, is_owner=False)
                # Broadcast spawn to all clients
                network_manager.send_player_spawn(client_id, spawn_pos)
        
        # Set up handlers for new players joining
        network_manager.server.add_message_handler(
            MessageType.CONNECT, 
            self._handle_new_player_connect
        )
    
    def setup_client_handlers(self, network_manager):
        """Set up handlers for player spawn/despawn messages."""
        network_manager.add_player_spawn_handler(self.on_player_spawn)
        network_manager.add_player_despawn_handler(self.on_player_despawn)
    
    def spawn_local_player(self):
        """Spawn the local player (for single player or client initial spawn)."""
        spawn_pos = self.get_next_spawn_position()
        self.spawn_player("local_player", spawn_pos, is_owner=True)
    
    def get_next_spawn_position(self) -> tuple:
        """Get the next available spawn position."""
        if self.next_spawn_index >= len(self.spawn_positions):
            # If we run out of predefined positions, create new ones spread horizontally
            return (150 + (self.next_spawn_index * 80), 350)
        
        pos = self.spawn_positions[self.next_spawn_index]
        self.next_spawn_index += 1
        return pos
    
    def spawn_player(self, player_id: str, spawn_position: tuple, is_owner: bool = False) -> Player:
        """Spawn a player at the specified position."""
        if player_id in self.spawned_players:
            return self.spawned_players[player_id]
        
        player = Player(player_id, is_owner)
        player.transform.local_position = pygame.Vector2(spawn_position[0], spawn_position[1])
        
        # Set player color based on ownership and ID for visual distinction
        sprite = player.get_component(SpriteComponent)
        if sprite:
            if is_owner:
                sprite.color = pygame.Color(0, 255, 0)  # Green for owned player
            elif player_id == "host":
                sprite.color = pygame.Color(0, 150, 255)  # Light blue for host
            else:
                # Different colors for different remote players
                colors = [
                    pygame.Color(255, 100, 100),  # Light red
                    pygame.Color(100, 100, 255),  # Light blue  
                    pygame.Color(255, 255, 100),  # Light yellow
                    pygame.Color(255, 100, 255),  # Light magenta
                    pygame.Color(100, 255, 255),  # Light cyan
                    pygame.Color(255, 165, 0),    # Orange
                ]
                color_index = hash(player_id) % len(colors)
                sprite.color = colors[color_index]
        
        self.add_actor(player)
        self.spawned_players[player_id] = player
        
        print(f"Spawned player {player_id} at {spawn_position} (owner: {is_owner})")
        return player
    
    def on_player_spawn(self, player_id: str, spawn_position: tuple):
        """Handle player spawn message from server."""
        print(f"Received player spawn: {player_id} at {spawn_position}")
        
        # Determine if this is our own player
        is_owner = False
        if self.game and hasattr(self.game, 'network_manager') and self.game.network_manager:
            if self.game.network_manager.mode == 'client' and self.game.network_manager.client:
                is_owner = (player_id == self.game.network_manager.client.client_id)
        
        self.spawn_player(player_id, spawn_position, is_owner=is_owner)
    
    def on_player_despawn(self, player_id: str):
        """Handle player despawn message from server."""
        print(f"Received player despawn: {player_id}")
        if player_id in self.spawned_players:
            player = self.spawned_players[player_id]
            self.remove_actor(player)
            del self.spawned_players[player_id]
        
    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.game:
                    self.game.pop_scene()