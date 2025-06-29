"""
Wicked Wizard Washdown - 2D Networked Game Engine
Core engine module providing the main Game class and engine functionality.
"""

import pygame
import time
from typing import Dict, List, Optional, Callable

# Import all engine modules
from .scene import Scene
from .input_manager import InputManager
from .asset_manager import AssetManager
from .networking import NetworkManager
from .actor import Actor, Component, Transform
from .components import (
    SpriteComponent, PhysicsComponent, InputComponent, 
    AudioComponent, AnimationComponent, HealthComponent
)
from .particles import ParticleSystem, ParticleEmitter, Particle
from .ui import UIManager, Widget, Panel, Label, Button, Slider

# Export main classes
__all__ = [
    'Game', 'Scene', 'Actor', 'Component', 'Transform',
    'SpriteComponent', 'PhysicsComponent', 'InputComponent', 
    'AudioComponent', 'AnimationComponent', 'HealthComponent',
    'ParticleSystem', 'ParticleEmitter', 'Particle',
    'UIManager', 'Widget', 'Panel', 'Label', 'Button', 'Slider',
    'InputManager', 'AssetManager', 'NetworkManager'
]

class Game:
    """
    Main game class that manages the game loop, scenes, and core systems.
    """
    
    def __init__(self, width: int = 800, height: int = 600, title: str = "Wicked Wizard Game"):
        """
        Initialize the game engine.
        
        Args:
            width: Screen width in pixels
            height: Screen height in pixels  
            title: Window title
        """
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
        self.network_manager = NetworkManager()
        
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
                
    def handle_events(self) -> None:
        """Process pygame events and call registered handlers."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            # Call registered event handlers
            if event.type in self.event_handlers:
                for handler in self.event_handlers[event.type]:
                    handler(event)
                    
            # Pass events to input manager and current scene
            self.input_manager.handle_event(event)
            if self.current_scene:
                self.current_scene.handle_event(event)
                
    def update(self, dt: float) -> None:
        """Update game systems with delta time."""
        self.input_manager.update(dt)
        self.network_manager.update(dt)
        
        if self.current_scene:
            self.current_scene.update(dt)
            
    def fixed_update(self) -> None:
        """Fixed timestep update for physics and networking."""
        if self.current_scene:
            self.current_scene.fixed_update(self.fixed_timestep)
            
    def render(self) -> None:
        """Render the current frame."""
        self.screen.fill((0, 0, 0))  # Clear screen
        
        if self.current_scene:
            self.current_scene.render(self.screen)
            
        pygame.display.flip()
        
    def run(self) -> None:
        """Main game loop."""
        self.running = True
        
        while self.running:
            current_time = time.time()
            self.delta_time = current_time - self.last_time
            self.last_time = current_time
            
            # Cap delta time to prevent spiral of death
            if self.delta_time > 0.25:
                self.delta_time = 0.25
                
            self.accumulator += self.delta_time
            
            # Handle events
            self.handle_events()
            
            # Fixed timestep updates
            while self.accumulator >= self.fixed_timestep:
                self.fixed_update()
                self.accumulator -= self.fixed_timestep
                
            # Variable timestep update
            self.update(self.delta_time)
            
            # Render
            self.render()
            
            # Maintain target FPS
            self.clock.tick(self.target_fps)
            
        self.cleanup()
        
    def cleanup(self) -> None:
        """Clean up resources before exiting."""
        if self.current_scene:
            self.current_scene.on_exit()
        self.asset_manager.cleanup()
        self.network_manager.cleanup()
        pygame.quit()
        
    def quit(self) -> None:
        """Request the game to quit."""
        self.running = False
