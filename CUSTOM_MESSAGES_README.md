# Custom Network Messages System

The enhanced networking system now supports versatile custom messages with priority-based processing instead of hard-coded message types. This makes the system much more flexible and extensible.

## Key Features

### 1. Priority-Based Processing
Messages are processed based on their priority level:
- **INSTANT**: Chat messages, critical events (processed immediately)
- **HIGH**: Player actions, game state changes (60 FPS)
- **MEDIUM**: Regular updates, position sync (20 FPS)
- **LOW**: Background data, statistics (5 FPS)

### 2. Custom Message Types
Instead of hard-coded message types like `CHAT_MESSAGE`, `PLAYER_JOIN`, etc., there's now a single `CUSTOM_MESSAGE` type that can carry any application-specific data.

## Usage Examples

### Basic Custom Messages

```python
from engine.networking import get_network_manager, NetworkPriority

network_manager = get_network_manager()

# Send a chat message with instant priority
network_manager.send_custom_message(
    "chat", 
    {"message": "Hello everyone!"}, 
    NetworkPriority.INSTANT, 
    "PlayerName"
)

# Send a game event with high priority
network_manager.send_custom_message(
    "spell_cast", 
    {"spell": "fireball", "target": "enemy1", "damage": 50}, 
    NetworkPriority.HIGH, 
    "Wizard123"
)

# Send a status update with medium priority
network_manager.send_custom_message(
    "status_update", 
    {"health": 80, "mana": 120}, 
    NetworkPriority.MEDIUM, 
    "PlayerName"
)
```

### Registering Message Handlers

```python
def handle_chat_message(event_data, sender_name, timestamp):
    message = event_data.get("message", "")
    print(f"[CHAT] {sender_name}: {message}")

def handle_spell_cast(event_data, sender_name, timestamp):
    spell = event_data.get("spell", "unknown")
    target = event_data.get("target", "none")
    damage = event_data.get("damage", 0)
    print(f"{sender_name} cast {spell} on {target} for {damage} damage")

# Register handlers
network_manager.register_custom_handler("chat", handle_chat_message)
network_manager.register_custom_handler("spell_cast", handle_spell_cast)
```

### Using the CustomMessageHelper

For even easier usage, there's a helper class:

```python
from engine.network_utils import get_custom_message_helper

msg_helper = get_custom_message_helper()

# Setup common handlers with appropriate priorities
msg_helper.setup_common_handlers()

# Add your own custom handlers
def handle_item_pickup(event_data, sender_name, timestamp):
    item = event_data.get("item", "unknown")
    print(f"{sender_name} picked up {item}")

msg_helper.register_handler("item_pickup", handle_item_pickup, NetworkPriority.HIGH)

# Send messages easily
msg_helper.broadcast_chat("Player1", "Found a rare sword!")
msg_helper.send("item_pickup", {"item": "rare_sword", "location": "dungeon"}, "Player1")
```

## Benefits

### 1. **Flexibility**
- Add new message types without modifying core networking code
- Each message type can have its own priority level
- Easy to extend for game-specific needs

### 2. **Performance**
- Critical messages (like chat) are processed instantly
- Non-critical updates are throttled to appropriate rates
- Reduces network congestion and improves responsiveness

### 3. **Simplicity**
- Single message type handles all application data
- Easy-to-use helper classes
- Consistent API across all message types

### 4. **Extensibility**
- Perfect for different game genres
- Can handle any JSON-serializable data
- Easy to add compression, encryption, or other features

## Migration from Old System

Old way (specific message types):
```python
# Before
network_manager.send_chat_message("Player1", "Hello!")
network_manager.announce_player_joined("Player2")
```

New way (custom messages):
```python
# After
network_manager.send_custom_message("chat", {"message": "Hello!"}, NetworkPriority.INSTANT, "Player1")
network_manager.send_custom_message("player_join", {"player_name": "Player2"}, NetworkPriority.HIGH)

# Or using the helper
msg_helper = get_custom_message_helper()
msg_helper.broadcast_chat("Player1", "Hello!")
msg_helper.send("player_join", {"player_name": "Player2"})
```

## Example: Complete Chat System

```python
class ChatSystem:
    def __init__(self):
        self.network_manager = get_network_manager()
        self.msg_helper = get_custom_message_helper()
        self.chat_history = []
        
        # Register chat handler with instant priority
        self.msg_helper.register_handler("chat", self.handle_chat_message, NetworkPriority.INSTANT)
    
    def handle_chat_message(self, event_data, sender_name, timestamp):
        message = event_data.get("message", "")
        self.chat_history.append({
            'sender': sender_name,
            'message': message,
            'timestamp': timestamp
        })
        print(f"[{timestamp}] {sender_name}: {message}")
    
    def send_message(self, sender_name, message):
        # Instant delivery for chat messages
        self.msg_helper.send("chat", {"message": message}, sender_name)
    
    def get_recent_messages(self, count=10):
        return self.chat_history[-count:]
```

This new system provides the foundation for any type of networked application, from simple chat systems to complex multiplayer games with real-time updates.
