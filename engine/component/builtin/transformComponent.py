import pygame
from typing import Optional
from engine.component.component import Component

class TransformComponent(Component):
    """
    Advanced transform component that extends the basic actor transform.
    Provides additional transformation features like parent-child relationships,
    local vs world coordinates, and smooth interpolation.
    """
    
    def __init__(self):
        super().__init__()
        
        # Parent-child transform relationships
        self.parent_transform: Optional['TransformComponent'] = None
        self.children_transforms: list = []
        
        # Local transform (relative to parent)
        self.local_position: pygame.Vector2 = pygame.Vector2(0, 0)
        self.local_rotation: float = 0.0
        self.local_scale: pygame.Vector2 = pygame.Vector2(1, 1)
        
        # Transform constraints
        self.lock_x: bool = False
        self.lock_y: bool = False
        self.lock_rotation: bool = False
        self.lock_scale: bool = False
        
    def set_parent(self, parent_transform: Optional['TransformComponent']) -> None:
        """Set this transform's parent."""
        # Remove from old parent
        if self.parent_transform and self in self.parent_transform.children_transforms:
            self.parent_transform.children_transforms.remove(self)
            
        # Set new parent
        self.parent_transform = parent_transform
        
        # Add to new parent
        if parent_transform and self not in parent_transform.children_transforms:
            parent_transform.children_transforms.append(self)
            
    def add_child(self, child_transform: 'TransformComponent') -> None:
        """Add a child transform."""
        child_transform.set_parent(self)
        
    def remove_child(self, child_transform: 'TransformComponent') -> None:
        """Remove a child transform."""
        if child_transform in self.children_transforms:
            child_transform.set_parent(None)
            
    def get_world_position(self) -> pygame.Vector2:
        """Get the world position considering parent transforms."""
        if not self.actor:
            return pygame.Vector2(0, 0)
            
        world_pos = self.actor.transform.position.copy()
        
        if self.parent_transform:
            parent_world = self.parent_transform.get_world_position()
            # Apply parent rotation to local position
            if self.parent_transform.actor:
                parent_rotation = self.parent_transform.actor.transform.rotation
                rotated_local = self.local_position.rotate(parent_rotation)
                world_pos = parent_world + rotated_local
            else:
                world_pos = parent_world + self.local_position
        else:
            world_pos += self.local_position
            
        return world_pos
        
    def get_world_rotation(self) -> float:
        """Get the world rotation considering parent transforms."""
        if not self.actor:
            return 0.0
            
        world_rot = self.actor.transform.rotation + self.local_rotation
        
        if self.parent_transform:
            parent_rot = self.parent_transform.get_world_rotation()
            world_rot += parent_rot
            
        return world_rot
        
    def get_world_scale(self) -> pygame.Vector2:
        """Get the world scale considering parent transforms."""
        if not self.actor:
            return pygame.Vector2(1, 1)
            
        world_scale = pygame.Vector2(
            self.actor.transform.scale.x * self.local_scale.x,
            self.actor.transform.scale.y * self.local_scale.y
        )
        
        if self.parent_transform:
            parent_scale = self.parent_transform.get_world_scale()
            world_scale.x *= parent_scale.x
            world_scale.y *= parent_scale.y
            
        return world_scale
        
    def set_world_position(self, world_pos: pygame.Vector2) -> None:
        """Set the world position, updating local position appropriately."""
        if not self.actor:
            return
            
        if self.parent_transform:
            parent_world = self.parent_transform.get_world_position()
            self.local_position = world_pos - parent_world
        else:
            self.actor.transform.position = world_pos
            self.local_position = pygame.Vector2(0, 0)
            
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
            
        if self.actor:
            self.actor.transform.rotation = target_rot
                
    def scale_to(self, target_scale: pygame.Vector2) -> None:
        """Scale to a target scale."""
        if self.lock_scale:
            return
            
        if self.actor:
            self.actor.transform.scale = target_scale
                
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
        
        # Don't serialize parent/child references as they would create circular dependencies
        # These should be re-established by the scene/actor management system
        if 'parent_transform' in data:
            del data['parent_transform']
        if 'children_transforms' in data:
            del data['children_transforms']
            
        return data
