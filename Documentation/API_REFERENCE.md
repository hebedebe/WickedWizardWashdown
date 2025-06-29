# Wicked Wizard Washdown - API Reference

## Overview

This is the complete API reference for the Wicked Wizard Washdown 2D game engine. The engine follows an Entity-Component-System (ECS) architecture built on pygame-ce with physics and animation capabilities.

## Quick Start

```python
from engine import Game, Scene, Actor, SpriteComponent
import pygame

class MyScene(Scene):
    def on_enter(self):
        super().on_enter()
        # Create a simple actor with sprite
        player = self.create_actor("Player", pygame.Vector2(400, 300))
        player.add_component(SpriteComponent(
            color=pygame.Color(0, 255, 0),
            size=pygame.Vector2(32, 32)
        ))

# Create and run the game
game = Game(800, 600, "My Game")
game.add_scene("main", MyScene())
game.load_scene("main")
game.run()
```

## Core Classes

### Game
The main game class that manages the game loop and core systems. Implemented as a singleton to ensure only one game instance exists and provide global access.

```python
from engine import Game

# Create the game instance (singleton)
game = Game(width=800, height=600, title="My Game")

# Get the game instance from anywhere in your code
game = Game.get_instance()

# Check if game instance exists
if Game.has_instance():
    game = Game.get_instance()

game.add_scene("main", my_scene)
game.load_scene("main")
game.run()
```

**Constructor Parameters:**
- `width` (int): Screen width in pixels (default: 800)
- `height` (int): Screen height in pixels (default: 600)
- `title` (str): Window title (default: "Wicked Wizard Game")

**Core Properties:**
- `screen` - The main pygame display surface
- `clock` - pygame Clock for timing
- `running` - Boolean indicating if game is running
- `current_scene` - Currently active scene
- `input_manager` - Global input manager
- `asset_manager` - Asset loading and caching
- `asset_manager` - Asset loading and management
- `physics_system` - Physics simulation system

**Key Methods:**
- `Game.get_instance()` - Get the singleton game instance
- `Game.has_instance()` - Check if game instance exists
- `add_scene(name, scene)` - Add a scene to the game
- `load_scene(name)` - Switch to a scene immediately
- `push_scene(name)` - Push scene onto stack (keeps current scene)
- `pop_scene()` - Return to previous scene
- `run()` - Start the main game loop
- `quit()` - Request game to quit gracefully

**Scene Stack Management:**
The game supports a scene stack for overlay scenes like menus:
```python
# Push a settings menu over current scene
game.push_scene("settings")

# Return to previous scene
game.pop_scene()
```

**Singleton Access:**
Since Game is a singleton, you can access it from anywhere:
```python
# From within a component
class MyComponent(Component):
    def update(self, dt):
        game = self.game  # Easy access to game instance
        game.load_scene("menu")

# From within an actor
class MyActor(Actor):
    def update(self, dt):
        game = self.game  # Easy access to game instance
        if some_condition:
            game.quit()

# From anywhere else
game = Game.get_instance()
```

### Actor
Game entities that can have children and components. Actors are the fundamental building blocks of your game world.

```python
from engine import Actor, SpriteComponent
import pygame

# Create an actor
actor = Actor("MyActor")

# Set position and transformation
actor.transform.local_position = pygame.Vector2(100, 100)
actor.transform.local_rotation = 45  # degrees
actor.transform.local_scale = pygame.Vector2(2.0, 2.0)

# Add components
sprite = SpriteComponent(color=pygame.Color(255, 0, 0))
actor.add_component(sprite)

# Hierarchy - add child actors
child = Actor("Child")
actor.add_child(child)

# Tags for identification
actor.add_tag("player")
actor.add_tag("controllable")
```

**Constructor Parameters:**
- `name` (str, optional): Actor name for identification

**Core Properties:**
- `id` - Unique identifier (UUID)
- `name` - Human-readable name
- `transform` - Transform component for position/rotation/scale
- `parent` - Parent actor (None if root)
- `children` - List of child actors
- `active` - Whether actor is active and updating
- `enabled` - Whether actor is enabled
- `tags` - List of string tags for identification

**Hierarchy Methods:**
- `add_child(actor)` - Add child actor
- `remove_child(actor)` - Remove child actor
- `find_child(name)` - Find direct child by name
- `find_children_with_tag(tag)` - Find children with specific tag

**Component Methods:**
- `add_component(component)` - Add component to actor
- `get_component(ComponentType)` - Get component by type
- `has_component(ComponentType)` - Check if actor has component type
- `remove_component(ComponentType)` - Remove component by type

**Tag Methods:**
- `add_tag(tag)` - Add identification tag
- `remove_tag(tag)` - Remove tag
- `has_tag(tag)` - Check if actor has tag

