# Wicked Wizard Washdown - API Reference

## Core Classes

### Game
The main game class that manages the game loop and core systems.

```python
from engine import Game

game = Game(width=800, height=600, title="My Game")
game.add_scene("main", my_scene)
game.load_scene("main")
game.run()
```

**Key Methods:**
- `add_scene(name, scene)` - Add a scene to the game
- `load_scene(name)` - Switch to a scene
- `push_scene(name)` - Push scene onto stack
- `pop_scene()` - Return to previous scene
- `run()` - Start the game loop
- `quit()` - Request game to quit

### Actor
Game entities that can have children and components.

```python
from engine import Actor

actor = Actor("MyActor")
actor.transform.local_position = pygame.Vector2(100, 100)
actor.add_component(SpriteComponent())
```

**Key Methods:**
- `add_child(actor)` - Add child actor
- `add_component(component)` - Add component
- `get_component(ComponentType)` - Get component by type
- `has_component(ComponentType)` - Check for component
- `add_tag(tag)` - Add identification tag
- `find_child(name)` - Find child by name

### Transform
Handles position, rotation, and scale with hierarchy support.

```python
transform = actor.transform
transform.local_position = pygame.Vector2(x, y)
transform.local_rotation = angle_in_degrees
transform.local_scale = pygame.Vector2(scale_x, scale_y)
```

**Properties:**
- `local_position` - Position relative to parent
- `local_rotation` - Rotation in degrees
- `local_scale` - Scale factors
- `world_position` - Calculated world position
- `world_rotation` - Calculated world rotation
- `world_scale` - Calculated world scale

## Components

### SpriteComponent
Renders sprites with transformation support.

```python
from engine import SpriteComponent

sprite = SpriteComponent(
    surface=my_surface,
    color=pygame.Color(255, 0, 0),
    size=pygame.Vector2(32, 32)
)
sprite.flip_x = True
sprite.alpha = 128
```

### PhysicsComponent
Simple physics simulation with collision detection.

```python
from engine import PhysicsComponent

physics = PhysicsComponent()
physics.velocity = pygame.Vector2(100, 0)
physics.gravity = pygame.Vector2(0, 300)
physics.apply_force(pygame.Vector2(50, -100))
```

### InputComponent
Handles input events and key bindings.

```python
from engine import InputComponent

input_comp = InputComponent()
input_comp.bind_key(pygame.K_SPACE, my_jump_function)
input_comp.bind_mouse(1, my_click_function)  # Left click
```

### AudioComponent
Manages sound effects and background music.

```python
from engine import AudioComponent

audio = AudioComponent()
audio.load_sound("jump", "assets/sounds/jump.wav")
audio.play_sound("jump", volume=0.8)
audio.play_music("assets/sounds/background.ogg")
```

### HealthComponent
Manages hit points and damage system.

```python
from engine import HealthComponent

health = HealthComponent(max_health=100.0)
health.on_death = lambda: print("Game Over!")
health.take_damage(25.0)
health.heal(10.0)
```

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

## Networking

### NetworkManager
Handles client-server networking.

```python
from engine import NetworkManager

network = NetworkManager()

# Server mode
network.start_server(port=12345)

# Client mode  
network.connect_to_server("localhost", 12345, "player1")

# Send game state
network.send_game_state({"player_pos": [x, y]})
```

**Key Methods:**
- `start_server(port)` - Start as server
- `connect_to_server(host, port, client_id)` - Connect as client
- `send_game_state(data)` - Send state update
- `is_connected()` - Check connection status

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
