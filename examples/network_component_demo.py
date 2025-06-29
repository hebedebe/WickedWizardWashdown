"""
Example demonstrating the NetworkComponent for automatic actor synchronization.
This example shows how to create networked actors that automatically sync
their state between server and clients.
"""

import pygame
import sys
import time
from typing import Dict, Optional
from engine import (
    Game, Scene, Actor, SpriteComponent, PhysicsComponent, 
    NetworkComponent, NetworkOwnership, NetworkManager
)


class NetworkedPlayer(Actor):
    """A player actor with networked synchronization."""
    
    def __init__(self, name: str, owner_id: str = "server", 
                 ownership: NetworkOwnership = NetworkOwnership.SERVER):
        super().__init__(name)
        
        # Add visual component
        sprite = SpriteComponent(
            color=pygame.Color(0, 128, 255),
            size=pygame.Vector2(32, 32)
        )
        self.add_component(sprite)
        
        # Add physics for movement
        physics = PhysicsComponent()
        physics.mass = 1.0
        physics.drag = 5.0  # Some drag for smoother movement
        self.add_component(physics)
        
        # Add network component for synchronization
        network_comp = NetworkComponent(
            owner_id=owner_id,
            ownership=ownership,
            sync_transform=True,
            sync_rate=30.0  # 30 updates per second
        )
        
        # Example of blacklisting - don't sync certain physics properties
        network_comp.blacklist_variable(PhysicsComponent, 'acceleration')
        network_comp.blacklist_variable(PhysicsComponent, 'mass')
        
        self.add_component(network_comp)
        
        # Movement speed
        self.move_speed = 200.0


