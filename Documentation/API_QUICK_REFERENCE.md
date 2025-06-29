# API Quick Reference

This is a concise API reference for the Wicked Wizard Washdown 2D game engine. For detailed documentation, see the specialized guides.

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

### Game (Singleton)
Main game management class.

```python
# Create/get instance
game = Game(width=800, height=600, title="My Game")
game = Game.get_instance()  # Access from anywhere

# Scene management
game.add_scene("main", my_scene)
game.load_scene("main")
game.push_scene("overlay")  # Stack scenes
game.pop_scene()

# Core properties
game.screen, game.clock, game.running
game.input_manager, game.asset_manager, game.physics_system
```

### Actor
Game entities with components and hierarchy.

```python
# Create and configure
actor = Actor("MyActor")
actor.transform.local_position = pygame.Vector2(100, 100)
actor.transform.local_rotation = 45  # degrees
actor.transform.local_scale = pygame.Vector2(2.0, 2.0)

# Components
actor.add_component(SpriteComponent(color=pygame.Color(255, 0, 0)))
sprite = actor.get_component(SpriteComponent)

# Hierarchy
actor.add_child(child_actor)
child = actor.find_child("ChildName")

# Tags
actor.add_tag("player")
if actor.has_tag("enemy"):
    # Handle enemy logic
```

### Scene
Container for actors and game logic.

```python
class MyScene(Scene):
    def on_enter(self):
        # Setup scene
        self.player = self.create_actor("Player")
        
    def update(self, dt):
        super().update(dt)
        # Custom update logic

# Methods
player = scene.create_actor("Player", position)
enemy = scene.find_actor("Enemy")
enemies = scene.find_actors_with_tag("enemy")
```

## Essential Components

### SpriteComponent
Visual rendering.

```python
# With image
sprite = SpriteComponent(surface=my_image)

# With color
sprite = SpriteComponent(
    color=pygame.Color(255, 0, 0),
    size=pygame.Vector2(32, 32)
)

# Properties
sprite.flip_x = True
sprite.alpha = 128
sprite.offset = pygame.Vector2(0, -16)
```

### Physics Components

**Simple Physics:**
```python
physics = PhysicsComponent()
physics.velocity = pygame.Vector2(100, 0)
physics.apply_force(pygame.Vector2(50, -100))
```

**Advanced Physics (Pymunk):**
```python
# Dynamic body
rigid_body = RigidBodyComponent(
    mass=1.0, shape_type="box", size=(32, 32)
)

# Static body (platforms)
platform = StaticBodyComponent(
    shape_type="box", size=(200, 20)
)

# Kinematic body (moving platforms)
kinematic = KinematicBodyComponent(
    shape_type="box", size=(64, 16)
)
```

### InputComponent
Handle player input.

```python
input_comp = InputComponent()
input_comp.bind_key(pygame.K_SPACE, jump_function)
input_comp.bind_mouse(1, shoot_function)  # Left click
```

### AudioComponent
Sound and music.

```python
audio = AudioComponent()
audio.load_sound("jump", "assets/sounds/jump.wav")
audio.play_sound("jump", volume=0.8)
audio.play_music("assets/sounds/bg.ogg", loops=-1)
```

### HealthComponent
Health management.

```python
health = HealthComponent(max_health=100.0)
health.on_death = lambda: game.load_scene("game_over")
health.take_damage(25.0)
health.heal(10.0)
```

### FileAnimationComponent
File-based animations.

```python
# Load from YAML/JSON
animation = FileAnimationComponent("assets/data/player_animations.yaml")
actor.add_component(animation)

# Control playback
animation.play_animation("walk")
animation.pause()
animation.resume()
```

## Common Patterns

### Player Setup
```python
def create_player(scene, position):
    player = scene.create_actor("Player", position)
    player.add_component(SpriteComponent(surface=player_image))
    player.add_component(RigidBodyComponent(mass=1.0, shape_type="box", size=(32, 48)))
    player.add_component(InputComponent())
    player.add_component(HealthComponent(100))
    player.add_component(FileAnimationComponent("assets/data/player_animations.yaml"))
    player.add_tag("player")
    return player
```

### Input Handling
```python
class PlayerController(Component):
    def update(self, dt):
        keys = pygame.key.get_pressed()
        physics = self.actor.get_component(RigidBodyComponent)
        
        if keys[pygame.K_LEFT]:
            physics.apply_force((-500, 0))
        if keys[pygame.K_RIGHT]:
            physics.apply_force((500, 0))
        if keys[pygame.K_SPACE]:
            physics.apply_impulse((0, -300))
```

### Scene Transitions
```python
# In any component or scene
game = Game.get_instance()

# Immediate transition
game.load_scene("main_menu")

# Overlay (pause menu, etc.)
game.push_scene("pause_menu")
game.pop_scene()  # Return to previous scene
```

## Detailed Documentation

For comprehensive information, see the specialized documentation:

- **[Game and Scenes](GAME_AND_SCENES.md)** - Scene management and game loop
- **[Actors and Components](ACTORS_AND_COMPONENTS.md)** - Entity-component system
- **[Physics System](PHYSICS_SYSTEM.md)** - Physics simulation and collision
- **[Animation System](ANIMATION_SYSTEM.md)** - Sprite animations and tweening
- **[Best Practices](BEST_PRACTICES.md)** - Code organization and patterns

## Asset Management

```python
# Load assets
assets = Game.get_instance().asset_manager
image = assets.load_image("player.png")
sound = assets.load_sound("jump.wav")
font = assets.load_font("arial", 24)
data = assets.load_data("config.json")

# Create surfaces
surface = assets.create_surface(64, 64, pygame.Color(255, 0, 0))
frames = assets.slice_spritesheet(spritesheet, 32, 32)
```

## UI System

```python
from engine.ui import UIManager, Button, Label

ui = UIManager(screen_size)

# Create widgets
button = Button(pygame.Rect(10, 10, 100, 30), "Click Me")
button.add_event_handler("clicked", my_callback)

label = Label(pygame.Rect(10, 50, 200, 30), "Score: 0")
label.align_x = 'center'

ui.add_widget(button)
ui.add_widget(label)
```
