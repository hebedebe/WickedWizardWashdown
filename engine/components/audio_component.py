"""
Audio component for actors.
"""

import pygame
from ..core.actor import Component


class AudioComponent(Component):
    """
    Component for playing audio using pygame.mixer.
    """
    
    def __init__(self):
        super().__init__()
        self.sounds: dict = {}
        self.music_volume = 1.0
        self.sfx_volume = 1.0
        
    def load_sound(self, name: str, path: str) -> None:
        """Load a sound effect."""
        try:
            sound = pygame.mixer.Sound(path)
            self.sounds[name] = sound
        except pygame.error as e:
            print(f"Could not load sound {path}: {e}")
            
    def play_sound(self, name: str, volume: float = 1.0) -> None:
        """Play a sound effect."""
        if name in self.sounds:
            sound = self.sounds[name]
            sound.set_volume(volume * self.sfx_volume)
            sound.play()
            
    def stop_sound(self, name: str) -> None:
        """Stop a playing sound."""
        if name in self.sounds:
            self.sounds[name].stop()
            
    def play_music(self, path: str, loops: int = -1, volume: float = 1.0) -> None:
        """Play background music."""
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume * self.music_volume)
            pygame.mixer.music.play(loops)
        except pygame.error as e:
            print(f"Could not play music {path}: {e}")
            
    def stop_music(self) -> None:
        """Stop background music."""
        pygame.mixer.music.stop()
        
    def update(self, dt: float) -> None:
        """Update audio component."""
        pass
