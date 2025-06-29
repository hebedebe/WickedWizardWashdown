"""
Physics system using Pymunk for high-performance 2D physics simulation.
Provides rigid body, collision detection, and physics constraints.
"""

import pygame
import pymunk
import pymunk.pygame_util
import math
from typing import Optional, List, Tuple, Callable, Dict, Any, Union
from .actor import Component, Actor
from abc import ABC, abstractmethod


class PhysicsWorld:
    """
    Singleton physics world manager using Pymunk.
    Manages the physics space, bodies, and constraints.
    """
    
    _instance: Optional['PhysicsWorld'] = None
    
    def __init__(self):
        if PhysicsWorld._instance is not None:
            raise RuntimeError("PhysicsWorld is a singleton. Use get_instance().")
            
        self.space = pymunk.Space()
        self.space.gravity = (0, 981)  # Default gravity (pixels/s²)
        
        # Physics settings
        self.iterations = 10  # Constraint solver iterations
        self.damping = 1.0   # Global velocity damping
        
        # Collision handlers
        self.collision_handlers: Dict[Tuple[int, int], Callable] = {}
        
        # Debug rendering
        self.debug_draw = True
        self.debug_options = (
            pymunk.pygame_util.DrawOptions.DRAW_SHAPES |
            pymunk.pygame_util.DrawOptions.DRAW_CONSTRAINTS |
            pymunk.pygame_util.DrawOptions.DRAW_COLLISION_POINTS
        )
        
        PhysicsWorld._instance = self
        
    @classmethod
    def get_instance(cls) -> 'PhysicsWorld':
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = PhysicsWorld()
        return cls._instance
        
    def set_gravity(self, gravity: Tuple[float, float]) -> None:
        """Set world gravity."""
        self.space.gravity = gravity
        
    def step(self, dt: float) -> None:
        """Step the physics simulation."""
        self.space.iterations = self.iterations
        self.space.damping = self.damping
        self.space.step(dt)
        
    def add_collision_handler(self, collision_type_a: int, collision_type_b: int, 
                            handler: Callable) -> None:
        """Add a collision handler for two collision types."""
        self.collision_handlers[(collision_type_a, collision_type_b)] = handler
        
        # Set up pymunk collision handler
        pymunk_handler = self.space.add_collision_handler(collision_type_a, collision_type_b)
        pymunk_handler.begin = handler
        
    def query_point(self, point: Tuple[float, float], max_distance: float = 0) -> List[pymunk.PointQueryInfo]:
        """Query for shapes at a point."""
        return self.space.point_query(point, max_distance, pymunk.ShapeFilter())
        
    def query_segment(self, start: Tuple[float, float], end: Tuple[float, float]) -> List[pymunk.SegmentQueryInfo]:
        """Query for shapes along a line segment."""
        return self.space.segment_query(start, end, 0, pymunk.ShapeFilter())
        
    def render_debug(self, screen: pygame.Surface, offset: pygame.Vector2 = None) -> None:
        """Render debug visualization."""
        if not self.debug_draw:
            return
            
        if offset:
            # Translate the screen for camera offset
            translated_screen = screen.copy()
            translated_screen.scroll(-int(offset.x), -int(offset.y))
            draw_options = pymunk.pygame_util.DrawOptions(translated_screen)
        else:
            draw_options = pymunk.pygame_util.DrawOptions(screen)
            
        draw_options.flags = self.debug_options
        self.space.debug_draw(draw_options)


