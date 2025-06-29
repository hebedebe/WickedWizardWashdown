"""
Asset management system for loading and caching game assets.
"""

import pygame
import os
import json
from typing import Dict, Optional, Any, List
from pathlib import Path

class AssetManager:
    """
    Manages loading, caching, and retrieval of game assets.
    """
    
    def __init__(self, base_path: str = "assets"):
        self.base_path = Path(base_path)
        
        # Asset caches
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.data: Dict[str, Any] = {}
        
        # Reference counting for memory management
        self.image_refs: Dict[str, int] = {}
        self.sound_refs: Dict[str, int] = {}
        self.font_refs: Dict[str, int] = {}
        
        # Asset directories
        self.image_path = self.base_path / "images"
        self.sound_path = self.base_path / "sounds"
        self.font_path = self.base_path / "fonts"
        self.data_path = self.base_path / "data"
        
        # Supported formats
        self.image_formats = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tga'}
        self.sound_formats = {'.wav', '.ogg', '.mp3'}
        self.font_formats = {'.ttf', '.otf'}
        
        # Create directories if they don't exist
        self._create_directories()
        
    def _create_directories(self) -> None:
        """Create asset directories if they don't exist."""
        directories = [self.base_path, self.image_path, self.sound_path, 
                      self.font_path, self.data_path]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
    def _get_full_path(self, asset_type: str, name: str) -> Path:
        """Get the full path for an asset."""
        type_paths = {
            'image': self.image_path,
            'sound': self.sound_path,
            'font': self.font_path,
            'data': self.data_path
        }
        return type_paths[asset_type] / name
        
    def load_image(self, name: str, convert_alpha: bool = True) -> Optional[pygame.Surface]:
        """
        Load an image asset.
        
        Args:
            name: Image filename or path relative to images directory
            convert_alpha: Whether to convert the image for optimal blitting
        """
        if name in self.images:
            self.image_refs[name] = self.image_refs.get(name, 0) + 1
            return self.images[name]
            
        # Try to find the file
        image_path = self._find_asset_file(self.image_path, name, self.image_formats)
        if not image_path:
            print(f"Could not find image: {name}")
            return None
            
        try:
            surface = pygame.image.load(str(image_path))
            if convert_alpha:
                surface = surface.convert_alpha()
            else:
                surface = surface.convert()
                
            self.images[name] = surface
            self.image_refs[name] = 1
            return surface
            
        except pygame.error as e:
            print(f"Could not load image {name}: {e}")
            return None
            
    def load_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """Load a sound asset."""
        if name in self.sounds:
            self.sound_refs[name] = self.sound_refs.get(name, 0) + 1
            return self.sounds[name]
            
        sound_path = self._find_asset_file(self.sound_path, name, self.sound_formats)
        if not sound_path:
            print(f"Could not find sound: {name}")
            return None
            
        try:
            sound = pygame.mixer.Sound(str(sound_path))
            self.sounds[name] = sound
            self.sound_refs[name] = 1
            return sound
            
        except pygame.error as e:
            print(f"Could not load sound {name}: {e}")
            return None
            
    def load_font(self, name: str, size: int = 24) -> Optional[pygame.font.Font]:
        """Load a font asset."""
        font_key = f"{name}_{size}"
        
        if font_key in self.fonts:
            self.font_refs[font_key] = self.font_refs.get(font_key, 0) + 1
            return self.fonts[font_key]
            
        # Try system font first
        if name in pygame.font.get_fonts():
            font = pygame.font.SysFont(name, size)
            self.fonts[font_key] = font
            self.font_refs[font_key] = 1
            return font
            
        # Try loading from file
        font_path = self._find_asset_file(self.font_path, name, self.font_formats)
        if not font_path:
            print(f"Could not find font: {name}, using default")
            font = pygame.font.Font(None, size)
            self.fonts[font_key] = font
            self.font_refs[font_key] = 1
            return font
            
        try:
            font = pygame.font.Font(str(font_path), size)
            self.fonts[font_key] = font
            self.font_refs[font_key] = 1
            return font
            
        except pygame.error as e:
            print(f"Could not load font {name}: {e}, using default")
            font = pygame.font.Font(None, size)
            self.fonts[font_key] = font
            self.font_refs[font_key] = 1
            return font
            
    def load_data(self, name: str) -> Optional[Any]:
        """Load data from JSON file."""
        if name in self.data:
            return self.data[name]
            
        data_path = self.data_path / name
        if not data_path.suffix:
            data_path = data_path.with_suffix('.json')
            
        if not data_path.exists():
            print(f"Could not find data file: {name}")
            return None
            
        try:
            with open(data_path, 'r') as f:
                data = json.load(f)
            self.data[name] = data
            return data
            
        except (json.JSONDecodeError, IOError) as e:
            print(f"Could not load data {name}: {e}")
            return None
            
    def _find_asset_file(self, base_path: Path, name: str, extensions: set) -> Optional[Path]:
        """Find an asset file with any of the supported extensions."""
        name_path = Path(name)
        
        # If the name already has an extension, use it
        if name_path.suffix.lower() in extensions:
            full_path = base_path / name
            if full_path.exists():
                return full_path
        else:
            # Try each supported extension
            for ext in extensions:
                full_path = base_path / (name + ext)
                if full_path.exists():
                    return full_path
                    
        return None
        
    def get_image(self, name: str) -> Optional[pygame.Surface]:
        """Get a loaded image (doesn't increment reference count)."""
        return self.images.get(name)
        
    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """Get a loaded sound (doesn't increment reference count)."""
        return self.sounds.get(name)
        
    def get_font(self, name: str, size: int = 24) -> Optional[pygame.font.Font]:
        """Get a loaded font (doesn't increment reference count)."""
        font_key = f"{name}_{size}"
        return self.fonts.get(font_key)
        
    def get_data(self, name: str) -> Optional[Any]:
        """Get loaded data."""
        return self.data.get(name)
        
    def release_image(self, name: str) -> None:
        """Release a reference to an image."""
        if name in self.image_refs:
            self.image_refs[name] -= 1
            if self.image_refs[name] <= 0:
                del self.images[name]
                del self.image_refs[name]
                
    def release_sound(self, name: str) -> None:
        """Release a reference to a sound."""
        if name in self.sound_refs:
            self.sound_refs[name] -= 1
            if self.sound_refs[name] <= 0:
                del self.sounds[name]
                del self.sound_refs[name]
                
    def release_font(self, name: str, size: int = 24) -> None:
        """Release a reference to a font."""
        font_key = f"{name}_{size}"
        if font_key in self.font_refs:
            self.font_refs[font_key] -= 1
            if self.font_refs[font_key] <= 0:
                del self.fonts[font_key]
                del self.font_refs[font_key]
                
    def create_surface(self, width: int, height: int, color: pygame.Color = None) -> pygame.Surface:
        """Create a new surface with optional color fill."""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        if color:
            surface.fill(color)
        return surface
        
    def create_gradient(self, width: int, height: int, 
                       start_color: pygame.Color, end_color: pygame.Color,
                       direction: str = 'vertical') -> pygame.Surface:
        """Create a gradient surface."""
        surface = pygame.Surface((width, height))
        
        if direction == 'vertical':
            for y in range(height):
                ratio = y / height
                color = pygame.Color(
                    int(start_color.r + (end_color.r - start_color.r) * ratio),
                    int(start_color.g + (end_color.g - start_color.g) * ratio),
                    int(start_color.b + (end_color.b - start_color.b) * ratio),
                    int(start_color.a + (end_color.a - start_color.a) * ratio)
                )
                pygame.draw.line(surface, color, (0, y), (width, y))
        else:  # horizontal
            for x in range(width):
                ratio = x / width
                color = pygame.Color(
                    int(start_color.r + (end_color.r - start_color.r) * ratio),
                    int(start_color.g + (end_color.g - start_color.g) * ratio),
                    int(start_color.b + (end_color.b - start_color.b) * ratio),
                    int(start_color.a + (end_color.a - start_color.a) * ratio)
                )
                pygame.draw.line(surface, color, (x, 0), (x, height))
                
        return surface
        
    def slice_spritesheet(self, image_name: str, tile_width: int, tile_height: int,
                         margin: int = 0, spacing: int = 0) -> List[pygame.Surface]:
        """Slice a spritesheet into individual sprites."""
        image = self.get_image(image_name)
        if not image:
            return []
            
        sprites = []
        image_width, image_height = image.get_size()
        
        y = margin
        while y + tile_height <= image_height - margin:
            x = margin
            while x + tile_width <= image_width - margin:
                rect = pygame.Rect(x, y, tile_width, tile_height)
                sprite = image.subsurface(rect).copy()
                sprites.append(sprite)
                x += tile_width + spacing
            y += tile_height + spacing
            
        return sprites
        
    def preload_assets(self, asset_list: List[Dict[str, Any]]) -> None:
        """Preload a list of assets."""
        for asset_info in asset_list:
            asset_type = asset_info.get('type')
            name = asset_info.get('name')
            
            if asset_type == 'image':
                self.load_image(name, asset_info.get('convert_alpha', True))
            elif asset_type == 'sound':
                self.load_sound(name)
            elif asset_type == 'font':
                size = asset_info.get('size', 24)
                self.load_font(name, size)
            elif asset_type == 'data':
                self.load_data(name)
                
    def cleanup(self) -> None:
        """Clean up all loaded assets."""
        self.images.clear()
        self.sounds.clear()
        self.fonts.clear()
        self.data.clear()
        self.image_refs.clear()
        self.sound_refs.clear()
        self.font_refs.clear()
        
    def get_memory_usage(self) -> Dict[str, int]:
        """Get memory usage statistics."""
        return {
            'images': len(self.images),
            'sounds': len(self.sounds),
            'fonts': len(self.fonts),
            'data_files': len(self.data)
        }
