# Physics System

The physics system provides realistic 2D physics simulation using the Pymunk physics engine, offering rigid body dynamics, collision detection, and constraints.

## Overview

The engine includes two physics systems:
1. **Simple PhysicsComponent** - Basic physics for simple games
2. **Advanced Physics Bodies** - Full Pymunk integration for complex physics

## Physics World

The PhysicsWorld is a singleton that manages the physics simulation space.

### Basic Setup

```python
from engine import PhysicsWorld

# Get the physics world instance
physics_world = PhysicsWorld.get_instance()

# Set gravity (x, y) in pixels per second squared
physics_world.set_gravity((0, 981))  # Earth-like gravity

# Access through game instance
game = Game.get_instance()
physics_system = game.physics_system
physics_system.set_gravity((0, 500))
```

### Physics Properties

```python
physics_world = PhysicsWorld.get_instance()

# Simulation properties
physics_world.damping = 0.95        # Global damping
physics_world.iterations = 10       # Solver iterations for accuracy
physics_world.sleep_time_threshold = 0.5  # Time before objects sleep

# Collision properties
physics_world.collision_slop = 0.1  # Collision tolerance
physics_world.collision_bias = pow(1.0 - 0.1, 60.0)  # Collision correction
```

## Physics Body Components

### RigidBodyComponent

Dynamic physics bodies that respond to forces and collisions:

```python
from engine import RigidBodyComponent

# Create dynamic body
rigid_body = RigidBodyComponent(
    mass=1.0,                    # Object mass
    shape_type="box",            # "box" or "circle"  
    size=(32, 32),               # (width, height) for box, (radius,) for circle
    friction=0.7,                # Surface friction (0.0 to 1.0)
    elasticity=0.3,              # Bounciness (0.0 to 1.0)
    collision_type=1             # Collision category
)

actor.add_component(rigid_body)
```

#### Applying Forces

```python
# Apply force over time (acceleration)
rigid_body.apply_force((100, 0))          # Force vector
rigid_body.apply_force_at_point((100, 0), (10, 10))  # Force at specific point

# Apply instant velocity change (impulse)
rigid_body.apply_impulse((0, -500))       # Impulse vector
rigid_body.apply_impulse_at_point((0, -500), (10, 10))  # Impulse at point

# Direct velocity control
rigid_body.set_velocity((50, 0))          # Set velocity directly
velocity = rigid_body.get_velocity()      # Get current velocity

# Angular motion
rigid_body.set_angular_velocity(90)       # degrees per second
rigid_body.apply_torque(100)              # Apply rotational force
```

#### Physics Properties

```python
# Material properties
rigid_body.mass = 2.0
rigid_body.friction = 0.8
rigid_body.elasticity = 0.5

# Motion constraints
rigid_body.velocity_limit = 300           # Maximum velocity
rigid_body.angular_velocity_limit = 180   # Maximum angular velocity

# Collision settings
rigid_body.collision_type = 2
rigid_body.collision_mask = 0b1111        # Which types this collides with
rigid_body.collision_group = 1            # Collision group
```

### StaticBodyComponent

Immovable objects like platforms, walls, and terrain:

```python
from engine import StaticBodyComponent

# Create static platform
platform = StaticBodyComponent(
    shape_type="box",
    size=(200, 20),
    friction=0.8,
    elasticity=0.1,
    collision_type=2
)

actor.add_component(platform)
```

Static bodies:
- Don't move or respond to forces
- Provide surfaces for dynamic bodies to collide with
- Use minimal CPU resources
- Perfect for level geometry

### KinematicBodyComponent

Objects that move but aren't affected by forces (moving platforms, elevators):

```python
from engine import KinematicBodyComponent

# Create kinematic body
kinematic = KinematicBodyComponent(
    shape_type="box",
    size=(64, 16),
    friction=0.5
)

actor.add_component(kinematic)

# Control movement directly
kinematic.set_velocity((50, 0))           # Constant movement
kinematic.set_angular_velocity(45)        # Constant rotation

# Kinematic bodies can push dynamic bodies
```

## Shape Types

### Box Shapes
Rectangular collision shapes:

```python
# Square box
rigid_body = RigidBodyComponent(
    shape_type="box",
    size=(32, 32)  # width, height
)

# Rectangular box
platform = StaticBodyComponent(
    shape_type="box", 
    size=(100, 20)  # width, height
)
```

### Circle Shapes
Circular collision shapes:

