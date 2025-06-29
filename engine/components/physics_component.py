"""
Physics components using pymunk for the game engine.
Provides rigid body physics, collision detection, and trigger zones.
"""

import pygame
import pymunk
import pymunk.pygame_util
from typing import Optional, Tuple, Callable, Any, List
from enum import Enum
from ..core.actor import Component


class PhysicsBodyType(Enum):
    """Types of physics bodies."""
    STATIC = "static"  # Immovable (walls, floors)
    KINEMATIC = "kinematic"  # Movable but not affected by forces (platforms)
    DYNAMIC = "dynamic"  # Fully simulated (players, objects)


class PhysicsShape(Enum):
    """Types of physics shapes."""
    CIRCLE = "circle"
    BOX = "box"
    POLYGON = "polygon"


class PhysicsComponent(Component):
    """
    Base physics component that manages a pymunk body and shape.
    Synchronizes with the actor's transform.
    """
    
    def __init__(self, body_type: PhysicsBodyType = PhysicsBodyType.DYNAMIC, 
                 mass: float = 1.0, moment: Optional[float] = None):
        super().__init__()
        self.body_type = body_type
        self.mass = mass
        self.moment = moment
        
        # Pymunk objects
        self.body: Optional[pymunk.Body] = None
        self.shape: Optional[pymunk.Shape] = None
        
        # Physics properties
        self.friction = 0.7
        self.elasticity = 0.2
        self.collision_type = 0
        
        # Constraints
        self.lock_rotation = False
        self.lock_x_axis = False
        self.lock_y_axis = False
        
        # Callbacks
        self.on_collision_begin: Optional[Callable] = None
        self.on_collision_end: Optional[Callable] = None
        
        # Network sync
        self.sync_to_network = True
        self.last_sync_position = pygame.Vector2(0, 0)
        self.last_sync_velocity = pygame.Vector2(0, 0)
        self.last_sync_angle = 0.0
        self.sync_threshold = 0.1  # Units to move before syncing
        
    def on_added(self, actor) -> None:
        """Called when component is added to an actor."""
        super().on_added(actor)
        # Try to initialize physics immediately if possible
        self._try_initialize_physics()
        
    def _try_initialize_physics(self):
        """Try to initialize physics if a physics world is available."""
        if self.body:  # Already initialized
            return
            
        physics_world = self._find_physics_world()
        if physics_world:
            self._create_physics_body(physics_world)
            
    def _find_physics_world(self):
        """Find the physics world for this component."""
        if not self.actor:
            return None
            
        # Try to get game and current scene
        game = getattr(self.actor, 'game', None) or self.game
        if not game:
            return None
            
        # Try current scene first
        current_scene = getattr(game, 'current_scene', None)
        if current_scene and hasattr(current_scene, 'physics_world') and current_scene.physics_world:
            return current_scene.physics_world
            
        # Search through all scenes for this actor
        if hasattr(game, 'scenes'):
            for scene in game.scenes.values():
                if (hasattr(scene, 'actors') and self.actor in scene.actors and 
                    hasattr(scene, 'physics_world') and scene.physics_world):
                    return scene.physics_world
                    
        return None
        
    def on_removed(self) -> None:
        """Called when component is removed from an actor."""
        if self.shape:
            physics_world = self._find_physics_world()
            if physics_world:
                physics_world.remove_physics_object(self)
        super().on_removed()
        
    def initialize_physics(self, physics_world):
        """Initialize the physics body with the given physics world."""
        if not self.body and physics_world:
            self._create_physics_body(physics_world)
        
    def _find_physics_world(self):
        """Find the physics world for this component's actor."""
        if not self.actor:
            return None
            
        # Try to get the game instance
        try:
            from .. import Game
            if Game.has_instance():
                game = Game.get_instance()
                # Look through all scenes to find the one containing this actor
                for scene in game.scenes.values():
                    if self.actor in scene.actors and scene.physics_world:
                        return scene.physics_world
                # If we can't find the scene, check if there's a current scene
                if game.current_scene and game.current_scene.physics_world:
                    return game.current_scene.physics_world
        except ImportError:
            pass
            
        return None
        
    def _create_physics_body(self, physics_world):
        """Create the pymunk body. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _create_physics_body")
        
    def apply_force(self, force: pygame.Vector2, point: Optional[pygame.Vector2] = None):
        """Apply a force to the body."""
        if self.body and self.body_type == PhysicsBodyType.DYNAMIC:
            if point:
                self.body.apply_force_at_world_point((force.x, force.y), (point.x, point.y))
            else:
                self.body.apply_force_at_local_point((force.x, force.y), (0, 0))
                
    def apply_impulse(self, impulse: pygame.Vector2, point: Optional[pygame.Vector2] = None):
        """Apply an impulse to the body."""
        if self.body and self.body_type == PhysicsBodyType.DYNAMIC:
            if point:
                self.body.apply_impulse_at_world_point((impulse.x, impulse.y), (point.x, point.y))
            else:
                self.body.apply_impulse_at_local_point((impulse.x, impulse.y), (0, 0))
                
    def set_velocity(self, velocity: pygame.Vector2):
        """Set the body's velocity."""
        if self.body:
            self.body.velocity = (velocity.x, velocity.y)
            
    def get_velocity(self) -> pygame.Vector2:
        """Get the body's velocity."""
        if self.body:
            return pygame.Vector2(self.body.velocity)
        return pygame.Vector2(0, 0)
        
    def set_angular_velocity(self, angular_velocity: float):
        """Set the body's angular velocity."""
        if self.body:
            self.body.angular_velocity = angular_velocity
            
    def get_angular_velocity(self) -> float:
        """Get the body's angular velocity."""
        if self.body:
            return self.body.angular_velocity
        return 0.0
        
    def update(self, dt: float) -> None:
        """Update the actor's transform from the physics body."""
        if not self.body:
            return
            
        # Apply constraints
        if self.lock_rotation:
            self.body.angular_velocity = 0
            self.body.angle = 0
            
        if self.lock_x_axis:
            vel = self.body.velocity
            self.body.velocity = (0, vel[1])
            
        if self.lock_y_axis:
            vel = self.body.velocity
            self.body.velocity = (vel[0], 0)
            
        # Sync physics to transform
        if self.actor:
            self.actor.transform.world_position.x = self.body.position.x
            self.actor.transform.world_position.y = self.body.position.y
            self.actor.transform.world_rotation = self.body.angle
            
    def fixed_update(self, dt: float) -> None:
        """Fixed update for physics synchronization."""
        if self.body and self.actor:
            # Check if we need to sync to network
            if self.sync_to_network and self._should_sync_to_network():
                self._update_network_sync_data()
                
    def _should_sync_to_network(self) -> bool:
        """Check if the body has moved enough to warrant network sync."""
        pos_diff = pygame.Vector2(self.body.position) - self.last_sync_position
        vel_diff = pygame.Vector2(self.body.velocity) - self.last_sync_velocity
        angle_diff = abs(self.body.angle - self.last_sync_angle)
        
        return (pos_diff.length() > self.sync_threshold or 
                vel_diff.length() > self.sync_threshold or 
                angle_diff > 0.1)
                
    def _update_network_sync_data(self):
        """Update the last synced network data."""
        self.last_sync_position = pygame.Vector2(self.body.position)
        self.last_sync_velocity = pygame.Vector2(self.body.velocity)
        self.last_sync_angle = self.body.angle
        
    def serialize_for_network(self) -> dict:
        """Serialize physics data for network transmission."""
        if not self.body:
            return {}
            
        return {
            'position': {'x': self.body.position.x, 'y': self.body.position.y},
            'velocity': {'x': self.body.velocity.x, 'y': self.body.velocity.y},
            'angle': self.body.angle,
            'angular_velocity': self.body.angular_velocity,
            'body_type': self.body_type.value,
            'enabled': self.enabled
        }
        
    def deserialize_from_network(self, data: dict) -> None:
        """Deserialize physics data from network."""
        if not self.body:
            return
            
        if 'position' in data:
            pos = data['position']
            self.body.position = (pos['x'], pos['y'])
            
        if 'velocity' in data:
            vel = data['velocity']
            self.body.velocity = (vel['x'], vel['y'])
            
        if 'angle' in data:
            self.body.angle = data['angle']
            
        if 'angular_velocity' in data:
            self.body.angular_velocity = data['angular_velocity']
            
        if 'enabled' in data:
            self.enabled = data['enabled']


