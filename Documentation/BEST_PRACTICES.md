# Best Practices

This guide covers recommended patterns, coding standards, and architectural decisions for building games with the Wicked Wizard Washdown engine.

## Project Organization

### Directory Structure

```
MyGame/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── config/                 # Configuration files
│   ├── settings.json
│   └── key_bindings.json
├── game/                   # Game-specific code
│   ├── __init__.py
│   ├── scenes/            # Game scenes
│   ├── actors/            # Custom actors
│   ├── components/        # Custom components
│   └── systems/           # Custom systems
├── assets/                # Game assets
│   ├── images/
│   ├── sounds/
│   ├── fonts/
│   └── data/
└── docs/                  # Game documentation
```

### File Naming Conventions

```python
# Use snake_case for files and functions
player_controller.py
enemy_spawner.py
main_menu_scene.py

# Use PascalCase for classes
class PlayerController(Component):
class EnemySpawner(Component):
class MainMenuScene(Scene):

# Use UPPER_CASE for constants
MAX_HEALTH = 100
GRAVITY_STRENGTH = 981
COLLISION_TYPE_PLAYER = 1
```

## Component Design Principles

### Single Responsibility

Each component should have one clear purpose:

```python
# ✅ Good - focused responsibility
class HealthComponent(Component):
    def take_damage(self, amount): ...
    def heal(self, amount): ...
    def is_alive(self): ...

# ❌ Bad - too many responsibilities
class PlayerComponent(Component):
    def handle_input(self): ...      # Input responsibility
    def update_health(self): ...     # Health responsibility
    def play_animations(self): ...   # Animation responsibility
    def manage_inventory(self): ...  # Inventory responsibility
```

### Data-Driven Design

Configure behavior through data rather than hardcoding:

```python
# config/enemies.json
{
  "goblin": {
    "health": 30,
    "speed": 50,
    "damage": 10,
    "sprite": "goblin.png",
    "loot": ["coin", "potion"]
  },
  "orc": {
    "health": 80,
    "speed": 30,
    "damage": 20,
    "sprite": "orc.png",
    "loot": ["coin", "gem", "weapon"]
  }
}

# Code
class EnemyFactory:
    def __init__(self):
        self.enemy_configs = self.load_enemy_configs()
        
    def create_enemy(self, enemy_type, position):
        config = self.enemy_configs[enemy_type]
        enemy = self.scene.create_actor(enemy_type, position)
        
        # Configure from data
        enemy.add_component(HealthComponent(config["health"]))
        enemy.add_component(MovementComponent(config["speed"]))
        enemy.add_component(SpriteComponent(config["sprite"]))
        enemy.add_component(LootComponent(config["loot"]))
        
        return enemy
```

### Component Communication

Use events and references rather than tight coupling:

```python
# ✅ Good - event-driven communication
class PlayerController(Component):
    def __init__(self):
        super().__init__()
        self.on_jump = None  # Event callback
        
    def update(self, dt):
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            if self.on_jump:
                self.on_jump()

class PlayerAnimator(Component):
    def start(self):
        controller = self.actor.get_component(PlayerController)
        if controller:
            controller.on_jump = self.play_jump_animation
            
    def play_jump_animation(self):
        animation = self.actor.get_component(FileAnimationComponent)
        if animation:
            animation.play_animation("jump")

# ❌ Bad - tight coupling
class PlayerController(Component):
    def update(self, dt):
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            # Directly accessing other components
            animation = self.actor.get_component(FileAnimationComponent)
            animation.play_animation("jump")
            audio = self.actor.get_component(AudioComponent)
            audio.play_sound("jump")
```

## Scene Management Patterns

### Scene Hierarchy

Organize scenes logically:

```python
# Base scene classes
class BaseMenuScene(Scene):
    """Base class for all menu scenes"""
    def __init__(self, name):
        super().__init__(name)
        self.ui_manager = None
        
    def on_enter(self):
        super().on_enter()
        self.setup_ui()
        
    def setup_ui(self):
        screen_size = pygame.display.get_surface().get_size()
        self.ui_manager = UIManager(screen_size)

class BaseGameScene(Scene):
    """Base class for all gameplay scenes"""
    def __init__(self, name):
        super().__init__(name)
        self.paused = False
        
    def handle_event(self, event):
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.toggle_pause()
            
    def toggle_pause(self):
        if not self.paused:
            self.game.push_scene("pause_menu")
        self.paused = not self.paused

# Specific scenes inherit from base classes
class MainMenuScene(BaseMenuScene):
    def __init__(self):
        super().__init__("MainMenu")
        
class GameScene(BaseGameScene):
    def __init__(self):
        super().__init__("Game")
```

### Scene Transitions

Handle transitions gracefully:

