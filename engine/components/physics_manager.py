"""
Physics manager for integrating physics world with the game engine.
Manages physics updates, world creation, and physics system lifecycle.
"""

import pygame
from typing import Optional, Tuple, Dict, Any
from .physics_world import PhysicsWorld
from .physics_component import PhysicsComponent, RigidBodyComponent, TriggerComponent


class PhysicsManager:
    """
    Manages the physics system integration with the game engine.
    Handles physics world creation, updates, and cleanup.
    """
    
    def __init__(self, gravity: Tuple[float, float] = (0, 981)):
        self.world: Optional[PhysicsWorld] = None
        self.gravity = gravity
        self.enabled = True
        self.debug_draw = False
        
        # Fixed timestep settings
        self.fixed_timestep = 1.0 / 60.0  # 60 FPS physics
        self.accumulator = 0.0
        self.max_steps = 5  # Maximum physics steps per frame
        
        # Performance tracking
        self.physics_time = 0.0
        self.physics_fps = 60.0
        
    def initialize(self):
        """Initialize the physics world."""
        if not self.world:
            self.world = PhysicsWorld(self.gravity)
            self.world.setup_default_collision_handlers()
            
    def shutdown(self):
        """Shutdown the physics system."""
        if self.world:
            self.world.clear()
            self.world = None
            
    def update(self, dt: float):
        """Update physics with fixed timestep."""
        if not self.enabled or not self.world:
            return
            
        import time
        start_time = time.time()
        
        # Accumulate time
        self.accumulator += dt
        
        # Perform fixed timestep updates
        steps = 0
        while self.accumulator >= self.fixed_timestep and steps < self.max_steps:
            self.world.step(self.fixed_timestep)
            self.accumulator -= self.fixed_timestep
            steps += 1
            
        # Calculate physics performance
        self.physics_time = time.time() - start_time
        if self.fixed_timestep > 0:
            self.physics_fps = 1.0 / max(self.physics_time, self.fixed_timestep)
            
    def render_debug(self, surface: pygame.Surface):
        """Render physics debug information."""
        if self.debug_draw and self.world:
            self.world.debug_draw(surface)
            
    def set_gravity(self, gravity: Tuple[float, float]):
        """Set world gravity."""
        self.gravity = gravity
        if self.world:
            self.world.set_gravity(gravity)
            
    def set_debug_draw(self, surface: pygame.Surface, enable: bool = True):
        """Enable/disable debug drawing."""
        self.debug_draw = enable
        if self.world:
            self.world.set_debug_draw(surface, enable)
            
    def toggle_debug_draw(self, surface: pygame.Surface):
        """Toggle debug drawing on/off."""
        self.set_debug_draw(surface, not self.debug_draw)
        
    def query_point(self, point: pygame.Vector2, max_distance: float = 0.0):
        """Query physics objects at a point."""
        if self.world:
            return self.world.query_point_nearest((point.x, point.y), max_distance)
        return None
        
    def query_point_all(self, point: pygame.Vector2, max_distance: float = 0.0):
        """Query all physics objects at a point."""
        if self.world:
            return self.world.query_point_all((point.x, point.y), max_distance)
        return []
        
    def query_area(self, rect: pygame.Rect):
        """Query physics objects in a rectangular area."""
        if self.world:
            bb = (rect.left, rect.bottom, rect.right, rect.top)
            return self.world.query_bb(bb)
        return []
        
    def raycast(self, start: pygame.Vector2, end: pygame.Vector2):
        """Perform a raycast."""
        if self.world:
            return self.world.raycast((start.x, start.y), (end.x, end.y))
        return None
        
    def raycast_all(self, start: pygame.Vector2, end: pygame.Vector2):
        """Perform a raycast returning all hits."""
        if self.world:
            return self.world.raycast_all((start.x, start.y), (end.x, end.y))
        return []
        
    def add_collision_handler(self, collision_type_a: int, collision_type_b: int, **kwargs):
        """Add collision handler between two collision types."""
        if self.world:
            self.world.add_collision_handler(collision_type_a, collision_type_b, **kwargs)
            
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get physics performance statistics."""
        stats = {
            'enabled': self.enabled,
            'physics_time': self.physics_time,
            'physics_fps': self.physics_fps,
            'fixed_timestep': self.fixed_timestep,
            'accumulator': self.accumulator,
            'debug_draw': self.debug_draw
        }
        
        if self.world:
            stats.update(self.world.get_performance_stats())
            
        return stats


# Convenience functions for creating physics components
def create_box_rigidbody(size: pygame.Vector2, mass: float = 1.0, 
                        body_type: str = "dynamic") -> RigidBodyComponent:
    """Create a box-shaped rigid body component."""
    from .physics_component import PhysicsBodyType, PhysicsShape
    
    body_type_enum = PhysicsBodyType.DYNAMIC
    if body_type == "static":
        body_type_enum = PhysicsBodyType.STATIC
    elif body_type == "kinematic":
        body_type_enum = PhysicsBodyType.KINEMATIC
        
    return RigidBodyComponent(
        shape_type=PhysicsShape.BOX,
        size=size,
        body_type=body_type_enum,
        mass=mass
    )


def create_circle_rigidbody(radius: float, mass: float = 1.0, 
                           body_type: str = "dynamic") -> RigidBodyComponent:
    """Create a circle-shaped rigid body component."""
    from .physics_component import PhysicsBodyType, PhysicsShape
    
    body_type_enum = PhysicsBodyType.DYNAMIC
    if body_type == "static":
        body_type_enum = PhysicsBodyType.STATIC
    elif body_type == "kinematic":
        body_type_enum = PhysicsBodyType.KINEMATIC
        
    return RigidBodyComponent(
        shape_type=PhysicsShape.CIRCLE,
        radius=radius,
        body_type=body_type_enum,
        mass=mass
    )


def create_box_trigger(size: pygame.Vector2) -> TriggerComponent:
    """Create a box-shaped trigger component."""
    from .physics_component import PhysicsShape
    
    return TriggerComponent(
        shape_type=PhysicsShape.BOX,
        size=size
    )


def create_circle_trigger(radius: float) -> TriggerComponent:
    """Create a circle-shaped trigger component."""
    from .physics_component import PhysicsShape
    
    return TriggerComponent(
        shape_type=PhysicsShape.CIRCLE,
        radius=radius
    )
