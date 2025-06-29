# Physics System Documentation

The Wicked Wizard Washdown engine now includes a high-performance physics system powered by **Pymunk**, a 2D physics library based on the Chipmunk physics engine.

## Features

- **Rigid Body Dynamics**: Dynamic objects with realistic physics simulation
- **Static Bodies**: Immovable objects like platforms and walls
- **Kinematic Bodies**: Objects that move but aren't affected by forces
- **Collision Detection**: Precise collision detection and response
- **Constraints**: Joints, springs, and other physics constraints
- **Material Properties**: Friction, elasticity, and density settings
- **Debug Visualization**: Visual debugging of physics shapes and constraints

## Core Classes

### PhysicsWorld

Singleton class that manages the physics simulation space.

```python
from engine import PhysicsWorld

# Get the physics world instance
physics_world = PhysicsWorld.get_instance()

# Set gravity (x, y) in pixels per second squared
physics_world.set_gravity((0, 981))  # Earth-like gravity

# Query for objects at a point
results = physics_world.query_point((x, y))

# Raycast between two points
ray_results = physics_world.query_segment((start_x, start_y), (end_x, end_y))
```

### PhysicsSystem

System that integrates physics updates into the game loop.

```python
# Access through the game instance
game = Game.get_instance()
physics_system = game.physics_system

# Set gravity
physics_system.set_gravity((0, 500))

# Render debug visualization
physics_system.render_debug(screen)
```

## Physics Components

### RigidBodyComponent

For dynamic objects that respond to forces and collisions.

```python
from engine import Actor, RigidBodyComponent, SpriteComponent

# Create a dynamic box
actor = Actor()
actor.add_component(SpriteComponent(size=pygame.Vector2(30, 30)))

# Add physics
rigid_body = RigidBodyComponent(
    mass=1.0,                    # Mass in arbitrary units
    shape_type="box",            # "box", "circle", or "polygon"
    size=(30, 30)               # Shape dimensions
)

# Set material properties
rigid_body.friction = 0.7       # Surface friction (0-1+)
rigid_body.elasticity = 0.3     # Bounciness (0-1)
rigid_body.collision_type = 1   # Collision category

actor.add_component(rigid_body)

# Apply forces and impulses
rigid_body.apply_force((100, 0))              # Continuous force
rigid_body.apply_impulse((50, -100))          # Instant velocity change
rigid_body.set_velocity((100, -200))          # Direct velocity setting
```

### StaticBodyComponent

For immovable objects like platforms, walls, and obstacles.

```python
# Create a static platform
platform = Actor()
platform.add_component(SpriteComponent(size=pygame.Vector2(200, 20)))

static_body = StaticBodyComponent(
    shape_type="box",
    size=(200, 20)
)
static_body.friction = 1.0       # High friction for platforms

platform.add_component(static_body)
```

### KinematicBodyComponent

For objects that move but aren't affected by physics forces.

```python
# Create a moving platform
moving_platform = Actor()
moving_platform.add_component(SpriteComponent(size=pygame.Vector2(100, 20)))

kinematic_body = KinematicBodyComponent(
    shape_type="box",
    size=(100, 20)
)

moving_platform.add_component(kinematic_body)

# Control movement
kinematic_body.set_velocity((50, 0))           # Move right at 50 pixels/second
kinematic_body.move_to((400, 300), 2.0)       # Move to position over 2 seconds
```

### PhysicsConstraintComponent

For creating joints and connections between physics bodies.

```python
# Create a pendulum
anchor = Actor()  # Static anchor point
bob = Actor()     # Dynamic pendulum bob

# Add physics to both
anchor.add_component(StaticBodyComponent(shape_type="circle", size=(10, 10)))
bob.add_component(RigidBodyComponent(mass=1.0, shape_type="circle", size=(20, 20)))

# Create pin joint constraint
constraint = PhysicsConstraintComponent(constraint_type="pin_joint")
constraint.anchor_a = (0, 0)    # Connection point on anchor
constraint.anchor_b = (0, 0)    # Connection point on bob
constraint.set_other_actor(anchor)

bob.add_component(constraint)
```

## Shape Types

### Box
```python
RigidBodyComponent(shape_type="box", size=(width, height))
```

### Circle
```python
RigidBodyComponent(shape_type="circle", size=(diameter, diameter))
```

### Polygon
```python
# Custom polygon vertices
vertices = [(-10, -10), (10, -10), (15, 10), (-15, 10)]
RigidBodyComponent(shape_type="polygon", size=vertices)
```

## Constraint Types

