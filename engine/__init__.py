"""
Wicked Wizard Washdown - 2D Game Engine
Core engine module providing the main Game class and engine functionality.
"""

import pygame
import time
from typing import Dict, List, Optional, Callable

# Import all engine modules - updated for new folder structure
from .core.scene import Scene
from .input.input_manager import InputManager
from .core.asset_manager import AssetManager
from .core.actor import Actor, Component, Transform
from .components import (
    SpriteComponent, AudioComponent, HealthComponent, TextComponent
)
from .input import InputComponent
# Networking imports
from .networking.networking import NetworkManager, NetworkMessage, MessageType, NetworkPriority, get_network_manager
from .networking.network_components import (
    NetworkComponent, NetworkSerialization, NetworkedActorManager, PriorityNetworkComponent,
    spawn_network_actor, destroy_network_actor, request_full_sync,
    get_networked_actor_manager
)
from .networking.network_utils import (
    NetworkedSceneManager, PlayerManager, NetworkOptimizer, NetworkDebugger,
    get_networked_scene_manager, get_player_manager, get_network_optimizer,
    get_network_debugger, change_scene_networked
)
from .rendering.enhanced_animation import FileAnimationComponent, AnimationFrame, AnimationSequence, PropertyAnimation, EasingType, create_animation_template

# Backward compatibility alias
AnimationComponent = FileAnimationComponent
from .rendering.particles import ParticleSystem, ParticleEmitter, Particle
from .rendering.ui import UIManager, Widget, Panel, Label, Button, Slider, FPSDisplay, TextInput

# Export main classes
__all__ = [
    'Game', 'Scene', 'Actor', 'Component', 'Transform',
    'SpriteComponent', 'InputComponent', 
    'AudioComponent', 'AnimationComponent', 'HealthComponent', 'TextComponent',
    'FileAnimationComponent', 'AnimationFrame', 'AnimationSequence', 'PropertyAnimation', 'EasingType', 'create_animation_template',
    'NetworkManager', 'NetworkMessage', 'MessageType', 'NetworkPriority', 'get_network_manager',
    'NetworkComponent', 'PriorityNetworkComponent', 'NetworkSerialization', 'NetworkedActorManager',
    'spawn_network_actor', 'destroy_network_actor', 'request_full_sync', 'get_networked_actor_manager',
    'NetworkedSceneManager', 'PlayerManager', 'NetworkOptimizer', 'NetworkDebugger',
    'get_networked_scene_manager', 'get_player_manager', 'get_network_optimizer',
    'get_network_debugger', 'change_scene_networked',
    'ParticleSystem', 'ParticleEmitter', 'Particle',
    'UIManager', 'Widget', 'Panel', 'Label', 'Button', 'Slider', 'FPSDisplay', 'TextInput',
    'AssetManager', 'InputManager'
]

