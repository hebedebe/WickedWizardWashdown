# Actors and Components

The Actor-Component system is the core of the engine's architecture, providing a flexible way to create game objects with modular behaviors.

## Actor System

Actors are the fundamental game entities that exist in your world. They can represent anything: players, enemies, platforms, UI elements, or invisible logic controllers.

### Creating Actors

```python
from engine import Actor
import pygame

# Basic actor creation
actor = Actor("MyActor")

# Set position and transformation
actor.transform.local_position = pygame.Vector2(100, 100)
actor.transform.local_rotation = 45  # degrees
actor.transform.local_scale = pygame.Vector2(2.0, 2.0)

# In a scene, use create_actor for automatic management
player = scene.create_actor("Player", pygame.Vector2(400, 300))
```

### Actor Properties

```python
actor = Actor("MyActor")

# Identity
actor.id        # Unique UUID string
actor.name      # Human-readable name

# Hierarchy
actor.parent    # Parent actor (None if root)
actor.children  # List of child actors

# State
actor.active    # Whether actor updates and renders
actor.enabled   # Whether actor processes events

# Transform
actor.transform # Transform component (always present)

# Tags
actor.tags      # List of string tags for identification
```

### Actor Hierarchy

Actors can have parent-child relationships, useful for complex objects:

```python
# Create a car with wheels
car = scene.create_actor("Car")
front_wheel = Actor("FrontWheel")
back_wheel = Actor("BackWheel")

# Establish hierarchy
car.add_child(front_wheel)
car.add_child(back_wheel)

# When car moves, wheels move with it
car.transform.local_position = pygame.Vector2(200, 300)

# Access hierarchy
parent = front_wheel.parent          # Returns car
siblings = car.children              # [front_wheel, back_wheel]
specific_child = car.find_child("FrontWheel")
```

### Actor Tags

Tags provide a way to categorize and find actors:

```python
# Add tags
player.add_tag("player")
player.add_tag("controllable")
enemy.add_tag("enemy")
enemy.add_tag("ground_unit")

# Check tags
if player.has_tag("controllable"):
    # Handle input

# Remove tags
player.remove_tag("controllable")

# Find actors by tag in scene
enemies = scene.find_actors_with_tag("enemy")
ground_units = scene.find_actors_with_tag("ground_unit")
```

### Actor Lifecycle

```python
class MyActor(Actor):
    def update(self, dt):
        """Called every frame when active"""
        super().update(dt)  # Updates all components
        # Custom actor logic
        
    def fixed_update(self, dt):
        """Called on fixed timestep for physics"""
        super().fixed_update(dt)
        # Physics-related updates
        
    def render(self, screen):
        """Called during rendering when active"""
        super().render(screen)  # Renders all components
        # Custom rendering
        
    def handle_event(self, event):
        """Called for input events"""
        super().handle_event(event)  # Forwards to components
        # Custom event handling
        
    def destroy(self):
        """Clean up when actor is destroyed"""
        # Custom cleanup
        super().destroy()  # Cleans up components
```

### Singleton Access to Game

Actors have easy access to the main game instance:

```python
class MyActor(Actor):
    def update(self, dt):
        game = self.game  # Access game instance
        
        if self.should_change_scene:
            game.load_scene("next_level")
            
        if self.should_quit:
            game.quit()
```

## Transform System

Every actor has a Transform component that handles position, rotation, and scale with full hierarchy support.

### Transform Properties

```python
transform = actor.transform

# Local transformation (relative to parent)
transform.local_position = pygame.Vector2(x, y)    # Position
transform.local_rotation = angle_in_degrees         # Rotation
transform.local_scale = pygame.Vector2(sx, sy)      # Scale

# World transformation (calculated automatically)
world_pos = transform.world_position    # Absolute position
world_rot = transform.world_rotation    # Absolute rotation  
world_scale = transform.world_scale     # Absolute scale
```

### Transform Hierarchy

Transforms are calculated relative to their parent:

```python
# Parent transform
parent.transform.local_position = pygame.Vector2(100, 100)
parent.transform.local_rotation = 45

# Child transform (relative to parent)
child.transform.local_position = pygame.Vector2(20, 0)
child.transform.local_rotation = 30

# Child's world transform is calculated automatically
# World position: (100, 100) + rotated(20, 0) at 45 degrees
# World rotation: 45 + 30 = 75 degrees
```

### Transform Operations

```python
# Get transformation matrix for advanced operations
matrix = transform.get_transformation_matrix()

# Force recalculation of world transform
transform.mark_dirty()

# Set parent relationship
child.transform.set_parent(parent.transform)
```

## Component System

Components provide modular functionality that can be attached to any actor. This composition-based approach is more flexible than inheritance.

### Base Component Class

```python
from engine import Component

class MyComponent(Component):
    def __init__(self):
        super().__init__()
        # Component initialization
        
    def start(self):
        """Called when component is first added to an actor"""
        pass
        
    def update(self, dt):
        """Called every frame"""
        pass
        
    def fixed_update(self, dt):
        """Called on fixed timestep"""
        pass
        
    def render(self, screen):
        """Called during rendering"""
        pass
        
    def handle_event(self, event):
        """Called for input events"""
        pass
        
    def destroy(self):
        """Called when component is removed or actor destroyed"""
        super().destroy()
```