```python
class SceneTransitionManager:
    def __init__(self, game):
        self.game = game
        self.transition_time = 0.5
        
    def fade_to_scene(self, scene_name):
        """Fade out, switch scene, fade in"""
        fade_out = PropertyAnimation(
            target=self,
            property_name="fade_alpha",
            start_value=0,
            end_value=255,
            duration=self.transition_time / 2,
            on_complete=lambda: self.switch_and_fade_in(scene_name)
        )
        fade_out.start()
        
    def switch_and_fade_in(self, scene_name):
        self.game.load_scene(scene_name)
        
        fade_in = PropertyAnimation(
            target=self,
            property_name="fade_alpha",
            start_value=255,
            end_value=0,
            duration=self.transition_time / 2
        )
        fade_in.start()
```

## Actor and Object Management

### Object Pooling

Reuse objects for better performance:

```python
class BulletPool:
    def __init__(self, scene, pool_size=100):
        self.scene = scene
        self.available_bullets = []
        self.active_bullets = []
        
        # Pre-create bullets
        for _ in range(pool_size):
            bullet = self.create_bullet()
            bullet.active = False
            self.available_bullets.append(bullet)
            
    def get_bullet(self, position, velocity):
        if self.available_bullets:
            bullet = self.available_bullets.pop()
            bullet.active = True
            bullet.transform.local_position = position
            
            physics = bullet.get_component(RigidBodyComponent)
            if physics:
                physics.set_velocity(velocity)
                
            self.active_bullets.append(bullet)
            return bullet
        return None
        
    def return_bullet(self, bullet):
        if bullet in self.active_bullets:
            bullet.active = False
            self.active_bullets.remove(bullet)
            self.available_bullets.append(bullet)
            
    def create_bullet(self):
        bullet = self.scene.create_actor("Bullet")
        bullet.add_component(SpriteComponent(color=pygame.Color(255, 255, 0)))
        bullet.add_component(RigidBodyComponent(mass=0.1, shape_type="circle"))
        bullet.add_tag("bullet")
        return bullet
```

### Factory Patterns

Centralize object creation:

```python
class ActorFactory:
    def __init__(self, scene):
        self.scene = scene
        self.asset_manager = scene.game.asset_manager
        
    def create_player(self, position, player_id):
        player = self.scene.create_actor("Player", position)
        
        # Visual components
        sprite = SpriteComponent()
        sprite.set_surface(self.asset_manager.load_image("player.png"))
        player.add_component(sprite)
        
        animation = FileAnimationComponent("player_animations.yaml")
        player.add_component(animation)
        
        # Gameplay components
        player.add_component(HealthComponent(100))
        player.add_component(RigidBodyComponent(mass=1.0, shape_type="box"))
        player.add_component(PlayerController())
        
        # Networking (if multiplayer)
        if player_id:
            network = NetworkComponent(
                owner_id=player_id,
                ownership=NetworkOwnership.CLIENT,
                sync_transform=True
            )
            player.add_component(network)
            
        player.add_tag("player")
        return player
        
    def create_enemy(self, enemy_type, position):
        config = self.load_enemy_config(enemy_type)
        enemy = self.scene.create_actor(f"Enemy_{enemy_type}", position)
        
        # Configure from data
        self.configure_enemy_from_data(enemy, config)
        
        enemy.add_tag("enemy")
        enemy.add_tag(enemy_type)
        return enemy
```

## Performance Optimization

### Update Optimization

Only update what's necessary:

```python
class OptimizedComponent(Component):
    def __init__(self):
        super().__init__()
        self.needs_update = True
        self.update_interval = 0.1  # Update 10 times per second
        self.last_update = 0
        
    def update(self, dt):
        if not self.needs_update:
            return
            
        current_time = time.time()
        if current_time - self.last_update < self.update_interval:
            return
            
        self.do_expensive_update()
        self.last_update = current_time
        self.needs_update = False
        
    def mark_dirty(self):
        self.needs_update = True
        
    def do_expensive_update(self):
        # Expensive operations here
        pass
```

### Spatial Partitioning

Optimize collision detection and queries:

```python
class SpatialGrid:
    def __init__(self, cell_size=64):
        self.cell_size = cell_size
        self.grid = {}
        
    def insert(self, actor, position):
        cell_x = int(position.x // self.cell_size)
        cell_y = int(position.y // self.cell_size)
        cell_key = (cell_x, cell_y)
        
        if cell_key not in self.grid:
            self.grid[cell_key] = []
        self.grid[cell_key].append(actor)
        
    def query_area(self, center, radius):
        """Find all actors within radius of center"""
        results = []
        
        # Check relevant cells
        cell_radius = int(radius // self.cell_size) + 1
        center_cell_x = int(center.x // self.cell_size)
        center_cell_y = int(center.y // self.cell_size)
        
        for dx in range(-cell_radius, cell_radius + 1):
            for dy in range(-cell_radius, cell_radius + 1):
                cell_key = (center_cell_x + dx, center_cell_y + dy)
                if cell_key in self.grid:
                    results.extend(self.grid[cell_key])
                    
        return results
```

