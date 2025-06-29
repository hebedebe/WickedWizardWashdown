"""
Core components for the game engine.
Includes rendering, physics, input, and audio components.
"""

import pygame
from typing import Optional, Callable, List, Tuple
from .actor import Component

class SpriteComponent(Component):
    """
    Component for rendering sprites using pygame.Surface.
    """
    
    def __init__(self, surface: pygame.Surface = None, 
                 color: pygame.Color = None,
                 size: pygame.Vector2 = None):
        super().__init__()
        self.surface = surface
        self.color = color or pygame.Color(255, 255, 255)
        self.size = size or pygame.Vector2(32, 32)
        
        # Create a default surface if none provided
        if not self.surface:
            self.surface = pygame.Surface((int(self.size.x), int(self.size.y)))
            self.surface.fill(self.color)
            
        self.rect = self.surface.get_rect()
        self.offset = pygame.Vector2(0, 0)  # Offset from actor position
        self.flip_x = False
        self.flip_y = False
        self.alpha = 255
        
    def set_surface(self, surface: pygame.Surface) -> None:
        """Set the sprite surface."""
        self.surface = surface
        self.rect = surface.get_rect()
        
    def set_color(self, color: pygame.Color) -> None:
        """Set sprite color (creates colored surface)."""
        self.color = color
        if self.surface:
            self.surface.fill(color)
            
    def update(self, dt: float) -> None:
        """Update sprite position from actor transform."""
        if self.actor:
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

class PhysicsComponent(Component):
    """
    Simple physics component using pygame.Vector2 for velocity and acceleration.
    """
    
    def __init__(self):
        super().__init__()
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)
        self.drag = 0.0  # Air resistance
        self.gravity = pygame.Vector2(0, 0)
        self.mass = 1.0
        self.bounce = 0.0  # Bounciness factor (0-1)
        self.friction = 0.0
        
        # Collision
        self.collider: Optional[pygame.Rect] = None
        self.is_trigger = False
        self.collision_layers = []
        
    def apply_force(self, force: pygame.Vector2) -> None:
        """Apply a force to the physics body."""
        self.acceleration += force / self.mass
        
    def apply_impulse(self, impulse: pygame.Vector2) -> None:
        """Apply an impulse (instant velocity change)."""
        self.velocity += impulse / self.mass
        
    def update(self, dt: float) -> None:
        """Update physics simulation."""
        if not self.actor:
            return
            
        # Apply gravity
        self.acceleration += self.gravity * dt
        
        # Apply drag
        if self.drag > 0:
            drag_force = self.velocity * -self.drag
            self.acceleration += drag_force
            
        # Update velocity and position
        self.velocity += self.acceleration * dt
        self.actor.transform.local_position += self.velocity * dt
        
        # Update collider position
        if self.collider:
            pos = self.actor.transform.world_position
            self.collider.center = (int(pos.x), int(pos.y))
            
        # Reset acceleration for next frame
        self.acceleration = pygame.Vector2(0, 0)
        
    def check_collision(self, other: 'PhysicsComponent') -> bool:
        """Check collision with another physics component."""
        if not self.collider or not other.collider:
            return False
        return self.collider.colliderect(other.collider)

