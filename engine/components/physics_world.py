"""
Physics world manager using pymunk.
Handles physics simulation, collision detection, and world setup.
"""

import pygame
import pymunk
import pymunk.pygame_util
from typing import Dict, Set, Callable, Optional, Tuple, Any
from ..core.actor import Component


class PhysicsWorld:
    """
    Manages the pymunk physics world and handles collision detection.
    """
    
    def __init__(self, gravity: Tuple[float, float] = (0, 981)):
        # Create pymunk space
        self.space = pymunk.Space()
        self.space.gravity = gravity
        
        # Physics settings
        self.iterations = 10
        self.damping = 0.999
        self.sleep_time_threshold = 0.5
        self.space.sleep_time_threshold = self.sleep_time_threshold
        
        # Collision handlers
        self.collision_handlers: Dict[Tuple[int, int], Dict[str, Callable]] = {}
        
        # Debug rendering
        self.debug_draw_options = None
        self.show_debug = False
        
        # Physics objects tracking
        self.physics_objects: Set[Component] = set()
        
        # Performance tracking
        self.last_step_time = 0.0
        
        # Manual collision tracking for pymunk 7.0+
        self.previous_collisions: Set[Tuple[int, int]] = set()
        self.current_collisions: Set[Tuple[int, int]] = set()
        
    def set_gravity(self, gravity: Tuple[float, float]):
        """Set world gravity."""
        self.space.gravity = gravity
        
    def add_physics_object(self, physics_component: Component):
        """Add a physics object to the world."""
        if hasattr(physics_component, 'body') and hasattr(physics_component, 'shape'):
            if physics_component.body and physics_component.shape:
                self.space.add(physics_component.body, physics_component.shape)
                self.physics_objects.add(physics_component)
                
    def remove_physics_object(self, physics_component: Component):
        """Remove a physics object from the world."""
        if physics_component in self.physics_objects:
            if hasattr(physics_component, 'body') and hasattr(physics_component, 'shape'):
                if physics_component.body and physics_component.shape:
                    try:
                        self.space.remove(physics_component.body, physics_component.shape)
                    except:
                        pass  # Object might already be removed
            self.physics_objects.discard(physics_component)
            
    def add_collision_handler(self, collision_type_a: int, collision_type_b: int,
                            begin: Optional[Callable] = None,
                            pre_solve: Optional[Callable] = None,
                            post_solve: Optional[Callable] = None,
                            separate: Optional[Callable] = None):
        """Add collision handlers between two collision types."""
        # Note: pymunk 7.0+ uses a different collision system
        # We'll use the on_collision callback for basic collision detection
        if hasattr(self.space, 'add_collision_handler'):
            # Older pymunk API
            handler = self.space.add_collision_handler(collision_type_a, collision_type_b)
            if begin:
                handler.begin = begin
            if pre_solve:
                handler.pre_solve = pre_solve
            if post_solve:
                handler.post_solve = post_solve
            if separate:
                handler.separate = separate
        else:
            # New pymunk 7.0+ API - use on_collision callback
            # Store callbacks for manual handling
            pass
            
        # Store for reference
        key = (min(collision_type_a, collision_type_b), max(collision_type_a, collision_type_b))
        self.collision_handlers[key] = {
            'begin': begin,
            'pre_solve': pre_solve,
            'post_solve': post_solve,
            'separate': separate
        }
        
    def setup_default_collision_handlers(self):
        """Setup default collision handlers for common physics interactions."""
        
        def default_collision_begin(arbiter, space, data):
            """Default collision begin handler."""
            shape_a, shape_b = arbiter.shapes
            
            # Get components
            component_a = getattr(shape_a, 'component', None)
            component_b = getattr(shape_b, 'component', None)
            
            if component_a and component_b:
                # Handle trigger components
                from .physics_component import TriggerComponent
                if isinstance(component_a, TriggerComponent):
                    component_a.handle_trigger_enter(component_b)
                if isinstance(component_b, TriggerComponent):
                    component_b.handle_trigger_enter(component_a)
                    
                # Call component collision callbacks
                if hasattr(component_a, 'on_collision_begin') and component_a.on_collision_begin:
                    component_a.on_collision_begin(component_a, component_b, arbiter)
                if hasattr(component_b, 'on_collision_begin') and component_b.on_collision_begin:
                    component_b.on_collision_begin(component_b, component_a, arbiter)
                    
            return True
            
        def default_collision_separate(arbiter, space, data):
            """Default collision separate handler."""
            shape_a, shape_b = arbiter.shapes
            
            # Get components
            component_a = getattr(shape_a, 'component', None)
            component_b = getattr(shape_b, 'component', None)
            
            if component_a and component_b:
                # Handle trigger components
                from .physics_component import TriggerComponent
                if isinstance(component_a, TriggerComponent):
                    component_a.handle_trigger_exit(component_b)
                if isinstance(component_b, TriggerComponent):
                    component_b.handle_trigger_exit(component_a)
                    
                # Call component collision callbacks
                if hasattr(component_a, 'on_collision_end') and component_a.on_collision_end:
                    component_a.on_collision_end(component_a, component_b, arbiter)
                if hasattr(component_b, 'on_collision_end') and component_b.on_collision_end:
                    component_b.on_collision_end(component_b, component_a, arbiter)
                    
            return True
            
        # Add default handler for all collision types (0 is default)
        self.add_collision_handler(
            0, 0,
            begin=default_collision_begin,
            separate=default_collision_separate
        )
        
    def step(self, dt: float):
        """Step the physics simulation."""
        import time
        start_time = time.time()
        
        # Clamp dt to prevent physics explosion
        dt = min(dt, 1.0 / 30.0)  # Max 30 FPS minimum
        
        # Step the simulation
        self.space.step(dt)
        
        self.last_step_time = time.time() - start_time
        
    def query_point_nearest(self, point: Tuple[float, float], max_distance: float = 0.0) -> Optional[Any]:
        """Query the nearest shape to a point."""
        query = self.space.point_query_nearest(point, max_distance, pymunk.ShapeFilter())
        return query.shape.component if query and hasattr(query.shape, 'component') else None
        
    def query_point_all(self, point: Tuple[float, float], max_distance: float = 0.0) -> list:
        """Query all shapes at a point."""
        queries = self.space.point_query(point, max_distance, pymunk.ShapeFilter())
        return [q.shape.component for q in queries if hasattr(q.shape, 'component')]
        
    def query_bb(self, bb: Tuple[float, float, float, float]) -> list:
        """Query all shapes in a bounding box (left, bottom, right, top)."""
        bbox = pymunk.BB(bb[0], bb[1], bb[2], bb[3])
        queries = self.space.bb_query(bbox, pymunk.ShapeFilter())
        return [shape.component for shape in queries if hasattr(shape, 'component')]
        
    def raycast(self, start: Tuple[float, float], end: Tuple[float, float]) -> Optional[Dict[str, Any]]:
        """Perform a raycast and return the first hit."""
        query = self.space.segment_query_first(start, end, 0, pymunk.ShapeFilter())
        if query:
            return {
                'component': getattr(query.shape, 'component', None),
                'point': query.point,
                'normal': query.normal,
                'alpha': query.alpha,
                'shape': query.shape
            }
        return None
        
    def raycast_all(self, start: Tuple[float, float], end: Tuple[float, float]) -> list:
        """Perform a raycast and return all hits."""
        queries = self.space.segment_query(start, end, 0, pymunk.ShapeFilter())
        results = []
        for query in queries:
            results.append({
                'component': getattr(query.shape, 'component', None),
                'point': query.point,
                'normal': query.normal,
                'alpha': query.alpha,
                'shape': query.shape
            })
        return results
        
    def set_debug_draw(self, surface: pygame.Surface, enable: bool = True):
        """Setup debug drawing."""
        self.show_debug = enable
        if enable:
            self.debug_draw_options = pymunk.pygame_util.DrawOptions(surface)
            self.debug_draw_options.flags = (
                pymunk.pygame_util.DrawOptions.DRAW_SHAPES |
                pymunk.pygame_util.DrawOptions.DRAW_COLLISION_POINTS |
                pymunk.pygame_util.DrawOptions.DRAW_CONSTRAINTS
            )
        else:
            self.debug_draw_options = None
            
    def debug_draw(self, surface: pygame.Surface):
        """Draw debug information."""
        if self.show_debug and self.debug_draw_options:
            self.debug_draw_options.surface = surface
            self.space.debug_draw(self.debug_draw_options)
            
    def clear(self):
        """Clear all objects from the physics world."""
        # Remove all physics objects
        for obj in list(self.physics_objects):
            self.remove_physics_object(obj)
            
        # Clear collision handlers
        self.collision_handlers.clear()
        
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get physics performance statistics."""
        return {
            'last_step_time': self.last_step_time,
            'object_count': len(self.physics_objects),
            'body_count': len(self.space.bodies),
            'shape_count': len(self.space.shapes),
            'constraint_count': len(self.space.constraints),
            'iterations': self.iterations,
            'gravity': self.space.gravity
        }


class PhysicsUtils:
    """
    Utility functions for physics calculations and conversions.
    """
    
    @staticmethod
    def pygame_to_pymunk(pos: pygame.Vector2) -> Tuple[float, float]:
        """Convert pygame coordinates to pymunk coordinates."""
        return (pos.x, pos.y)
        
    @staticmethod
    def pymunk_to_pygame(pos: Tuple[float, float]) -> pygame.Vector2:
        """Convert pymunk coordinates to pygame coordinates."""
        return pygame.Vector2(pos[0], pos[1])
        
    @staticmethod
    def degrees_to_radians(degrees: float) -> float:
        """Convert degrees to radians."""
        import math
        return math.radians(degrees)
        
    @staticmethod
    def radians_to_degrees(radians: float) -> float:
        """Convert radians to degrees."""
        import math
        return math.degrees(radians)
        
    @staticmethod
    def calculate_impulse_for_velocity(mass: float, current_velocity: pygame.Vector2, 
                                     target_velocity: pygame.Vector2) -> pygame.Vector2:
        """Calculate the impulse needed to achieve a target velocity."""
        velocity_change = target_velocity - current_velocity
        return velocity_change * mass
        
    @staticmethod
    def calculate_force_for_acceleration(mass: float, acceleration: pygame.Vector2) -> pygame.Vector2:
        """Calculate the force needed for a given acceleration."""
        return acceleration * mass
        
    @staticmethod
    def is_point_in_circle(point: pygame.Vector2, center: pygame.Vector2, radius: float) -> bool:
        """Check if a point is inside a circle."""
        return (point - center).length() <= radius
        
    @staticmethod
    def is_point_in_rect(point: pygame.Vector2, rect_center: pygame.Vector2, size: pygame.Vector2) -> bool:
        """Check if a point is inside a rectangle."""
        half_size = size * 0.5
        return (abs(point.x - rect_center.x) <= half_size.x and 
                abs(point.y - rect_center.y) <= half_size.y)