class PhysicsBodyComponent(Component):
    """
    Base component for physics bodies using Pymunk.
    """
    
    def __init__(self, body_type: int = pymunk.Body.DYNAMIC):
        super().__init__()
        self.body_type = body_type
        self.body: Optional[pymunk.Body] = None
        self.shapes: List[pymunk.Shape] = []
        self.physics_world = PhysicsWorld.get_instance()
        
        # Physics properties
        self.mass = 1.0
        self.moment = pymunk.moment_for_circle(1.0, 0, 10)  # Default moment
        
        # Material properties
        self.friction = 0.7
        self.elasticity = 0.0  # Bounciness (0-1)
        self.collision_type = 0
        self.group = 0
        self.category = 1
        self.mask = 0xFFFFFFFF
        
        # Transform synchronization
        self._physics_driven = True  # When True, physics updates transform
        self._last_physics_pos = None
        self._last_physics_angle = None
        
        # Callbacks
        self.on_collision_begin: Optional[Callable] = None
        self.on_collision_pre_solve: Optional[Callable] = None
        self.on_collision_post_solve: Optional[Callable] = None
        self.on_collision_separate: Optional[Callable] = None
        
    def create_body(self) -> None:
        """Create the physics body. Override in subclasses."""
        if self.body_type == pymunk.Body.STATIC:
            self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        elif self.body_type == pymunk.Body.KINEMATIC:
            self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        else:
            self.body = pymunk.Body(self.mass, self.moment)
            
        # Set initial position from actor transform (use world position)
        if self.actor:
            # Ensure transform is up to date before reading world position
            self.actor.update_transform()
            pos = self.actor.transform.world_position
            angle = self.actor.transform.world_rotation
            self.body.position = (pos.x, pos.y)
            self.body.angle = math.radians(angle)
            
            # Initialize tracking variables
            self._last_physics_pos = (pos.x, pos.y)
            self._last_physics_angle = angle
            
    def add_to_space(self) -> None:
        """Add body and shapes to physics space."""
        if self.body and self.body not in self.physics_world.space.bodies:
            self.physics_world.space.add(self.body)
            
        for shape in self.shapes:
            if shape not in self.physics_world.space.shapes:
                self.physics_world.space.add(shape)
                
    def remove_from_space(self) -> None:
        """Remove body and shapes from physics space."""
        for shape in self.shapes:
            if shape in self.physics_world.space.shapes:
                self.physics_world.space.remove(shape)
                
        if self.body and self.body in self.physics_world.space.bodies:
            self.physics_world.space.remove(self.body)
            
    def apply_force(self, force: Tuple[float, float], point: Optional[Tuple[float, float]] = None) -> None:
        """Apply force to the body."""
        if self.body:
            if point:
                self.body.apply_force_at_world_point(force, point)
            else:
                self.body.apply_force_at_local_point(force, (0, 0))
                
    def apply_impulse(self, impulse: Tuple[float, float], point: Optional[Tuple[float, float]] = None) -> None:
        """Apply impulse to the body."""
        if self.body:
            if point:
                self.body.apply_impulse_at_world_point(impulse, point)
            else:
                self.body.apply_impulse_at_local_point(impulse, (0, 0))
                
    def set_velocity(self, velocity: Tuple[float, float]) -> None:
        """Set body velocity."""
        if self.body:
            self.body.velocity = velocity
            
    def set_angular_velocity(self, angular_velocity: float) -> None:
        """Set body angular velocity."""
        if self.body:
            self.body.angular_velocity = angular_velocity
            
    def on_added(self, actor: Actor) -> None:
        """Called when component is added to an actor."""
        super().on_added(actor)
        self.create_body()
        self.add_to_space()
        
    def on_removed(self) -> None:
        """Called when component is removed from an actor."""
        self.remove_from_space()
        super().on_removed()
        
    def sync_transform_to_physics(self) -> None:
        """Sync actor transform to physics body (for manual transform changes)."""
        if not self.body or not self.actor:
            return
            
        # Update transform hierarchy first
        self.actor.update_transform()
        
        # Set physics body to match world transform
        world_pos = self.actor.transform.world_position
        world_rot = self.actor.transform.world_rotation
        
        self.body.position = (world_pos.x, world_pos.y)
        self.body.angle = math.radians(world_rot)
        
        # Update our tracking variables
        self._last_physics_pos = (world_pos.x, world_pos.y)
        self._last_physics_angle = world_rot
        
    def update(self, dt: float) -> None:
        """Update actor transform from physics body."""
        if not self.body or not self.actor or not self._physics_driven:
            return
            
        # Get current physics body state
        current_pos = self.body.position
        current_angle = math.degrees(self.body.angle)
        
        # Only update transform if physics body has moved
        if (self._last_physics_pos is None or 
            abs(current_pos[0] - self._last_physics_pos[0]) > 0.001 or
            abs(current_pos[1] - self._last_physics_pos[1]) > 0.001 or
            abs(current_angle - (self._last_physics_angle or 0)) > 0.01):
            
            # Handle world vs local position correctly based on parent hierarchy
            if self.actor.parent:
                # If we have a parent, we need to convert world position to local position
                parent_world_pos = self.actor.parent.transform.world_position
                parent_world_rot = self.actor.parent.transform.world_rotation
                parent_world_scale = self.actor.parent.transform.world_scale
                
                # Calculate local position relative to parent
                world_offset = pygame.Vector2(current_pos[0] - parent_world_pos.x, current_pos[1] - parent_world_pos.y)
                
                # Unrotate by parent rotation
                if parent_world_rot != 0:
                    world_offset = world_offset.rotate(-parent_world_rot)
                
                # Unscale by parent scale
                local_pos = pygame.Vector2(
                    world_offset.x / parent_world_scale.x if parent_world_scale.x != 0 else world_offset.x,
                    world_offset.y / parent_world_scale.y if parent_world_scale.y != 0 else world_offset.y
                )
                
                self.actor.transform.local_position = local_pos
                self.actor.transform.local_rotation = current_angle - parent_world_rot
            else:
                # No parent, world position equals local position
                self.actor.transform.local_position.x = current_pos[0]
                self.actor.transform.local_position.y = current_pos[1]
                self.actor.transform.local_rotation = current_angle
                
            # Mark transform as dirty to ensure world transform is recalculated
            self.actor.transform.mark_dirty()
            
            # Update tracking variables
            self._last_physics_pos = current_pos
            self._last_physics_angle = current_angle

    def set_physics_driven(self, enabled: bool) -> None:
        """Enable or disable physics-driven transform updates."""
        self._physics_driven = enabled
        
    def is_physics_driven(self) -> bool:
        """Check if physics is driving the transform updates."""
        return self._physics_driven
        
    def teleport_to(self, position: Tuple[float, float], angle: float = None) -> None:
        """Instantly move physics body to a new position and optionally rotation."""
        if not self.body:
            return
            
        # Set physics body position
        self.body.position = position
        if angle is not None:
            self.body.angle = math.radians(angle)
            
        # Update tracking variables
        self._last_physics_pos = position
        self._last_physics_angle = math.degrees(self.body.angle) if angle is not None else self._last_physics_angle
        
        # Clear velocities to prevent momentum from teleport
        if hasattr(self.body, 'velocity'):
            self.body.velocity = (0, 0)
        if hasattr(self.body, 'angular_velocity'):
            self.body.angular_velocity = 0