**Lifecycle Methods:**
- `update(dt)` - Called every frame
- `fixed_update(dt)` - Called on fixed timestep for physics
- `render(screen)` - Called during rendering
- `handle_event(event)` - Called for input events
- `destroy()` - Clean up actor and components

### Transform
Handles position, rotation, and scale with full hierarchy support. All transformations are calculated relative to parent transforms.

```python
transform = actor.transform

# Local transformation (relative to parent)
transform.local_position = pygame.Vector2(x, y)
transform.local_rotation = angle_in_degrees
transform.local_scale = pygame.Vector2(scale_x, scale_y)

# World transformation (calculated automatically)
world_pos = transform.world_position
world_rot = transform.world_rotation
world_scale = transform.world_scale

# Matrix operations
matrix = transform.get_transformation_matrix()
```

**Properties:**
- `local_position` - Position relative to parent (pygame.Vector2)
- `local_rotation` - Rotation in degrees (float)
- `local_scale` - Scale factors (pygame.Vector2)
- `world_position` - Calculated world position (read-only)
- `world_rotation` - Calculated world rotation (read-only)
- `world_scale` - Calculated world scale (read-only)

**Methods:**
- `get_transformation_matrix()` - Get 3x3 transformation matrix
- `mark_dirty()` - Force recalculation of world transform
- `set_parent(parent_transform)` - Set parent transform

## Components

Components provide specific functionality to actors. All components inherit from the base `Component` class.

### SpriteComponent
Renders sprites with transformation support and visual effects.

```python
from engine import SpriteComponent
import pygame

# Create with surface
sprite = SpriteComponent(surface=my_surface)

# Create with color and size
sprite = SpriteComponent(
    color=pygame.Color(255, 0, 0),
    size=pygame.Vector2(32, 32)
)

# Modify appearance
sprite.flip_x = True
sprite.flip_y = False
sprite.alpha = 128  # Semi-transparent
sprite.offset = pygame.Vector2(0, -16)  # Offset from actor position
```

**Constructor Parameters:**
- `surface` (pygame.Surface, optional): Image to display
- `color` (pygame.Color, optional): Color for generated surface
- `size` (pygame.Vector2, optional): Size for generated surface

**Properties:**
- `surface` - The pygame Surface to render
- `rect` - pygame.Rect for positioning
- `color` - Current color
- `size` - Current size
- `offset` - Offset from actor position
- `flip_x` - Horizontal flip flag
- `flip_y` - Vertical flip flag  
- `alpha` - Transparency (0-255)

**Methods:**
- `set_surface(surface)` - Set new surface
- `set_color(color)` - Change color (creates new colored surface)

### PhysicsComponent
**Note:** This is the simple physics component. For advanced physics, use the Physics Body Components.

Simple physics simulation with basic collision detection.

```python
from engine import PhysicsComponent
import pygame

physics = PhysicsComponent()
physics.velocity = pygame.Vector2(100, 0)
physics.gravity = pygame.Vector2(0, 300)
physics.mass = 1.0
physics.drag = 0.98

# Apply forces
physics.apply_force(pygame.Vector2(50, -100))
physics.apply_impulse(pygame.Vector2(0, -200))
```

**Properties:**
- `velocity` - Current velocity (pygame.Vector2)
- `acceleration` - Current acceleration (pygame.Vector2)
- `gravity` - Gravity force applied each frame (pygame.Vector2)
- `mass` - Object mass for force calculations (float)
- `drag` - Velocity damping factor 0-1 (float)
- `bounce` - Bounce factor for collisions (float)
- `friction` - Friction coefficient (float)

**Methods:**
- `apply_force(force)` - Apply force over time
- `apply_impulse(impulse)` - Apply instant velocity change

### Physics Body Components
Advanced physics using the pymunk physics engine. Choose the appropriate body type:

#### RigidBodyComponent
Dynamic physics bodies affected by forces and collisions.

```python
from engine import RigidBodyComponent
import pygame

# Create dynamic body
rigid_body = RigidBodyComponent(
    mass=1.0,
    shape_type="box",  # "box" or "circle"
    size=(32, 32),     # For box: (width, height), for circle: (radius,)
    friction=0.7,
    elasticity=0.3
)

# Apply forces
rigid_body.apply_force((100, 0))
rigid_body.apply_impulse((0, -500))
rigid_body.set_velocity((50, 0))
```

#### StaticBodyComponent
Immovable objects like platforms and walls.

```python
from engine import StaticBodyComponent

# Create static platform
platform = StaticBodyComponent(
    shape_type="box",
    size=(200, 20),
    friction=0.8
)
```

#### KinematicBodyComponent
Objects that move but aren't affected by forces (moving platforms, etc.).

