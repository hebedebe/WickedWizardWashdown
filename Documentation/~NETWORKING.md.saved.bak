# Networking System

The networking system provides client-server multiplayer capabilities with automatic synchronization of actors and components across network connections.

## Overview

The networking system consists of:
- **NetworkManager** - Handles client-server connections
- **NetworkComponent** - Synchronizes individual actors across the network
- **Message System** - Handles communication between clients and server

## Basic Setup

### Setting Up Network Manager

```python
from engine import NetworkManager, NetworkComponent

# Create network manager
network_manager = NetworkManager()

# Set up NetworkComponent to use this manager
NetworkComponent.set_network_manager(network_manager)
```

### Server Setup

```python
# Start as server
if is_server:
    network_manager.start_server(port=12345)
    print("Server started on port 12345")
```

### Client Setup

```python
# Connect as client
if is_client:
    success = network_manager.connect_to_server("localhost", 12345, client_id="player1")
    if success:
        print("Connected to server")
    else:
        print("Failed to connect")
```

## NetworkComponent

The NetworkComponent automatically synchronizes actors across network connections.

### Basic Networked Actor

```python
from engine import Actor, SpriteComponent, NetworkComponent, NetworkOwnership

# Create an actor
player = Actor("NetworkedPlayer")

# Add visual component
sprite = SpriteComponent(color=pygame.Color(0, 255, 0), size=pygame.Vector2(32, 32))
player.add_component(sprite)

# Add network component
network_comp = NetworkComponent(
    owner_id="player1",                    # Who owns this object
    ownership=NetworkOwnership.CLIENT,     # Ownership type
    sync_transform=True                    # Sync position/rotation
)
player.add_component(network_comp)

# Add to scene
scene.add_actor(player)
```

### Network Ownership Types

```python
from engine import NetworkOwnership

# Server owns the object (authoritative)
NetworkOwnership.SERVER

# Client owns the object (sends updates to server)
NetworkOwnership.CLIENT  

# Local-only object (not synchronized)
NetworkOwnership.LOCAL
```

### Component Synchronization

```python
# Create networked actor with multiple components
actor = Actor("ComplexNetworkedActor")

# Add components that will be synchronized
actor.add_component(SpriteComponent())
actor.add_component(HealthComponent(100))
actor.add_component(RigidBodyComponent())

# Network component automatically syncs all components
network_comp = NetworkComponent(
    owner_id="server",
    ownership=NetworkOwnership.SERVER,
    sync_transform=True
)

# Exclude specific components from sync
network_comp.blacklist_component(AudioComponent)  # Don't sync audio

# Exclude specific variables from sync
network_comp.blacklist_variable("SpriteComponent", "surface")  # Don't sync sprite surface

actor.add_component(network_comp)
```

## NetworkManager

Handles the underlying client-server communication.

### Server Operations

```python
network_manager = NetworkManager()

# Start server
network_manager.start_server(port=12345, max_clients=8)

# Check server status
if network_manager.is_server():
    print("Running as server")
    
# Get connected clients
clients = network_manager.get_connected_clients()
print(f"Connected clients: {len(clients)}")

# Send message to specific client
network_manager.send_to_client("player1", {"type": "welcome", "message": "Hello!"})

# Broadcast to all clients
network_manager.broadcast_message({"type": "game_start"})

# Stop server
network_manager.stop_server()
```

### Client Operations

```python
# Connect to server
success = network_manager.connect_to_server("192.168.1.100", 12345, "player2")

# Check connection status
if network_manager.is_connected():
    print("Connected to server")
    
# Send message to server
network_manager.send_to_server({"type": "player_input", "keys": ["w", "a"]})

# Disconnect
network_manager.disconnect()
```

### Message Handling

```python
# Set up message handlers
def handle_player_join(message):
    player_id = message["player_id"]
    print(f"Player {player_id} joined the game")
    
def handle_game_state(message):
    game_state = message["game_state"]
    # Update local game state
    
# Register handlers
network_manager.add_message_handler("player_join", handle_player_join)
network_manager.add_message_handler("game_state", handle_game_state)
```

## Game Integration

### In Main Game Setup

```python
# main.py
from engine import Game, NetworkComponent
from game import scenes

def main():
    game = Game(800, 600, "Multiplayer Game")
    
    # Configure networking
    NetworkComponent.set_network_manager(game.network_manager)
    
    # Add scenes
    game.add_scene("menu", MainMenuScene())
    game.add_scene("game", MultiplayerGameScene())
    
    game.load_scene("menu")
    game.run()
```

### In Scene Setup