class RigidBodyComponent(PhysicsBodyComponent):
    """
    Rigid body component for dynamic physics objects.
    """
    
    def __init__(self, mass: float = 1.0, shape_type: str = "circle", size: Tuple[float, float] = (20, 20)):
        super().__init__(pymunk.Body.DYNAMIC)
        self.mass = mass
        self.shape_type = shape_type
        self.size = size
        
    def create_body(self) -> None:
        """Create the rigid body with specified shape."""
        # Calculate moment of inertia based on shape
        if self.shape_type == "circle":
            radius = self.size[0] / 2
            self.moment = pymunk.moment_for_circle(self.mass, 0, radius)
            self.body = pymunk.Body(self.mass, self.moment)
            
            # Create circle shape
            shape = pymunk.Circle(self.body, radius)
            
        elif self.shape_type == "box":
            width, height = self.size
            self.moment = pymunk.moment_for_box(self.mass, (width, height))
            self.body = pymunk.Body(self.mass, self.moment)
            
            # Create box shape
            vertices = [(-width/2, -height/2), (width/2, -height/2), 
                       (width/2, height/2), (-width/2, height/2)]
            shape = pymunk.Poly(self.body, vertices)
            
        elif self.shape_type == "polygon":
            # For custom polygon shapes (size should be a list of vertices)
            vertices = self.size if isinstance(self.size, list) else [(0, 0), (20, 0), (10, 20)]
            self.moment = pymunk.moment_for_poly(self.mass, vertices)
            self.body = pymunk.Body(self.mass, self.moment)
            
            shape = pymunk.Poly(self.body, vertices)
            
        else:
            raise ValueError(f"Unsupported shape type: {self.shape_type}")
            
        # Set shape properties
        shape.friction = self.friction
        shape.elasticity = self.elasticity
        shape.collision_type = self.collision_type
        
        self.shapes.append(shape)
        
        # Set initial position (use world position)
        if self.actor:
            # Ensure transform is up to date before reading world position
            self.actor.update_transform()
            pos = self.actor.transform.world_position
            angle = self.actor.transform.world_rotation
            self.body.position = (pos.x, pos.y)
            self.body.angle = math.radians(angle)
            
            # Initialize tracking variables
            self._last_physics_pos = (pos.x, pos.y)
            self._last_physics_angle = angle