class InputComponent(Component):
    """
    Component for handling input events.
    """
    
    def __init__(self):
        super().__init__()
        self.key_handlers: dict = {}
        self.mouse_handlers: dict = {}
        self.input_handlers: List[Callable] = []
        
    def bind_key(self, key: int, callback: Callable, event_type: int = pygame.KEYDOWN) -> None:
        """Bind a key to a callback function."""
        if event_type not in self.key_handlers:
            self.key_handlers[event_type] = {}
        self.key_handlers[event_type][key] = callback
        
    def bind_mouse(self, button: int, callback: Callable, event_type: int = pygame.MOUSEBUTTONDOWN) -> None:
        """Bind a mouse button to a callback function."""
        if event_type not in self.mouse_handlers:
            self.mouse_handlers[event_type] = {}
        self.mouse_handlers[event_type][button] = callback
        
    def add_input_handler(self, handler: Callable) -> None:
        """Add a general input handler."""
        self.input_handlers.append(handler)
        
    def update(self, dt: float) -> None:
        """Check for continuous input (held keys)."""
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        
        # Process held keys
        for handler in self.input_handlers:
            handler(keys, mouse_buttons, dt)
            
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle discrete input events."""
        if event.type in self.key_handlers:
            if event.key in self.key_handlers[event.type]:
                self.key_handlers[event.type][event.key](event)
                
        if event.type in self.mouse_handlers:
            if event.button in self.mouse_handlers[event.type]:
                self.mouse_handlers[event.type][event.button](event)

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



class HealthComponent(Component):
    """
    Component for managing actor health/hit points.
    """
    
    def __init__(self, max_health: float = 100.0):
        super().__init__()
        self.max_health = max_health
        self.current_health = max_health
        self.invulnerable = False
        self.invulnerability_time = 0.0
        
        # Events
        self.on_damage_taken: Optional[Callable] = None
        self.on_health_changed: Optional[Callable] = None
        self.on_death: Optional[Callable] = None
        
    def take_damage(self, amount: float) -> None:
        """Apply damage to this component."""
        if self.invulnerable:
            return
            
        self.current_health -= amount
        self.current_health = max(0, self.current_health)
        
        if self.on_damage_taken:
            self.on_damage_taken(amount)
        if self.on_health_changed:
            self.on_health_changed(self.current_health, self.max_health)
            
        if self.current_health <= 0 and self.on_death:
            self.on_death()
            
    def heal(self, amount: float) -> None:
        """Heal this component."""
        self.current_health += amount
        self.current_health = min(self.max_health, self.current_health)
        
        if self.on_health_changed:
            self.on_health_changed(self.current_health, self.max_health)
            
    def set_invulnerable(self, duration: float) -> None:
        """Make temporarily invulnerable."""
        self.invulnerable = True
        self.invulnerability_time = duration
        
    def update(self, dt: float) -> None:
        """Update health component."""
        if self.invulnerable:
            self.invulnerability_time -= dt
            if self.invulnerability_time <= 0:
                self.invulnerable = False
                
    @property
    def health_percentage(self) -> float:
        """Get health as a percentage (0-1)."""
        return self.current_health / self.max_health if self.max_health > 0 else 0
        
    @property
    def is_alive(self) -> bool:
        """Check if actor is alive."""
        return self.current_health > 0


class TextComponent(Component):
    """Component for rendering text that can be animated."""
    
    def __init__(self, text: str = "", font: pygame.font.Font = None, 
                 color: pygame.Color = pygame.Color(255, 255, 255),
                 size: int = 24):
        super().__init__()
        self.text = text
        self.font = font
        self.color = color
        self.size = size
        self.surface = None
        self.rect = None
        self.alpha = 255
        self.offset = pygame.Vector2(0, 0)
        
        # Auto-create font if not provided
        if not self.font:
            try:
                # Try to use the game's default font
                from engine import Game
                self.font = Game.get_instance().asset_manager.get_default_font(self.size)
            except:
                # Fallback to pygame default
                self.font = pygame.font.Font(None, self.size)
        
        self._render_text()
        
    def set_text(self, text: str) -> None:
        """Update the text content."""
        self.text = text
        self._render_text()
        
    def set_font(self, font: pygame.font.Font) -> None:
        """Update the font."""
        self.font = font
        self._render_text()
        
    def set_color(self, color: pygame.Color) -> None:
        """Update the text color."""
        self.color = color
        self._render_text()
        
    def set_alpha(self, alpha: int) -> None:
        """Set text transparency (0-255)."""
        self.alpha = max(0, min(255, alpha))
        if self.surface:
            self.surface.set_alpha(self.alpha)
            
    def _render_text(self) -> None:
        """Render the text to a surface."""
        if self.font and self.text:
            self.surface = self.font.render(self.text, True, self.color)
            self.surface.set_alpha(self.alpha)
            self.rect = self.surface.get_rect()
            
    def update(self, dt: float) -> None:
        """Update text position from actor transform."""
        if self.actor and self.rect:
            pos = self.actor.transform.world_position + self.offset
            self.rect.center = (int(pos.x), int(pos.y))
            # Debug: print position updates
            # print(f"Text position: {pos}, Actor position: {self.actor.transform.position}")
            
    def render(self, screen: pygame.Surface) -> None:
        """Render the text to the screen."""
        if self.surface and self.rect:
            screen.blit(self.surface, self.rect)