```python
# Circle shape
ball = RigidBodyComponent(
    shape_type="circle",
    size=(16,)  # radius (note the comma for tuple)
)

# Circles are more efficient for round objects
coin = StaticBodyComponent(
    shape_type="circle",
    size=(8,)  # radius
)
```

## Collision Detection

### Collision Types and Groups

Organize collisions using types and groups:

```python
# Define collision types
COLLISION_TYPE_PLAYER = 1
COLLISION_TYPE_ENEMY = 2  
COLLISION_TYPE_PLATFORM = 3
COLLISION_TYPE_PICKUP = 4

# Create bodies with types
player_body = RigidBodyComponent(
    mass=1.0,
    shape_type="box",
    size=(32, 32),
    collision_type=COLLISION_TYPE_PLAYER
)

enemy_body = RigidBodyComponent(
    mass=0.8,
    shape_type="circle", 
    size=(16,),
    collision_type=COLLISION_TYPE_ENEMY
)

# Collision groups (same group = no collision)
player_body.collision_group = 1
friendly_npc_body.collision_group = 1  # Won't collide with player
```

### Collision Callbacks

Handle collision events:

```python
class PlayerPhysics(RigidBodyComponent):
    def __init__(self):
        super().__init__(mass=1.0, shape_type="box", size=(32, 32))
        
    def on_collision_begin(self, other_actor, collision_point):
        """Called when collision starts"""
        if other_actor.has_tag("enemy"):
            health = self.actor.get_component(HealthComponent)
            if health:
                health.take_damage(10)
                
    def on_collision_end(self, other_actor):
        """Called when collision ends"""
        if other_actor.has_tag("platform"):
            print("Left platform")
```

### Collision Queries

Query the physics world for objects:

```python
physics_world = PhysicsWorld.get_instance()

# Point query - find objects at a specific point
results = physics_world.query_point((x, y))
for result in results:
    actor = result.actor
    print(f"Found {actor.name} at point")

# Segment query - raycast between two points
ray_results = physics_world.query_segment((start_x, start_y), (end_x, end_y))
for result in ray_results:
    actor = result.actor
    hit_point = result.point
    distance = result.distance

# Bounding box query - find objects in an area
bbox_results = physics_world.query_bbox((min_x, min_y, max_x, max_y))
```

## Simple Physics Component

For basic games that don't need full physics simulation:

```python
from engine import PhysicsComponent

physics = PhysicsComponent()

# Basic properties
physics.velocity = pygame.Vector2(100, 0)      # Current velocity
physics.acceleration = pygame.Vector2(0, 0)    # Current acceleration
physics.gravity = pygame.Vector2(0, 300)       # Gravity force
physics.mass = 1.0                             # Object mass
physics.drag = 0.98                            # Velocity damping (0-1)
physics.bounce = 0.7                           # Bounce factor
physics.friction = 0.8                         # Friction coefficient

# Apply forces
physics.apply_force(pygame.Vector2(50, -100))   # Continuous force
physics.apply_impulse(pygame.Vector2(0, -200))  # Instant velocity change
```

The simple physics component:
- Updates position based on velocity
- Applies gravity, drag, and friction
- Handles basic collision response
- Good for platformers and simple games

## Physics Constraints

Connect physics bodies with constraints (joints):

### Distance Joint
Maintains fixed distance between bodies:

```python
from engine import PhysicsConstraintComponent

# Create constraint between two actors
constraint = PhysicsConstraintComponent(
    constraint_type="distance",
    other_actor=other_actor,
    anchor_a=(0, 0),      # Anchor point on this actor
    anchor_b=(0, 0),      # Anchor point on other actor
    distance=50           # Fixed distance
)

actor.add_component(constraint)
```

### Pin Joint
Connects bodies at a point (allows rotation):

```python
pin_joint = PhysicsConstraintComponent(
    constraint_type="pin",
    other_actor=other_actor,
    anchor_a=(0, 0),
    anchor_b=(0, 0)
)
```

### Spring
Flexible connection with spring properties:

```python
spring = PhysicsConstraintComponent(
    constraint_type="spring",
    other_actor=other_actor,
    anchor_a=(0, 0),
    anchor_b=(0, 0),
    rest_length=30,
    stiffness=100,
    damping=5
)
```

## Debug Visualization

Visualize physics shapes and constraints for debugging:

```python
# Enable debug rendering
physics_system = game.physics_system
physics_system.debug_draw = True

# In your scene's render method
def render(self, screen):
    super().render(screen)
    
    # Render physics debug info
    self.game.physics_system.render_debug(screen)
```

