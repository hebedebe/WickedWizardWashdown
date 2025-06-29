# API Reference - Wicked Wizard Washdown Engine

## Networking Components

### NetworkComponent

Automatically synchronizes actors and their components across network connections.

```python
from engine import NetworkComponent, NetworkOwnership

network_comp = NetworkComponent(
    owner_id="client_123",                # Who owns this object
    ownership=NetworkOwnership.CLIENT,    # Authority model
    sync_transform=True,                  # Sync position/rotation/scale
    sync_rate=30.0                       # Updates per second
)
```

**Key Methods:**
- `blacklist_component(component_type)` - Exclude entire component from sync
- `blacklist_variable(component_type, variable_name)` - Exclude specific variable
- `force_sync_next_update()` - Force immediate sync
- `mark_component_dirty(component_type)` - Mark component for sync

**Class Methods:**
- `NetworkComponent.set_network_manager(network_manager)` - Set global network manager
- `NetworkComponent.spawn_networked_actor(actor, owner_id, ownership)` - Spawn networked actor
- `NetworkComponent.get_networked_actor(network_id)` - Get actor by network ID

### NetworkOwnership

Enum defining who has authority over a networked object:

```python
from engine import NetworkOwnership

NetworkOwnership.SERVER    # Server has authority
NetworkOwnership.CLIENT    # Specific client has authority  
NetworkOwnership.LOCAL     # Local only, not networked
```

## Core Networking

### NetworkManager

High-level networking interface supporting client/server architecture.

```python
from engine import NetworkManager

network_manager = NetworkManager()

# Server mode
network_manager.start_server(port=12345)

# Client mode  
network_manager.connect_to_server("localhost", 12345)

# Update in game loop
network_manager.update(dt)
```

### MessageType

Extended message types for networking:

```python
from engine.networking import MessageType

MessageType.CONNECT       # Client connection
MessageType.DISCONNECT    # Client disconnection
MessageType.GAME_STATE    # General game state
MessageType.PLAYER_INPUT  # Player input
MessageType.CHAT          # Chat messages
MessageType.CUSTOM        # Custom messages
MessageType.ACTOR_SYNC    # Actor synchronization (NEW)
MessageType.ACTOR_SPAWN   # Actor spawning (NEW)
MessageType.ACTOR_DESTROY # Actor destruction (NEW)
MessageType.COMPONENT_SYNC # Component sync (NEW)
```

## Example Usage

### Basic Networked Actor

```python
from engine import Actor, SpriteComponent, PhysicsComponent, NetworkComponent, NetworkOwnership

# Create actor
player = Actor("NetworkedPlayer")
player.add_component(SpriteComponent())
player.add_component(PhysicsComponent())

# Add networking - automatically syncs all components
network_comp = NetworkComponent(
    owner_id="server",
    ownership=NetworkOwnership.SERVER,
    sync_transform=True
)
player.add_component(network_comp)
```

### Selective Synchronization

```python
# Don't sync physics mass and acceleration
network_comp.blacklist_variable(PhysicsComponent, 'mass')
network_comp.blacklist_variable(PhysicsComponent, 'acceleration')

# Don't sync entire audio component
network_comp.blacklist_component(AudioComponent)
```

### Game Integration

```python
class NetworkedGame(Game):
    def __init__(self):
        super().__init__()
        self.network_manager = NetworkManager()
    
    def initialize(self):
        # Set up networking
        if self.is_server:
            self.network_manager.start_server(12345)
        else:
            self.network_manager.connect_to_server("localhost", 12345)
        
        # Configure NetworkComponent
        NetworkComponent.set_network_manager(self.network_manager)
        return super().initialize()
    
    def update(self, dt):
        self.network_manager.update(dt)  # Handle networking
        super().update(dt)               # Update game
```