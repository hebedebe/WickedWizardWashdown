import pygame
import pymunk

from .game import Game
from .ui import UIManager

class Scene:
    def __init__(self, name="Scene"):
        self.game = Game()
        self.ui_manager = UIManager()
        self.physics_space = pymunk.Space()
        self.physics_space.gravity = (0, 900)
        
        self.name = name

        self.actors = []
        self.actor_map = {}

        self.worldOffset = pygame.Vector2(0, 0)  # Offset for rendering the world

    def world_mouse_pos(self, as_tuple=False):
        """Get the mouse position in world coordinates."""
        pos = pygame.mouse.get_pos() + pygame.Vector2(self.worldOffset)
        return pos if not as_tuple else (pos.x, pos.y)

#region Actor Management
    def add_actor(self, actor):
        """Add an actor to the scene."""
        actor.scene = self
        self.actors.append(actor)
        self.actor_map[actor.name] = actor
        actor.start()

    def get_actor(self, name):
        """Get an actor by name."""
        return self.actor_map.get(name)

    def remove_actor(self, actor):
        """Remove an actor from the scene."""
        actor.stop()
        actor.scene = None
        self.actors.remove(actor)
        self.actor_map.pop(actor.name, None)

    def add_physics(self, actor):
        """Add an actor's physics body to the scene's physics space."""
        from ..builtin.components.physics_component import PhysicsComponent
        physics_component = actor.getComponent(PhysicsComponent, allow_inheritance=True)
        if physics_component and physics_component.body:
            self.physics_space.add(physics_component.body)
            # Also add all shapes associated with the body
            for shape in physics_component.shapes:
                self.physics_space.add(shape)

    def remove_physics(self, actor):
        """Remove an actor's physics body from the scene's physics space."""
        from ..builtin.components.physics_component import PhysicsComponent
        physics_component = actor.getComponent(PhysicsComponent, allow_inheritance=True)
        if physics_component and physics_component.body:
            self.physics_space.remove(physics_component.body)
            # Also remove all shapes associated with the body
            for shape in physics_component.shapes:
                self.physics_space.remove(shape)
            
#endregion

#region Lifecycle Methods
    def on_enter(self):
        """Called when the scene is entered."""
        print(f"Entering scene: {self.name}")

    def on_exit(self):
        """Called when the scene is exited."""
        print(f"Exiting scene: {self.name}")

    def on_pause(self):
        """Called when the scene is paused."""
        print(f"Pausing scene: {self.name}")

    def on_resume(self):
        """Called when the scene is resumed."""
        print(f"Resuming scene: {self.name}")

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
        # Step the physics simulation
        self.physics_space.step(dt)
        
        # Update all actors
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