### Asset Management

Efficient asset loading and caching:

```python
class AssetPreloader:
    def __init__(self, asset_manager):
        self.asset_manager = asset_manager
        self.preload_lists = {}
        
    def add_preload_list(self, scene_name, assets):
        """Add assets to preload for a specific scene"""
        self.preload_lists[scene_name] = assets
        
    def preload_for_scene(self, scene_name):
        """Preload all assets for a scene"""
        if scene_name in self.preload_lists:
            for asset in self.preload_lists[scene_name]:
                if asset["type"] == "image":
                    self.asset_manager.load_image(asset["path"])
                elif asset["type"] == "sound":
                    self.asset_manager.load_sound(asset["path"])
                elif asset["type"] == "data":
                    self.asset_manager.load_data(asset["path"])
                    
    def unload_scene_assets(self, scene_name):
        """Unload assets that are no longer needed"""
        # Implementation depends on asset manager's cleanup capabilities
        pass

# Usage
preloader = AssetPreloader(game.asset_manager)
preloader.add_preload_list("game", [
    {"type": "image", "path": "player.png"},
    {"type": "image", "path": "enemy.png"},
    {"type": "sound", "path": "jump.wav"},
    {"type": "data", "path": "level1.json"}
])

# In scene on_enter
preloader.preload_for_scene("game")
```

## Error Handling and Debugging

### Defensive Programming

Check for component existence:

```python
class SafeComponent(Component):
    def update(self, dt):
        # Always check if components exist
        physics = self.actor.get_component(RigidBodyComponent)
        if physics:
            physics.apply_force((100, 0))
            
        health = self.actor.get_component(HealthComponent)
        if health and health.is_alive():
            # Only update if alive
            self.update_behavior(dt)
            
    def get_required_component(self, component_type):
        """Get component with error handling"""
        component = self.actor.get_component(component_type)
        if not component:
            raise ValueError(f"Required component {component_type} not found on {self.actor.name}")
        return component
```

### Logging and Debug Information

Implement comprehensive logging:

```python
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('game.log'),
        logging.StreamHandler()
    ]
)

class DebugComponent(Component):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        
    def update(self, dt):
        try:
            self.do_update(dt)
        except Exception as e:
            self.logger.error(f"Error in {self.actor.name}: {e}")
            raise
            
    def do_update(self, dt):
        # Actual update logic
        pass
```

### Debug Visualization

Add visual debugging tools:

```python
class DebugRenderer:
    def __init__(self):
        self.enabled = False
        self.show_physics = True
        self.show_actor_names = True
        self.show_performance = True
        
    def render_debug_info(self, screen, scene):
        if not self.enabled:
            return
            
        if self.show_physics:
            scene.game.physics_system.render_debug(screen)
            
        if self.show_actor_names:
            self.render_actor_names(screen, scene)
            
        if self.show_performance:
            self.render_performance_info(screen)
            
    def render_actor_names(self, screen, scene):
        font = pygame.font.Font(None, 16)
        for actor in scene.actors:
            if actor.active:
                pos = actor.transform.world_position
                text = font.render(actor.name, True, pygame.Color(255, 255, 255))
                screen.blit(text, (pos.x, pos.y - 20))
```

## Testing Strategies

### Component Testing

```python
class TestableComponent(Component):
    def __init__(self):
        super().__init__()
        self.test_mode = False
        
    def update(self, dt):
        if self.test_mode:
            self.update_test_mode(dt)
        else:
            self.update_normal_mode(dt)
            
    def update_test_mode(self, dt):
        # Simplified update for testing
        pass
        
    def update_normal_mode(self, dt):
        # Full update logic
        pass

# Unit test example
import unittest

class TestPlayerController(unittest.TestCase):
    def setUp(self):
        self.scene = Scene("TestScene")
        self.actor = Actor("TestPlayer")
        self.controller = PlayerController()
        self.controller.test_mode = True
        self.actor.add_component(self.controller)
        
    def test_movement_input(self):
        # Test movement logic
        pass
```

## Configuration Management

### Settings System

```python
class GameSettings:
    def __init__(self, config_file="config/settings.json"):
        self.config_file = config_file
        self.settings = self.load_settings()
        
    def load_settings(self):
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_settings()
            
    def get_default_settings(self):
        return {
            "graphics": {
                "resolution": [800, 600],
                "fullscreen": False,
                "vsync": True
            },
            "audio": {
                "master_volume": 1.0,
                "music_volume": 0.7,
                "sfx_volume": 0.8
            },
            "input": {
                "move_left": "a",
                "move_right": "d",
                "jump": "space"
            }
        }
        
    def save_settings(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.settings, f, indent=2)
            
    def get(self, key_path, default=None):
        """Get setting by dot notation (e.g., 'audio.master_volume')"""
        keys = key_path.split('.')
        value = self.settings
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return value
```

Following these best practices will help you create maintainable, performant, and scalable games with the engine.
