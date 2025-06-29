"""
Tilemap component for creating collidable tilemaps with networking support.
Provides efficient tile-based collision detection and synchronized tile data.
"""

import pygame
import pymunk
from typing import List, Dict, Any, Optional, Tuple, Set
from enum import Enum
from engine.core.actor import Component
from engine.components.physics_component import PhysicsComponent, PhysicsBodyType
from engine.components.physics_world import PhysicsWorld


class TileType(Enum):
    """Types of tiles for different behaviors."""
    EMPTY = 0
    SOLID = 1
    PLATFORM = 2  # One-way collision (can jump through from below)
    LADDER = 3
    SPIKE = 4
    WATER = 5
    ICE = 6


class TileData:
    """Data structure for individual tiles."""
    
    def __init__(self, tile_type: TileType = TileType.EMPTY, texture_id: str = None, 
                 collision_enabled: bool = None, properties: Dict[str, Any] = None):
        self.tile_type = tile_type
        self.texture_id = texture_id
        self.collision_enabled = collision_enabled if collision_enabled is not None else tile_type != TileType.EMPTY
        self.properties = properties or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'tile_type': self.tile_type.value,
            'texture_id': self.texture_id,
            'collision_enabled': self.collision_enabled,
            'properties': self.properties
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TileData':
        """Create from dictionary for deserialization."""
        return cls(
            tile_type=TileType(data.get('tile_type', 0)),
            texture_id=data.get('texture_id'),
            collision_enabled=data.get('collision_enabled'),
            properties=data.get('properties', {})
        )


