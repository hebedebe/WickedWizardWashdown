# Game and Scene Management

The Game class and Scene system form the backbone of the engine, managing the game loop, scenes, and core systems.

## Game Class

The Game class is implemented as a singleton and manages the main game loop and all core systems.

### Creating and Accessing the Game

```python
from engine import Game

# Create the game instance (only one can exist)
game = Game(800, 600, "My Game")

# Access from anywhere in your code
game = Game.get_instance()

# Check if instance exists
if Game.has_instance():
    game = Game.get_instance()
```

### Constructor Parameters

```python
Game(width=800, height=600, title="Wicked Wizard Game")
```

- `width` (int): Screen width in pixels
- `height` (int): Screen height in pixels  
- `title` (str): Window title

### Core Properties

```python
game = Game.get_instance()

# Display and timing
screen = game.screen              # pygame.Surface - main display
clock = game.clock               # pygame.Clock - timing
running = game.running           # bool - game state
delta_time = game.delta_time     # float - frame time in seconds

# Current scene
current_scene = game.current_scene  # Scene or None

# Core systems
input_manager = game.input_manager     # InputManager
asset_manager = game.asset_manager     # AssetManager  
network_manager = game.network_manager # NetworkManager
physics_system = game.physics_system   # PhysicsSystem

# Scene management
scenes = game.scenes                   # Dict[str, Scene]
scene_stack = game.scene_stack         # List[Scene]
```

### Scene Management Methods

#### Basic Scene Operations

```python
# Add a scene to the game
game.add_scene("main_menu", MainMenuScene())
game.add_scene("game", GameScene())
game.add_scene("settings", SettingsScene())

# Switch to a scene (replaces current scene)
game.load_scene("main_menu")

# Check if scene exists
if "game" in game.scenes:
    game.load_scene("game")
```

#### Scene Stack Operations

The scene stack allows you to overlay scenes (like pause menus) while keeping the previous scene in memory:

```python
# Push a scene onto the stack (overlays current scene)
game.push_scene("pause_menu")    # Current scene is paused
game.push_scene("settings")      # Can stack multiple scenes

# Return to previous scene
game.pop_scene()                 # Back to pause_menu
game.pop_scene()                 # Back to original scene
```

### Game Loop Control

```python
# Start the main game loop
game.run()

# Request the game to quit gracefully
game.quit()

# Timing properties
game.target_fps = 60              # Target frame rate
game.fixed_timestep = 1.0/60.0    # Fixed timestep for physics
```

### Event Handling

```python
# Add global event handlers
def on_quit_request(event):
    game.quit()

game.add_event_handler(pygame.QUIT, on_quit_request)

# Remove event handlers
game.remove_event_handler(pygame.QUIT, on_quit_request)

# Emit custom events
game.emit_event(pygame.USEREVENT, custom_data="example")
```

### Accessing Game from Anywhere

Since Game is a singleton, you can access it from any component or actor:

```python
class MyComponent(Component):
    def update(self, dt):
        game = self.game  # Automatic access through actor hierarchy
        # or
        game = Game.get_instance()  # Direct singleton access
        
        if some_condition:
            game.load_scene("game_over")

class MyActor(Actor):
    def update(self, dt):
        game = self.game  # Available in actors too
        if self.should_quit:
            game.quit()
```

## Scene System

Scenes are containers that manage collections of actors and provide organizational structure for your game.

### Creating Scenes

```python
from engine import Scene

class MyScene(Scene):
    def __init__(self):
        super().__init__("MySceneName")
        # Initialize scene-specific data
        self.score = 0
        self.enemies = []
        
    def on_enter(self):
        """Called when scene becomes active"""
        super().on_enter()
        # Set up actors, load resources, etc.
        self.setup_level()
        
    def on_exit(self):
        """Called when leaving scene"""
        super().on_exit()
        # Clean up resources
        
    def update(self, dt):
        """Called every frame"""
        super().update(dt)  # Updates all actors
        # Custom scene logic
        self.check_win_condition()
```

### Scene Lifecycle

#### Scene States

Scenes have several states and corresponding events:

```python
class GameScene(Scene):
    def on_enter(self):
        """Scene becomes the active scene"""
        print("Scene started")
        self.setup_actors()
        
    def on_exit(self):
        """Scene is being removed/replaced"""
        print("Scene ending")
        self.cleanup_resources()
        
    def on_pause(self):
        """Another scene was pushed on top"""
        print("Scene paused")
        self.pause_music()
        
    def on_resume(self):
        """Returned to from scene stack"""
        print("Scene resumed")
        self.resume_music()
```

### Actor Management

#### Creating and Managing Actors

```python
class MyScene(Scene):
    def setup_level(self):
        # Create actors in the scene
        player = self.create_actor("Player", pygame.Vector2(100, 100))
        enemy = self.create_actor("Enemy", pygame.Vector2(200, 100))
        
        # Add components
        player.add_component(SpriteComponent())
        player.add_component(RigidBodyComponent())
        
        # Store references if needed
        self.player = player
        
    def cleanup_level(self):
        # Remove all actors
        self.clear()  # Removes and destroys all actors
        
    def remove_enemy(self, enemy):
        # Remove specific actor
        self.destroy_actor(enemy)
```

