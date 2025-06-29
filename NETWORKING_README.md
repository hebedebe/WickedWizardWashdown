# Networking System Documentation

The networking system provides comprehensive multiplayer functionality for the Wicked Wizard Washdown game engine. It enables automatic synchronization of game objects and their components across multiple clients in a client-server architecture.

## Features

- **Automatic Component Synchronization**: All components on networked actors are automatically synchronized without needing special networked versions
- **Flexible Sync Filtering**: Whitelist/blacklist modes to control which components are synchronized
- **Secure Serialization**: Custom serialization system (no pickle) for security and compatibility
- **Optimized Network Traffic**: Intelligent throttling and delta compression to minimize bandwidth usage
- **Late-joining Support**: Full synchronization for clients that connect after objects are spawned
- **Scene Synchronization**: Networked scene changes that affect all connected clients
- **Player Management**: Built-in player tracking with configurable maximum player limits
- **Robust Error Handling**: Comprehensive error handling and connection management

## Core Components

### NetworkManager
Central network coordinator that handles:
- Server hosting and client connections
- Message routing and delivery
- Connection state management
- Player limits and authentication

### NetworkComponent
The single component type needed for networking:
- Attach to any actor to make it networked
- Automatically syncs all other components on the actor
- Configurable sync filtering (blacklist/whitelist)
- Handles ownership and authority

### NetworkSerialization
Secure serialization system:
- JSON-based serialization (no pickle)
- Handles pygame types (Vector2, Color, Rect)
- Recursive serialization of complex objects
- Version-safe deserialization

## Quick Start

### Basic Server/Client Setup

```python
from engine import get_network_manager, spawn_network_actor, Actor, SpriteComponent

# Get the network manager
network_manager = get_network_manager()

# Server
network_manager.host("localhost", 8888)

# Client
network_manager.connect("localhost", 8888)
```

### Spawning Networked Actors

```python
# Create an actor with components
actor = Actor("MyNetworkedActor")
actor.add_component(SpriteComponent())

# Spawn it on the network - NetworkComponent is automatically added
spawn_network_actor(actor)

# The actor and all its components will be synchronized across all clients
```

### Component Synchronization

All components are automatically synchronized by default. You can control this behavior:

```python
# Get the NetworkComponent
network_comp = actor.get_component(NetworkComponent)

# Use blacklist mode (sync everything except blacklisted)
network_comp.set_sync_mode("blacklist")
network_comp.add_to_blacklist("SomeComponent")

# Use whitelist mode (only sync whitelisted components)
network_comp.set_sync_mode("whitelist")
network_comp.add_to_whitelist("SpriteComponent")
network_comp.add_to_whitelist("PhysicsComponent")
```

### Player Controllers

For player-controlled actors, use separate player controller and network components:

```python
class PlayerController:
    def __init__(self, player_id):
        self.player_id = player_id
        self.actor = None
        self.enabled = True
    
    def update(self, dt):
        # Handle input and update actor
        pass

# Create player actor
player_actor = Actor(f"Player_{player_id}")
player_actor.add_component(SpriteComponent())
player_actor.add_component(PlayerController(player_id))

# Spawn on network with specific owner
spawn_network_actor(player_actor, owner_id=player_id)
```

### Scene Management

```python
from engine import change_scene_networked

# Only the server can initiate scene changes
if network_manager.is_server:
    change_scene_networked("new_scene_name")
```

## Advanced Features

### Full Synchronization

Clients can request complete state synchronization:

```python
from engine import request_full_sync

# Request all networked objects from server
request_full_sync()
```

### Player Management

```python
from engine import get_player_manager

player_manager = get_player_manager()

# Check player count
current_players = player_manager.get_player_count()
max_players = player_manager.get_max_players()

# Get player list
player_ids = player_manager.get_player_list()

# Set/get player data
player_manager.set_player_data(player_id, {"score": 100, "level": 5})
data = player_manager.get_player_data(player_id)
```

### Network Optimization

```python
from engine import get_network_optimizer

optimizer = get_network_optimizer()

# Enable compression
optimizer.enable_compression(True)

# Enable delta compression
optimizer.enable_delta_compression(True)

# Get network statistics
stats = optimizer.get_network_stats()
print(f"Bytes sent: {stats['bytes_sent']}")
```

### Debugging

```python
from engine import get_network_debugger

debugger = get_network_debugger()

# Get recent network messages
recent_messages = debugger.get_recent_messages(10)

# Get message statistics
stats = debugger.get_message_stats()

# Diagnose connection issues
issues = debugger.diagnose_connection_issues()
for issue in issues:
    print(f"Network issue: {issue}")
```

## Message Types

The system uses these internal message types:

- `CONNECT_REQUEST/RESPONSE`: Client connection handshake
- `DISCONNECT`: Clean disconnection notification
- `SPAWN_ACTOR`: Create new networked actor
- `DESTROY_ACTOR`: Remove networked actor
- `COMPONENT_UPDATE`: Sync component changes
- `SCENE_CHANGE`: Synchronize scene transitions
- `FULL_SYNC_REQUEST/DATA`: Complete state synchronization
- `PING/PONG`: Connection health monitoring

## Performance Considerations

### Update Rates
- Network updates: 20 Hz (configurable)
- Component sync: Only when changed (delta compression)
- Full sync: On-demand only

### Bandwidth Optimization
- JSON compression for large messages
- Delta compression for component updates
- Intelligent throttling prevents spam
- Automatic message batching

### Memory Management
- Automatic cleanup on disconnection
- Circular message buffers
- Garbage collection of stale references

## Security Features

### Safe Serialization
- No `pickle` or `eval()` usage
- JSON-only data format
- Type validation on deserialization
- Sanitized attribute access

### Connection Security
- Client validation on connect
- Message authentication
- Rate limiting protection
- Automatic bad client disconnection

## Error Handling

The system gracefully handles:
- Network disconnections
- Malformed messages
- Serialization errors
- Missing components/actors
- Resource exhaustion

## Testing

Run the comprehensive test suite:

```bash
python test_networking.py
```

The tests cover:
- Basic connection establishment
- Actor spawning and synchronization
- Component updates
- Error conditions
- Performance scenarios

## Example Usage

See `networking_demo.py` for a complete example showing:
- Server hosting and client connection
- Player creation and movement
- Dynamic object spawning
- Scene management
- Real-time synchronization

## Integration with Game Loop

The networking system integrates seamlessly with the game engine:

```python
# In your game initialization
game = Game(800, 600, "My Networked Game")

# The network manager is automatically available
network_manager = game.network_manager

# Network updates happen automatically in the game loop
# No manual update calls needed
```

## Limitations

- Maximum 16 players per server (configurable)
- TCP-based (reliable but higher latency than UDP)
- No built-in voice chat or complex matchmaking
- Client-server only (no peer-to-peer)

## Future Enhancements

Planned improvements:
- UDP option for real-time data
- Built-in lag compensation
- Advanced interpolation/extrapolation
- Hierarchical networking for large worlds
- Built-in anti-cheat measures
