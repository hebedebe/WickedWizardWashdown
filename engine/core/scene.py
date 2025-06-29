"""
Scene management system for organizing and managing game actors.
"""

import pygame
from typing import List, Dict, Optional, Type, TypeVar
from .actor import Actor, Component

T = TypeVar('T', bound=Component)

class Scene:
    """
    Container for managing actors and game objects.
    """
    
    def __init__(self, name: str = "Scene"):
        self.name = name
        self.game = None  # Will be set by Game class
        
        # Actor management
        self.actors: List[Actor] = []
        self.actor_lookup: Dict[str, Actor] = {}  # By name
        self.actors_by_tag: Dict[str, List[Actor]] = {}
        
        # Scene state
        self.active = True
        self.paused = False
        
        # Background
        self.background_color = pygame.Color(0, 0, 0)
        self.background_image: Optional[pygame.Surface] = None
        
    def add_actor(self, actor: Actor) -> None:
        """Add an actor to the scene."""
        if actor not in self.actors:
            self.actors.append(actor)
            self.actor_lookup[actor.name] = actor
            
            # Add to tag lookup
            for tag in actor.tags:
                if tag not in self.actors_by_tag:
                    self.actors_by_tag[tag] = []
                self.actors_by_tag[tag].append(actor)
                
    def remove_actor(self, actor: Actor) -> None:
        """Remove an actor from the scene."""
        if actor in self.actors:
            self.actors.remove(actor)
            
            # Remove from lookups
            if actor.name in self.actor_lookup:
                del self.actor_lookup[actor.name]
                
            for tag in actor.tags:
                if tag in self.actors_by_tag and actor in self.actors_by_tag[tag]:
                    self.actors_by_tag[tag].remove(actor)
                    if not self.actors_by_tag[tag]:
                        del self.actors_by_tag[tag]
                        
    def find_actor(self, name: str) -> Optional[Actor]:
        """Find an actor by name."""
        return self.actor_lookup.get(name)
        
    def find_actors_with_tag(self, tag: str) -> List[Actor]:
        """Find all actors with a specific tag."""
        return self.actors_by_tag.get(tag, []).copy()
        
    def find_actors_with_component(self, component_type: Type[T]) -> List[Actor]:
        """Find all actors that have a specific component type."""
        result = []
        for actor in self.actors:
            if actor.has_component(component_type):
                result.append(actor)
        return result
        
    def get_components(self, component_type: Type[T]) -> List[T]:
        """Get all components of a specific type from all actors."""
        components = []
        for actor in self.actors:
            component = actor.get_component(component_type)
            if component:
                components.append(component)
        return components
        
    def create_actor(self, name: str = None, position: pygame.Vector2 = None) -> Actor:
        """Create and add a new actor to the scene."""
        actor = Actor(name)
        if position:
            actor.transform.local_position = pygame.Vector2(position)
        self.add_actor(actor)
        return actor
        
    def destroy_actor(self, actor: Actor) -> None:
        """Destroy an actor and remove it from the scene."""
        self.remove_actor(actor)
        actor.destroy()
        
    def clear(self) -> None:
        """Remove all actors from the scene."""
        for actor in list(self.actors):
            self.destroy_actor(actor)
            
    def set_background_color(self, color: pygame.Color) -> None:
        """Set the scene background color."""
        self.background_color = color
        
    def set_background_image(self, image: pygame.Surface) -> None:
        """Set the scene background image."""
        self.background_image = image
        
    def update(self, dt: float) -> None:
        """Update all actors in the scene."""
        if self.paused:
            return
            
        # Update all actors
        for actor in list(self.actors):  # Use list() to handle actors being removed during update
            if actor.active:
                actor.update(dt)
                
    def fixed_update(self, dt: float) -> None:
        """Fixed timestep update for physics."""
        if self.paused:
            return
            
        for actor in self.actors:
            if actor.active:
                actor.fixed_update(dt)
                
    def render(self, screen: pygame.Surface) -> None:
        """Render the scene."""
        # Clear background
        if self.background_image:
            screen.blit(self.background_image, (0, 0))
        else:
            screen.fill(self.background_color)
            
        # Render all actors
        for actor in self.actors:
            if actor.active:
                actor.render(screen)
                
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle events for all actors in the scene."""
        if self.paused:
            return
            
        for actor in self.actors:
            if actor.active:
                actor.handle_event(event)
                
    def on_enter(self) -> None:
        """Called when the scene becomes active."""
        self.active = True
        self.paused = False
        
    def on_exit(self) -> None:
        """Called when the scene becomes inactive."""
        self.active = False
        
    def on_pause(self) -> None:
        """Called when the scene is paused (another scene pushed on top)."""
        self.paused = True
        
    def on_resume(self) -> None:
        """Called when the scene is resumed (returned to from scene stack)."""
        self.paused = False


class SceneManager:
    """
    Utility class for managing multiple scenes with transitions.
    """
    
    def __init__(self):
        self.scenes: Dict[str, Scene] = {}
        self.current_scene: Optional[Scene] = None
        self.transitioning = False
        self.transition_duration = 0.0
        self.transition_time = 0.0
        self.transition_callback: Optional[callable] = None
        
    def add_scene(self, name: str, scene: Scene) -> None:
        """Add a scene to the manager."""
        self.scenes[name] = scene
        
    def load_scene(self, name: str, transition_duration: float = 0.0) -> None:
        """Load a scene with optional transition."""
        if name not in self.scenes:
            return
            
        if transition_duration > 0:
            self.start_transition(name, transition_duration)
        else:
            self.switch_scene(name)
            
    def start_transition(self, target_scene: str, duration: float) -> None:
        """Start a scene transition."""
        self.transitioning = True
        self.transition_duration = duration
        self.transition_time = 0.0
        self.transition_callback = lambda: self.switch_scene(target_scene)
        
    def switch_scene(self, name: str) -> None:
        """Immediately switch to a scene."""
        if self.current_scene:
            self.current_scene.on_exit()
            
        self.current_scene = self.scenes.get(name)
        if self.current_scene:
            self.current_scene.on_enter()
            
        self.transitioning = False
        
    def update(self, dt: float) -> None:
        """Update the current scene and handle transitions."""
        if self.transitioning:
            self.transition_time += dt
            if self.transition_time >= self.transition_duration:
                if self.transition_callback:
                    self.transition_callback()
        elif self.current_scene:
            self.current_scene.update(dt)
            
    def render(self, screen: pygame.Surface) -> None:
        """Render the current scene with transition effects."""
        if self.current_scene:
            self.current_scene.render(screen)
            
        # Apply transition effect
        if self.transitioning:
            progress = self.transition_time / self.transition_duration
            alpha = int(255 * progress)
            
            # Simple fade to black transition
            fade_surface = pygame.Surface(screen.get_size())
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(alpha)
            screen.blit(fade_surface, (0, 0))
