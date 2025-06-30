import pygame
from typing import Optional, Set, Callable, Any
from enum import Enum
from engine.component.component import Component

class ColliderType(Enum):
    """Types of colliders."""
    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    POINT = "point"

class ColliderComponent(Component):
    """
    Component for collision detection and physics interactions.
    Provides basic collision shapes and event callbacks.
    """
    
    # Exclude runtime collision state from serialization
    __serialization_exclude__ = ["_current_collisions", "on_collision_enter", "on_collision_stay", "on_collision_exit"]
    
    def __init__(self, collider_type: ColliderType = ColliderType.RECTANGLE, 
                 width: float = 32, height: float = 32, radius: float = 16):
        super().__init__()
        
        # Collider properties
        self.collider_type: ColliderType = collider_type
        self.width: float = width
        self.height: float = height
        self.radius: float = radius
        
        # Collision settings
        self.is_trigger: bool = False  # If True, detects collisions but doesn't block movement
        self.collision_layer: int = 0  # Collision layer for filtering
        self.collision_mask: int = 0xFFFFFFFF  # Which layers this collider can collide with
        
        # Offset from actor position
        self.offset: pygame.Vector2 = pygame.Vector2(0, 0)
        
        # Runtime collision tracking
        self._current_collisions: Set['ColliderComponent'] = set()
        
        # Collision event callbacks (not serialized)
        self.on_collision_enter: Optional[Callable[['ColliderComponent'], None]] = None
        self.on_collision_stay: Optional[Callable[['ColliderComponent'], None]] = None
        self.on_collision_exit: Optional[Callable[['ColliderComponent'], None]] = None
        
        # Visual debug rendering
        self.debug_render: bool = False
        self.debug_color: pygame.Color = pygame.Color(0, 255, 0, 128)
        self.debug_color_collision: pygame.Color = pygame.Color(255, 0, 0, 128)
        
    def get_bounds(self) -> pygame.Rect:
        """Get the axis-aligned bounding box of the collider."""
        if not self.actor:
            return pygame.Rect(0, 0, 0, 0)
            
        center = self.actor.transform.position + self.offset
        
        if self.collider_type == ColliderType.RECTANGLE:
            # Apply actor's scale to collider size
            scaled_width = self.width * self.actor.transform.scale.x
            scaled_height = self.height * self.actor.transform.scale.y
            
            return pygame.Rect(
                center.x - scaled_width / 2,
                center.y - scaled_height / 2,
                scaled_width,
                scaled_height
            )
        elif self.collider_type == ColliderType.CIRCLE:
            # Circle's bounding box
            scaled_radius = self.radius * max(self.actor.transform.scale.x, self.actor.transform.scale.y)
            return pygame.Rect(
                center.x - scaled_radius,
                center.y - scaled_radius,
                scaled_radius * 2,
                scaled_radius * 2
            )
        else:  # POINT
            return pygame.Rect(center.x, center.y, 1, 1)
            
    def get_center(self) -> pygame.Vector2:
        """Get the center position of the collider."""
        if not self.actor:
            return pygame.Vector2(0, 0)
        return self.actor.transform.position + self.offset
        
    def contains_point(self, point: pygame.Vector2) -> bool:
        """Check if a point is inside this collider."""
        if not self.actor:
            return False
            
        center = self.get_center()
        
        if self.collider_type == ColliderType.RECTANGLE:
            bounds = self.get_bounds()
            return bounds.collidepoint(point.x, point.y)
        elif self.collider_type == ColliderType.CIRCLE:
            scaled_radius = self.radius * max(self.actor.transform.scale.x, self.actor.transform.scale.y)
            distance = (point - center).length()
            return distance <= scaled_radius
        else:  # POINT
            return (point - center).length() < 1.0
            
    def overlaps_with(self, other: 'ColliderComponent') -> bool:
        """Check if this collider overlaps with another collider."""
        if not self.actor or not other.actor:
            return False
            
        # Check collision layer compatibility
        if not (self.collision_mask & (1 << other.collision_layer)):
            return False
        if not (other.collision_mask & (1 << self.collision_layer)):
            return False
            
        # Get positions
        center1 = self.get_center()
        center2 = other.get_center()
        
        # Handle different collision type combinations
        if (self.collider_type == ColliderType.RECTANGLE and 
            other.collider_type == ColliderType.RECTANGLE):
            return self._rect_rect_collision(other)
        elif (self.collider_type == ColliderType.CIRCLE and 
              other.collider_type == ColliderType.CIRCLE):
            return self._circle_circle_collision(other)
        elif ((self.collider_type == ColliderType.RECTANGLE and other.collider_type == ColliderType.CIRCLE) or
              (self.collider_type == ColliderType.CIRCLE and other.collider_type == ColliderType.RECTANGLE)):
            return self._rect_circle_collision(other)
        else:
            # Point collisions or mixed with point
            if self.collider_type == ColliderType.POINT:
                return other.contains_point(center1)
            elif other.collider_type == ColliderType.POINT:
                return self.contains_point(center2)
                
        return False
        
    def _rect_rect_collision(self, other: 'ColliderComponent') -> bool:
        """Check rectangle-rectangle collision."""
        bounds1 = self.get_bounds()
        bounds2 = other.get_bounds()
        return bounds1.colliderect(bounds2)
        
    def _circle_circle_collision(self, other: 'ColliderComponent') -> bool:
        """Check circle-circle collision."""
        center1 = self.get_center()
        center2 = other.get_center()
        
        radius1 = self.radius * max(self.actor.transform.scale.x, self.actor.transform.scale.y)
        radius2 = other.radius * max(other.actor.transform.scale.x, other.actor.transform.scale.y)
        
        distance = (center2 - center1).length()
        return distance <= (radius1 + radius2)
        
    def _rect_circle_collision(self, other: 'ColliderComponent') -> bool:
        """Check rectangle-circle collision."""
        if self.collider_type == ColliderType.RECTANGLE:
            rect_collider = self
            circle_collider = other
        else:
            rect_collider = other
            circle_collider = self
            
        rect_bounds = rect_collider.get_bounds()
        circle_center = circle_collider.get_center()
        circle_radius = circle_collider.radius * max(
            circle_collider.actor.transform.scale.x, 
            circle_collider.actor.transform.scale.y
        )
        
        # Find closest point on rectangle to circle center
        closest_x = max(rect_bounds.left, min(circle_center.x, rect_bounds.right))
        closest_y = max(rect_bounds.top, min(circle_center.y, rect_bounds.bottom))
        closest_point = pygame.Vector2(closest_x, closest_y)
        
        # Check if closest point is within circle radius
        distance = (circle_center - closest_point).length()
        return distance <= circle_radius
        
    def check_collision_with(self, other: 'ColliderComponent') -> None:
        """Check collision with another collider and trigger events."""
        is_colliding = self.overlaps_with(other)
        was_colliding = other in self._current_collisions
        
        if is_colliding and not was_colliding:
            # Collision enter
            self._current_collisions.add(other)
            if self.on_collision_enter:
                self.on_collision_enter(other)
        elif is_colliding and was_colliding:
            # Collision stay
            if self.on_collision_stay:
                self.on_collision_stay(other)
        elif not is_colliding and was_colliding:
            # Collision exit
            self._current_collisions.discard(other)
            if self.on_collision_exit:
                self.on_collision_exit(other)
                
    def get_all_collisions(self) -> Set['ColliderComponent']:
        """Get all currently colliding colliders."""
        return self._current_collisions.copy()
        
    def is_colliding_with(self, other: 'ColliderComponent') -> bool:
        """Check if currently colliding with another specific collider."""
        return other in self._current_collisions
        
    def is_colliding_with_layer(self, layer: int) -> bool:
        """Check if colliding with any collider on a specific layer."""
        for collider in self._current_collisions:
            if collider.collision_layer == layer:
                return True
        return False
        
    def set_size(self, width: float, height: float = None) -> None:
        """Set the size of the collider."""
        if self.collider_type == ColliderType.RECTANGLE:
            self.width = width
            self.height = height if height is not None else width
        elif self.collider_type == ColliderType.CIRCLE:
            self.radius = width
            
    def render_debug(self, surface: pygame.Surface) -> None:
        """Render debug visualization of the collider."""
        if not self.debug_render or not self.actor:
            return
            
        # Choose color based on collision state
        color = self.debug_color_collision if self._current_collisions else self.debug_color
        
        center = self.get_center()
        
        if self.collider_type == ColliderType.RECTANGLE:
            bounds = self.get_bounds()
            # Create a surface for alpha blending
            debug_surface = pygame.Surface((bounds.width, bounds.height), pygame.SRCALPHA)
            debug_surface.fill(color)
            surface.blit(debug_surface, bounds.topleft)
            
            # Draw outline
            pygame.draw.rect(surface, color, bounds, 2)
            
        elif self.collider_type == ColliderType.CIRCLE:
            scaled_radius = self.radius * max(self.actor.transform.scale.x, self.actor.transform.scale.y)
            
            # Draw filled circle with alpha
            debug_surface = pygame.Surface((scaled_radius * 2, scaled_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(debug_surface, color, (scaled_radius, scaled_radius), scaled_radius)
            surface.blit(debug_surface, (center.x - scaled_radius, center.y - scaled_radius))
            
            # Draw outline
            pygame.draw.circle(surface, color, (int(center.x), int(center.y)), int(scaled_radius), 2)
            
        else:  # POINT
            pygame.draw.circle(surface, color, (int(center.x), int(center.y)), 3)
            
    def render(self, surface: pygame.Surface) -> None:
        """Render the collider (only debug visualization)."""
        if self.debug_render:
            self.render_debug(surface)
            
    def update(self, dt: float) -> None:
        """Update the collider component."""
        super().update(dt)
        
        # Note: Collision detection is typically handled by a physics/collision system
        # This component provides the data and methods for collision detection
        
    def serialize(self) -> dict:
        """Serialize the collider component data."""
        data = super().serialize()
        
        # Convert enum to string for serialization
        data['collider_type'] = self.collider_type.value
        
        return data
        
    def deserialize(self, data: dict):
        """Deserialize the collider component data."""
        super().deserialize(data)
        
        # Convert string back to enum
        if 'collider_type' in data:
            self.collider_type = ColliderType(data['collider_type'])
            
        # Reset runtime state
        self._current_collisions.clear()
        
        return self