```python
class MultiplayerGameScene(Scene):
    def __init__(self):
        super().__init__("MultiplayerGame")
        self.is_server = False
        self.players = {}
        
    def on_enter(self):
        super().on_enter()
        
        # Set up networking based on mode
        network_manager = self.game.network_manager
        
        if self.is_server:
            network_manager.start_server(port=12345)
            self.setup_server_handlers()
        else:
            network_manager.connect_to_server("localhost", 12345, "client")
            self.setup_client_handlers()
            
        self.create_local_player()
        
    def setup_server_handlers(self):
        network_manager = self.game.network_manager
        network_manager.add_message_handler("client_connect", self.on_client_connect)
        network_manager.add_message_handler("player_input", self.on_player_input)
        
    def setup_client_handlers(self):
        network_manager = self.game.network_manager
        network_manager.add_message_handler("game_state", self.on_game_state)
        
    def create_local_player(self):
        # Create player owned by this instance
        player_id = "server" if self.is_server else "client"
        ownership = NetworkOwnership.SERVER if self.is_server else NetworkOwnership.CLIENT
        
        player = self.create_actor(f"Player_{player_id}")
        player.add_component(SpriteComponent(color=pygame.Color(0, 255, 0)))
        player.add_component(NetworkComponent(
            owner_id=player_id,
            ownership=ownership,
            sync_transform=True
        ))
        
        self.players[player_id] = player
```

## Advanced Features

### Custom Network Messages

```python
class GameMessage:
    def __init__(self, message_type, data):
        self.type = message_type
        self.data = data
        self.timestamp = time.time()
        
    def to_dict(self):
        return {
            "type": self.type,
            "data": self.data,
            "timestamp": self.timestamp
        }

# Send custom message
message = GameMessage("chat", {"player": "Alice", "text": "Hello!"})
network_manager.send_to_server(message.to_dict())
```

### State Synchronization

```python
class GameStateManager:
    def __init__(self, scene):
        self.scene = scene
        self.last_update = 0
        self.update_rate = 30  # Updates per second
        
    def update(self, dt):
        current_time = time.time()
        if current_time - self.last_update > 1.0 / self.update_rate:
            self.send_game_state()
            self.last_update = current_time
            
    def send_game_state(self):
        state = {
            "players": {},
            "timestamp": time.time()
        }
        
        # Collect player states
        for player_id, player in self.scene.players.items():
            pos = player.transform.world_position
            state["players"][player_id] = {
                "position": {"x": pos.x, "y": pos.y},
                "health": player.get_component(HealthComponent).current_health
            }
            
        # Send to clients
        network_manager = self.scene.game.network_manager
        network_manager.broadcast_message({"type": "game_state", "state": state})
```

### Lag Compensation

```python
class LagCompensation:
    def __init__(self):
        self.position_history = []
        self.max_history = 60  # Keep 1 second of history at 60fps
        
    def record_position(self, position, timestamp):
        self.position_history.append({
            "position": position,
            "timestamp": timestamp
        })
        
        # Keep only recent history
        if len(self.position_history) > self.max_history:
            self.position_history.pop(0)
            
    def get_position_at_time(self, timestamp):
        # Find position at specific timestamp for lag compensation
        for record in reversed(self.position_history):
            if record["timestamp"] <= timestamp:
                return record["position"]
        return None
```

## Best Practices

### Network Optimization

1. **Limit Update Frequency** - Don't sync every frame
```python
# Only sync when significant changes occur
if movement_vector.length() > threshold:
    network_comp.mark_dirty()
```

2. **Use Appropriate Ownership** - Server authoritative for important objects
```python
# Server owns game-critical objects
game_manager = NetworkComponent(
    owner_id="server",
    ownership=NetworkOwnership.SERVER
)

# Clients own their input/UI
player_ui = NetworkComponent(
    owner_id="player1", 
    ownership=NetworkOwnership.CLIENT
)
```

3. **Selective Synchronization** - Don't sync everything
```python
# Blacklist expensive or unnecessary data
network_comp.blacklist_component(ParticleSystem)  # Don't sync particles
network_comp.blacklist_variable("SpriteComponent", "surface")  # Don't sync images
```

### Error Handling

```python
def safe_network_operation():
    try:
        network_manager.send_to_server({"type": "ping"})
    except NetworkError as e:
        print(f"Network error: {e}")
        # Handle disconnection
        game.load_scene("connection_lost")
        
# Check connection before sending
if network_manager.is_connected():
    network_manager.send_message(data)
```

### Security Considerations

1. **Validate Input** - Always validate data from clients
2. **Server Authority** - Server makes final decisions on game state
3. **Rate Limiting** - Prevent message spam
4. **Sanitize Data** - Clean user input before processing

### Performance Tips

1. **Batch Updates** - Group multiple changes into single messages
2. **Prioritize Updates** - Send important data more frequently
3. **Use Binary Protocols** - For high-frequency data
4. **Implement Delta Compression** - Only send what changed

The networking system provides a foundation for multiplayer games while keeping the complexity manageable for most use cases.