class TilemapComponent(Component):
    """
    Tilemap component that provides:
    - Efficient tile-based rendering
    - Collision detection using pymunk
    - Network synchronization
    - Dynamic tile modification
    """
    
    def __init__(self, width: int, height: int, tile_size: int = 32, 
                 default_tile: TileData = None, chunk_size: int = 16):
        super().__init__()
        
        # Tilemap dimensions
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.chunk_size = chunk_size  # For efficient collision culling
        
        # Tile data
        self.default_tile = default_tile or TileData()
        self.tiles: List[List[TileData]] = []
        self._initialize_tiles()
        
        # Rendering properties
        self.visible = True
        self.render_chunks_only = True  # Only render visible chunks
        self.camera_culling = True
        
        # Physics/collision properties
        self.collision_enabled = True
        self.collision_type = 1  # Collision type for pymunk
        self.friction = 0.7
        self.elasticity = 0.0
        
        # Physics bodies for collision (organized by chunks for efficiency)
        self.collision_bodies: Dict[Tuple[int, int], List[pymunk.Body]] = {}
        self.collision_shapes: Dict[Tuple[int, int], List[pymunk.Shape]] = {}
        self.physics_world: Optional[PhysicsWorld] = None
        
        # Networking properties
        self.sync_tiles = True
        self.dirty_chunks: Set[Tuple[int, int]] = set()  # Chunks that need network sync
        self.last_sync_version = 0
        self.sync_version = 0
        
        # Rendering cache
        self._render_cache: Dict[Tuple[int, int], pygame.Surface] = {}
        self._cache_dirty: Set[Tuple[int, int]] = set()
        
    def _initialize_tiles(self):
        """Initialize the tile grid with default tiles."""
        self.tiles = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(TileData(
                    tile_type=self.default_tile.tile_type,
                    texture_id=self.default_tile.texture_id,
                    collision_enabled=self.default_tile.collision_enabled,
                    properties=self.default_tile.properties.copy()
                ))
            self.tiles.append(row)
    
    def on_added(self, actor):
        """Called when component is added to an actor."""
        super().on_added(actor)
        self._setup_physics()
        
    def on_removed(self):
        """Called when component is removed from an actor."""
        self._cleanup_physics()
        super().on_removed()
        
    def _setup_physics(self):
        """Setup physics world integration."""
        if self.game and hasattr(self.game, 'physics_manager') and self.game.physics_manager.world:
            self.physics_world = self.game.physics_manager.world
            if self.collision_enabled:
                self._rebuild_collision()
                
    def _cleanup_physics(self):
        """Remove all physics bodies from the world."""
        if self.physics_world:
            for bodies in self.collision_bodies.values():
                for body in bodies:
                    self.physics_world.space.remove(body)
            for shapes_list in self.collision_shapes.values():
                for shape in shapes_list:
                    self.physics_world.space.remove(shape)
        self.collision_bodies.clear()
        self.collision_shapes.clear()
        
    def get_tile(self, x: int, y: int) -> Optional[TileData]:
        """Get tile at grid coordinates."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None
        
    def set_tile(self, x: int, y: int, tile_data: TileData, sync_network: bool = True):
        """Set tile at grid coordinates."""
        if 0 <= x < self.width and 0 <= y < self.height:
            old_tile = self.tiles[y][x]
            self.tiles[y][x] = tile_data
            
            # Mark chunk as dirty for rendering
            chunk_x, chunk_y = x // self.chunk_size, y // self.chunk_size
            self._cache_dirty.add((chunk_x, chunk_y))
            
            # Update collision if needed
            if old_tile.collision_enabled != tile_data.collision_enabled or old_tile.tile_type != tile_data.tile_type:
                self._update_chunk_collision(chunk_x, chunk_y)
                
            # Mark for network sync
            if sync_network and self.sync_tiles:
                self.dirty_chunks.add((chunk_x, chunk_y))
                self.sync_version += 1
                
    def get_tile_at_world_pos(self, world_pos: pygame.Vector2) -> Optional[TileData]:
        """Get tile at world position."""
        if not self.actor:
            return None
            
        # Convert world position to local tile coordinates
        local_pos = world_pos - self.actor.transform.world_position
        tile_x = int(local_pos.x // self.tile_size)
        tile_y = int(local_pos.y // self.tile_size)
        return self.get_tile(tile_x, tile_y)
        
    def set_tile_at_world_pos(self, world_pos: pygame.Vector2, tile_data: TileData, sync_network: bool = True):
        """Set tile at world position."""
        if not self.actor:
            return
            
        # Convert world position to local tile coordinates
        local_pos = world_pos - self.actor.transform.world_position
        tile_x = int(local_pos.x // self.tile_size)
        tile_y = int(local_pos.y // self.tile_size)
        self.set_tile(tile_x, tile_y, tile_data, sync_network)
        
    def get_chunk_bounds(self, chunk_x: int, chunk_y: int) -> Tuple[int, int, int, int]:
        """Get the tile bounds for a chunk."""
        start_x = chunk_x * self.chunk_size
        start_y = chunk_y * self.chunk_size
        end_x = min(start_x + self.chunk_size, self.width)
        end_y = min(start_y + self.chunk_size, self.height)
        return start_x, start_y, end_x, end_y
        
    def _update_chunk_collision(self, chunk_x: int, chunk_y: int):
        """Update collision bodies for a specific chunk."""
        if not self.physics_world or not self.collision_enabled:
            return
            
        chunk_key = (chunk_x, chunk_y)
        
        # Remove existing collision bodies for this chunk
        if chunk_key in self.collision_bodies:
            for body in self.collision_bodies[chunk_key]:
                self.physics_world.space.remove(body)
            for shape in self.collision_shapes[chunk_key]:
                self.physics_world.space.remove(shape)
                
        # Create new collision bodies
        bodies = []
        shapes = []
        
        start_x, start_y, end_x, end_y = self.get_chunk_bounds(chunk_x, chunk_y)
        
        # Group adjacent solid tiles into larger collision shapes for efficiency
        processed = [[False for _ in range(end_x - start_x)] for _ in range(end_y - start_y)]
        
        for local_y in range(end_y - start_y):
            for local_x in range(end_x - start_x):
                if processed[local_y][local_x]:
                    continue
                    
                tile_x, tile_y = start_x + local_x, start_y + local_y
                tile = self.get_tile(tile_x, tile_y)
                
                if not tile or not tile.collision_enabled or tile.tile_type == TileType.EMPTY:
                    continue
                    
                # Find the largest rectangle of solid tiles starting from this position
                width = 1
                height = 1
                
                # Expand horizontally
                while (local_x + width < end_x - start_x and 
                       not processed[local_y][local_x + width]):
                    check_tile = self.get_tile(start_x + local_x + width, tile_y)
                    if (check_tile and check_tile.collision_enabled and 
                        check_tile.tile_type == tile.tile_type):
                        width += 1
                    else:
                        break
                        
                # Expand vertically
                can_expand_height = True
                while (local_y + height < end_y - start_y and can_expand_height):
                    # Check if entire row can be expanded
                    for w in range(width):
                        if processed[local_y + height][local_x + w]:
                            can_expand_height = False
                            break
                        check_tile = self.get_tile(start_x + local_x + w, start_y + local_y + height)
                        if (not check_tile or not check_tile.collision_enabled or 
                            check_tile.tile_type != tile.tile_type):
                            can_expand_height = False
                            break
                    if can_expand_height:
                        height += 1
                    
                # Mark all tiles in this rectangle as processed
                for h in range(height):
                    for w in range(width):
                        processed[local_y + h][local_x + w] = True
                        
                # Create collision body for this rectangle
                world_x = (self.actor.transform.world_position.x + 
                          (tile_x + width * 0.5) * self.tile_size)
                world_y = (self.actor.transform.world_position.y + 
                          (tile_y + height * 0.5) * self.tile_size)
                          
                body = pymunk.Body(body_type=pymunk.Body.STATIC)
                body.position = world_x, world_y
                
                shape_width = width * self.tile_size
                shape_height = height * self.tile_size
                shape = pymunk.Poly.create_box(body, (shape_width, shape_height))
                
                # Set collision properties based on tile type
                shape.friction = self.friction
                shape.elasticity = self.elasticity
                shape.collision_type = self.collision_type
                
                # Store tile type in shape for collision handling
                shape.tile_type = tile.tile_type
                shape.tile_component = self
                
                bodies.append(body)
                shapes.append(shape)
                
                self.physics_world.space.add(body, shape)
                
        self.collision_bodies[chunk_key] = bodies
        self.collision_shapes[chunk_key] = shapes
        
    def _rebuild_collision(self):
        """Rebuild all collision bodies."""
        self._cleanup_physics()
        
        if not self.physics_world or not self.collision_enabled:
            return
            
        # Process all chunks
        chunks_x = (self.width + self.chunk_size - 1) // self.chunk_size
        chunks_y = (self.height + self.chunk_size - 1) // self.chunk_size
        
        for chunk_y in range(chunks_y):
            for chunk_x in range(chunks_x):
                self._update_chunk_collision(chunk_x, chunk_y)
                
    def update(self, dt: float):
        """Update the tilemap component."""
        # Update physics if position changed
        if self.actor and self.actor.transform.dirty and self.collision_enabled:
            self._rebuild_collision()
            
    def render(self, screen: pygame.Surface):
        """Render the tilemap."""
        if not self.visible or not self.actor:
            return
            
        # Get camera bounds for culling if available
        camera_rect = None
        if (self.camera_culling and self.game and 
            hasattr(self.game, 'camera') and self.game.camera):
            camera_rect = self.game.camera.get_view_rect()
            
        # Calculate which chunks to render
        chunks_to_render = self._get_visible_chunks(camera_rect)
        
        for chunk_x, chunk_y in chunks_to_render:
            self._render_chunk(screen, chunk_x, chunk_y)
            
    def _get_visible_chunks(self, camera_rect: Optional[pygame.Rect]) -> List[Tuple[int, int]]:
        """Get list of chunks that should be rendered."""
        chunks = []
        
        if not camera_rect:
            # Render all chunks
            chunks_x = (self.width + self.chunk_size - 1) // self.chunk_size
            chunks_y = (self.height + self.chunk_size - 1) // self.chunk_size
            for chunk_y in range(chunks_y):
                for chunk_x in range(chunks_x):
                    chunks.append((chunk_x, chunk_y))
        else:
            # Only render visible chunks
            tilemap_pos = self.actor.transform.world_position
            
            # Convert camera rect to tile coordinates
            left_tile = max(0, int((camera_rect.left - tilemap_pos.x) // self.tile_size))
            top_tile = max(0, int((camera_rect.top - tilemap_pos.y) // self.tile_size))
            right_tile = min(self.width, int((camera_rect.right - tilemap_pos.x) // self.tile_size) + 1)
            bottom_tile = min(self.height, int((camera_rect.bottom - tilemap_pos.y) // self.tile_size) + 1)
            
            # Convert to chunk coordinates
            left_chunk = left_tile // self.chunk_size
            top_chunk = top_tile // self.chunk_size
            right_chunk = (right_tile + self.chunk_size - 1) // self.chunk_size
            bottom_chunk = (bottom_tile + self.chunk_size - 1) // self.chunk_size
            
            for chunk_y in range(top_chunk, bottom_chunk):
                for chunk_x in range(left_chunk, right_chunk):
                    chunks.append((chunk_x, chunk_y))
                    
        return chunks
        
    def _render_chunk(self, screen: pygame.Surface, chunk_x: int, chunk_y: int):
        """Render a specific chunk."""
        chunk_key = (chunk_x, chunk_y)
        
        # Check if we need to regenerate the chunk cache
        if chunk_key in self._cache_dirty or chunk_key not in self._render_cache:
            self._generate_chunk_cache(chunk_x, chunk_y)
            
        # Render the cached chunk surface
        if chunk_key in self._render_cache:
            chunk_surface = self._render_cache[chunk_key]
            world_pos = self.actor.transform.world_position
            chunk_world_x = world_pos.x + chunk_x * self.chunk_size * self.tile_size
            chunk_world_y = world_pos.y + chunk_y * self.chunk_size * self.tile_size
            screen.blit(chunk_surface, (chunk_world_x, chunk_world_y))
            
    def _generate_chunk_cache(self, chunk_x: int, chunk_y: int):
        """Generate cached surface for a chunk."""
        chunk_key = (chunk_x, chunk_y)
        start_x, start_y, end_x, end_y = self.get_chunk_bounds(chunk_x, chunk_y)
        
        chunk_width = (end_x - start_x) * self.tile_size
        chunk_height = (end_y - start_y) * self.tile_size
        
        chunk_surface = pygame.Surface((chunk_width, chunk_height), pygame.SRCALPHA)
        
        for tile_y in range(start_y, end_y):
            for tile_x in range(start_x, end_x):
                tile = self.get_tile(tile_x, tile_y)
                if not tile or tile.tile_type == TileType.EMPTY:
                    continue
                    
                # Get tile surface
                tile_surface = self._get_tile_surface(tile)
                if tile_surface:
                    local_x = (tile_x - start_x) * self.tile_size
                    local_y = (tile_y - start_y) * self.tile_size
                    chunk_surface.blit(tile_surface, (local_x, local_y))
                    
        self._render_cache[chunk_key] = chunk_surface
        self._cache_dirty.discard(chunk_key)
        
    def _get_tile_surface(self, tile: TileData) -> Optional[pygame.Surface]:
        """Get the surface for rendering a tile."""
        # Try to get from asset manager first
        if tile.texture_id and self.game and hasattr(self.game, 'asset_manager'):
            try:
                surface = self.game.asset_manager.get_texture(tile.texture_id)
                if surface:
                    return surface
            except:
                pass
                
        # Generate procedural tile based on type
        surface = pygame.Surface((self.tile_size, self.tile_size))
        
        if tile.tile_type == TileType.SOLID:
            surface.fill(pygame.Color(100, 100, 100))
        elif tile.tile_type == TileType.PLATFORM:
            surface.fill(pygame.Color(150, 75, 0))
        elif tile.tile_type == TileType.LADDER:
            surface.fill(pygame.Color(139, 69, 19))
        elif tile.tile_type == TileType.SPIKE:
            surface.fill(pygame.Color(255, 0, 0))
        elif tile.tile_type == TileType.WATER:
            surface.fill(pygame.Color(0, 100, 255))
        elif tile.tile_type == TileType.ICE:
            surface.fill(pygame.Color(200, 200, 255))
        else:
            return None
            
        return surface
        
    # Networking methods
    
    def serialize_for_network(self) -> Dict[str, Any]:
        """Serialize tilemap for network transmission."""
        if not self.sync_tiles:
            return {'sync_tiles': False}
            
        # Only serialize dirty chunks for efficiency
        dirty_chunk_data = {}
        for chunk_x, chunk_y in self.dirty_chunks:
            chunk_key = f"{chunk_x},{chunk_y}"
            chunk_tiles = []
            
            start_x, start_y, end_x, end_y = self.get_chunk_bounds(chunk_x, chunk_y)
            for tile_y in range(start_y, end_y):
                for tile_x in range(start_x, end_x):
                    tile = self.get_tile(tile_x, tile_y)
                    if tile:
                        chunk_tiles.append({
                            'x': tile_x,
                            'y': tile_y,
                            'data': tile.to_dict()
                        })
            dirty_chunk_data[chunk_key] = chunk_tiles
            
        return {
            'width': self.width,
            'height': self.height,
            'tile_size': self.tile_size,
            'chunk_size': self.chunk_size,
            'collision_enabled': self.collision_enabled,
            'collision_type': self.collision_type,
            'friction': self.friction,
            'elasticity': self.elasticity,
            'sync_version': self.sync_version,
            'dirty_chunks': dirty_chunk_data,
            'sync_tiles': self.sync_tiles
        }
        
    def deserialize_from_network(self, data: Dict[str, Any]):
        """Deserialize tilemap from network transmission."""
        if not data.get('sync_tiles', True):
            return
            
        # Update basic properties
        if 'collision_enabled' in data:
            self.collision_enabled = data['collision_enabled']
        if 'collision_type' in data:
            self.collision_type = data['collision_type']
        if 'friction' in data:
            self.friction = data['friction']
        if 'elasticity' in data:
            self.elasticity = data['elasticity']
            
        # Process dirty chunks
        if 'dirty_chunks' in data:
            updated_chunks = set()
            
            for chunk_key, chunk_tiles in data['dirty_chunks'].items():
                chunk_x, chunk_y = map(int, chunk_key.split(','))
                
                for tile_info in chunk_tiles:
                    tile_x = tile_info['x']
                    tile_y = tile_info['y']
                    tile_data = TileData.from_dict(tile_info['data'])
                    
                    # Set tile without triggering network sync
                    self.set_tile(tile_x, tile_y, tile_data, sync_network=False)
                    
                updated_chunks.add((chunk_x, chunk_y))
                
            # Update collision for modified chunks
            for chunk_x, chunk_y in updated_chunks:
                self._update_chunk_collision(chunk_x, chunk_y)
                
        # Update sync version
        if 'sync_version' in data:
            self.last_sync_version = data['sync_version']
            
        # Clear dirty chunks since we just synced
        self.dirty_chunks.clear()
        
    def load_from_data(self, tilemap_data: List[List[int]], tile_mappings: Dict[int, TileData]):
        """Load tilemap from 2D array data with tile mappings."""
        if len(tilemap_data) != self.height or len(tilemap_data[0]) != self.width:
            raise ValueError("Tilemap data dimensions don't match component dimensions")
            
        for y in range(self.height):
            for x in range(self.width):
                tile_id = tilemap_data[y][x]
                tile_data = tile_mappings.get(tile_id, self.default_tile)
                self.set_tile(x, y, tile_data, sync_network=False)
                
        self._rebuild_collision()
        
    def to_data_array(self) -> List[List[int]]:
        """Export tilemap to 2D array of tile type values."""
        data = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                tile = self.get_tile(x, y)
                row.append(tile.tile_type.value if tile else 0)
            data.append(row)
        return data
