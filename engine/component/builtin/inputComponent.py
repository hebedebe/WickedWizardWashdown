from engine.component.component import Component

from typing import Callable

class InputComponent(Component):
    """
    InputComponent handles user input for actors.
    It can process keyboard and mouse events.
    """

    def __init__(self):
        super().__init__()
        self.key_bindings = {}
        self.mouse_bindings = {}

    def bind_key(self, key: str, action: Callable):
        """Bind a key to an action."""
        self.key_bindings[key] = action

    def bind_mouse(self, button: str, action: Callable):
        """Bind a mouse button to an action."""
        self.mouse_bindings[button] = action

    def handle_key_event(self, key: str):
        """Handle a key event."""
        if key in self.key_bindings:
            self.key_bindings[key]()

    def handle_mouse_event(self, button: str):
        """Handle a mouse event."""
        if button in self.mouse_bindings:
            self.mouse_bindings[button]()