"""
Advanced animation component with file loading and property animation capabilities.
Supports YAML animation definitions for human-readable animation data.
Can animate component properties, transform values, and includes built-in easing functions.
"""

import pygame
import yaml
import os
import json
import math
from typing import Dict, List, Optional, Union, Any, Tuple, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

from ..core.actor import Component
from ..components import SpriteComponent


class EasingType(Enum):
    """Built-in easing functions for smooth animations."""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    BOUNCE = "bounce"
    ELASTIC = "elastic"
    SINE = "sine"
    COSINE = "cosine"
    SINE_WAVE = "sine_wave"  # Continuous sine wave
    PULSE = "pulse"          # Pulse effect
    SMOOTH_STEP = "smooth_step"


def apply_easing(t: float, easing: EasingType) -> float:
    """
    Apply easing function to a normalized time value (0-1).
    
    Args:
        t: Time value between 0 and 1
        easing: Easing function to apply
        
    Returns:
        Eased value between 0 and 1
    """
    t = max(0.0, min(1.0, t))  # Clamp to 0-1
    
    if easing == EasingType.LINEAR:
        return t
    elif easing == EasingType.EASE_IN:
        return t * t
    elif easing == EasingType.EASE_OUT:
        return 1 - (1 - t) * (1 - t)
    elif easing == EasingType.EASE_IN_OUT:
        if t < 0.5:
            return 2 * t * t
        else:
            return 1 - 2 * (1 - t) * (1 - t)
    elif easing == EasingType.BOUNCE:
        if t < 0.36:
            return 7.5625 * t * t
        elif t < 0.72:
            t -= 0.545
            return 7.5625 * t * t + 0.75
        elif t < 0.9:
            t -= 0.818
            return 7.5625 * t * t + 0.9375
        else:
            t -= 0.955
            return 7.5625 * t * t + 0.984375
    elif easing == EasingType.ELASTIC:
        if t == 0 or t == 1:
            return t
        return -(2 ** (10 * (t - 1))) * math.sin((t - 1.1) * 5 * math.pi)
    elif easing == EasingType.SINE:
        return math.sin(t * math.pi / 2)
    elif easing == EasingType.COSINE:
        return 1 - math.cos(t * math.pi / 2)
    elif easing == EasingType.SINE_WAVE:
        return (math.sin(t * 2 * math.pi) + 1) / 2  # 0-1 sine wave
    elif easing == EasingType.PULSE:
        return abs(math.sin(t * math.pi))
    elif easing == EasingType.SMOOTH_STEP:
        return t * t * (3 - 2 * t)
    else:
        return t


@dataclass
class PropertyAnimation:
    """Animates a property on a component or transform over time."""
    target: str  # "transform.position.x", "SpriteComponent.alpha", etc.
    start_value: Union[float, int, tuple]
    end_value: Union[float, int, tuple]
    duration: float
    easing: EasingType = EasingType.LINEAR
    loop: bool = False
    ping_pong: bool = False
    offset: float = 0.0  # Start time offset
    
    # For sine waves and continuous animations
    frequency: Optional[float] = None  # For sine wave frequency
    amplitude: Optional[float] = None  # For sine wave amplitude
    base_value: Optional[Union[float, int, tuple]] = None  # Base value for oscillation


@dataclass
class AnimationFrame:
    """Represents a single animation frame."""
    source: str  # Image file path or spritesheet reference
    duration: float = 0.1  # Duration in seconds
    offset_x: int = 0  # X offset for this frame
    offset_y: int = 0  # Y offset for this frame
    flip_x: bool = False  # Flip horizontally
    flip_y: bool = False  # Flip vertically
    
    # For spritesheets
    rect_x: Optional[int] = None  # X position in spritesheet
    rect_y: Optional[int] = None  # Y position in spritesheet
    rect_w: Optional[int] = None  # Width in spritesheet
    rect_h: Optional[int] = None  # Height in spritesheet
    
    # Property animations for this frame
    property_animations: Optional[List[PropertyAnimation]] = None