```python
from engine import KinematicBodyComponent

# Create kinematic body
kinematic = KinematicBodyComponent(
    shape_type="box",
    size=(64, 16)
)
kinematic.set_velocity((50, 0))  # Constant movement
```

### InputComponent
Handles input events and key bindings with flexible callback system.

```python
from engine import InputComponent
import pygame

input_comp = InputComponent()

# Bind keys to functions
def jump():
    print("Jump!")

def move_left():
    print("Moving left")

input_comp.bind_key(pygame.K_SPACE, jump)
input_comp.bind_key(pygame.K_a, move_left)

# Bind mouse buttons
input_comp.bind_mouse(1, lambda: print("Left click"))  # Left click
input_comp.bind_mouse(3, lambda: print("Right click")) # Right click

# Custom update function for continuous input
def custom_input_handler(dt):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        # Handle continuous left movement
        pass

input_comp.update = custom_input_handler
```

**Methods:**
- `bind_key(key, callback)` - Bind keyboard key to function
- `bind_mouse(button, callback)` - Bind mouse button to function
- `unbind_key(key)` - Remove key binding
- `unbind_mouse(button)` - Remove mouse binding

### AudioComponent
Manages sound effects and background music with volume control.

```python
from engine import AudioComponent

audio = AudioComponent()

# Load and play sounds
audio.load_sound("jump", "assets/sounds/jump.wav")
audio.load_sound("coin", "assets/sounds/coin.wav")

# Play sounds with volume control
audio.play_sound("jump", volume=0.8)
audio.play_sound("coin", volume=0.5, loops=0)

# Background music
audio.play_music("assets/sounds/background.ogg", volume=0.6, loops=-1)
audio.stop_music()
audio.pause_music()
audio.unpause_music()

# Master volume control
audio.set_master_volume(0.7)
```

**Methods:**
- `load_sound(name, path)` - Load sound file
- `play_sound(name, volume=1.0, loops=0)` - Play loaded sound
- `stop_sound(name)` - Stop specific sound
- `play_music(path, volume=1.0, loops=-1)` - Play background music
- `stop_music()` - Stop background music
- `pause_music()` - Pause background music
- `unpause_music()` - Resume background music
- `set_master_volume(volume)` - Set master volume (0.0-1.0)

### HealthComponent
Manages hit points, damage, and health-related game mechanics.

```python
from engine import HealthComponent

health = HealthComponent(max_health=100.0)

# Set up callbacks
health.on_damage = lambda damage: print(f"Took {damage} damage!")
health.on_heal = lambda amount: print(f"Healed {amount} points!")
health.on_death = lambda: print("Game Over!")

# Health operations
health.take_damage(25.0)
health.heal(10.0)
health.set_health(50.0)

# Check status
if health.is_alive():
    print(f"Health: {health.current_health}/{health.max_health}")
    print(f"Health percentage: {health.get_health_percentage():.1%}")
```

**Constructor Parameters:**
- `max_health` (float): Maximum health points

**Properties:**
- `max_health` - Maximum health points
- `current_health` - Current health points
- `on_damage` - Callback when damage is taken
- `on_heal` - Callback when healing occurs
- `on_death` - Callback when health reaches 0

**Methods:**
- `take_damage(amount)` - Reduce health
- `heal(amount)` - Increase health (up to max)
- `set_health(amount)` - Set health directly
- `is_alive()` - Check if health > 0
- `get_health_percentage()` - Get health as 0.0-1.0

### Animation Components

#### FileAnimationComponent (Recommended)
File-based animation system supporting YAML/JSON animation definitions.

```python
from engine import FileAnimationComponent

# Load from animation file
animation = FileAnimationComponent("assets/data/player_animations.yaml")
actor.add_component(animation)

# Control playback
animation.play_animation("walk")
animation.stop()
animation.pause()
animation.resume()

# Animation events
def on_animation_complete():
    print("Animation finished!")

animation.on_animation_complete = on_animation_complete
```

**Note:** `AnimationComponent` is an alias for `FileAnimationComponent` for backward compatibility.

## Scene System

### Scene
Container for actors and game logic.

```python
from engine import Scene

class MyScene(Scene):
    def __init__(self):
        super().__init__("MyScene")
        
    def on_enter(self):
        # Setup scene
        player = self.create_actor("Player")
        
    def update(self, dt):
        super().update(dt)
        # Custom update logic
```

**Key Methods:**
- `create_actor(name, position)` - Create and add actor
- `find_actor(name)` - Find actor by name
- `find_actors_with_tag(tag)` - Find actors with tag
- `destroy_actor(actor)` - Remove and destroy actor

## Asset Management

### AssetManager
Loads and caches game assets.

