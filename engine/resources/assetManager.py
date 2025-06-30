"""
Asset management system for loading and caching game assets.
"""

import pygame
import os
import json
from typing import Dict, Optional, Any, List
from pathlib import Path
from engine.logger import Logger, LogType

class AssetManager:
    """
    Manages loading, caching, and retrieval of game assets.
    """
    
    def __init__(self, basePath: str = "assets"):
        self.basePath = Path(basePath)
        
        # Asset caches
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.data: Dict[str, Any] = {}
        
        # Reference counting for memory management
        self.imageRefs: Dict[str, int] = {}
        self.soundRefs: Dict[str, int] = {}
        self.fontRefs: Dict[str, int] = {}
        
        # Default font settings
        self.defaultFontName: Optional[str] = None
        self.defaultFontSize: int = 24
        self._defaultFontCache: Optional[pygame.font.Font] = None
        
        # Asset directories
        self.imagePath = self.basePath / "images"
        self.soundPath = self.basePath / "sounds"
        self.fontPath = self.basePath / "fonts"
        self.dataPath = self.basePath / "data"
        
        # Supported formats
        self.imageFormats = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tga'}
        self.soundFormats = {'.wav', '.ogg', '.mp3'}
        self.fontFormats = {'.ttf', '.otf'}
        
        # Create directories if they don't exist
        self._createDirectories()
        
    def _createDirectories(self) -> None:
        """Create asset directories if they don't exist."""
        directories = [self.basePath, self.imagePath, self.soundPath, 
                      self.fontPath, self.dataPath]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
    def _getFullPath(self, asset_type: str, name: str) -> Path:
        """Get the full path for an asset."""
        type_paths = {
            'image': self.imagePath,
            'sound': self.soundPath,
            'font': self.fontPath,
            'data': self.dataPath
        }
        return type_paths[asset_type] / name
        
    def loadImage(self, name: str, convert_alpha: bool = True) -> Optional[pygame.Surface]:
        """
        Load an image asset.
        
        Args:
            name: Image filename or path relative to images directory
            convert_alpha: Whether to convert the image for optimal blitting
        """
        if name in self.images:
            self.imageRefs[name] = self.imageRefs.get(name, 0) + 1
            return self.images[name]
            
        # Try to find the file
        image_path = self._findAssetFile(self.imagePath, name, self.imageFormats)
        if not image_path:
            print(f"Could not find image: {name}")
            Logger.warning(f"Could not find image: {name}")
            return None
            
        try:
            surface = pygame.image.load(str(image_path))
            if convert_alpha:
                surface = surface.convert_alpha()
            else:
                surface = surface.convert()
                
            self.images[name] = surface
            self.imageRefs[name] = 1
            return surface
            
        except pygame.error as e:
            print(f"Could not load image {name}: {e}")
            Logger.error(f"Could not load image {name}: {e}")
            return None
            
    def loadSound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """Load a sound asset."""
        if name in self.sounds:
            self.soundRefs[name] = self.soundRefs.get(name, 0) + 1
            return self.sounds[name]
            
        sound_path = self._findAssetFile(self.soundPath, name, self.soundFormats)
        if not sound_path:
            print(f"Could not find sound: {name}")
            Logger.warning(f"Could not find sound: {name}")
            return None
            
        try:
            sound = pygame.mixer.Sound(str(sound_path))
            self.sounds[name] = sound
            self.soundRefs[name] = 1
            return sound
            
        except pygame.error as e:
            print(f"Could not load sound {name}: {e}")
            Logger.error(f"Could not load sound {name}: {e}")
            return None
            
    def loadFont(self, name: str, size: int = 24) -> Optional[pygame.font.Font]:
        """Load a font asset."""
        font_key = f"{name}_{size}"
        
        if font_key in self.fonts:
            self.fontRefs[font_key] = self.fontRefs.get(font_key, 0) + 1
            return self.fonts[font_key]
            
        # Try system font first
        if name in pygame.font.get_fonts():
            font = pygame.font.SysFont(name, size)
            self.fonts[font_key] = font
            self.fontRefs[font_key] = 1
            return font
            
        # Try loading from file
        font_path = self._findAssetFile(self.fontPath, name, self.fontFormats)
        if not font_path:
            print(f"Could not find font: {name}, using default")
            Logger.warning(f"Could not find font: {name}, using default")
            font = pygame.font.Font(None, size)
            self.fonts[font_key] = font
            self.fontRefs[font_key] = 1
            return font
            
        try:
            font = pygame.font.Font(str(font_path), size)
            self.fonts[font_key] = font
            self.fontRefs[font_key] = 1
            return font
            
        except pygame.error as e:
            print(f"Could not load font {name}: {e}, using default")
            Logger.error(f"Could not load font {name}: {e}, using default")
            font = pygame.font.Font(None, size)
            self.fonts[font_key] = font
            self.fontRefs[font_key] = 1
            return font
            
    def loadData(self, name: str) -> Optional[Any]:
        """Load data from JSON file."""
        if name in self.data:
            return self.data[name]
            
        data_path = self.dataPath / name
        if not data_path.suffix:
            data_path = data_path.with_suffix('.json')
            
        if not data_path.exists():
            print(f"Could not find data file: {name}")
            Logger.warning(f"Could not find data file: {name}")
            return None
            
        try:
            with open(data_path, 'r') as f:
                data = json.load(f)
            self.data[name] = data
            return data
            
        except (json.JSONDecodeError, IOError) as e:
            print(f"Could not load data {name}: {e}")
            Logger.error(f"Could not load data {name}: {e}")
            return None
            
    def _findAssetFile(self, base_path: Path, name: str, extensions: set) -> Optional[Path]:
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
        
    def getImage(self, name: str) -> Optional[pygame.Surface]:
        """Get a loaded image (doesn't increment reference count)."""
        return self.images.get(name)
        
    def getSound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """Get a loaded sound (doesn't increment reference count)."""
        return self.sounds.get(name)
        
    def getFont(self, name: str, size: int = 24) -> Optional[pygame.font.Font]:
        """Get a loaded font (doesn't increment reference count)."""
        font_key = f"{name}_{size}"
        return self.fonts.get(font_key)
        
    def getData(self, name: str) -> Optional[Any]:
        """Get loaded data."""
        return self.data.get(name)
        
    def releaseImage(self, name: str) -> None:
        """Release a reference to an image."""
        if name in self.imageRefs:
            self.imageRefs[name] -= 1
            if self.imageRefs[name] <= 0:
                del self.images[name]
                del self.imageRefs[name]
                
    def releaseSound(self, name: str) -> None:
        """Release a reference to a sound."""
        if name in self.soundRefs:
            self.soundRefs[name] -= 1
            if self.soundRefs[name] <= 0:
                del self.sounds[name]
                del self.soundRefs[name]
                
    def releaseFont(self, name: str, size: int = 24) -> None:
        """Release a reference to a font."""
        font_key = f"{name}_{size}"
        if font_key in self.fontRefs:
            self.fontRefs[font_key] -= 1
            if self.fontRefs[font_key] <= 0:
                del self.fonts[font_key]
                del self.fontRefs[font_key]
                
    def createSurface(self, width: int, height: int, color: pygame.Color = None) -> pygame.Surface:
        """Create a new surface with optional color fill."""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        if color:
            surface.fill(color)
        return surface
        
    def createGradient(self, width: int, height: int, 
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
        
    def sliceSpritesheet(self, image_name: str, tile_width: int, tile_height: int,
                         margin: int = 0, spacing: int = 0) -> List[pygame.Surface]:
        """Slice a spritesheet into individual sprites."""
        image = self.getImage(image_name)
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
        
    def preloadAssets(self, asset_list: List[Dict[str, Any]]) -> None:
        """Preload a list of assets."""
        for asset_info in asset_list:
            asset_type = asset_info.get('type')
            name = asset_info.get('name')
            
            if asset_type == 'image':
                self.loadImage(name, asset_info.get('convert_alpha', True))
            elif asset_type == 'sound':
                self.loadSound(name)
            elif asset_type == 'font':
                size = asset_info.get('size', 24)
                self.loadFont(name, size)
            elif asset_type == 'data':
                self.loadData(name)
                
    def cleanup(self) -> None:
        """Clean up all loaded assets."""
        self.images.clear()
        self.sounds.clear()
        self.fonts.clear()
        self.data.clear()
        self.imageRefs.clear()
        self.soundRefs.clear()
        self.fontRefs.clear()
        
    def getMemoryUsage(self) -> Dict[str, int]:
        """Get memory usage statistics."""
        return {
            'images': len(self.images),
            'sounds': len(self.sounds),
            'fonts': len(self.fonts),
            'data_files': len(self.data)
        }
    
    def setDefaultFont(self, font_name: str, size: int = 24) -> None:
        """Set the default font for the application."""
        self.defaultFontName = font_name
        self.defaultFontSize = size
        self._defaultFontCache = None  # Reset cache
        
        # Load the font to ensure it exists
        self.loadFont(font_name, size)
        
    def getDefaultFont(self, size: int = None) -> pygame.font.Font:
        """Get the default font, optionally with a different size."""
        if size is None:
            size = self.defaultFontSize
            
        if self.defaultFontName:
            # Use the set default font
            if size == self.defaultFontSize and self._defaultFontCache:
                return self._defaultFontCache
                
            font = self.loadFont(self.defaultFontName, size)
            if font and size == self.defaultFontSize:
                self._defaultFontCache = font
            return font or pygame.font.Font(None, size)
        else:
            # Fall back to pygame default
            return pygame.font.Font(None, size)