### Managing Components

```python
# Add components to actors
sprite = SpriteComponent()
physics = RigidBodyComponent()

actor.add_component(sprite)
actor.add_component(physics)

# Get components by type
sprite_comp = actor.get_component(SpriteComponent)
physics_comp = actor.get_component(RigidBodyComponent)

# Check if actor has component
if actor.has_component(HealthComponent):
    health = actor.get_component(HealthComponent)
    health.take_damage(10)

# Remove components
removed_sprite = actor.remove_component(SpriteComponent)
```

### Component Communication

Components on the same actor can communicate through the actor:

```python
class PlayerController(Component):
    def update(self, dt):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_SPACE]:
            # Tell physics component to jump
            physics = self.actor.get_component(RigidBodyComponent)
            if physics:
                physics.apply_impulse((0, -300))
                
            # Tell audio component to play sound
            audio = self.actor.get_component(AudioComponent)
            if audio:
                audio.play_sound("jump")
                
            # Update health component
            health = self.actor.get_component(HealthComponent)
            if health:
                health.take_damage(1)  # Jumping costs health
```

### Accessing Game and Scene

Components have access to the game instance and current scene:

```python
class MyComponent(Component):
    def update(self, dt):
        # Access game
        game = self.game
        
        # Access current scene (if actor is in a scene)
        scene = self.actor.scene
        
        if some_condition:
            game.load_scene("game_over")
```

## Core Components

The engine provides several built-in components for common functionality.

### SpriteComponent

Renders visual representation of actors:

```python
from engine import SpriteComponent
import pygame

# Create with image
sprite = SpriteComponent(surface=my_image)

# Create with solid color
sprite = SpriteComponent(
    color=pygame.Color(255, 0, 0),
    size=pygame.Vector2(32, 32)
)

# Modify appearance
sprite.flip_x = True          # Horizontal flip
sprite.flip_y = False         # Vertical flip
sprite.alpha = 128            # Transparency (0-255)
sprite.offset = pygame.Vector2(0, -16)  # Offset from actor position

# Change sprite
sprite.set_surface(new_image)
sprite.set_color(pygame.Color(0, 255, 0))
```

### Physics Components

#### Simple PhysicsComponent
Basic physics simulation:

```python
from engine import PhysicsComponent

physics = PhysicsComponent()
physics.velocity = pygame.Vector2(100, 0)
physics.gravity = pygame.Vector2(0, 300)
physics.mass = 1.0
physics.drag = 0.98
physics.bounce = 0.7
physics.friction = 0.8

# Apply forces
physics.apply_force(pygame.Vector2(50, -100))
physics.apply_impulse(pygame.Vector2(0, -200))
```

#### Advanced Physics Bodies (Pymunk-based)

**RigidBodyComponent** - Dynamic physics objects:
```python
from engine import RigidBodyComponent

rigid_body = RigidBodyComponent(
    mass=1.0,
    shape_type="box",      # "box" or "circle"
    size=(32, 32),         # (width, height) for box, (radius,) for circle
    friction=0.7,
    elasticity=0.3
)

# Apply physics forces
rigid_body.apply_force((100, 0))
rigid_body.apply_impulse((0, -500))
rigid_body.set_velocity((50, 0))
```

**StaticBodyComponent** - Immovable objects:
```python
from engine import StaticBodyComponent

platform = StaticBodyComponent(
    shape_type="box",
    size=(200, 20),
    friction=0.8
)
```

**KinematicBodyComponent** - Controlled movement:
```python
from engine import KinematicBodyComponent

moving_platform = KinematicBodyComponent(
    shape_type="box",
    size=(64, 16)
)
moving_platform.set_velocity((50, 0))
```

### InputComponent

Handles input events with key bindings:

```python
from engine import InputComponent
import pygame

input_comp = InputComponent()

# Bind individual keys
def jump():
    print("Jump!")

input_comp.bind_key(pygame.K_SPACE, jump)
input_comp.bind_key(pygame.K_w, jump)

# Bind mouse buttons
input_comp.bind_mouse(1, lambda: print("Left click"))   # Left mouse
input_comp.bind_mouse(3, lambda: print("Right click"))  # Right mouse

# Custom update function for continuous input
def handle_continuous_input(dt):
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        # Move left
        pass
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        # Move right
        pass

input_comp.update = handle_continuous_input
```

### AudioComponent

Manages sound effects and music:

```python
from engine import AudioComponent

audio = AudioComponent()

# Load sounds
audio.load_sound("jump", "assets/sounds/jump.wav")
audio.load_sound("coin", "assets/sounds/coin.wav")

# Play sounds
audio.play_sound("jump", volume=0.8)
audio.play_sound("coin", volume=0.5, loops=0)

# Background music
audio.play_music("assets/sounds/background.ogg", volume=0.6, loops=-1)
audio.pause_music()
audio.unpause_music()
audio.stop_music()

# Volume control
audio.set_master_volume(0.7)
```

### HealthComponent

Manages hit points and damage:

