"""
Sprite rendering component for actors.
"""

import pygame
from typing import Optional
from ..core.actor import Component


class SpriteComponent(Component):
    """
    Component for rendering sprites using pygame.Surface.
    Network-optimized to use texture IDs and procedural generation.
    """
    
    def __init__(self, surface: pygame.Surface = None, 
                 color: pygame.Color = None,
                 size: pygame.Vector2 = None,
                 texture_id: str = None):
        super().__init__()
        self.color = color or pygame.Color(255, 255, 255)
        self.size = size or pygame.Vector2(32, 32)
        self.texture_id = texture_id  # For loaded textures from asset manager
        
        # Runtime properties (not serialized)
        self.surface = surface
        self.rect = None
        
        # Sprite properties
        self.offset = pygame.Vector2(0, 0)  # Offset from actor position
        self.flip_x = False
        self.flip_y = False
        self.alpha = 255
        
        # Create surface
        self._create_surface()
        
    def _create_surface(self) -> None:
        """Create or recreate the surface based on current properties."""
        if self.texture_id and self.game and hasattr(self.game, 'asset_manager'):
            # Try to load from asset manager
            try:
                self.surface = self.game.asset_manager.get_texture(self.texture_id)
                if self.surface:
                    self.rect = self.surface.get_rect()
                    return
            except:
                pass  # Fall back to procedural generation
        
        # Create procedural surface (colored rectangle)
        if not self.surface:
            self.surface = pygame.Surface((int(self.size.x), int(self.size.y)))
            self.surface.fill(self.color)
            self.rect = self.surface.get_rect()
    
    def set_texture_id(self, texture_id: str) -> None:
        """Set texture by ID from asset manager."""
        self.texture_id = texture_id
        self._create_surface()
        
    def set_surface(self, surface: pygame.Surface) -> None:
        """Set the sprite surface directly."""
        self.surface = surface
        self.rect = surface.get_rect()
        self.texture_id = None  # Clear texture ID since we're using direct surface
        
    def set_color(self, color: pygame.Color) -> None:
        """Set sprite color (recreates surface for solid colors)."""
        self.color = color
        if not self.texture_id:  # Only update if not using a texture
            self._create_surface()
    
    def set_size(self, size: pygame.Vector2) -> None:
        """Set sprite size (recreates surface)."""
        self.size = size
        self._create_surface()
            
    def update(self, dt: float) -> None:
        """Update sprite position from actor transform."""
        if self.actor and self.rect:
            pos = self.actor.transform.world_position + self.offset
            self.rect.center = (int(pos.x), int(pos.y))
            
    def render(self, screen: pygame.Surface) -> None:
        """Render the sprite."""
        if not self.surface:
            return
            
        # Apply transformations
        surface = self.surface
        
        # Flip
        if self.flip_x or self.flip_y:
            surface = pygame.transform.flip(surface, self.flip_x, self.flip_y)
            
        # Scale
        if self.actor and (self.actor.transform.world_scale.x != 1.0 or 
                          self.actor.transform.world_scale.y != 1.0):
            new_size = (
                int(surface.get_width() * self.actor.transform.world_scale.x),
                int(surface.get_height() * self.actor.transform.world_scale.y)
            )
            if new_size[0] > 0 and new_size[1] > 0:
                surface = pygame.transform.scale(surface, new_size)
                
        # Rotation
        if self.actor and self.actor.transform.world_rotation != 0:
            surface = pygame.transform.rotate(surface, -self.actor.transform.world_rotation)
            
        # Alpha
        if self.alpha != 255:
            surface.set_alpha(self.alpha)
            
        # Calculate final position
        rect = surface.get_rect()
        if self.actor:
            pos = self.actor.transform.world_position + self.offset
            rect.center = (int(pos.x), int(pos.y))
            
        screen.blit(surface, rect)
    
    def serialize_for_network(self) -> dict:
        """
        Custom network serialization for SpriteComponent.
        Only sends essential data, not the actual surface.
        """
        return {
            'color': [self.color.r, self.color.g, self.color.b, self.color.a],
            'size': [self.size.x, self.size.y],
            'texture_id': self.texture_id,
            'offset': [self.offset.x, self.offset.y],
            'flip_x': self.flip_x,
            'flip_y': self.flip_y,
            'alpha': self.alpha
        }
    
    def deserialize_from_network(self, data: dict) -> None:
        """
        Custom network deserialization for SpriteComponent.
        Reconstructs the surface from the received data.
        """
        # Restore basic properties
        if 'color' in data:
            color_data = data['color']
            self.color = pygame.Color(color_data[0], color_data[1], color_data[2], color_data[3])
        
        if 'size' in data:
            size_data = data['size']
            self.size = pygame.Vector2(size_data[0], size_data[1])
        
        if 'texture_id' in data:
            self.texture_id = data['texture_id']
        
        if 'offset' in data:
            offset_data = data['offset']
            self.offset = pygame.Vector2(offset_data[0], offset_data[1])
        
        if 'flip_x' in data:
            self.flip_x = data['flip_x']
        
        if 'flip_y' in data:
            self.flip_y = data['flip_y']
        
        if 'alpha' in data:
            self.alpha = data['alpha']
        
        # Recreate the surface based on the received data
        self._create_surface()
        
        # Apply alpha to the surface if needed
        if self.surface and self.alpha != 255:
            self.surface.set_alpha(self.alpha)