class RigidBodyComponent(PhysicsComponent):
    """
    Rigid body physics component with customizable shape.
    """
    
    def __init__(self, shape_type: PhysicsShape = PhysicsShape.BOX,
                 size: pygame.Vector2 = None, radius: float = None,
                 vertices: List[Tuple[float, float]] = None,
                 body_type: PhysicsBodyType = PhysicsBodyType.DYNAMIC,
                 mass: float = 1.0, moment: Optional[float] = None):
        super().__init__(body_type, mass, moment)
        self.shape_type = shape_type
        self.size = size or pygame.Vector2(32, 32)
        self.radius = radius or 16.0
        self.vertices = vertices or []
        
    def _create_physics_body(self, physics_world):
        """Create the pymunk body and shape."""
        if not physics_world:
            return
            
        # Create body
        if self.body_type == PhysicsBodyType.STATIC:
            self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        elif self.body_type == PhysicsBodyType.KINEMATIC:
            self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        else:  # DYNAMIC
            if self.moment is None:
                if self.shape_type == PhysicsShape.CIRCLE:
                    self.moment = pymunk.moment_for_circle(self.mass, 0, self.radius)
                elif self.shape_type == PhysicsShape.BOX:
                    self.moment = pymunk.moment_for_box(self.mass, (self.size.x, self.size.y))
                else:  # POLYGON
                    self.moment = pymunk.moment_for_poly(self.mass, self.vertices)
            self.body = pymunk.Body(self.mass, self.moment)
            
        # Set initial position from actor transform
        if self.actor:
            # Make sure transform is updated
            self.actor.update_transform()
            self.body.position = (self.actor.transform.world_position.x, 
                                self.actor.transform.world_position.y)
            self.body.angle = self.actor.transform.world_rotation
            
        # Create shape
        if self.shape_type == PhysicsShape.CIRCLE:
            self.shape = pymunk.Circle(self.body, self.radius)
        elif self.shape_type == PhysicsShape.BOX:
            half_width = self.size.x / 2
            half_height = self.size.y / 2
            vertices = [(-half_width, -half_height), (half_width, -half_height),
                       (half_width, half_height), (-half_width, half_height)]
            self.shape = pymunk.Poly(self.body, vertices)
        else:  # POLYGON
            self.shape = pymunk.Poly(self.body, self.vertices)
            
        # Set shape properties
        self.shape.friction = self.friction
        self.shape.elasticity = self.elasticity
        self.shape.collision_type = self.collision_type
        
        # Store reference to this component
        self.shape.component = self
        self.body.component = self
        
        # Add to physics world
        physics_world.add_physics_object(self)