```python
from engine import HealthComponent

health = HealthComponent(max_health=100.0)

# Set up event callbacks
health.on_damage = lambda damage: print(f"Took {damage} damage!")
health.on_heal = lambda amount: print(f"Healed {amount} points!")
health.on_death = lambda: print("Game Over!")

# Health operations
health.take_damage(25.0)
health.heal(10.0)
health.set_health(50.0)

# Check status
if health.is_alive():
    current = health.current_health
    maximum = health.max_health
    percentage = health.get_health_percentage()
```

### NetworkComponent

Synchronizes actors across network connections:

```python
from engine import NetworkComponent, NetworkOwnership

# Create networked actor
network_comp = NetworkComponent(
    owner_id="player1",
    ownership=NetworkOwnership.CLIENT,
    sync_transform=True
)

actor.add_component(network_comp)

# The component automatically handles:
# - Transform synchronization
# - Component state synchronization  
# - Network spawning/destroying
```

## Creating Custom Components

### Basic Custom Component

```python
from engine import Component
import pygame

class RotatorComponent(Component):
    """Rotates the actor continuously"""
    
    def __init__(self, rotation_speed=90):
        super().__init__()
        self.rotation_speed = rotation_speed  # degrees per second
        
    def update(self, dt):
        current_rotation = self.actor.transform.local_rotation
        new_rotation = current_rotation + self.rotation_speed * dt
        self.actor.transform.local_rotation = new_rotation

# Usage
rotator = RotatorComponent(rotation_speed=180)  # 180 degrees/second
actor.add_component(rotator)
```

### Component with Events

```python
class TriggerComponent(Component):
    """Triggers events when actors enter/exit an area"""
    
    def __init__(self, trigger_area):
        super().__init__()
        self.trigger_area = trigger_area  # pygame.Rect
        self.actors_inside = set()
        self.on_enter = None
        self.on_exit = None
        
    def update(self, dt):
        # Find actors in trigger area
        current_actors = set()
        
        for actor in self.actor.scene.actors:
            if actor != self.actor:  # Don't trigger on self
                pos = actor.transform.world_position
                if self.trigger_area.collidepoint(pos):
                    current_actors.add(actor)
                    
        # Check for new entries
        new_actors = current_actors - self.actors_inside
        for actor in new_actors:
            if self.on_enter:
                self.on_enter(actor)
                
        # Check for exits
        exited_actors = self.actors_inside - current_actors
        for actor in exited_actors:
            if self.on_exit:
                self.on_exit(actor)
                
        self.actors_inside = current_actors

# Usage
trigger = TriggerComponent(pygame.Rect(100, 100, 50, 50))
trigger.on_enter = lambda actor: print(f"{actor.name} entered trigger")
trigger.on_exit = lambda actor: print(f"{actor.name} exited trigger")
```

### Data-Driven Component

```python
class StatsComponent(Component):
    """Generic stats system driven by data"""
    
    def __init__(self, stats_data=None):
        super().__init__()
        self.stats = stats_data or {}
        self.base_stats = self.stats.copy()
        self.modifiers = {}
        
    def get_stat(self, stat_name):
        """Get final stat value including modifiers"""
        base = self.base_stats.get(stat_name, 0)
        modifier = self.modifiers.get(stat_name, 0)
        return base + modifier
        
    def add_modifier(self, stat_name, value, modifier_id):
        """Add temporary stat modifier"""
        if stat_name not in self.modifiers:
            self.modifiers[stat_name] = {}
        self.modifiers[stat_name][modifier_id] = value
        
    def remove_modifier(self, stat_name, modifier_id):
        """Remove stat modifier"""
        if stat_name in self.modifiers:
            self.modifiers[stat_name].pop(modifier_id, None)

# Usage with data files
stats_data = {
    "strength": 10,
    "agility": 15,
    "intelligence": 8
}
stats = StatsComponent(stats_data)
actor.add_component(stats)

# Use stats
strength = stats.get_stat("strength")
stats.add_modifier("strength", 5, "potion_boost")
```

## Best Practices

### Component Design

1. **Single Responsibility** - Each component should do one thing well
2. **Data-Driven** - Use configuration files when possible
3. **Event-Based Communication** - Use callbacks for loose coupling
4. **Resource Cleanup** - Always clean up in `destroy()`

### Performance Considerations

1. **Component Pooling** - Reuse components for frequently created objects
2. **Efficient Updates** - Only update when necessary
3. **Batch Operations** - Group similar operations together
4. **Memory Management** - Clean up references to prevent memory leaks

### Organization Patterns

```python
# Group related components
def create_player(scene, position):
    player = scene.create_actor("Player", position)
    
    # Visual
    player.add_component(SpriteComponent("player.png"))
    player.add_component(AnimationComponent("player_anims.yaml"))
    
    # Physics
    player.add_component(RigidBodyComponent(mass=1.0, shape_type="box"))
    
    # Gameplay
    player.add_component(HealthComponent(100))
    player.add_component(InputComponent())
    player.add_component(PlayerController())
    
    # Tags
    player.add_tag("player")
    player.add_tag("controllable")
    
    return player
```