class StaticBodyComponent(PhysicsBodyComponent):
    """
    Static body component for immovable objects like platforms and walls.
    """
    
    def __init__(self, shape_type: str = "box", size: Tuple[float, float] = (100, 20)):
        super().__init__(pymunk.Body.STATIC)
        self.shape_type = shape_type
        self.size = size
        
    def create_body(self) -> None:
        """Create static body with specified shape."""
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        
        if self.shape_type == "box":
            width, height = self.size
            vertices = [(-width/2, -height/2), (width/2, -height/2), 
                       (width/2, height/2), (-width/2, height/2)]
            shape = pymunk.Poly(self.body, vertices)
            
        elif self.shape_type == "circle":
            radius = self.size[0] / 2
            shape = pymunk.Circle(self.body, radius)
            
        elif self.shape_type == "segment":
            # For line segments (size should be start and end points)
            start, end = self.size if len(self.size) == 2 else ((0, 0), (100, 0))
            shape = pymunk.Segment(self.body, start, end, 1)  # 1 pixel thick
            
        else:
            raise ValueError(f"Unsupported shape type: {self.shape_type}")
            
        # Set shape properties
        shape.friction = self.friction
        shape.elasticity = self.elasticity
        shape.collision_type = self.collision_type
        
        self.shapes.append(shape)
        
        # Set position (use world position)
        if self.actor:
            # Ensure transform is up to date before reading world position
            self.actor.update_transform()
            pos = self.actor.transform.world_position
            angle = self.actor.transform.world_rotation
            self.body.position = (pos.x, pos.y)
            self.body.angle = math.radians(angle)
            
            # Initialize tracking variables
            self._last_physics_pos = (pos.x, pos.y)
            self._last_physics_angle = angle


class KinematicBodyComponent(PhysicsBodyComponent):
    """
    Kinematic body component for objects that move but don't respond to physics forces.
    Useful for moving platforms, doors, etc.
    """
    
    def __init__(self, shape_type: str = "box", size: Tuple[float, float] = (50, 20)):
        super().__init__(pymunk.Body.KINEMATIC)
        self.shape_type = shape_type
        self.size = size
        
    def create_body(self) -> None:
        """Create kinematic body."""
        self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        
        if self.shape_type == "box":
            width, height = self.size
            vertices = [(-width/2, -height/2), (width/2, -height/2), 
                       (width/2, height/2), (-width/2, height/2)]
            shape = pymunk.Poly(self.body, vertices)
            
        elif self.shape_type == "circle":
            radius = self.size[0] / 2
            shape = pymunk.Circle(self.body, radius)
            
        else:
            raise ValueError(f"Unsupported shape type: {self.shape_type}")
            
        # Set shape properties
        shape.friction = self.friction
        shape.elasticity = self.elasticity
        shape.collision_type = self.collision_type
        
        self.shapes.append(shape)
        
        # Set position (use world position)
        if self.actor:
            # Ensure transform is up to date before reading world position
            self.actor.update_transform()
            pos = self.actor.transform.world_position
            angle = self.actor.transform.world_rotation
            self.body.position = (pos.x, pos.y)
            self.body.angle = math.radians(angle)
            
            # Initialize tracking variables
            self._last_physics_pos = (pos.x, pos.y)
            self._last_physics_angle = angle
            
    def move_to(self, position: Tuple[float, float], duration: float = 0.0) -> None:
        """Move kinematic body to a position."""
        if self.body:
            if duration > 0:
                # Calculate velocity to reach position in given time
                current_pos = self.body.position
                distance = (position[0] - current_pos[0], position[1] - current_pos[1])
                velocity = (distance[0] / duration, distance[1] / duration)
                self.body.velocity = velocity
            else:
                # Instant movement
                self.body.position = position


