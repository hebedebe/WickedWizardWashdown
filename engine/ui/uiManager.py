"""
User Interface system with widgets and event handling.
"""

import pygame
from typing import Dict, List, Optional, Callable, Any, Tuple
from .widget import Widget

        
class UIManager:
    """
    Manages the UI system and widget hierarchy.
    """
    
    def __init__(self, screen_size: Tuple[int, int] = None):
        self.screen_size = screen_size
        self.root_widgets: List[Widget] = []
        self.focused_widget: Optional[Widget] = None
        
    def addWidget(self, widget: Widget) -> None:
        """Add a root-level widget."""
        self.root_widgets.append(widget)
        
    def removeWidget(self, widget: Widget) -> None:
        """Remove a root-level widget."""
        if widget in self.root_widgets:
            self.root_widgets.remove(widget)
            
    def findWidget(self, name: str) -> Optional[Widget]:
        """Find a widget by name."""
        for widget in self.root_widgets:
            if widget.name == name:
                return widget
            result = widget.find_child(name)
            if result:
                return result
        return None
        
    def update(self, dt: float) -> None:
        """Update all widgets."""
        for widget in self.root_widgets:
            widget.update(dt)

    def lateUpdate(self, dt: float) -> None:
        """Late update for all widgets."""
        for widget in self.root_widgets:
            widget.lateUpdate(dt)
            
    def handleEvent(self, event: pygame.event.Event) -> bool:
        """Handle events for all widgets."""
        # Process widgets in reverse order (front to back)
        for widget in reversed(self.root_widgets):
            if widget.handle_event(event):
                return True
        return False
        
    def render(self, screen: pygame.Surface) -> None:
        """Render all widgets."""
        for widget in self.root_widgets:
            widget.render(screen)