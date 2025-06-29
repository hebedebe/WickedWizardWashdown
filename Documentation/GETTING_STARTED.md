# Getting Started

This guide will help you set up and create your first game with the Wicked Wizard Washdown engine.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Install Dependencies

1. **Clone or download the project**
2. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

The engine requires:
- `pygame-ce` >= 2.5.5 - Main game framework
- `pymunk` >= 6.7.0 - Physics simulation
- `numpy` >= 1.24.0 - Mathematical operations
- `PyYAML` >= 6.0 - YAML file parsing
- `Pillow` >= 10.0.0 - Image processing

### Verify Installation

Test that everything is working:
```bash
python dev.py check
```

Or run the main game:
```bash
python main.py
```

## Your First Game

Let's create a simple game to understand the basic concepts:

### 1. Basic Game Setup

```python
# my_game.py
from engine import Game, Scene, Actor, SpriteComponent
import pygame

class MyScene(Scene):
    def __init__(self):
        super().__init__("MyScene")
        
    def on_enter(self):
        """Called when the scene becomes active."""
        super().on_enter()
        
        # Create a player actor
        player = self.create_actor("Player", pygame.Vector2(400, 300))
        
        # Add a sprite component to make it visible
        sprite = SpriteComponent(
            color=pygame.Color(0, 255, 0),  # Green color
            size=pygame.Vector2(32, 32)     # 32x32 pixels
        )
        player.add_component(sprite)
        
        print("Game scene loaded!")

def main():
    # Create the game
    game = Game(800, 600, "My First Game")
    
    # Add our scene
    game.add_scene("main", MyScene())
    
    # Start with our scene
    game.load_scene("main")
    
    # Run the game
    game.run()

if __name__ == "__main__":
    main()
```

### 2. Adding Movement

Let's make the player controllable:

```python
from engine import InputComponent

class MyScene(Scene):
    def on_enter(self):
        super().on_enter()
        
        # Create player
        self.player = self.create_actor("Player", pygame.Vector2(400, 300))
        
        # Add sprite
        sprite = SpriteComponent(
            color=pygame.Color(0, 255, 0),
            size=pygame.Vector2(32, 32)
        )
        self.player.add_component(sprite)
        
        # Add input handling
        input_comp = InputComponent()
        input_comp.update = self.handle_player_input
        self.player.add_component(input_comp)
        
    def handle_player_input(self, dt):
        """Handle player movement."""
        keys = pygame.key.get_pressed()
        speed = 200  # pixels per second
        
        movement = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            movement.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            movement.x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            movement.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            movement.y += 1
            
        # Apply movement
        if movement.length() > 0:
            movement = movement.normalize()
            new_pos = self.player.transform.local_position + movement * speed * dt
            self.player.transform.local_position = new_pos
```

### 3. Adding Physics

For more realistic movement, add physics:

```python
from engine import RigidBodyComponent

class MyScene(Scene):
    def on_enter(self):
        super().on_enter()
        
        # Create player
        self.player = self.create_actor("Player", pygame.Vector2(400, 300))
        
        # Add sprite
        sprite = SpriteComponent(
            color=pygame.Color(0, 255, 0),
            size=pygame.Vector2(32, 32)
        )
        self.player.add_component(sprite)
        
        # Add physics body
        physics = RigidBodyComponent(
            mass=1.0,
            shape_type="box",
            size=(32, 32),
            friction=0.7
        )
        self.player.add_component(physics)
        
        # Add input handling
        input_comp = InputComponent()
        input_comp.update = self.handle_player_input
        self.player.add_component(input_comp)
        
        # Create a platform
        platform = self.create_actor("Platform", pygame.Vector2(400, 500))
        platform.add_component(SpriteComponent(
            color=pygame.Color(139, 69, 19),  # Brown
            size=pygame.Vector2(200, 20)
        ))
        platform.add_component(StaticBodyComponent(
            shape_type="box",
            size=(200, 20)
        ))
        
    def handle_player_input(self, dt):
        """Handle player movement with physics."""
        keys = pygame.key.get_pressed()
        physics = self.player.get_component(RigidBodyComponent)
        
        if not physics:
            return
            
        force_strength = 500
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            physics.apply_force((-force_strength, 0))
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            physics.apply_force((force_strength, 0))
        if keys[pygame.K_SPACE]:
            # Jump (only if on ground - simplified)
            physics.apply_impulse((0, -300))
```

## Key Concepts

### Actors and Components

- **Actors** are game objects (player, enemies, platforms)
- **Components** add functionality to actors (sprite, physics, input)
- Use `actor.add_component()` to attach behaviors
- Use `actor.get_component()` to access components

### Scenes

- **Scenes** contain and manage actors
- Use `self.create_actor()` to add actors to scenes
- Override `on_enter()` for scene setup
- Override `update()` for custom scene logic

### Game Loop

The engine automatically handles:
- Input processing
- Physics simulation
- Component updates
- Rendering

## Next Steps

1. **Explore Examples**: Check the `examples/` directory for more complex examples
2. **Read Core Concepts**: Understand the engine architecture better
3. **Add Assets**: Learn to load images, sounds, and fonts
4. **Create Multiple Scenes**: Build menus and game states
5. **Add Networking**: Create multiplayer games

## Common Patterns

### Creating a Game Object

```python
def create_enemy(self, position):
    enemy = self.create_actor("Enemy", position)
    
    # Visual representation
    enemy.add_component(SpriteComponent(
        color=pygame.Color(255, 0, 0),
        size=pygame.Vector2(24, 24)
    ))
    
    # Health system
    enemy.add_component(HealthComponent(max_health=50))
    
    # Physics
    enemy.add_component(RigidBodyComponent(
        mass=0.8,
        shape_type="circle",
        size=(12,)  # radius
    ))
    
    return enemy
```

### Scene Transitions

```python
def check_win_condition(self):
    if self.player_reached_goal():
        self.game.load_scene("victory_screen")
        
def handle_game_over(self):
    self.game.push_scene("game_over_menu")  # Overlay menu
```

## Troubleshooting

**Game window doesn't appear:**
- Check that pygame-ce is installed correctly
- Verify Python version (3.8+)

**Import errors:**
- Run `python dev.py check` to verify dependencies
- Make sure you're in the project directory

**Performance issues:**
- Use StaticBodyComponent for non-moving objects
- Limit particle effects
- Profile with the built-in FPS display