Debug visualization shows:
- Collision shapes (boxes, circles)
- Constraint connections
- Velocity vectors
- Contact points
- Sleeping objects (dimmed)

## Performance Optimization

### Object Sleeping
Objects automatically "sleep" when not moving:

```python
# Configure sleep behavior
rigid_body.sleep_time_threshold = 1.0  # Time before sleeping
rigid_body.velocity_threshold = 10     # Velocity threshold for sleeping

# Manually control sleep
rigid_body.sleep()                     # Force sleep
rigid_body.wake()                      # Force wake
is_sleeping = rigid_body.is_sleeping() # Check sleep state
```

### Collision Optimization

```python
# Use appropriate collision groups
rigid_body.collision_group = 1  # Same group = no collision checking

# Use collision masks for selective collision
rigid_body.collision_mask = 0b1101  # Binary mask for collision types

# Disable unused collision types
rigid_body.collision_type = 0  # No collisions at all
```

### Shape Efficiency

```python
# Circles are faster than boxes
ball = RigidBodyComponent(shape_type="circle", size=(radius,))

# Use static bodies for non-moving objects
platform = StaticBodyComponent(shape_type="box", size=(width, height))

# Kinematic for controlled movement
elevator = KinematicBodyComponent(shape_type="box", size=(width, height))
```

## Common Physics Patterns

### Character Controller

```python
class PlayerController(Component):
    def __init__(self):
        super().__init__()
        self.move_speed = 300
        self.jump_force = 500
        self.grounded = False
        
    def update(self, dt):
        physics = self.actor.get_component(RigidBodyComponent)
        if not physics:
            return
            
        keys = pygame.key.get_pressed()
        
        # Horizontal movement
        if keys[pygame.K_LEFT]:
            physics.apply_force((-self.move_speed, 0))
        if keys[pygame.K_RIGHT]:
            physics.apply_force((self.move_speed, 0))
            
        # Jumping (only when grounded)
        if keys[pygame.K_SPACE] and self.grounded:
            physics.apply_impulse((0, -self.jump_force))
            self.grounded = False
            
    def on_collision_begin(self, other_actor, collision_point):
        if other_actor.has_tag("ground"):
            self.grounded = True
```

### Projectile Physics

```python
def create_bullet(scene, start_pos, direction, speed):
    bullet = scene.create_actor("Bullet", start_pos)
    
    # Visual
    bullet.add_component(SpriteComponent(
        color=pygame.Color(255, 255, 0),
        size=pygame.Vector2(4, 4)
    ))
    
    # Physics
    physics = RigidBodyComponent(
        mass=0.1,
        shape_type="circle",
        size=(2,),
        collision_type=COLLISION_TYPE_BULLET
    )
    
    # Set initial velocity
    velocity = direction.normalize() * speed
    physics.set_velocity((velocity.x, velocity.y))
    
    bullet.add_component(physics)
    bullet.add_tag("bullet")
    
    return bullet
```

### Destructible Objects

```python
class DestructibleBox(Component):
    def __init__(self, health=10):
        super().__init__()
        self.health = health
        
    def on_collision_begin(self, other_actor, collision_point):
        if other_actor.has_tag("bullet"):
            self.health -= 5
            
            if self.health <= 0:
                self.destroy_box()
                
    def destroy_box(self):
        # Create debris
        for i in range(4):
            debris = self.create_debris()
            # Add random forces to debris
            
        # Remove this actor
        self.actor.scene.destroy_actor(self.actor)
```

## Best Practices

### Performance
1. **Use appropriate body types** - Static for terrain, kinematic for platforms
2. **Optimize collision detection** - Use groups and masks effectively
3. **Let objects sleep** - Don't unnecessarily wake sleeping objects
4. **Limit constraint count** - Too many constraints can slow simulation

### Design
1. **Match visual and physics** - Keep sprites and collision shapes aligned
2. **Use consistent units** - Establish pixel-to-meter ratios
3. **Test collision types** - Ensure collision layers work as expected
4. **Debug visualization** - Use debug rendering during development

### Common Pitfalls
1. **Don't mix physics systems** - Choose either simple or advanced physics
2. **Avoid tiny objects** - Very small physics objects can be unstable
3. **Limit velocity** - Extremely fast objects can tunnel through thin walls
4. **Clean up constraints** - Remove constraints when actors are destroyed
