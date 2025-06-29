from engine import Component
from dataclasses import dataclass

@dataclass
class Tile:
    image: str

class Tilemap(Component):
    def __init__(self, width: int, height: int, tile_size: int = 32):
        super().__init__()
        self.tile_size = tile_size
        self.tiles = {}
        self.map_data = [] # data stored in a single list (pos = x + y * width)
        self.width = width
        self.height = height

    def register_tile(self, tile_id: str, image: str):
        """Register a tile with an ID and image path."""
        self.tiles[tile_id] = Tile(image=image)

    def get_tile(self, x: int, y: int) -> Tile:
        """Get the tile at the specified (x, y) position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            index = x + y * self.width
            return self.map_data[index]
        raise IndexError("Tile position out of bounds")
    
    def set_tile(self, x: int, y: int, tile_id: str):
        """Set the tile at the specified (x, y) position."""
        if tile_id not in self.tiles:
            raise ValueError(f"Tile ID '{tile_id}' not registered")
        if 0 <= x < self.width and 0 <= y < self.height:
            index = x + y * self.width
            self.map_data[index] = self.tiles[tile_id]
        else:
            raise IndexError("Tile position out of bounds")