class PhysicsConstraintComponent(Component):
    """
    Component for creating physics constraints between bodies.
    """
    
    def __init__(self, constraint_type: str = "pin_joint"):
        super().__init__()
        self.constraint_type = constraint_type
        self.constraint: Optional[pymunk.Constraint] = None
        self.physics_world = PhysicsWorld.get_instance()
        
        # Constraint properties
        self.other_body: Optional[pymunk.Body] = None
        self.anchor_a: Tuple[float, float] = (0, 0)
        self.anchor_b: Tuple[float, float] = (0, 0)
        self.max_force = float('inf')
        self.error_bias = 0.0
        
    def create_constraint(self, body_a: pymunk.Body, body_b: pymunk.Body) -> None:
        """Create the constraint between two bodies."""
        if self.constraint_type == "pin_joint":
            self.constraint = pymunk.PinJoint(body_a, body_b, self.anchor_a, self.anchor_b)
            
        elif self.constraint_type == "slide_joint":
            min_dist = getattr(self, 'min_distance', 0)
            max_dist = getattr(self, 'max_distance', 100)
            self.constraint = pymunk.SlideJoint(body_a, body_b, self.anchor_a, self.anchor_b, min_dist, max_dist)
            
        elif self.constraint_type == "spring":
            rest_length = getattr(self, 'rest_length', 50)
            stiffness = getattr(self, 'stiffness', 100)
            damping = getattr(self, 'damping', 5)
            self.constraint = pymunk.DampedSpring(body_a, body_b, self.anchor_a, self.anchor_b, 
                                                rest_length, stiffness, damping)
                                                
        elif self.constraint_type == "rotary_limit":
            min_angle = getattr(self, 'min_angle', -1.57)  # -90 degrees
            max_angle = getattr(self, 'max_angle', 1.57)   # 90 degrees
            self.constraint = pymunk.RotaryLimitJoint(body_a, body_b, min_angle, max_angle)
            
        else:
            raise ValueError(f"Unsupported constraint type: {self.constraint_type}")
            
        # Set constraint properties
        self.constraint.max_force = self.max_force
        self.constraint.error_bias = self.error_bias
        
        # Add to physics space
        self.physics_world.space.add(self.constraint)
        
    def set_other_actor(self, other_actor: Actor) -> None:
        """Set the other actor to constrain to."""
        physics_comp = other_actor.get_component(PhysicsBodyComponent)
        if physics_comp and physics_comp.body:
            self.other_body = physics_comp.body
            
            # Create constraint if we have our own body
            if self.actor:
                our_physics = self.actor.get_component(PhysicsBodyComponent)
                if our_physics and our_physics.body:
                    self.create_constraint(our_physics.body, self.other_body)
                    
    def on_added(self, actor: Actor) -> None:
        """Called when component is added to an actor."""
        super().on_added(actor)
        
        # If we already have an other_body, create the constraint
        if self.other_body:
            our_physics = self.actor.get_component(PhysicsBodyComponent)
            if our_physics and our_physics.body:
                self.create_constraint(our_physics.body, self.other_body)
                
    def on_removed(self) -> None:
        """Called when component is removed from an actor."""
        if self.constraint and self.constraint in self.physics_world.space.constraints:
            self.physics_world.space.remove(self.constraint)
        super().on_removed()
        
    def update(self, dt: float) -> None:
        """Update constraint (usually no action needed)."""
        pass


class PhysicsSystem:
    """
    System for managing physics updates and debug rendering.
    """
    
    def __init__(self):
        self.physics_world = PhysicsWorld.get_instance()
        self.accumulator = 0.0
        self.fixed_timestep = 1.0 / 60.0  # 60 FPS physics
        
    def update(self, dt: float) -> None:
        """Update physics with fixed timestep."""
        self.accumulator += dt
        
        while self.accumulator >= self.fixed_timestep:
            self.physics_world.step(self.fixed_timestep)
            self.accumulator -= self.fixed_timestep
            
    def render_debug(self, screen: pygame.Surface, camera_offset: pygame.Vector2 = None) -> None:
        """Render physics debug information."""
        self.physics_world.render_debug(screen, camera_offset)
        
    def set_gravity(self, gravity: Tuple[float, float]) -> None:
        """Set world gravity."""
        self.physics_world.set_gravity(gravity)
        
    def query_point(self, point: Tuple[float, float]) -> List[pymunk.PointQueryInfo]:
        """Query for physics bodies at a point."""
        return self.physics_world.query_point(point)
        
    def query_ray(self, start: Tuple[float, float], end: Tuple[float, float]) -> List[pymunk.SegmentQueryInfo]:
        """Query for physics bodies along a ray."""
        return self.physics_world.query_segment(start, end)

    def update_physics_components(self, scene) -> None:
        """Update all physics components' transforms after physics simulation."""
        if not scene:
            return
            
        # Find all actors with physics components and update their transforms
        for actor in scene.actors:
            physics_comp = actor.get_component(PhysicsBodyComponent)
            if physics_comp and physics_comp.is_physics_driven():
                # Update the component's transform from physics
                physics_comp.update(self.fixed_timestep)
