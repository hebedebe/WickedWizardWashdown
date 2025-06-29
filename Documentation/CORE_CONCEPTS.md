# Core Concepts

Understanding the fundamental architecture of the Wicked Wizard Washdown engine will help you build better games.

## Engine Architecture

The engine follows an **Entity-Component-System (ECS)** pattern:

```
Game
 ├── Scenes (containers for game objects)
 │   ├── Actors (game entities)
 │   │   ├── Components (behaviors and data)
 │   │   └── Transform (position, rotation, scale)
 │   └── Systems (physics, rendering, etc.)
 └── Managers (input, assets)
```

## Core Classes Overview

### Game (Singleton)
The main orchestrator that manages everything:
- Game loop and timing
- Scene management
- System coordination
- Global managers

### Scene
Containers that organize and manage related game objects:
- Hold collections of actors
- Manage scene-specific logic
- Handle scene transitions
- Provide lifecycle events

### Actor
Game entities that can be composed with components:
- Have a transform (position, rotation, scale)
- Can have child actors (hierarchy)
- Can be tagged for easy finding
- Act as containers for components

### Component
Modular pieces of functionality that can be attached to actors:
- Provide specific behaviors (rendering, physics, input)
- Are data-driven and reusable
- Can communicate with other components on the same actor

### Transform
Handles spatial relationships:
- Position, rotation, and scale
- Hierarchical transformations (parent-child relationships)
- Local vs world coordinates

## The Component Pattern

Instead of inheritance, we use composition:

```python
# ❌ Traditional inheritance (rigid)
class Player(GameObject):
    def __init__(self):
        self.sprite = PlayerSprite()
        self.physics = PlayerPhysics()
        self.input = PlayerInput()

# ✅ Component composition (flexible)
player = Actor("Player")
player.add_component(SpriteComponent())
player.add_component(RigidBodyComponent())
player.add_component(InputComponent())
```

### Benefits of Components:
- **Reusability**: Components work on any actor
- **Modularity**: Easy to add/remove functionality
- **Testability**: Components can be tested in isolation
- **Flexibility**: Mix and match behaviors easily

## Scene Management

### Scene Lifecycle

```python
class MyScene(Scene):
    def on_enter(self):
        """Called when scene becomes active"""
        # Set up actors, UI, etc.
        
    def on_exit(self):
        """Called when leaving scene"""
        # Clean up resources
        
    def on_pause(self):
        """Called when another scene is pushed on top"""
        # Pause updates but keep in memory
        
    def on_resume(self):
        """Called when returning from scene stack"""
        # Resume updates
        
    def update(self, dt):
        """Called every frame"""
        super().update(dt)  # Updates all actors
        # Custom scene logic
```

### Scene Stack vs Scene Switching

**Scene Switching** (replaces current scene):
```python
game.load_scene("main_menu")  # Completely switch scenes
```

**Scene Stack** (overlays scenes):
```python
game.push_scene("pause_menu")  # Overlay on current scene
game.pop_scene()               # Return to previous scene
```

## Actor Hierarchy

Actors can have parent-child relationships:

```python
# Create a car
car = scene.create_actor("Car")

# Add wheels as children
wheel1 = Actor("FrontWheel")
wheel2 = Actor("BackWheel")

car.add_child(wheel1)
car.add_child(wheel2)

# When car moves, wheels move with it automatically
car.transform.local_position = pygame.Vector2(100, 100)
```

### Transform Hierarchy

Transforms are calculated relative to parents:

```python
# Parent at (100, 100)
parent.transform.local_position = pygame.Vector2(100, 100)

# Child at (20, 20) relative to parent
child.transform.local_position = pygame.Vector2(20, 20)

# Child's world position is (120, 120)
world_pos = child.transform.world_position  # (120, 120)
```

## Component Communication

Components on the same actor can communicate:

```python
class PlayerController(Component):
    def update(self, dt):
        # Get input
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            # Tell physics component to jump
            physics = self.actor.get_component(RigidBodyComponent)
            if physics:
                physics.apply_impulse((0, -300))
                
            # Tell audio component to play sound
            audio = self.actor.get_component(AudioComponent)
            if audio:
                audio.play_sound("jump")
```

## Event-Driven Architecture

Many systems use events for loose coupling:

