"""
Input handling component for actors.
"""

import pygame
from typing import Callable, List
from ..core.actor import Component


class InputComponent(Component):
    """
    Component for handling input events.
    """
    
    def __init__(self):
        super().__init__()
        self.key_handlers: dict = {}
        self.mouse_handlers: dict = {}
        self.input_handlers: List[Callable] = []
        
    def bind_key(self, key: int, callback: Callable, event_type: int = pygame.KEYDOWN) -> None:
        """Bind a key to a callback function."""
        if event_type not in self.key_handlers:
            self.key_handlers[event_type] = {}
        self.key_handlers[event_type][key] = callback
        
    def bind_mouse(self, button: int, callback: Callable, event_type: int = pygame.MOUSEBUTTONDOWN) -> None:
        """Bind a mouse button to a callback function."""
        if event_type not in self.mouse_handlers:
            self.mouse_handlers[event_type] = {}
        self.mouse_handlers[event_type][button] = callback
        
    def add_input_handler(self, handler: Callable) -> None:
        """Add a general input handler."""
        self.input_handlers.append(handler)
        
    def update(self, dt: float) -> None:
        """Check for continuous input (held keys)."""
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        
        # Process held keys
        for handler in self.input_handlers:
            handler(keys, mouse_buttons, dt)
            
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle discrete input events."""
        if event.type in self.key_handlers:
            if event.key in self.key_handlers[event.type]:
                self.key_handlers[event.type][event.key](event)
                
        if event.type in self.mouse_handlers:
            if event.button in self.mouse_handlers[event.type]:
                self.mouse_handlers[event.type][event.button](event)
