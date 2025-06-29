"""
Actor system for the game engine.
Actors are game entities that can have children and components.
"""

import pygame
from typing import List, Dict, Optional, Type, TypeVar, Any
from abc import ABC, abstractmethod
import uuid

T = TypeVar('T', bound='Component')

class Transform:
    """
    Transform component using pygame.Vector2 for position and scale.
    """
    
    def __init__(self, position: pygame.Vector2 = None, rotation: float = 0.0, scale: pygame.Vector2 = None):
        self.local_position = position or pygame.Vector2(0, 0)
        self.local_rotation = rotation
        self.local_scale = scale or pygame.Vector2(1, 1)
        
        # World transform (calculated from parent hierarchy)
        self.world_position = pygame.Vector2(self.local_position)
        self.world_rotation = rotation
        self.world_scale = pygame.Vector2(self.local_scale)
        
        self.dirty = True  # Needs recalculation
        
    def mark_dirty(self):
        """Mark this transform as needing recalculation."""
        self.dirty = True
        
    def calculate_world_transform(self, parent_transform: Optional['Transform'] = None):
        """Calculate world transform from parent hierarchy."""
        if not self.dirty and not (parent_transform and parent_transform.dirty):
            return
            
        if parent_transform:
            # Apply parent transformation
            self.world_rotation = parent_transform.world_rotation + self.local_rotation
            
            # Scale local position by parent scale and rotate
            scaled_pos = pygame.Vector2(
                self.local_position.x * parent_transform.world_scale.x,
                self.local_position.y * parent_transform.world_scale.y
            )
            rotated_pos = scaled_pos.rotate(parent_transform.world_rotation)
            self.world_position = parent_transform.world_position + rotated_pos
            
            self.world_scale = pygame.Vector2(
                self.local_scale.x * parent_transform.world_scale.x,
                self.local_scale.y * parent_transform.world_scale.y
            )
        else:
            # No parent, world = local
            self.world_position = pygame.Vector2(self.local_position)
            self.world_rotation = self.local_rotation
            self.world_scale = pygame.Vector2(self.local_scale)
            
        self.dirty = False

class Component(ABC):
    """
    Base class for all components that can be attached to actors.
    """
    
    def __init__(self):
        self.actor: Optional['Actor'] = None
        self.enabled = True
        
    @property
    def game(self):
        """Get the game instance. Provides easy access to game systems from any component."""
        from . import Game
        return Game.get_instance()
        
    def on_added(self, actor: 'Actor') -> None:
        """Called when component is added to an actor."""
        self.actor = actor
        
    def on_removed(self) -> None:
        """Called when component is removed from an actor."""
        self.actor = None
        
    @abstractmethod
    def update(self, dt: float) -> None:
        """Update the component."""
        pass
        
    def fixed_update(self, dt: float) -> None:
        """Fixed timestep update for physics."""
        pass
        
    def render(self, screen: pygame.Surface) -> None:
        """Render the component."""
        pass
        
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        pass

class Actor:
    """
    Game entity that can have children and components.
    Uses pygame classes where possible.
    """
    
    def __init__(self, name: str = None):
        self.id = str(uuid.uuid4())
        self.name = name or f"Actor_{self.id[:8]}"
        
        # Transform
        self.transform = Transform()
        
        # Hierarchy
        self.parent: Optional['Actor'] = None
        self.children: List['Actor'] = []
        
        # Components
        self.components: Dict[Type[Component], Component] = {}
        self.component_list: List[Component] = []
        
        # State
        self.active = True
        self.enabled = True
        
        # Tags for identification
        self.tags: List[str] = []
        
    @property
    def game(self):
        """Get the game instance. Provides easy access to game systems from any actor."""
        from . import Game
        return Game.get_instance()
        
    def add_child(self, child: 'Actor') -> None:
        """Add a child actor."""
        if child.parent:
            child.parent.remove_child(child)
        child.parent = self
        self.children.append(child)
        child.transform.mark_dirty()
        
    def remove_child(self, child: 'Actor') -> None:
        """Remove a child actor."""
        if child in self.children:
            child.parent = None
            self.children.remove(child)
            child.transform.mark_dirty()
            
    def find_child(self, name: str) -> Optional['Actor']:
        """Find a child by name."""
        for child in self.children:
            if child.name == name:
                return child
        return None
        
    def find_children_with_tag(self, tag: str) -> List['Actor']:
        """Find all children with a specific tag."""
        result = []
        for child in self.children:
            if tag in child.tags:
                result.append(child)
            result.extend(child.find_children_with_tag(tag))
        return result
        
    def add_component(self, component: Component) -> None:
        """Add a component to this actor."""
        component_type = type(component)
        if component_type in self.components:
            self.remove_component(component_type)
            
        self.components[component_type] = component
        self.component_list.append(component)
        component.on_added(self)
        
    def remove_component(self, component_type: Type[T]) -> Optional[T]:
        """Remove a component by type."""
        if component_type in self.components:
            component = self.components[component_type]
            del self.components[component_type]
            self.component_list.remove(component)
            component.on_removed()
            return component
        return None
        
    def get_component(self, component_type: Type[T]) -> Optional[T]:
        """Get a component by type."""
        return self.components.get(component_type)
        
    def has_component(self, component_type: Type[Component]) -> bool:
        """Check if actor has a component of the given type."""
        return component_type in self.components
        
    def add_tag(self, tag: str) -> None:
        """Add a tag to this actor."""
        if tag not in self.tags:
            self.tags.append(tag)
            
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from this actor."""
        if tag in self.tags:
            self.tags.remove(tag)
            
    def has_tag(self, tag: str) -> bool:
        """Check if actor has a specific tag."""
        return tag in self.tags
        
    def update_transform(self) -> None:
        """Update world transform from parent hierarchy."""
        parent_transform = self.parent.transform if self.parent else None
        self.transform.calculate_world_transform(parent_transform)
        
        # Update children transforms
        for child in self.children:
            child.update_transform()
            
    def update(self, dt: float) -> None:
        """Update actor and all components."""
        if not self.active:
            return
            
        # Update transform
        self.update_transform()
        
        # Update components
        if self.enabled:
            for component in self.component_list:
                if component.enabled:
                    component.update(dt)
                    
        # Update children
        for child in self.children:
            child.update(dt)
            
    def fixed_update(self, dt: float) -> None:
        """Fixed timestep update."""
        if not self.active:
            return
            
        if self.enabled:
            for component in self.component_list:
                if component.enabled:
                    component.fixed_update(dt)
                    
        for child in self.children:
            child.fixed_update(dt)
            
    def render(self, screen: pygame.Surface) -> None:
        """Render actor and all components."""
        if not self.active:
            return
            
        if self.enabled:
            for component in self.component_list:
                if component.enabled:
                    component.render(screen)
                    
        for child in self.children:
            child.render(screen)
            
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle events for actor and components."""
        if not self.active or not self.enabled:
            return
            
        for component in self.component_list:
            if component.enabled:
                component.handle_event(event)
                
        for child in self.children:
            child.handle_event(event)
            
    def destroy(self) -> None:
        """Destroy this actor and all children."""
        # Remove from parent
        if self.parent:
            self.parent.remove_child(self)
            
        # Destroy children
        for child in list(self.children):
            child.destroy()
            
        # Remove all components
        for component in list(self.component_list):
            component.on_removed()
        self.components.clear()
        self.component_list.clear()
        
        self.active = False