class Game:
    """
    Main game class that manages the game loop and core systems.
    Singleton pattern ensures only one game instance exists.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, width: int = 800, height: int = 600, title: str = "Wicked Wizard Game"):
        """
        Initialize the game engine.
        
        Args:
            width: Screen width in pixels
            height: Screen height in pixels  
            title: Window title
        """
        # Prevent re-initialization of singleton
        if self._initialized:
            return
            
        pygame.init()
        
        # Core properties
        self.width = width
        self.height = height
        self.title = title
        self.running = False
        
        # Display setup
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        
        # Core systems
        self.clock = pygame.time.Clock()
        self.input_manager = InputManager()
        self.asset_manager = AssetManager()
        
        # Networking system
        self.network_manager = get_network_manager()
        self.network_manager.game = self
        
        # Scene management
        self.scenes: Dict[str, Scene] = {}
        self.current_scene: Optional[Scene] = None
        self.scene_stack: List[Scene] = []
        
        # Timing
        self.target_fps = 60
        self.delta_time = 0.0
        self.fixed_timestep = 1.0 / 60.0  # 60 FPS fixed timestep
        self.accumulator = 0.0
        self.last_time = time.time()
        
        # Events
        self.event_handlers: Dict[int, List[Callable]] = {}
        
        # Mark as initialized
        Game._initialized = True
        
    @classmethod
    def get_instance(cls):
        """Get the game instance. Creates one if it doesn't exist."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    @classmethod
    def has_instance(cls) -> bool:
        """Check if a game instance exists."""
        return cls._instance is not None
        
    def add_scene(self, name: str, scene: Scene) -> None:
        """Add a scene to the game."""
        self.scenes[name] = scene
        scene.game = self
        
    def load_scene(self, name: str) -> None:
        """Load and switch to a scene."""
        if name in self.scenes:
            if self.current_scene:
                self.current_scene.on_exit()
            self.current_scene = self.scenes[name]
            self.current_scene.on_enter()
            
    def push_scene(self, name: str) -> None:
        """Push a scene onto the scene stack."""
        if name in self.scenes:
            if self.current_scene:
                self.scene_stack.append(self.current_scene)
                self.current_scene.on_pause()
            self.current_scene = self.scenes[name]
            self.current_scene.on_enter()
            
    def pop_scene(self) -> None:
        """Pop the current scene and return to the previous one."""
        if self.current_scene:
            self.current_scene.on_exit()
        if self.scene_stack:
            self.current_scene = self.scene_stack.pop()
            self.current_scene.on_resume()
        else:
            self.current_scene = None
            
    def add_event_handler(self, event_type: int, handler: Callable) -> None:
        """Add an event handler for a specific event type."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        
    def remove_event_handler(self, event_type: int, handler: Callable) -> None:
        """Remove an event handler."""
        if event_type in self.event_handlers:
            if handler in self.event_handlers[event_type]:
                self.event_handlers[event_type].remove(handler)
                
    def emit_event(self, event_type: int, **kwargs) -> None:
        """Emit a custom event."""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                handler(**kwargs)
                
    def quit(self) -> None:
        """Request the game to quit."""
        self.running = False
        
    def run(self) -> None:
        """Run the main game loop."""
        self.running = True
        
        while self.running:
            current_time = time.time()
            frame_time = current_time - self.last_time
            self.last_time = current_time
            
            # Cap frame time to prevent spiral of death
            frame_time = min(frame_time, 0.25)
            
            # Fixed timestep accumulator
            self.accumulator += frame_time
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                    
                # Handle global events
                if event.type in self.event_handlers:
                    for handler in self.event_handlers[event.type]:
                        handler(event)
                        
                # Handle input manager
                self.input_manager.handle_event(event)
                
                # Handle current scene
                if self.current_scene:
                    self.current_scene.handle_event(event)
                    
            # Fixed timestep updates
            while self.accumulator >= self.fixed_timestep:
                # Update input manager
                self.input_manager.update(self.fixed_timestep)
                
                # Update current scene (fixed timestep for physics)
                if self.current_scene:
                    self.current_scene.fixed_update(self.fixed_timestep)
                
                # Update networking
                self.network_manager.update()
                    
                self.accumulator -= self.fixed_timestep
                
            # Calculate variable timestep for interpolation
            interpolation = self.accumulator / self.fixed_timestep
            self.delta_time = frame_time
            
            # Variable timestep updates
            if self.current_scene:
                self.current_scene.update(frame_time)
            
            # Render
            self.screen.fill((0, 0, 0))  # Clear screen
            
            if self.current_scene:
                self.current_scene.render(self.screen)
                
                # Render physics debug if scene has physics
                if hasattr(self.current_scene, 'physics_world') and self.current_scene.physics_world:
                    self.current_scene.physics_world.debug_draw(self.screen)
                
            pygame.display.flip()
            self.clock.tick(self.target_fps)
            
        # Cleanup
        self.network_manager.disconnect()
        pygame.quit()