class NetworkDemoScene(Scene):
    """Scene demonstrating networked actors."""
    
    def __init__(self):
        super().__init__("NetworkDemo")
        self.players: Dict[str, NetworkedPlayer] = {}
        self.is_server = False
        self.network_manager: Optional[NetworkManager] = None
        
    def start(self) -> None:
        """Initialize the scene."""
        super().start()
        
        # Get network manager from game
        self.network_manager = self.game.network_manager
        
        # Set the network manager for NetworkComponent
        NetworkComponent.set_network_manager(self.network_manager)
        
        # Check if we're running as server
        if self.network_manager and self.network_manager.mode == 'server':
            self.is_server = True
            self._create_server_players()
        else:
            self._create_client_player()
    
    def _create_server_players(self) -> None:
        """Create AI or server-controlled players."""
        # Create a server-controlled player
        server_player = NetworkedPlayer(
            "ServerPlayer", 
            owner_id="server",
            ownership=NetworkOwnership.SERVER
        )
        server_player.transform.local_position = pygame.Vector2(100, 100)
        server_player.add_tag("server_player")
        
        self.add_actor(server_player)
        self.players["server"] = server_player
    
    def _create_client_player(self) -> None:
        """Create a client-controlled player."""
        if self.network_manager and self.network_manager.client:
            client_id = self.network_manager.client.client_id
            
            client_player = NetworkedPlayer(
                f"Player_{client_id}",
                owner_id=client_id,
                ownership=NetworkOwnership.CLIENT
            )
            client_player.transform.local_position = pygame.Vector2(200, 200)
            client_player.add_tag("client_player")
            
            # Different color for client player
            sprite = client_player.get_component(SpriteComponent)
            if sprite:
                sprite.set_color(pygame.Color(255, 128, 0))
            
            self.add_actor(client_player)
            self.players[client_id] = client_player
    
    def update(self, dt: float) -> None:
        """Update the scene."""
        super().update(dt)
        
        # Handle player input for owned players
        self._handle_player_input(dt)
        
        # Example of server-side AI movement
        if self.is_server and "server" in self.players:
            self._update_server_player_ai(dt)
    
    def _handle_player_input(self, dt: float) -> None:
        """Handle input for client-controlled players."""
        if not self.network_manager or self.network_manager.mode != 'client':
            return
        
        client_id = self.network_manager.client.client_id if self.network_manager.client else ""
        if client_id not in self.players:
            return
        
        player = self.players[client_id]
        physics = player.get_component(PhysicsComponent)
        if not physics:
            return
        
        # Get input
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
        
        # Apply movement
        if movement.length() > 0:
            movement = movement.normalize()
            force = movement * player.move_speed * physics.mass
            physics.apply_force(force)
            
            # Mark network component as dirty for immediate sync
            network_comp = player.get_component(NetworkComponent)
            if network_comp:
                network_comp.mark_component_dirty(PhysicsComponent)
    
    def _update_server_player_ai(self, dt: float) -> None:
        """Simple AI movement for server player."""
        player = self.players["server"]
        physics = player.get_component(PhysicsComponent)
        if not physics:
            return
        
        # Simple circular movement
        current_time = time.time()
        target_pos = pygame.Vector2(
            300 + 100 * pygame.math.cos(current_time),
            300 + 100 * pygame.math.sin(current_time)
        )
        
        # Move towards target
        current_pos = player.transform.world_position
        direction = target_pos - current_pos
        
        if direction.length() > 5:
            direction = direction.normalize()
            force = direction * player.move_speed * physics.mass
            physics.apply_force(force)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle events."""
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Example: Spawn a new networked object
                self._spawn_example_object()
    
    def _spawn_example_object(self) -> None:
        """Example of spawning a networked object."""
        # Create a simple networked box
        box = Actor("NetworkedBox")
        
        # Random position
        import random
        box.transform.local_position = pygame.Vector2(
            random.randint(50, 750),
            random.randint(50, 550)
        )
        
        # Add sprite
        sprite = SpriteComponent(
            color=pygame.Color(255, 0, 255),
            size=pygame.Vector2(24, 24)
        )
        box.add_component(sprite)
        
        # Add physics
        physics = PhysicsComponent()
        physics.mass = 0.5
        physics.gravity = pygame.Vector2(0, 100)  # Gravity
        physics.bounce = 0.8
        box.add_component(physics)
        
        # Add network component
        if self.network_manager:
            if self.network_manager.mode == 'server':
                ownership = NetworkOwnership.SERVER
                owner_id = "server"
            else:
                ownership = NetworkOwnership.CLIENT
                owner_id = self.network_manager.client.client_id if self.network_manager.client else "client"
            
            network_comp = NetworkComponent(
                owner_id=owner_id,
                ownership=ownership,
                sync_transform=True,
                sync_rate=20.0
            )
            box.add_component(network_comp)
        
        self.add_actor(box)
        print(f"Spawned networked box at {box.transform.local_position}")


class NetworkDemoGame(Game):
    """Game demonstrating networked components."""
    
    def __init__(self, mode: str = "client", host: str = "localhost", port: int = 12345):
        super().__init__(
            title="Network Component Demo",
            window_size=(800, 600),
            target_fps=60
        )
        
        self.mode = mode
        self.host = host
        self.port = port
        self.network_manager = NetworkManager()
        
    def initialize(self) -> bool:
        """Initialize the game."""
        if not super().initialize():
            return False
        
        # Set up networking
        if self.mode == "server":
            if not self.network_manager.start_server(self.port):
                print("Failed to start server")
                return False
            print(f"Server started on port {self.port}")
        else:
            if not self.network_manager.connect_to_server(self.host, self.port):
                print(f"Failed to connect to server at {self.host}:{self.port}")
                return False
            print(f"Connected to server at {self.host}:{self.port}")
        
        # Create and start the demo scene
        demo_scene = NetworkDemoScene()
        self.scene_manager.add_scene(demo_scene)
        self.scene_manager.set_active_scene("NetworkDemo")
        
        return True
    
    def update(self, dt: float) -> None:
        """Update the game."""
        # Update network manager
        self.network_manager.update(dt)
        
        # Update game
        super().update(dt)
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.network_manager.cleanup()
        super().cleanup()
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle events."""
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.quit()


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Network Component Demo')
    parser.add_argument('--mode', choices=['server', 'client'], default='client',
                      help='Run as server or client')
    parser.add_argument('--host', default='localhost',
                      help='Server host (client mode only)')
    parser.add_argument('--port', type=int, default=12345,
                      help='Server port')
    
    args = parser.parse_args()
    
    # Create and run game
    game = NetworkDemoGame(args.mode, args.host, args.port)
    
    if game.initialize():
        print(f"Starting in {args.mode} mode...")
        print("Controls:")
        print("  WASD/Arrow Keys: Move player")
        print("  Space: Spawn networked box")
        print("  Escape: Quit")
        print()
        
        if args.mode == "server":
            print("Waiting for clients to connect...")
        
        game.run()
    else:
        print("Failed to initialize game")
        sys.exit(1)


if __name__ == "__main__":
    main()