class TriggerComponent(PhysicsComponent):
    """
    Trigger zone component for detecting collisions without physical response.
    """
    
    def __init__(self, shape_type: PhysicsShape = PhysicsShape.BOX,
                 size: pygame.Vector2 = None, radius: float = None,
                 vertices: List[Tuple[float, float]] = None):
        super().__init__(PhysicsBodyType.KINEMATIC, 0, 0)
        self.shape_type = shape_type
        self.size = size or pygame.Vector2(32, 32)
        self.radius = radius or 16.0
        self.vertices = vertices or []
        
        # Trigger-specific callbacks
        self.on_trigger_enter: Optional[Callable] = None
        self.on_trigger_exit: Optional[Callable] = None
        self.on_trigger_stay: Optional[Callable] = None
        
        # Track objects in trigger
        self.objects_in_trigger: set = set()
        
    def _create_physics_body(self, physics_world):
        """Create the pymunk body and shape for trigger."""
        if not physics_world:
            return
            
        # Create kinematic body
        self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        
        # Set initial position from actor transform
        if self.actor:
            # Make sure transform is updated
            self.actor.update_transform()
            self.body.position = (self.actor.transform.world_position.x, 
                                self.actor.transform.world_position.y)
            
        # Create shape
        if self.shape_type == PhysicsShape.CIRCLE:
            self.shape = pymunk.Circle(self.body, self.radius)
        elif self.shape_type == PhysicsShape.BOX:
            half_width = self.size.x / 2
            half_height = self.size.y / 2
            vertices = [(-half_width, -half_height), (half_width, -half_height),
                       (half_width, half_height), (-half_width, half_height)]
            self.shape = pymunk.Poly(self.body, vertices)
        else:  # POLYGON
            self.shape = pymunk.Poly(self.body, self.vertices)
            
        # Make it a sensor (no collision response)
        self.shape.sensor = True
        self.shape.collision_type = self.collision_type
        
        # Store reference to this component
        self.shape.component = self
        self.body.component = self
        
        # Add to physics world
        physics_world.add_physics_object(self)
        
    def handle_trigger_enter(self, other_component):
        """Handle when an object enters the trigger."""
        if other_component not in self.objects_in_trigger:
            self.objects_in_trigger.add(other_component)
            if self.on_trigger_enter:
                self.on_trigger_enter(self, other_component)
                
    def handle_trigger_exit(self, other_component):
        """Handle when an object exits the trigger."""
        if other_component in self.objects_in_trigger:
            self.objects_in_trigger.remove(other_component)
            if self.on_trigger_exit:
                self.on_trigger_exit(self, other_component)
                
    def update(self, dt: float) -> None:
        """Update trigger position."""
        if self.body and self.actor:
            # Update position from actor transform
            self.body.position = (self.actor.transform.world_position.x,
                                self.actor.transform.world_position.y)
            
            # Call stay callbacks for objects in trigger
            if self.on_trigger_stay:
                for obj in self.objects_in_trigger.copy():
                    self.on_trigger_stay(self, obj)