```python
# UI events
button.add_event_handler("clicked", self.on_button_click)

# Component events
health = HealthComponent(100)
health.on_death = self.handle_player_death
health.on_damage = lambda dmg: print(f"Took {dmg} damage!")

# Custom events
def on_level_complete():
    self.game.load_scene("next_level")
```

## Resource Management

### Singleton Pattern
Some systems use singletons for global access:

```python
# Game instance (singleton)
game = Game.get_instance()

# Physics world (singleton)
physics_world = PhysicsWorld.get_instance()
```

### Asset Management
Assets are loaded once and cached:

```python
# First load reads from disk
image1 = asset_manager.load_image("player.png")

# Second load returns cached version
image2 = asset_manager.load_image("player.png")  # Same object
```

## Data Flow

1. **Input** → Input Manager → Components
2. **Logic** → Components update themselves and communicate
3. **Physics** → Physics system updates physics components
4. **Rendering** → Graphics components render to screen
5. **Audio** → Audio components play sounds

```
Frame Start
    ↓
Handle Input Events
    ↓
Update Components (logic)
    ↓
Update Physics (fixed timestep)
    ↓
Update Transforms
    ↓
Render Scene
    ↓
Frame End
```

## Memory and Performance

### Object Pooling
For frequently created/destroyed objects:

```python
class BulletPool:
    def __init__(self, size=100):
        self.bullets = [self.create_bullet() for _ in range(size)]
        self.available = list(self.bullets)
        
    def get_bullet(self):
        if self.available:
            return self.available.pop()
        return None  # Pool exhausted
        
    def return_bullet(self, bullet):
        bullet.reset()
        self.available.append(bullet)
```

### Component Cleanup
Always clean up resources:

```python
class MyComponent(Component):
    def destroy(self):
        # Clean up any resources
        if self.texture:
            del self.texture
        super().destroy()
```

## Best Practices

### 1. Keep Components Focused
Each component should have a single responsibility:

```python
# ✅ Good - focused responsibility
class HealthComponent(Component):
    def take_damage(self, amount): ...
    def heal(self, amount): ...

# ❌ Bad - too many responsibilities  
class PlayerComponent(Component):
    def handle_input(self): ...
    def update_health(self): ...
    def play_animations(self): ...
```

### 2. Use Tags for Organization
Tag actors for easy grouping:

```python
player.add_tag("player")
enemy.add_tag("enemy")
enemy.add_tag("ground_unit")

# Find all enemies
enemies = scene.find_actors_with_tag("enemy")

# Find specific types
ground_enemies = scene.find_actors_with_tag("ground_unit")
```

### 3. Prefer Data-Driven Design
Configure behavior through data rather than code:

```python
# Configuration file: enemy_config.json
{
    "goblin": {
        "health": 30,
        "speed": 50,
        "damage": 10,
        "sprite": "goblin.png"
    }
}

# Code
def create_enemy(self, enemy_type, position):
    config = self.enemy_configs[enemy_type]
    enemy = self.create_actor(enemy_type, position)
    
    enemy.add_component(HealthComponent(config["health"]))
    enemy.add_component(SpriteComponent(config["sprite"]))
    # etc...
```

### 4. Handle Edge Cases
Always check for component existence:

```python
def update(self, dt):
    physics = self.actor.get_component(RigidBodyComponent)
    if physics:  # Component might not exist
        physics.apply_force(self.movement_force)
```

## Common Patterns

### State Machines
For complex behaviors:

```python
class EnemyAI(Component):
    def __init__(self):
        self.state = "patrol"
        self.states = {
            "patrol": self.patrol_update,
            "chase": self.chase_update,
            "attack": self.attack_update
        }
        
    def update(self, dt):
        self.states[self.state](dt)
        
    def set_state(self, new_state):
        self.state = new_state
```

### Observer Pattern
For decoupled communication:

```python
class EventManager:
    def __init__(self):
        self.listeners = {}
        
    def subscribe(self, event_type, callback):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
        
    def emit(self, event_type, data):
        for callback in self.listeners.get(event_type, []):
            callback(data)

# Usage
events = EventManager()
events.subscribe("player_died", self.handle_player_death)
events.emit("player_died", {"player_id": "player1"})
```

This architecture provides flexibility, maintainability, and scalability for game development.
