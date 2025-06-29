# NetworkComponent - Quick Start Guide

The `NetworkComponent` automatically synchronizes actors and their components across clients and servers. This allows for easy creation of networked gameplay without manual network code.

## Quick Setup

### 1. Add NetworkComponent to any Actor

```python
from engine import Actor, NetworkComponent, NetworkOwnership

# Create your actor
player = Actor("NetworkedPlayer")

# Add any components you want (sprites, physics, etc.)
player.add_component(SpriteComponent())
player.add_component(PhysicsComponent())

# Add network component for automatic sync
network_comp = NetworkComponent(
    owner_id="client_123",           # Who controls this actor
    ownership=NetworkOwnership.CLIENT,  # Client has authority
    sync_transform=True,             # Sync position/rotation automatically
    sync_rate=30.0                  # 30 updates per second
)
player.add_component(network_comp)
```

### 2. Set up Network Manager (once per game)

```python
from engine import NetworkManager

# Initialize networking
network_manager = NetworkManager()

# Start server or connect to one
if is_server:
    network_manager.start_server(12345)
else:
    network_manager.connect_to_server("localhost", 12345)

# Tell NetworkComponent about the network manager
NetworkComponent.set_network_manager(network_manager)

# Update in your game loop
def update(dt):
    network_manager.update(dt)  # This handles all the networking
    # ... rest of your game update
```

## That's It!

Your actors will now automatically:
- ✅ Spawn on all connected clients
- ✅ Sync their position, rotation, and scale
- ✅ Sync all component data
- ✅ Destroy on all clients when removed

## Control What Gets Synced

```python
# Don't sync the entire physics component
network_comp.blacklist_component(PhysicsComponent)

# Or just blacklist specific variables
network_comp.blacklist_variable(PhysicsComponent, 'mass')
network_comp.blacklist_variable(PhysicsComponent, 'acceleration')
```

## Examples

Run the example:
```bash
# Terminal 1 (Server)
python examples/network_component_demo.py --mode server

# Terminal 2 (Client)
python examples/network_component_demo.py --mode client
```

Move around with WASD, press Space to spawn objects. Everything syncs automatically!

## How It Works

1. **Ownership**: Each networked object has an owner (server or specific client)
2. **Authority**: Only the owner sends updates for that object
3. **Automatic Sync**: Components detect changes and sync at the specified rate
4. **Selective Sync**: Blacklist system lets you control what data is sent
5. **Spawning**: Objects are automatically created on all clients when added

The NetworkComponent handles all the networking complexity - you just focus on your game logic!