```python
from engine import AssetManager

assets = AssetManager()
image = assets.load_image("player.png")
sound = assets.load_sound("jump.wav")
font = assets.load_font("arial", 24)
data = assets.load_data("config.json")
```

**Key Methods:**
- `load_image(name, convert_alpha=True)` - Load image
- `load_sound(name)` - Load sound effect
- `load_font(name, size)` - Load font
- `load_data(name)` - Load JSON data
- `create_surface(width, height, color)` - Create surface
- `slice_spritesheet(image, tile_w, tile_h)` - Slice spritesheet

## Particle System

### ParticleSystem
Component for managing particle emitters.

```python
from engine import ParticleSystem
from engine.particles import create_explosion_emitter

particles = ParticleSystem()
explosion = create_explosion_emitter(position, color)
particles.add_emitter(explosion)
actor.add_component(particles)
```

### ParticleEmitter
Emits and manages individual particles.

```python
from engine.particles import ParticleEmitter

emitter = ParticleEmitter(position)
emitter.emission_rate = 30  # particles per second
emitter.lifetime_range = (1.0, 3.0)
emitter.speed_range = (50, 150)
emitter.size_range = (2, 8)
```

**Properties:**
- `emission_rate` - Particles per second
- `max_particles` - Maximum particle count
- `lifetime_range` - Particle lifespan range
- `speed_range` - Initial speed range
- `size_range` - Particle size range
- `gravity` - Gravity vector
- `emission_shape` - 'point', 'circle', 'rectangle', 'line'

## UI System

### UIManager
Manages UI widgets and events.

```python
from engine.ui import UIManager, Button, Label

ui = UIManager(screen_size)
button = Button(pygame.Rect(10, 10, 100, 30), "Click Me")
button.add_event_handler("clicked", my_callback)
ui.add_widget(button)
```

### Widget Types

**Button:**
```python
button = Button(rect, text)
button.add_event_handler("clicked", callback)
```

**Label:**
```python
label = Label(rect, text, font, text_color)
label.align_x = 'center'  # 'left', 'center', 'right'
```

**Slider:**
```python
slider = Slider(rect, min_val, max_val, initial_val)
slider.add_event_handler("value_changed", callback)
```

**Panel:**
```python
panel = Panel(rect, background_color, border_color, border_width)
panel.add_child(other_widget)
```

**FPSDisplay:**
```python
fps_display = FPSDisplay(rect, update_interval=0.25)
fps_display.text_color = pygame.Color(255, 255, 0)  # Yellow
current_fps = fps_display.get_fps()
```

## Input Management

### InputManager
Centralized input handling with action mapping.

```python
from engine import InputManager

input_mgr = InputManager()
input_mgr.bind_key("jump", pygame.K_SPACE)
input_mgr.bind_mouse("shoot", 1)  # Left mouse

# In update loop:
if input_mgr.is_action_pressed("jump"):
    player.jump()
    
movement = input_mgr.get_movement_vector()
```

**Key Methods:**
- `bind_key(action, key)` - Bind key to action
- `bind_mouse(action, button)` - Bind mouse button
- `is_action_down(action)` - Check if action is held
- `is_action_pressed(action)` - Check if just pressed
- `get_movement_vector()` - Get WASD/arrow movement

## Event Handling

### Custom Events
Widgets and components use event systems.

```python
def on_button_click(event):
    print(f"Button {event.widget.name} was clicked!")
    
button.add_event_handler("clicked", on_button_click)

# Component events
health.on_death = lambda: game.load_scene("game_over")
health.on_damage_taken = lambda dmg: print(f"Took {dmg} damage!")
```

## Best Practices

### 1. Actor-Component Pattern
```python
# Create actors with specific behaviors
player = scene.create_actor("Player")
player.add_component(SpriteComponent(player_image))
player.add_component(PhysicsComponent())
player.add_component(InputComponent())
player.add_component(HealthComponent(100))
```

### 2. Scene Organization
```python
class GameScene(Scene):
    def on_enter(self):
        self.setup_player()
        self.setup_enemies()
        self.setup_ui()
        
    def setup_player(self):
        # Player setup
        pass
```

### 3. Asset Preloading
```python
assets = [
    {"type": "image", "name": "player.png"},
    {"type": "sound", "name": "jump.wav"},
    {"type": "font", "name": "arial", "size": 24}
]
game.asset_manager.preload_assets(assets)
```

### 4. Component Communication
```python
# Use actor references for component communication
class PlayerController(Component):
    def update(self, dt):
        physics = self.actor.get_component(PhysicsComponent)
        if physics and self.should_jump():
            physics.apply_impulse(pygame.Vector2(0, -300))
```

### 5. Memory Management
```python
# Clean up resources
scene.clear()  # Remove all actors
asset_manager.cleanup()  # Free cached assets
```