### Pin Joint
Creates a pivot point connection between two bodies.
```python
constraint = PhysicsConstraintComponent(constraint_type="pin_joint")
```

### Slide Joint
Allows bodies to slide along a line between min and max distances.
```python
constraint = PhysicsConstraintComponent(constraint_type="slide_joint")
constraint.min_distance = 20
constraint.max_distance = 100
```

### Spring
Creates a spring connection with damping.
```python
constraint = PhysicsConstraintComponent(constraint_type="spring")
constraint.rest_length = 50    # Natural spring length
constraint.stiffness = 100     # Spring strength
constraint.damping = 5         # Energy dissipation
```

### Rotary Limit
Limits rotation between two bodies.
```python
constraint = PhysicsConstraintComponent(constraint_type="rotary_limit")
constraint.min_angle = -1.57   # -90 degrees
constraint.max_angle = 1.57    # 90 degrees
```

## Material Properties

### Friction
Controls surface friction between objects.
- `0.0`: No friction (ice-like)
- `0.7`: Normal friction (default)
- `1.0+`: High friction (sticky)

### Elasticity (Bounciness)
Controls how bouncy collisions are.
- `0.0`: No bounce (inelastic)
- `0.5`: Medium bounce
- `1.0`: Perfect bounce (no energy loss)

### Collision Filtering

Control which objects can collide:

```python
rigid_body.collision_type = 1      # Object type
rigid_body.group = 0               # Collision group (0 = no group)
rigid_body.category = 1            # Collision category bitmask
rigid_body.mask = 0xFFFFFFFF       # Which categories this can collide with
```

## Collision Detection

### Collision Handlers

Set up callbacks for when objects collide:

```python
def player_enemy_collision(arbiter, space, data):
    """Called when player collides with enemy."""
    # Get the collision shapes
    shape_a, shape_b = arbiter.shapes
    
    # Handle collision logic
    print("Player hit enemy!")
    return True  # Allow collision to proceed

# Register collision handler
physics_world = PhysicsWorld.get_instance()
physics_world.add_collision_handler(
    collision_type_a=1,  # Player collision type
    collision_type_b=2,  # Enemy collision type  
    handler=player_enemy_collision
)
```

### Queries

Check for objects at specific locations:

```python
# Point query
mouse_pos = pygame.mouse.get_pos()
objects_at_mouse = physics_world.query_point(mouse_pos)

# Raycast
start_pos = (100, 100)
end_pos = (200, 200)
ray_hits = physics_world.query_segment(start_pos, end_pos)
```

## Performance Tips

1. **Use Static Bodies** for immovable objects instead of high-mass dynamic bodies
2. **Limit Collision Checks** using collision categories and masks
3. **Group Related Objects** to optimize collision detection
4. **Adjust Solver Iterations** for quality vs performance trade-offs:
   ```python
   physics_world.space.iterations = 10  # Default, higher = more accurate
   ```

## Debug Visualization

Enable physics debug rendering to see collision shapes:

```python
# In your scene's render method
def render(self, screen):
    super().render(screen)
    
    # Render physics debug info
    self.game.physics_system.render_debug(screen)
```

Debug visualization shows:
- Collision shapes (wireframe)
- Constraint connections
- Collision contact points
- Velocity vectors (optional)

## Example: Complete Physics Scene

```python
from engine import *
import pygame

class PhysicsScene(Scene):
    def on_enter(self):
        # Set up gravity
        physics_world = PhysicsWorld.get_instance()
        physics_world.set_gravity((0, 500))
        
        # Create ground
        ground = Actor(Transform(pygame.Vector2(400, 550)))
        ground.add_component(SpriteComponent(color=pygame.Color(100, 100, 100)))
        ground.add_component(StaticBodyComponent(shape_type="box", size=(800, 40)))
        self.add_actor(ground)
        
        # Create falling boxes
        for i in range(5):
            box = Actor(Transform(pygame.Vector2(200 + i * 50, 100)))
            box.add_component(SpriteComponent(color=pygame.Color(255, 100, 100)))
            
            rigid_body = RigidBodyComponent(mass=1.0, shape_type="box", size=(30, 30))
            rigid_body.friction = 0.7
            rigid_body.elasticity = 0.3
            box.add_component(rigid_body)
            
            self.add_actor(box)
    
    def render(self, screen):
        super().render(screen)
        # Show physics debug visualization
        self.game.physics_system.render_debug(screen)
```

This physics system provides a solid foundation for creating games with realistic physics simulation, from simple platformers to complex physics puzzles!
