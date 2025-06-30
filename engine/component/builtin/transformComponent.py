import pygame
from typing import Optional
from engine.component.component import Component

class TransformComponent(Component):
    """
    Advanced transform component that extends the basic actor transform.
    Provides additional transformation features using actor parent-child relationships,
    local vs world coordinates, and transform constraints.
    """
    
    def __init__(self):
        super().__init__()
        
        # Local transform (relative to parent)
        self.local_position: pygame.Vector2 = pygame.Vector2(0, 0)
        self.local_rotation: float = 0.0
        self.local_scale: pygame.Vector2 = pygame.Vector2(1, 1)
        
        # Transform constraints
        self.lock_x: bool = False
        self.lock_y: bool = False
        self.lock_rotation: bool = False
        self.lock_scale: bool = False
        
    def _get_parent_transform_component(self) -> Optional['TransformComponent']:
        """Get the parent actor's TransformComponent if it exists."""
        if not self.actor or not self.actor.parent:
            return None
        return self.actor.parent.getComponent(TransformComponent)
        
    def get_world_position(self) -> pygame.Vector2:
        """Get the world position considering parent transforms."""
        if not self.actor:
            return pygame.Vector2(0, 0)
        
        parent_transform = self._get_parent_transform_component()
        if parent_transform:
            parent_world = parent_transform.get_world_position()
            parent_rotation = parent_transform.get_world_rotation()
            rotated_local = self.local_position.rotate(parent_rotation)
            world_pos = parent_world + rotated_local
        else:
            world_pos = self.local_position.copy()
        return world_pos

    def get_world_rotation(self) -> float:
        """Get the world rotation considering parent transforms."""
        if not self.actor:
            return 0.0
        world_rot = self.local_rotation
        parent_transform = self._get_parent_transform_component()
        if parent_transform:
            parent_rot = parent_transform.get_world_rotation()
            world_rot += parent_rot
        return world_rot

    def get_world_scale(self) -> pygame.Vector2:
        """Get the world scale considering parent transforms."""
        if not self.actor:
            return pygame.Vector2(1, 1)
        world_scale = self.local_scale.copy()
        parent_transform = self._get_parent_transform_component()
        if parent_transform:
            parent_scale = parent_transform.get_world_scale()
            world_scale.x *= parent_scale.x
            world_scale.y *= parent_scale.y
        return world_scale

    def set_world_position(self, world_pos: pygame.Vector2) -> None:
        """Set the world position, updating local position appropriately."""
        if not self.actor:
            return
        parent_transform = self._get_parent_transform_component()
        if parent_transform:
            parent_world = parent_transform.get_world_position()
            parent_rotation = parent_transform.get_world_rotation()
            # Undo parent rotation for local position
            local_pos = world_pos - parent_world
            self.local_position = local_pos.rotate(-parent_rotation)
        else:
            self.local_position = world_pos.copy()

    def move_to(self, target_pos: pygame.Vector2) -> None:
        """Move to a target position."""
        if not self.lock_x and not self.lock_y:
            self.set_world_position(target_pos)
        elif not self.lock_x:
            current = self.get_world_position()
            self.set_world_position(pygame.Vector2(target_pos.x, current.y))
        elif not self.lock_y:
            current = self.get_world_position()
            self.set_world_position(pygame.Vector2(current.x, target_pos.y))

    def rotate_to(self, target_rot: float) -> None:
        """Rotate to a target rotation."""
        if self.lock_rotation:
            return
        self.local_rotation = target_rot

    def scale_to(self, target_scale: pygame.Vector2) -> None:
        """Scale to a target scale."""
        if self.lock_scale:
            return
        self.local_scale = target_scale.copy()
                
    def update(self, dt: float) -> None:
        """Update the transform component."""
        super().update(dt)
        
        if not self.actor:
            return
            
        # Update children if we moved
        self._update_children()
        
    def _update_children(self) -> None:
        """Update child transforms."""
        # Children will handle their own updates based on our transform
        pass
        
    def look_at(self, target_pos: pygame.Vector2) -> None:
        """Rotate to look at a target position."""
        if self.lock_rotation or not self.actor:
            return
            
        current_pos = self.get_world_position()
        direction = target_pos - current_pos
        
        if direction.length() > 0:
            # Calculate angle to target
            angle = direction.angle_to(pygame.Vector2(1, 0))  # Angle from right vector
            self.rotate_to(angle)
            
    def serialize(self) -> dict:
        """Serialize the transform component data."""
        data = super().serialize()
        # Parent-child relationships are now handled by Actor serialization
        # so no need to exclude anything here
        return data