@dataclass
class AnimationSequence:
    """Represents a complete animation sequence."""
    name: str
    frames: List[AnimationFrame]
    loop: bool = True
    ping_pong: bool = False  # Play forward then backward
    next_animation: Optional[str] = None  # Animation to play after this one
    
    # Events
    on_start: Optional[str] = None  # Callback when animation starts
    on_end: Optional[str] = None    # Callback when animation ends
    on_loop: Optional[str] = None   # Callback when animation loops
    
    # Frame events - dict of frame_index: callback_name
    frame_events: Optional[Dict[int, str]] = None
    
    # Property animations that run for the entire sequence
    property_animations: Optional[List[PropertyAnimation]] = None


@dataclass
class AnimationSet:
    """Collection of animations for a character/object."""
    name: str
    base_path: str  # Base path for image files
    default_animation: Optional[str] = None
    animations: Dict[str, AnimationSequence] = None
    
    def __post_init__(self):
        if self.animations is None:
            self.animations = {}


class FileAnimationComponent(Component):
    """
    File-based animation component with property animation and advanced features.
    Loads animations from YAML/JSON files and can animate component properties.
    """
    
    def __init__(self, animation_file: str = None):
        super().__init__()
        
        # Animation data
        self.animation_set: Optional[AnimationSet] = None
        self.loaded_surfaces: Dict[str, pygame.Surface] = {}  # Cache for loaded images
        
        # Current state
        self.current_animation: Optional[str] = None
        self.current_sequence: Optional[AnimationSequence] = None
        self.current_frame_index: int = 0
        self.frame_time: float = 0.0
        self.playing: bool = False
        self.paused: bool = False
        
        # Playback settings
        self.animation_speed: float = 1.0
        self.ping_pong_direction: int = 1  # 1 for forward, -1 for backward
        
        # Property animation tracking
        self.active_property_animations: List[Tuple[PropertyAnimation, float]] = []  # (animation, start_time)
        self.animation_start_time: float = 0.0
        
        # Events
        self.event_callbacks: Dict[str, Callable] = {}
        
        # Load animation file if provided
        if animation_file:
            self.load_animation_file(animation_file)
    
    def load_animation_file(self, file_path: str) -> bool:
        """
        Load animations from a YAML or JSON file.
        
        Args:
            file_path: Path to the animation definition file
            
        Returns:
            True if loaded successfully
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                print(f"Animation file not found: {file_path}")
                return False
            
            # Load based on file extension
            with open(path, 'r') as f:
                if path.suffix.lower() == '.yaml' or path.suffix.lower() == '.yml':
                    data = yaml.safe_load(f)
                elif path.suffix.lower() == '.json':
                    data = json.load(f)
                else:
                    print(f"Unsupported animation file format: {path.suffix}")
                    return False
            
            # Parse the data
            self.animation_set = self._parse_animation_data(data, path.parent)
            
            # Load default animation if specified
            if (self.animation_set.default_animation and 
                self.animation_set.default_animation in self.animation_set.animations):
                self.set_animation(self.animation_set.default_animation)
            
            print(f"Loaded animation set: {self.animation_set.name}")
            return True
            
        except Exception as e:
            print(f"Error loading animation file {file_path}: {e}")
            return False
    
    def _parse_animation_data(self, data: Dict[str, Any], base_dir: Path) -> AnimationSet:
        """Parse animation data from loaded file."""
        # Create animation set
        anim_set = AnimationSet(
            name=data.get('name', 'Unknown'),
            base_path=str(base_dir / data.get('base_path', '')),
            default_animation=data.get('default_animation')
        )
        
        # Parse animations
        animations_data = data.get('animations', {})
        for anim_name, anim_data in animations_data.items():
            sequence = self._parse_animation_sequence(anim_name, anim_data)
            anim_set.animations[anim_name] = sequence
        
        return anim_set
    
    def _parse_animation_sequence(self, name: str, data: Dict[str, Any]) -> AnimationSequence:
        """Parse a single animation sequence."""
        # Parse frames
        frames = []
        frames_data = data.get('frames', [])
        
        for frame_data in frames_data:
            if isinstance(frame_data, str):
                # Simple format: just image path
                frame = AnimationFrame(source=frame_data)
            elif isinstance(frame_data, dict):
                # Parse property animations for this frame
                prop_anims = None
                if 'property_animations' in frame_data:
                    prop_anims = self._parse_property_animations(frame_data['property_animations'])
                
                # Full format with all properties
                frame = AnimationFrame(
                    source=frame_data['source'],
                    duration=frame_data.get('duration', 0.1),
                    offset_x=frame_data.get('offset_x', 0),
                    offset_y=frame_data.get('offset_y', 0),
                    flip_x=frame_data.get('flip_x', False),
                    flip_y=frame_data.get('flip_y', False),
                    rect_x=frame_data.get('rect_x'),
                    rect_y=frame_data.get('rect_y'),
                    rect_w=frame_data.get('rect_w'),
                    rect_h=frame_data.get('rect_h'),
                    property_animations=prop_anims
                )
            else:
                continue
            
            frames.append(frame)
        
        # Parse sequence-level property animations
        sequence_prop_anims = None
        if 'property_animations' in data:
            sequence_prop_anims = self._parse_property_animations(data['property_animations'])
        
        # Create sequence
        sequence = AnimationSequence(
            name=name,
            frames=frames,
            loop=data.get('loop', True),
            ping_pong=data.get('ping_pong', False),
            next_animation=data.get('next_animation'),
            on_start=data.get('on_start'),
            on_end=data.get('on_end'),
            on_loop=data.get('on_loop'),
            frame_events=data.get('frame_events'),
            property_animations=sequence_prop_anims
        )
        
        return sequence
    
    def _parse_property_animations(self, prop_anims_data: List[Dict[str, Any]]) -> List[PropertyAnimation]:
        """Parse property animations from data."""
        prop_anims = []
        
        for prop_data in prop_anims_data:
            # Parse easing
            easing_str = prop_data.get('easing', 'linear')
            try:
                easing = EasingType(easing_str)
            except ValueError:
                easing = EasingType.LINEAR
            
            prop_anim = PropertyAnimation(
                target=prop_data['target'],
                start_value=prop_data.get('start_value', 0),
                end_value=prop_data.get('end_value', 1),
                duration=prop_data.get('duration', 1.0),
                easing=easing,
                loop=prop_data.get('loop', False),
                ping_pong=prop_data.get('ping_pong', False),
                offset=prop_data.get('offset', 0.0),
                frequency=prop_data.get('frequency'),
                amplitude=prop_data.get('amplitude'),
                base_value=prop_data.get('base_value')
            )
            prop_anims.append(prop_anim)
        
        return prop_anims
    
    def _load_frame_surface(self, frame: AnimationFrame) -> Optional[pygame.Surface]:
        """Load the pygame surface for a frame."""
        if not self.animation_set:
            return None
        
        # Check cache first
        cache_key = f"{frame.source}_{frame.rect_x}_{frame.rect_y}_{frame.rect_w}_{frame.rect_h}"
        if cache_key in self.loaded_surfaces:
            surface = self.loaded_surfaces[cache_key]
        else:
            # Load from file
            image_path = os.path.join(self.animation_set.base_path, frame.source)
            
            try:
                surface = pygame.image.load(image_path).convert_alpha()
                
                # Extract from spritesheet if needed
                if all(x is not None for x in [frame.rect_x, frame.rect_y, frame.rect_w, frame.rect_h]):
                    rect = pygame.Rect(frame.rect_x, frame.rect_y, frame.rect_w, frame.rect_h)
                    surface = surface.subsurface(rect).copy()
                
                # Cache the surface
                self.loaded_surfaces[cache_key] = surface
                
            except pygame.error as e:
                print(f"Error loading image {image_path}: {e}")
                return None
        
        # Apply transformations
        if frame.flip_x or frame.flip_y:
            surface = pygame.transform.flip(surface, frame.flip_x, frame.flip_y)
        
        return surface
    
    def set_animation(self, animation_name: str, restart: bool = True) -> bool:
        """
        Set the current animation.
        
        Args:
            animation_name: Name of the animation to play
            restart: Whether to restart if already playing this animation
            
        Returns:
            True if animation was set successfully
        """
        if not self.animation_set or animation_name not in self.animation_set.animations:
            return False
        
        # Don't restart if already playing the same animation
        if not restart and self.current_animation == animation_name and self.playing:
            return True
        
        # Set new animation
        self.current_animation = animation_name
        self.current_sequence = self.animation_set.animations[animation_name]
        self.current_frame_index = 0
        self.frame_time = 0.0
        self.ping_pong_direction = 1
        self.animation_start_time = 0.0  # Will be set in update
        
        # Start property animations
        self._start_property_animations()
        
        # Trigger start event
        if self.current_sequence.on_start:
            self._trigger_event(self.current_sequence.on_start)
        
        return True
    
    def _start_property_animations(self) -> None:
        """Start property animations for the current sequence."""
        import time
        current_time = time.time()
        self.animation_start_time = current_time
        self.active_property_animations.clear()
        
        if self.current_sequence and self.current_sequence.property_animations:
            for prop_anim in self.current_sequence.property_animations:
                start_time = current_time + prop_anim.offset
                self.active_property_animations.append((prop_anim, start_time))
    
    def play(self, animation_name: str = None) -> None:
        """Start playing an animation."""
        if animation_name:
            self.set_animation(animation_name)
        
        self.playing = True
        self.paused = False
    
    def stop(self) -> None:
        """Stop the current animation."""
        self.playing = False
        self.paused = False
        self.current_frame_index = 0
        self.frame_time = 0.0
    
    def pause(self) -> None:
        """Pause the current animation."""
        self.paused = True
    
    def resume(self) -> None:
        """Resume a paused animation."""
        if self.playing:
            self.paused = False
    
    def get_current_frame(self) -> Optional[AnimationFrame]:
        """Get the current animation frame."""
        if not self.current_sequence or not self.current_sequence.frames:
            return None
        
        if 0 <= self.current_frame_index < len(self.current_sequence.frames):
            return self.current_sequence.frames[self.current_frame_index]
        
        return None
    
    def add_event_callback(self, event_name: str, callback: Callable) -> None:
        """Add a callback for animation events."""
        self.event_callbacks[event_name] = callback
    
    def _trigger_event(self, event_name: str) -> None:
        """Trigger an animation event."""
        if event_name in self.event_callbacks:
            self.event_callbacks[event_name]()
    
    def update(self, dt: float) -> None:
        """Update the animation."""
        if not self.playing or self.paused or not self.current_sequence:
            return
        
        # Update property animations
        self._update_property_animations()
        
        # Get current frame
        current_frame = self.get_current_frame()
        if not current_frame:
            return
        
        # Update frame time
        self.frame_time += dt * self.animation_speed
        
        # Check if it's time to advance frame
        if self.frame_time >= current_frame.duration:
            self.frame_time = 0.0
            
            # Trigger frame event if exists
            if (self.current_sequence.frame_events and 
                self.current_frame_index in self.current_sequence.frame_events):
                event_name = self.current_sequence.frame_events[self.current_frame_index]
                self._trigger_event(event_name)
            
            # Advance frame
            if self.current_sequence.ping_pong:
                self._advance_ping_pong_frame()
            else:
                self._advance_normal_frame()
            
            # Update sprite component with new frame
            self._update_sprite_component()
    
    def _update_property_animations(self) -> None:
        """Update all active property animations."""
        import time
        current_time = time.time()
        
        for prop_anim, start_time in self.active_property_animations[:]:  # Copy list for safe iteration
            if current_time < start_time:
                continue  # Animation hasn't started yet
            
            # Calculate animation progress
            elapsed_time = current_time - start_time
            
            if prop_anim.frequency is not None:
                # Continuous sine wave animation
                self._update_sine_wave_property(prop_anim, elapsed_time)
            else:
                # Regular property animation
                progress = elapsed_time / prop_anim.duration
                
                if progress >= 1.0:
                    if prop_anim.loop:
                        # Reset for loop
                        if prop_anim.ping_pong:
                            # Swap start and end values for ping-pong
                            prop_anim.start_value, prop_anim.end_value = prop_anim.end_value, prop_anim.start_value
                        # Reset start time
                        start_time = current_time
                        # Update the tuple in the list
                        index = self.active_property_animations.index((prop_anim, start_time))
                        self.active_property_animations[index] = (prop_anim, start_time)
                        progress = 0.0
                    else:
                        # Animation finished
                        progress = 1.0
                        self.active_property_animations.remove((prop_anim, start_time))
                
                # Apply easing and set property value
                eased_progress = apply_easing(progress, prop_anim.easing)
                self._set_property_value(prop_anim, eased_progress)
    
    def _update_sine_wave_property(self, prop_anim: PropertyAnimation, elapsed_time: float) -> None:
        """Update a sine wave property animation."""
        if prop_anim.frequency is None or prop_anim.amplitude is None:
            return
        
        # Calculate sine wave value
        wave_value = math.sin(elapsed_time * prop_anim.frequency * 2 * math.pi)
        
        # Apply amplitude and base value
        base = prop_anim.base_value if prop_anim.base_value is not None else 0
        if isinstance(base, (list, tuple)):
            # Handle vector values
            result = []
            amplitude = prop_anim.amplitude
            if isinstance(amplitude, (list, tuple)):
                for i, b in enumerate(base):
                    amp = amplitude[i] if i < len(amplitude) else amplitude[0]
                    result.append(b + wave_value * amp)
            else:
                for b in base:
                    result.append(b + wave_value * amplitude)
            value = tuple(result)
        else:
            value = base + wave_value * prop_anim.amplitude
        
        # Set the property directly
        self._set_property_direct(prop_anim.target, value)
    
    def _set_property_value(self, prop_anim: PropertyAnimation, progress: float) -> None:
        """Set a property value based on animation progress."""
        start = prop_anim.start_value
        end = prop_anim.end_value
        
        # Interpolate between start and end values
        if isinstance(start, (list, tuple)) and isinstance(end, (list, tuple)):
            # Handle vector values
            value = []
            for i in range(len(start)):
                end_val = end[i] if i < len(end) else end[0]
                interpolated = start[i] + (end_val - start[i]) * progress
                value.append(interpolated)
            value = tuple(value)
        else:
            # Handle scalar values
            value = start + (end - start) * progress
        
        self._set_property_direct(prop_anim.target, value)
    
    def _set_property_direct(self, target: str, value: Any) -> None:
        """Set a property value directly using dot notation."""
        if not self.actor:
            return
        
        parts = target.split('.')
        obj = self.actor
        
        try:
            # Navigate to the target object
            for part in parts[:-1]:
                if part == 'transform':
                    obj = obj.transform
                elif part.endswith('Component'):
                    # Get component by class name
                    for component in obj.component_list:
                        if type(component).__name__ == part:
                            obj = component
                            break
                    else:
                        return  # Component not found
                else:
                    obj = getattr(obj, part)
            
            # Set the final property
            property_name = parts[-1]
            
            # Handle special cases for pygame types
            if property_name in ['position', 'local_position', 'world_position']:
                if isinstance(value, (list, tuple)) and len(value) >= 2:
                    setattr(obj, property_name, pygame.Vector2(value[0], value[1]))
                else:
                    print(f"Warning: Invalid position value: {value}")
            elif property_name in ['scale', 'local_scale', 'world_scale']:
                if isinstance(value, (list, tuple)) and len(value) >= 2:
                    setattr(obj, property_name, pygame.Vector2(value[0], value[1]))
                else:
                    print(f"Warning: Invalid scale value: {value}")
            elif property_name in ['rotation', 'local_rotation', 'world_rotation']:
                setattr(obj, property_name, float(value))
                if hasattr(obj, 'mark_dirty'):
                    obj.mark_dirty()
            else:
                # Regular property
                setattr(obj, property_name, value)
                
        except (AttributeError, IndexError, TypeError) as e:
            print(f"Warning: Could not set property '{target}' to {value}: {e}")
    
    def _advance_normal_frame(self) -> None:
        """Advance frame in normal playback mode."""
        self.current_frame_index += 1
        
        if self.current_frame_index >= len(self.current_sequence.frames):
            if self.current_sequence.loop:
                self.current_frame_index = 0
                # Trigger loop event
                if self.current_sequence.on_loop:
                    self._trigger_event(self.current_sequence.on_loop)
            else:
                # Animation finished
                self.current_frame_index = len(self.current_sequence.frames) - 1
                self.playing = False
                
                # Trigger end event
                if self.current_sequence.on_end:
                    self._trigger_event(self.current_sequence.on_end)
                
                # Play next animation if specified
                if self.current_sequence.next_animation:
                    self.play(self.current_sequence.next_animation)
    
    def _advance_ping_pong_frame(self) -> None:
        """Advance frame in ping-pong mode."""
        self.current_frame_index += self.ping_pong_direction
        
        # Check bounds and reverse direction if needed
        if self.current_frame_index >= len(self.current_sequence.frames):
            if self.current_sequence.loop:
                self.current_frame_index = len(self.current_sequence.frames) - 2
                self.ping_pong_direction = -1
                # Trigger loop event
                if self.current_sequence.on_loop:
                    self._trigger_event(self.current_sequence.on_loop)
            else:
                self.current_frame_index = len(self.current_sequence.frames) - 1
                self.playing = False
                if self.current_sequence.on_end:
                    self._trigger_event(self.current_sequence.on_end)
        elif self.current_frame_index < 0:
            if self.current_sequence.loop:
                self.current_frame_index = 1
                self.ping_pong_direction = 1
                # Trigger loop event
                if self.current_sequence.on_loop:
                    self._trigger_event(self.current_sequence.on_loop)
            else:
                self.current_frame_index = 0
                self.playing = False
                if self.current_sequence.on_end:
                    self._trigger_event(self.current_sequence.on_end)
    
    def _update_sprite_component(self) -> None:
        """Update the actor's sprite component with the current frame."""
        if not self.actor:
            return
        
        sprite = self.actor.get_component(SpriteComponent)
        if not sprite:
            return
        
        current_frame = self.get_current_frame()
        if not current_frame:
            return
        
        # Load frame surface
        surface = self._load_frame_surface(current_frame)
        if surface:
            sprite.set_surface(surface)
            sprite.offset.x = current_frame.offset_x
            sprite.offset.y = current_frame.offset_y
    
    def add_property_animation(self, target: str, start_value: Any, end_value: Any, 
                             duration: float, easing: EasingType = EasingType.LINEAR) -> None:
        """
        Add a property animation programmatically.
        
        Args:
            target: Property path like "transform.position.x" or "SpriteComponent.alpha"
            start_value: Starting value
            end_value: Ending value
            duration: Animation duration in seconds
            easing: Easing function to use
        """
        import time
        prop_anim = PropertyAnimation(
            target=target,
            start_value=start_value,
            end_value=end_value,
            duration=duration,
            easing=easing
        )
        
        start_time = time.time()
        self.active_property_animations.append((prop_anim, start_time))
    
    def add_sine_wave_animation(self, target: str, base_value: Any, amplitude: Any, 
                               frequency: float = 1.0) -> None:
        """
        Add a continuous sine wave animation.
        
        Args:
            target: Property path
            base_value: Base value to oscillate around
            amplitude: Amplitude of oscillation
            frequency: Frequency in Hz
        """
        import time
        prop_anim = PropertyAnimation(
            target=target,
            start_value=0,  # Not used for sine waves
            end_value=0,    # Not used for sine waves
            duration=float('inf'),  # Continuous
            base_value=base_value,
            amplitude=amplitude,
            frequency=frequency,
            loop=True
        )
        
        start_time = time.time()
        self.active_property_animations.append((prop_anim, start_time))
    
    def stop_property_animations(self, target: str = None) -> None:
        """
        Stop property animations.
        
        Args:
            target: If specified, only stop animations for this target
        """
        if target is None:
            self.active_property_animations.clear()
        else:
            self.active_property_animations = [
                (anim, start_time) for anim, start_time in self.active_property_animations
                if anim.target != target
            ]
    
    def get_animation_names(self) -> List[str]:
        """Get list of available animation names."""
        if not self.animation_set:
            return []
        return list(self.animation_set.animations.keys())
    
    def is_playing(self, animation_name: str = None) -> bool:
        """Check if an animation is playing."""
        if animation_name:
            return self.playing and self.current_animation == animation_name
        return self.playing
    
    def save_animation_file(self, file_path: str) -> bool:
        """
        Save the current animation set to a file.
        
        Args:
            file_path: Path where to save the animation file
            
        Returns:
            True if saved successfully
        """
        if not self.animation_set:
            return False
        
        try:
            # Convert to dict format
            data = {
                'name': self.animation_set.name,
                'base_path': os.path.relpath(self.animation_set.base_path),
                'default_animation': self.animation_set.default_animation,
                'animations': {}
            }
            
            for name, sequence in self.animation_set.animations.items():
                anim_data = {
                    'loop': sequence.loop,
                    'ping_pong': sequence.ping_pong,
                    'frames': []
                }
                
                # Add optional fields
                if sequence.next_animation:
                    anim_data['next_animation'] = sequence.next_animation
                if sequence.on_start:
                    anim_data['on_start'] = sequence.on_start
                if sequence.on_end:
                    anim_data['on_end'] = sequence.on_end
                if sequence.on_loop:
                    anim_data['on_loop'] = sequence.on_loop
                if sequence.frame_events:
                    anim_data['frame_events'] = sequence.frame_events
                
                # Add frames
                for frame in sequence.frames:
                    frame_data = asdict(frame)
                    # Remove None values for cleaner output
                    frame_data = {k: v for k, v in frame_data.items() if v is not None}
                    anim_data['frames'].append(frame_data)
                
                data['animations'][name] = anim_data
            
            # Save to file
            path = Path(file_path)
            with open(path, 'w') as f:
                if path.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
                else:
                    json.dump(data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving animation file {file_path}: {e}")
            return False


# Convenience function for creating animation files
def create_animation_template(file_path: str, name: str = "MyAnimation") -> bool:
    """
    Create a template animation file with property animation examples.
    
    Args:
        file_path: Where to save the template
        name: Name for the animation set
        
    Returns:
        True if created successfully
    """
    template = {
        'name': name,
        'base_path': 'images/',
        'default_animation': 'idle',
        'animations': {
            'idle': {
                'loop': True,
                'frames': [
                    'character_idle_01.png',
                    'character_idle_02.png',
                    'character_idle_03.png',
                    'character_idle_04.png'
                ],
                'property_animations': [
                    {
                        'target': 'transform.position.y',
                        'start_value': 0,
                        'amplitude': 3,
                        'frequency': 2.0,
                        'base_value': 0,
                        'easing': 'sine_wave'
                    }
                ]
            },
            'walk': {
                'loop': True,
                'frames': [
                    {'source': 'character_walk_01.png', 'duration': 0.1},
                    {'source': 'character_walk_02.png', 'duration': 0.1},
                    {'source': 'character_walk_03.png', 'duration': 0.1},
                    {'source': 'character_walk_04.png', 'duration': 0.1}
                ]
            },
            'attack': {
                'loop': False,
                'next_animation': 'idle',
                'on_end': 'attack_finished',
                'frame_events': {
                    2: 'deal_damage'
                },
                'frames': [
                    {'source': 'character_attack_01.png', 'duration': 0.1},
                    {'source': 'character_attack_02.png', 'duration': 0.1},
                    {'source': 'character_attack_03.png', 'duration': 0.2},
                    {'source': 'character_attack_04.png', 'duration': 0.1}
                ],
                'property_animations': [
                    {
                        'target': 'transform.scale.x',
                        'start_value': 1.0,
                        'end_value': 1.2,
                        'duration': 0.2,
                        'easing': 'ease_out',
                        'ping_pong': True
                    },
                    {
                        'target': 'SpriteComponent.alpha',
                        'start_value': 255,
                        'end_value': 128,
                        'duration': 0.1,
                        'offset': 0.1,
                        'easing': 'ease_in_out',
                        'ping_pong': True
                    }
                ]
            },
            'floating': {
                'loop': True,
                'frames': [
                    {'source': 'character_idle_01.png', 'duration': 0.5}
                ],
                'property_animations': [
                    {
                        'target': 'transform.position.y',
                        'base_value': 0,
                        'amplitude': 10,
                        'frequency': 0.5,
                        'easing': 'sine_wave'
                    },
                    {
                        'target': 'transform.rotation',
                        'base_value': 0,
                        'amplitude': 5,
                        'frequency': 0.3,
                        'easing': 'sine_wave'
                    }
                ]
            }
        }
    }
    
    try:
        path = Path(file_path)
        with open(path, 'w') as f:
            if path.suffix.lower() in ['.yaml', '.yml']:
                yaml.dump(template, f, default_flow_style=False, sort_keys=False)
            else:
                json.dump(template, f, indent=2)
        return True
    except Exception as e:
        print(f"Error creating template: {e}")
        return False
