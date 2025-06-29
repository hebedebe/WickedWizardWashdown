# NetworkComponent Documentation

The `NetworkComponent` is a powerful system for automatically synchronizing actors and their components across a network. It handles spawning, updating, and destroying networked objects with minimal setup required.

## Features

- **Automatic Synchronization**: Automatically syncs actor transforms and component data
- **Selective Blacklisting**: Choose which components or variables to exclude from sync
- **Ownership Management**: Support for server, client, and local ownership models
- **Efficient Updates**: Only sends data when changes are detected
- **Spawning/Destroying**: Networked creation and destruction of actors
- **Transform Sync**: Optional automatic synchronization of position, rotation, and scale

## Basic Usage

### 1. Setting Up the Network Manager

First, ensure your NetworkComponent has access to the NetworkManager:

```python
from engine import NetworkComponent, NetworkManager

# Create network manager
network_manager = NetworkManager()

# Start as server or connect as client
if is_server:
    network_manager.start_server(port=12345)
else:
    network_manager.connect_to_server("localhost", 12345)

# Set the network manager for all NetworkComponents
NetworkComponent.set_network_manager(network_manager)
```

### 2. Creating a Networked Actor

```python
from engine import Actor, SpriteComponent, NetworkComponent, NetworkOwnership

# Create an actor
actor = Actor("MyNetworkedActor")

# Add visual component
sprite = SpriteComponent(color=pygame.Color(255, 0, 0))
actor.add_component(sprite)

# Add network component for synchronization
network_comp = NetworkComponent(
    owner_id="server",                    # Who owns this object
    ownership=NetworkOwnership.SERVER,    # Server has authority
    sync_transform=True,                  # Sync position/rotation/scale
    sync_rate=30.0                       # 30 updates per second
)
actor.add_component(network_comp)
```

### 3. Ownership Models

#### Server Ownership
```python
# Server has authority over this object
network_comp = NetworkComponent(
    owner_id="server",
    ownership=NetworkOwnership.SERVER
)
```

#### Client Ownership
```python
# Specific client has authority
client_id = "client_12345"
network_comp = NetworkComponent(
    owner_id=client_id,
    ownership=NetworkOwnership.CLIENT
)
```

#### Local Only
```python
# Object exists only locally (not synced)
network_comp = NetworkComponent(
    ownership=NetworkOwnership.LOCAL
)
```

## Advanced Features

### Blacklisting Components and Variables

You can control exactly what gets synchronized:

```python
# Don't sync the entire PhysicsComponent
network_comp.blacklist_component(PhysicsComponent)

# Only blacklist specific variables from a component
network_comp.blacklist_variable(PhysicsComponent, 'mass')
network_comp.blacklist_variable(PhysicsComponent, 'acceleration')

# Remove from blacklist
network_comp.whitelist_component(PhysicsComponent)
network_comp.whitelist_variable(PhysicsComponent, 'mass')
```

### Manual Sync Control

```python
# Force a sync on the next update
network_comp.force_sync_next_update()

# Mark a specific component as needing sync
network_comp.mark_component_dirty(PhysicsComponent)
```

### Convenience Methods

```python
# Easy way to spawn a networked actor
network_comp = NetworkComponent.spawn_networked_actor(
    actor, 
    owner_id="server", 
    ownership=NetworkOwnership.SERVER
)

# Find a networked actor by its network ID
actor = NetworkComponent.get_networked_actor(network_id)
```

## Example: Networked Player

```python
class NetworkedPlayer(Actor):
    def __init__(self, owner_id: str):
        super().__init__(f"Player_{owner_id}")
        
        # Visual component
        sprite = SpriteComponent(
            color=pygame.Color(0, 128, 255),
            size=pygame.Vector2(32, 32)
        )
        self.add_component(sprite)
        
        # Physics for movement
        physics = PhysicsComponent()
        physics.mass = 1.0
        physics.drag = 5.0
        self.add_component(physics)
        
        # Health system
        health = HealthComponent(max_health=100.0)
        self.add_component(health)
        
        # Network synchronization
        network_comp = NetworkComponent(
            owner_id=owner_id,
            ownership=NetworkOwnership.CLIENT if owner_id != "server" else NetworkOwnership.SERVER,
            sync_transform=True,
            sync_rate=30.0
        )
        
        # Don't sync physics acceleration (calculated locally)
        network_comp.blacklist_variable(PhysicsComponent, 'acceleration')
        
        self.add_component(network_comp)
```

## Integration with Game Loop

```python
class MyGame(Game):
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
    
    def update(self, dt: float):
        # Update network manager (handles message processing)
        self.network_manager.update(dt)
        
        # Update game (NetworkComponents will sync automatically)
        super().update(dt)
    
    def cleanup(self):
        self.network_manager.cleanup()
        super().cleanup()
```

## Message Types

The NetworkComponent adds these message types to the networking system:

- `ACTOR_SYNC`: Synchronizes actor state between clients
- `ACTOR_SPAWN`: Spawns a new networked actor
- `ACTOR_DESTROY`: Destroys a networked actor
- `COMPONENT_SYNC`: Synchronizes individual component data

## Best Practices

1. **Use appropriate sync rates**: Higher rates = more responsive but more bandwidth
2. **Blacklist unnecessary data**: Don't sync computed values or large data structures
3. **Proper ownership**: Let the authoritative source control movement/state changes
4. **Test with latency**: Use network simulation tools to test real-world conditions

## Performance Considerations

- Only syncs when data actually changes
- Configurable sync rates to balance responsiveness vs bandwidth
- Selective synchronization through blacklisting
- Efficient serialization using pickle
- Delta compression (future enhancement)

## Limitations

- Components must be serializable with pickle
- pygame.Surface objects are automatically skipped
- Circular references should be avoided
- Large objects can impact network performance

## Future Enhancements

- Delta compression for efficient updates
- Prediction and lag compensation
- Custom serialization for specific types
- Bandwidth monitoring and throttling
- Automatic interpolation for smooth movement