#### Finding Actors

```python
# Find by name
player = self.find_actor("Player")

# Find by tag
enemies = self.find_actors_with_tag("enemy")
powerups = self.find_actors_with_tag("powerup")

# Find by component type
all_physics_objects = self.find_actors_with_component(RigidBodyComponent)

# Get all components of a type from all actors
all_health_components = self.get_components(HealthComponent)
```

### Scene Properties

```python
scene = MyScene()

# Basic properties
scene.name = "MyScene"           # Scene identifier
scene.active = True              # Whether scene is active
scene.paused = False             # Whether scene is paused

# Background
scene.background_color = pygame.Color(50, 50, 100)
scene.background_image = background_surface

# Actor collections
scene.actors = []                # List of all actors
scene.actor_lookup = {}          # Dict for name-based lookup
scene.actors_by_tag = {}         # Dict for tag-based lookup
```

### Custom Scene Updates

```python
class GameScene(Scene):
    def update(self, dt):
        # Always call super() first to update actors
        super().update(dt)
        
        # Custom scene logic
        self.update_score()
        self.check_collisions()
        self.spawn_enemies()
        
    def update_score(self):
        # Update game score
        pass
        
    def check_collisions(self):
        # Handle collisions between actors
        pass
        
    def spawn_enemies(self):
        # Spawn new enemies based on game state
        pass
```

### Scene Rendering

```python
class MyScene(Scene):
    def render(self, screen):
        # Set background
        self.background_color = pygame.Color(20, 30, 40)
        super().render(screen)  # Renders all actors
        
        # Custom rendering on top
        self.render_ui(screen)
        self.render_debug_info(screen)
        
    def render_ui(self, screen):
        # Render UI elements
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, pygame.Color(255, 255, 255))
        screen.blit(score_text, (10, 10))
```

## Common Scene Patterns

### Menu Scene

```python
class MainMenuScene(Scene):
    def __init__(self):
        super().__init__("MainMenu")
        self.ui_manager = None
        
    def on_enter(self):
        super().on_enter()
        
        # Set up UI
        screen_size = pygame.display.get_surface().get_size()
        self.ui_manager = UIManager(screen_size)
        
        # Create menu buttons
        play_button = Button(pygame.Rect(350, 200, 100, 50), "Play")
        play_button.add_event_handler("clicked", self.on_play_clicked)
        self.ui_manager.add_widget(play_button)
        
    def on_play_clicked(self, event):
        self.game.load_scene("game")
        
    def update(self, dt):
        super().update(dt)
        if self.ui_manager:
            self.ui_manager.update(dt)
            
    def render(self, screen):
        super().render(screen)
        if self.ui_manager:
            self.ui_manager.render(screen)
```

### Game Scene with Levels

```python
class GameScene(Scene):
    def __init__(self):
        super().__init__("Game")
        self.level = 1
        self.score = 0
        
    def on_enter(self):
        super().on_enter()
        self.load_level(self.level)
        
    def load_level(self, level_num):
        # Clear existing actors
        self.clear()
        
        # Load level data
        level_data = self.game.asset_manager.load_data(f"level_{level_num}.json")
        
        # Create actors based on level data
        for actor_data in level_data["actors"]:
            self.create_actor_from_data(actor_data)
            
    def check_win_condition(self):
        enemies = self.find_actors_with_tag("enemy")
        if not enemies:  # No enemies left
            self.level += 1
            if self.level <= self.max_levels:
                self.load_level(self.level)
            else:
                self.game.load_scene("victory")
```

### Pause Overlay Scene

```python
class PauseScene(Scene):
    def __init__(self):
        super().__init__("Pause")
        
    def on_enter(self):
        super().on_enter()
        
        # Semi-transparent overlay
        screen_size = pygame.display.get_surface().get_size()
        self.overlay = pygame.Surface(screen_size)
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(128)
        
        # Create resume button
        resume_button = Button(pygame.Rect(350, 250, 100, 50), "Resume")
        resume_button.add_event_handler("clicked", self.on_resume_clicked)
        
    def on_resume_clicked(self, event):
        self.game.pop_scene()  # Return to previous scene
        
    def render(self, screen):
        # Render overlay
        screen.blit(self.overlay, (0, 0))
        super().render(screen)
```

## Best Practices

### Scene Organization

1. **Keep scenes focused** - Each scene should have a clear purpose
2. **Use scene stack for overlays** - Pause menus, dialogs, etc.
3. **Clean up resources** - Always clean up in `on_exit()`
4. **Use data-driven design** - Load scene configuration from files

### Performance Tips

1. **Pool frequently created objects** - Bullets, particles, etc.
2. **Use tags for efficient searches** - Avoid iterating through all actors
3. **Limit active actors** - Deactivate off-screen objects
4. **Batch similar operations** - Group similar rendering operations

### Memory Management

```python
class MyScene(Scene):
    def on_exit(self):
        # Clean up resources before leaving
        self.clear()  # Remove all actors
        
        # Clean up scene-specific resources
        if self.background_music:
            self.background_music.stop()
            
        if self.ui_manager:
            self.ui_manager.cleanup()
            
        super().on_exit()
```
