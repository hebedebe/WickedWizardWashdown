import pygame
import time
from typing import Dict, List, Optional, Callable, Tuple

from ..actor.actor import Actor
from ..ui.uiManager import UIManager
from engine.logger import Logger, LogType

class Scene:
    def __init__(self):
        """Initialize the scene."""
        # Actor management
        self.actors: List[Actor] = []
        self.actor_lookup: Dict[str, Actor] = {}  # By name
        self.actors_by_tag: Dict[str, List[Actor]] = {}
        
        # Scene state
        self.active = True
        self.paused = False

        # UI Management
        from .. import Game
        self.uiManager = UIManager((Game().width, Game().height))

    def addActor(self, actor: Actor):
        """Add an actor to the scene."""
        if actor.name in self.actor_lookup:
            print(f"WARN: Actor with name '{actor.name}' already exists in the scene.")
            Logger.warning(f"Actor with name '{actor.name}' already exists in the scene.")
        
        self.actors.append(actor)
        self.actor_lookup[actor.name] = actor
        
        # Add actor to tags
        for tag in actor.tags:
            if tag not in self.actors_by_tag:
                self.actors_by_tag[tag] = []
            self.actors_by_tag[tag].append(actor)

    def removeActor(self, actor: Actor):
        """Remove an actor from the scene."""
        if actor.name not in self.actor_lookup:
            raise ValueError(f"Actor with name '{actor.name}' does not exist in the scene.")
        
        self.actors.remove(actor)
        del self.actor_lookup[actor.name]
        
        # Remove actor from tags
        for tag in actor.tags:
            if tag in self.actors_by_tag:
                self.actors_by_tag[tag].remove(actor)
                if not self.actors_by_tag[tag]:
                    del self.actors_by_tag[tag]

    def onEnter(self):
        """Called when the scene is entered."""
        pass

    def onExit(self):
        """Called when the scene is exited."""
        pass

    def onPause(self):
        """Called when the scene is paused."""
        pass

    def onResume(self):
        """Called when the scene is resumed."""
        pass

    def update(self, dt: float):
        """Update the scene."""
        if not self.active or self.paused:
            return
        
        # Update all actors
        for actor in self.actors:
            actor.handleUpdate(dt)

        # Update UI Manager
        self.uiManager.update(dt)

    def render(self, surface: pygame.Surface):
        """Render the scene."""
        if not self.active or self.paused:
            return
        for actor in self.actors:
            actor.handleRender(surface)

        # Render UI
        self.uiManager.render(surface)

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
            "paused": self.paused
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
    
    @staticmethod
    def createFromSerializedData(data: dict) -> 'Scene':
        """Create a scene from serialized data."""
        scene = Scene()
        scene.deserialize(data)
        return scene