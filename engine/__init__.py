import pygame
import time
from typing import Dict, List, Optional, Callable
from math import sin, cos, radians, degrees

from .actor.actor import Actor
from .component import *
from .input.inputManager import InputManager
from .networking import *
from .resources.assetManager import AssetManager
from .scene.scene import Scene
from .ui import *


serialization_registry = {}

def register_serializer(type_, to_json, from_json):
    serialization_registry[type_] = (to_json, from_json)

### Default Serializers ###

register_serializer(
    pygame.Vector2,
    lambda v: [v.x, v.y],
    lambda data: pygame.Vector2(*data)
)

register_serializer(
    pygame.Rect,
    lambda r: [r.x, r.y, r.width, r.height],
    lambda data: pygame.Rect(*data)
)


### Game Engine Class ###

class Game:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, width: int = 800, height: int = 600, title: str = "Game Window"):
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
        self.clearColour = (0, 0, 0)  # Default clear color
        
        # Core systems
        self.clock = pygame.time.Clock()
        self.inputManager = InputManager()
        self.assetManager = AssetManager()
        
        # Networking system
        self.networkManager = NetworkManager()
        
        # Scene management
        self.scenes: Dict[str, 'Scene'] = {}
        self.currentScene: Optional['Scene'] = None
        self.sceneStack: List['Scene'] = []
        
        # Timing
        self.targetFps = 60
        self.deltaTime = 0.0
        self.fixedTimestep = 1.0 / 60.0  # 60 FPS fixed timestep
        self.accumulator = 0.0
        self.lastTime = time.time()

        # Events
        self.eventHandlers: Dict[int, List[Callable]] = {}

        # Mark as initialized
        Game._initialized = True

    def addScene(self, name: str, scene: 'Scene') -> None:
        """Add a scene to the game."""
        self.scenes[name] = scene
        scene.game = self
        
    def loadScene(self, name: str) -> None:
        """Load and switch to a scene."""
        if name in self.scenes:
            if self.currentScene:
                self.currentScene.onExit()
            self.currentScene = self.scenes[name]
            self.currentScene.onEnter()

    def pushScene(self, name: str) -> None:
        """Push a scene onto the scene stack."""
        if name in self.scenes:
            if self.currentScene:
                self.sceneStack.append(self.currentScene)
                self.currentScene.onPause()
            self.currentScene = self.scenes[name]
            self.currentScene.onEnter()

    def popScene(self) -> None:
        """Pop the current scene and return to the previous one."""
        if self.currentScene:
            self.currentScene.onExit()
        if self.sceneStack:
            self.currentScene = self.sceneStack.pop()
            self.currentScene.onResume()
        else:
            self.currentScene = None

    def addEventHandler(self, event_type: int, handler: Callable) -> None:
        """Add an event handler for a specific event type."""
        if event_type not in self.eventHandlers:
            self.eventHandlers[event_type] = []
        self.eventHandlers[event_type].append(handler)

    def removeEventHandler(self, event_type: int, handler: Callable) -> None:
        """Remove an event handler."""
        if event_type in self.eventHandlers:
            if handler in self.eventHandlers[event_type]:
                self.eventHandlers[event_type].remove(handler)

    def emitEvent(self, event_type: int, **kwargs) -> None:
        """Emit a custom event."""
        if event_type in self.eventHandlers:
            for handler in self.eventHandlers[event_type]:
                handler(**kwargs)
                
    def quit(self) -> None:
        """Request the game to quit."""
        self.running = False
        
    def run(self) -> None:
        """Run the main game loop."""
        self.running = True
        
        while self.running:
            currentTime = time.time()
            frameTime = currentTime - self.lastTime
            self.lastTime = currentTime

            # Cap frame time to prevent spiral of death
            frameTime = min(frameTime, 0.25)

            # Fixed timestep accumulator
            self.accumulator += frameTime

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                    
                # Handle global events
                if event.type in self.eventHandlers:
                    for handler in self.eventHandlers[event.type]:
                        handler(event)
                
                # Handle current scene
                if self.currentScene:
                    self.currentScene.handleEvent(event)
                    
            self.inputManager.update()

            # Fixed timestep updates
            while self.accumulator >= self.fixedTimestep:
                # Update current scene
                if self.currentScene:
                    self.currentScene.update(self.fixedTimestep)

                # Update networking
                self.networkManager.update()

                self.accumulator -= self.fixedTimestep

            self.deltaTime = frameTime

            # Render
            self.screen.fill(self.clearColour)  # Clear screen

            if self.currentScene:
                self.currentScene.render(self.screen)
                
            pygame.display.flip()
            self.clock.tick(self.targetFps)
            
        # Cleanup
        self.networkManager.disconnect()
        pygame.quit()