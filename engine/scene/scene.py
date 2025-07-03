import pygame
import time
from typing import Dict, List, Optional, Callable, Tuple
import pymunk

from ..actor.actor import Actor
from ..ui.uiManager import UIManager
from engine.logger import Logger, LogType
from ..component.builtin.physicsComponent import PhysicsComponent

class Scene:
    def __init__(self):
        """Initialize the scene."""
        # Actor management
        self.actors: List[Actor] = []
        self.actor_lookup: Dict[str, Actor] = {}  # By name
        self.actors_by_tag: Dict[str, List[Actor]] = {}

        self.worldOffset = pygame.Vector2(0, 0)
        
        # Scene state
        self.active = True
        self.paused = False

        # Physics
        self.physicsSpace = pymunk.Space()
        self.physicsSpace.gravity = (0, 900)

        # UI Management
        from .. import Game
        self.uiManager = UIManager((Game._instance.width, Game._instance.height))
        
        # Lambda scripts for scene lifecycle events
        self.lambda_scripts: Dict[str, List[str]] = {
            'onEnter': [],
            'onExit': [],
            'onPause': [],
            'onResume': [],
            'update': [],
            'lateUpdate': [],
            'preRender': [],
            'postRender': []
        }

    def addPhysics(self, actor: Actor):
        physicsComponent = actor.getComponent(PhysicsComponent)
        if not physicsComponent:
            Logger.warning(f"Actor {actor.name} does not have a PhysicsComponent.")
            return

        self.physicsSpace.add(physicsComponent.body, *physicsComponent.shapes)
        Logger.debug(f"Added actor {actor.name} to physics space.")

    def removePhysics(self, actor: Actor):
        physicsComponent = actor.getComponent(PhysicsComponent)
        if not physicsComponent:
            Logger.warning(f"Actor {actor.name} does not have a PhysicsComponent.")
            return

        self.physicsSpace.remove(physicsComponent.body, *physicsComponent.shapes)
        Logger.debug(f"Removed actor {actor.name} from physics space.")

    def add_lambda_script(self, event_type: str, script: str) -> None:
        """Add a lambda script for a scene lifecycle event."""
        if event_type in self.lambda_scripts:
            self.lambda_scripts[event_type].append(script)
        else:
            print(f"Warning: Unknown scene event type '{event_type}'. Available: {list(self.lambda_scripts.keys())}")
            
    def remove_lambda_script(self, event_type: str, script: str) -> None:
        """Remove a specific lambda script from a scene lifecycle event."""
        if event_type in self.lambda_scripts and script in self.lambda_scripts[event_type]:
            self.lambda_scripts[event_type].remove(script)
            
    def clear_lambda_scripts(self, event_type: str) -> None:
        """Clear all lambda scripts for a scene lifecycle event."""
        if event_type in self.lambda_scripts:
            self.lambda_scripts[event_type].clear()
            
    def execute_lambda_scripts(self, event_type: str, **kwargs) -> None:
        """Execute all lambda scripts for a specific event type."""
        if event_type in self.lambda_scripts:
            for script in self.lambda_scripts[event_type]:
                try:
                    # Create a safe execution environment
                    safe_globals = {
                        '__builtins__': {
                            'print': print,
                            'len': len,
                            'str': str,
                            'int': int,
                            'float': float,
                            'bool': bool,
                            'min': min,
                            'max': max,
                            'abs': abs,
                            'round': round,
                        },
                        'scene': self,
                        'actors': self.actors,
                        'actor_lookup': self.actor_lookup,
                        'actors_by_tag': self.actors_by_tag,
                        'pygame': pygame,
                        **kwargs  # Additional context like dt, surface, etc.
                    }
                    
                    # Execute the lambda script
                    exec(script, safe_globals)
                    
                except Exception as e:
                    print(f"Error executing lambda script for {event_type}: {e}")
                    print(f"Script: {script}")

    def addActor(self, actor: Actor):
        """Add an actor to the scene."""
        if actor.name in self.actor_lookup:
            Logger.warning(f"Actor with name '{actor.name}' already exists in the scene.")

        actor.scene = self  # Set the scene reference in the actor
        
        self.actors.append(actor)
        self.actor_lookup[actor.name] = actor
        
        # Add actor to tags
        for tag in actor.tags:
            if tag not in self.actors_by_tag:
                self.actors_by_tag[tag] = []
            self.actors_by_tag[tag].append(actor)

    def addActors(self, *actors):
        """Add multiple actors to the scene."""
        for actor in actors:
            if not isinstance(actor, Actor):
                raise TypeError(f"Expected Actor instance, got {type(actor).__name__}")
            self.addActor(actor)

    def removeActor(self, actor: Actor):
        """Remove an actor from the scene."""
        if actor.name not in self.actor_lookup:
            raise ValueError(f"Actor with name '{actor.name}' does not exist in the scene.")
        
        actor.scene = None  # Clear the scene reference in the actor
        
        self.actors.remove(actor)
        del self.actor_lookup[actor.name]
        
        # Remove actor from tags
        for tag in actor.tags:
            if tag in self.actors_by_tag:
                self.actors_by_tag[tag].remove(actor)
                if not self.actors_by_tag[tag]:
                    del self.actors_by_tag[tag]

    def addWidget(self, widget):
        """Add a widget to the UI Manager."""
        self.uiManager.addWidget(widget)

    def removeWidget(self, widget):
        """Remove a widget from the UI Manager."""
        self.uiManager.removeWidget(widget)

    def onEnter(self):
        """Called when the scene is entered."""
        self.execute_lambda_scripts('onEnter')

    def onExit(self):
        """Called when the scene is exited."""
        self.execute_lambda_scripts('onExit')

    def onPause(self):
        """Called when the scene is paused."""
        self.execute_lambda_scripts('onPause')

    def onResume(self):
        """Called when the scene is resumed."""
        self.execute_lambda_scripts('onResume')

    def update(self, dt: float):
        """Update the scene."""
        if not self.active or self.paused:
            return
        
        # Execute lambda scripts for update
        self.execute_lambda_scripts('update', dt=dt)
        
        # Update all actors
        for actor in self.actors:
            actor.handleUpdate(dt)

        # Update UI Manager
        self.uiManager.update(dt)

    def physicsUpdate(self, dt: float):
        """Update the physics simulation."""
        self.physicsSpace.step(dt)

    def lateUpdate(self, dt: float):
        """Late update the scene."""
        if not self.active or self.paused:
            return
        
        # Update all actors
        for actor in self.actors:
            actor.handleLateUpdate(dt)

        # Update UI Manager
        self.uiManager.lateUpdate(dt)
        
        # Execute lambda scripts for late update
        self.execute_lambda_scripts('lateUpdate', dt=dt)

    def render(self, surface: pygame.Surface):
        """Render the scene."""
        if not self.active or self.paused:
            return
            
        # Execute pre-render lambda scripts
        self.execute_lambda_scripts('preRender', surface=surface)
        
        for actor in self.actors:
            actor.handleRender(surface)

        # Render UI
        self.uiManager.render(surface)
        
        # Execute post-render lambda scripts
        self.execute_lambda_scripts('postRender', surface=surface)

    def handleEvent(self, event: pygame.event.Event):
        """Handle an event."""
        # First let UI handle the event
        ui_handled = self.uiManager.handleEvent(event)
        
        # If UI didn't handle it, forward to actors
        if not ui_handled:
            for actor in self.actors:
                if hasattr(actor, 'handleEvent'):
                    if actor.handleEvent(event):
                        break  # Stop if an actor handled the event

    def serialize(self) -> dict:
        """Serialize the scene to a dictionary."""
        return {
            "actors": [actor.serialize() for actor in self.actors],
            "active": self.active,
            "paused": self.paused,
            "lambda_scripts": self.lambda_scripts
        }
    
    def deserialize(self, data: dict) -> None:
        """Deserialize the scene from a dictionary."""
        # Clear current actors
        self.actors.clear()
        self.actor_lookup.clear() 
        self.actors_by_tag.clear()
        
        # Deserialize actors
        new_actors = []
        for actor_data in data.get("actors", []):
            actor = Actor.createFromSerializedData(actor_data)
            new_actors.append(actor)
        
        # Re-establish parent-child relationships
        Actor.establishRelationshipsFromSerialization(new_actors)
        
        # Add actors to scene
        for actor in new_actors:
            self.addActor(actor)
        
        # Restore scene state
        self.active = data.get("active", True)
        self.paused = data.get("paused", False)
        
        # Restore lambda scripts
        self.lambda_scripts = data.get("lambda_scripts", {
            'onEnter': [],
            'onExit': [],
            'onPause': [],
            'onResume': [],
            'update': [],
            'lateUpdate': [],
            'preRender': [],
            'postRender': []
        })
    
    @staticmethod
    def createFromSerializedData(data: dict) -> 'Scene':
        """Create a scene from serialized data."""
        scene = Scene()
        scene.deserialize(data)
        return scene