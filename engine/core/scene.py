import pygame

from .game import Game
from .ui import UIManager

class Scene:
    def __init__(self, name="Scene"):
        self.game = Game()
        self.ui_manager = UIManager()
        
        self.name = name

        self.actors = []
        self.actor_map = {}

        self.worldOffset = pygame.Vector2(0, 0)  # Offset for rendering the world


#region Actor Management
    def add_actor(self, actor):
        """Add an actor to the scene."""
        actor.scene = self
        self.actors.append(actor)
        self.actor_map[actor.name] = actor

    def remove_actor(self, actor):
        """Remove an actor from the scene."""
        actor.scene = None
        self.actors.remove(actor)
        self.actor_map.pop(actor.name, None)
#endregion

#region Lifecycle Methods
    def on_enter(self):
        """Called when the scene is entered."""
        print(f"Entering scene: {self.name}")

    def on_exit(self):
        """Called when the scene is exited."""
        print(f"Exiting scene: {self.name}")

    def handle_event(self, event):
        """Handle events for the scene."""
        for actor in self.actors:
            actor.handleEvent(event)

        self.ui_manager.handle_event(event)

#region Update Methods
    def update(self, dt):
        """Update the scene with the given delta time."""
        for actor in self.actors:
            actor.handleUpdate(dt)

    def phys_update(self, dt):
        """Update the scene with the given delta time."""
        for actor in self.actors:
            actor.handlePhysUpdate(dt)

    def late_update(self, dt):
        """Update the scene with the given delta time."""
        for actor in self.actors:
            actor.handleLateUpdate(dt)
#endregion

    def render(self):
        """Render the scene to the given surface."""
        for actor in self.actors:
            actor.handleRender()

        self.ui_manager.render(self.game.buffer)
#endregion