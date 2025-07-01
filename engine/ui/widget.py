import pygame
from typing import Dict, List, Optional, Callable, Any, Tuple
from abc import ABC, abstractmethod
from enum import Enum
from .event import UIEvent

class WidgetState(Enum):
    """Widget visual states."""
    NORMAL = "normal"
    HOVER = "hover"
    PRESSED = "pressed"
    DISABLED = "disabled"

class Widget(ABC):
    """
    Base class for all UI widgets.
    """
    
    def __init__(self, rect: pygame.Rect, name: str = ""):
        self.rect = pygame.Rect(rect)
        self.name = name
        
        # Hierarchy
        self.parent: Optional['Widget'] = None
        self.children: List['Widget'] = []
        
        # State
        self.visible = True
        self.enabled = True
        self.state = WidgetState.NORMAL
        
        # Layout
        self.anchor = pygame.Vector2(0, 0)  # 0-1 relative to parent
        self.margin = pygame.Rect(0, 0, 0, 0)  # left, top, right, bottom
        self.padding = pygame.Rect(0, 0, 0, 0)
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Input state
        self.mouse_inside = False
        self.mouse_pressed = False
        
    def add_child(self, child: 'Widget') -> None:
        """Add a child widget."""
        if child.parent:
            child.parent.remove_child(child)
        child.parent = self
        self.children.append(child)
        
    def remove_child(self, child: 'Widget') -> None:
        """Remove a child widget."""
        if child in self.children:
            child.parent = None
            self.children.remove(child)
            
    def find_child(self, name: str) -> Optional['Widget']:
        """Find a child widget by name."""
        for child in self.children:
            if child.name == name:
                return child
            # Search recursively
            result = child.find_child(name)
            if result:
                return result
        return None
        
    def add_event_handler(self, event_type: str, handler: Callable) -> None:
        """Add an event handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        
    def remove_event_handler(self, event_type: str, handler: Callable) -> None:
        """Remove an event handler."""
        if event_type in self.event_handlers:
            if handler in self.event_handlers[event_type]:
                self.event_handlers[event_type].remove(handler)
                
    def emit_event(self, event_type: str, data: Any = None) -> None:
        """Emit a UI event."""
        event = UIEvent(event_type, self, data)
        
        # Call local handlers
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                handler(event)
                
        # Bubble up to parent
        if self.parent:
            self.parent.handle_child_event(event)
            
    def handle_child_event(self, event: UIEvent) -> None:
        """Handle events from child widgets."""
        # Can be overridden by subclasses
        pass
        
    def get_world_rect(self) -> pygame.Rect:
        """Get widget rectangle in world coordinates."""
        if self.parent:
            parent_rect = self.parent.get_content_rect()
            world_rect = pygame.Rect(
                parent_rect.x + self.rect.x,
                parent_rect.y + self.rect.y,
                self.rect.width,
                self.rect.height
            )
            return world_rect
        return pygame.Rect(self.rect)
        
    def get_content_rect(self) -> pygame.Rect:
        """Get the content area (excluding padding)."""
        world_rect = self.get_world_rect()
        return pygame.Rect(
            world_rect.x + self.padding.left,
            world_rect.y + self.padding.top,
            world_rect.width - self.padding.left - self.padding.right,
            world_rect.height - self.padding.top - self.padding.bottom
        )
        
    def contains_point(self, point: pygame.Vector2) -> bool:
        """Check if a point is inside this widget."""
        world_rect = self.get_world_rect()
        return world_rect.collidepoint(int(point.x), int(point.y))
        
    def update(self, dt: float) -> None:
        """Update widget logic."""
        if not self.visible:
            return
            
        # Update children
        for child in self.children:
            child.update(dt)

    def lateUpdate(self, dt: float) -> None:
        """Late update for widget logic."""
        if not self.visible:
            return
            
        # Late update children
        for child in self.children:
            child.lateUpdate(dt)
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events. Returns True if event was handled."""
        if not self.visible or not self.enabled:
            return False
            
        # Handle children first (front to back)
        for child in reversed(self.children):
            if child.handle_event(event):
                return True
        
        # Handle mouse events for this widget only if children didn't handle it
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.Vector2(event.pos)
            was_inside = self.mouse_inside
            self.mouse_inside = self.contains_point(mouse_pos)
            
            if self.mouse_inside and not was_inside:
                self.state = WidgetState.HOVER
                self.emit_event("mouse_enter")
            elif not self.mouse_inside and was_inside:
                self.state = WidgetState.NORMAL if not self.mouse_pressed else WidgetState.PRESSED
                self.emit_event("mouse_leave")
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.Vector2(event.pos)
                if self.contains_point(mouse_pos):
                    self.mouse_pressed = True
                    self.state = WidgetState.PRESSED
                    self.emit_event("mouse_down", event)
                    return True
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                if self.mouse_pressed:
                    self.mouse_pressed = False
                    mouse_pos = pygame.Vector2(event.pos)
                    
                    if self.contains_point(mouse_pos):
                        self.state = WidgetState.HOVER
                        self.emit_event("clicked", event)
                    else:
                        self.state = WidgetState.NORMAL
                        
                    self.emit_event("mouse_up", event)
                    return True
                
        return False
        
    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """Render the widget."""
        pass