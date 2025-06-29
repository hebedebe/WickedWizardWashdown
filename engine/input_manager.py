"""
Input management system for handling keyboard, mouse, and controller input.
"""

import pygame
from typing import Dict, List, Set, Optional, Callable, Any
from enum import Enum

class InputState(Enum):
    """Input states for keys and buttons."""
    UP = 0
    DOWN = 1
    PRESSED = 2  # Just pressed this frame
    RELEASED = 3  # Just released this frame

class InputManager:
    """
    Centralized input management system.
    """
    
    def __init__(self):
        # Keyboard state
        self.keys_current: Set[int] = set()
        self.keys_previous: Set[int] = set()
        
        # Mouse state
        self.mouse_buttons_current: Set[int] = set()
        self.mouse_buttons_previous: Set[int] = set()
        self.mouse_position = pygame.Vector2(0, 0)
        self.mouse_delta = pygame.Vector2(0, 0)
        self.mouse_wheel = pygame.Vector2(0, 0)
        
        # Input bindings
        self.key_bindings: Dict[str, List[int]] = {}
        self.mouse_bindings: Dict[str, List[int]] = {}
        
        # Action states
        self.actions: Dict[str, InputState] = {}
        self.action_handlers: Dict[str, List[Callable]] = {}
        
        # Event history
        self.events: List[pygame.event.Event] = []
        
        # Controller support
        self.controllers: List[pygame.joystick.Joystick] = []
        self.controller_buttons_current: Dict[int, Set[int]] = {}
        self.controller_buttons_previous: Dict[int, Set[int]] = {}
        self.controller_axes: Dict[int, List[float]] = {}
        
        # Initialize controllers
        self._init_controllers()
        
    def _init_controllers(self) -> None:
        """Initialize game controllers."""
        pygame.joystick.init()
        
        for i in range(pygame.joystick.get_count()):
            controller = pygame.joystick.Joystick(i)
            controller.init()
            self.controllers.append(controller)
            self.controller_buttons_current[i] = set()
            self.controller_buttons_previous[i] = set()
            self.controller_axes[i] = [0.0] * controller.get_numaxes()
            
    def bind_key(self, action: str, key: int) -> None:
        """Bind a key to an action."""
        if action not in self.key_bindings:
            self.key_bindings[action] = []
        if key not in self.key_bindings[action]:
            self.key_bindings[action].append(key)
            
    def bind_mouse(self, action: str, button: int) -> None:
        """Bind a mouse button to an action."""
        if action not in self.mouse_bindings:
            self.mouse_bindings[action] = []
        if button not in self.mouse_bindings[action]:
            self.mouse_bindings[action].append(button)
            
    def unbind_key(self, action: str, key: int) -> None:
        """Unbind a key from an action."""
        if action in self.key_bindings and key in self.key_bindings[action]:
            self.key_bindings[action].remove(key)
            
    def unbind_mouse(self, action: str, button: int) -> None:
        """Unbind a mouse button from an action."""
        if action in self.mouse_bindings and button in self.mouse_bindings[action]:
            self.mouse_bindings[action].remove(button)
            
    def add_action_handler(self, action: str, handler: Callable) -> None:
        """Add a handler for an action."""
        if action not in self.action_handlers:
            self.action_handlers[action] = []
        self.action_handlers[action].append(handler)
        
    def remove_action_handler(self, action: str, handler: Callable) -> None:
        """Remove a handler from an action."""
        if action in self.action_handlers and handler in self.action_handlers[action]:
            self.action_handlers[action].remove(handler)
            
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle a pygame event."""
        self.events.append(event)
        
        if event.type == pygame.KEYDOWN:
            self.keys_current.add(event.key)
        elif event.type == pygame.KEYUP:
            self.keys_current.discard(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_buttons_current.add(event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_buttons_current.discard(event.button)
        elif event.type == pygame.MOUSEMOTION:
            new_pos = pygame.Vector2(event.pos)
            self.mouse_delta = new_pos - self.mouse_position
            self.mouse_position = new_pos
        elif event.type == pygame.MOUSEWHEEL:
            self.mouse_wheel = pygame.Vector2(event.x, event.y)
        elif event.type == pygame.JOYBUTTONDOWN:
            controller_id = event.instance_id
            if controller_id in self.controller_buttons_current:
                self.controller_buttons_current[controller_id].add(event.button)
        elif event.type == pygame.JOYBUTTONUP:
            controller_id = event.instance_id
            if controller_id in self.controller_buttons_current:
                self.controller_buttons_current[controller_id].discard(event.button)
        elif event.type == pygame.JOYAXISMOTION:
            controller_id = event.instance_id
            if controller_id in self.controller_axes:
                if event.axis < len(self.controller_axes[controller_id]):
                    self.controller_axes[controller_id][event.axis] = event.value
                    
    def update(self, dt: float) -> None:
        """Update input states and process actions."""
        # Update action states
        self._update_action_states()
        
        # Call action handlers
        self._process_action_handlers()
        
        # Update previous states
        self.keys_previous = self.keys_current.copy()
        self.mouse_buttons_previous = self.mouse_buttons_current.copy()
        
        for controller_id in self.controller_buttons_current:
            self.controller_buttons_previous[controller_id] = self.controller_buttons_current[controller_id].copy()
            
        # Reset frame-specific values
        self.mouse_delta = pygame.Vector2(0, 0)
        self.mouse_wheel = pygame.Vector2(0, 0)
        self.events.clear()
        
    def _update_action_states(self) -> None:
        """Update the state of all bound actions."""
        for action in set(self.key_bindings.keys()) | set(self.mouse_bindings.keys()):
            current_down = self._is_action_down(action)
            previous_down = self.actions.get(action, InputState.UP) in [InputState.DOWN, InputState.PRESSED]
            
            if current_down and not previous_down:
                self.actions[action] = InputState.PRESSED
            elif current_down and previous_down:
                self.actions[action] = InputState.DOWN
            elif not current_down and previous_down:
                self.actions[action] = InputState.RELEASED
            else:
                self.actions[action] = InputState.UP
                
    def _is_action_down(self, action: str) -> bool:
        """Check if any key/button bound to an action is currently down."""
        # Check keyboard
        if action in self.key_bindings:
            for key in self.key_bindings[action]:
                if key in self.keys_current:
                    return True
                    
        # Check mouse
        if action in self.mouse_bindings:
            for button in self.mouse_bindings[action]:
                if button in self.mouse_buttons_current:
                    return True
                    
        return False
        
    def _process_action_handlers(self) -> None:
        """Process action handlers for state changes."""
        for action, state in self.actions.items():
            if action in self.action_handlers:
                for handler in self.action_handlers[action]:
                    handler(action, state)
                    
    def is_key_down(self, key: int) -> bool:
        """Check if a key is currently held down."""
        return key in self.keys_current
        
    def is_key_pressed(self, key: int) -> bool:
        """Check if a key was just pressed this frame."""
        return key in self.keys_current and key not in self.keys_previous
        
    def is_key_released(self, key: int) -> bool:
        """Check if a key was just released this frame."""
        return key not in self.keys_current and key in self.keys_previous
        
    def is_mouse_button_down(self, button: int) -> bool:
        """Check if a mouse button is currently held down."""
        return button in self.mouse_buttons_current
        
    def is_mouse_button_pressed(self, button: int) -> bool:
        """Check if a mouse button was just pressed this frame."""
        return button in self.mouse_buttons_current and button not in self.mouse_buttons_previous
        
    def is_mouse_button_released(self, button: int) -> bool:
        """Check if a mouse button was just released this frame."""
        return button not in self.mouse_buttons_current and button in self.mouse_buttons_previous
        
    def is_action_down(self, action: str) -> bool:
        """Check if an action is currently active."""
        return self.actions.get(action, InputState.UP) in [InputState.DOWN, InputState.PRESSED]
        
    def is_action_pressed(self, action: str) -> bool:
        """Check if an action was just activated this frame."""
        return self.actions.get(action, InputState.UP) == InputState.PRESSED
        
    def is_action_released(self, action: str) -> bool:
        """Check if an action was just deactivated this frame."""
        return self.actions.get(action, InputState.UP) == InputState.RELEASED
        
    def get_mouse_position(self) -> pygame.Vector2:
        """Get the current mouse position."""
        return pygame.Vector2(self.mouse_position)
        
    def get_mouse_delta(self) -> pygame.Vector2:
        """Get the mouse movement delta for this frame."""
        return pygame.Vector2(self.mouse_delta)
        
    def get_mouse_wheel(self) -> pygame.Vector2:
        """Get the mouse wheel delta for this frame."""
        return pygame.Vector2(self.mouse_wheel)
        
    def get_controller_axis(self, controller_id: int, axis: int) -> float:
        """Get a controller axis value (-1 to 1)."""
        if controller_id in self.controller_axes:
            if 0 <= axis < len(self.controller_axes[controller_id]):
                return self.controller_axes[controller_id][axis]
        return 0.0
        
    def is_controller_button_down(self, controller_id: int, button: int) -> bool:
        """Check if a controller button is currently held down."""
        if controller_id in self.controller_buttons_current:
            return button in self.controller_buttons_current[controller_id]
        return False
        
    def is_controller_button_pressed(self, controller_id: int, button: int) -> bool:
        """Check if a controller button was just pressed this frame."""
        current = controller_id in self.controller_buttons_current and button in self.controller_buttons_current[controller_id]
        previous = controller_id in self.controller_buttons_previous and button in self.controller_buttons_previous[controller_id]
        return current and not previous
        
    def is_controller_button_released(self, controller_id: int, button: int) -> bool:
        """Check if a controller button was just released this frame."""
        current = controller_id in self.controller_buttons_current and button in self.controller_buttons_current[controller_id]
        previous = controller_id in self.controller_buttons_previous and button in self.controller_buttons_previous[controller_id]
        return not current and previous
        
    def get_events_by_type(self, event_type: int) -> List[pygame.event.Event]:
        """Get all events of a specific type from this frame."""
        return [event for event in self.events if event.type == event_type]
        
    def setup_default_bindings(self) -> None:
        """Set up default input bindings."""
        # Movement
        self.bind_key("move_up", pygame.K_w)
        self.bind_key("move_up", pygame.K_UP)
        self.bind_key("move_down", pygame.K_s)
        self.bind_key("move_down", pygame.K_DOWN)
        self.bind_key("move_left", pygame.K_a)
        self.bind_key("move_left", pygame.K_LEFT)
        self.bind_key("move_right", pygame.K_d)
        self.bind_key("move_right", pygame.K_RIGHT)
        
        # Actions
        self.bind_key("action", pygame.K_SPACE)
        self.bind_key("jump", pygame.K_SPACE)
        self.bind_key("interact", pygame.K_e)
        self.bind_key("pause", pygame.K_ESCAPE)
        
        # Mouse
        self.bind_mouse("primary_action", 1)  # Left click
        self.bind_mouse("secondary_action", 3)  # Right click
        
    def get_movement_vector(self) -> pygame.Vector2:
        """Get a normalized movement vector from input."""
        movement = pygame.Vector2(0, 0)
        
        if self.is_action_down("move_left"):
            movement.x -= 1
        if self.is_action_down("move_right"):
            movement.x += 1
        if self.is_action_down("move_up"):
            movement.y -= 1
        if self.is_action_down("move_down"):
            movement.y += 1
            
        # Normalize diagonal movement
        if movement.length() > 0:
            movement = movement.normalize()
            
        return movement
        
    def save_bindings(self, filename: str) -> None:
        """Save input bindings to a file."""
        import json
        
        bindings_data = {
            'key_bindings': {action: keys for action, keys in self.key_bindings.items()},
            'mouse_bindings': {action: buttons for action, buttons in self.mouse_bindings.items()}
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(bindings_data, f, indent=2)
        except IOError as e:
            print(f"Could not save input bindings: {e}")
            
    def load_bindings(self, filename: str) -> None:
        """Load input bindings from a file."""
        import json
        
        try:
            with open(filename, 'r') as f:
                bindings_data = json.load(f)
                
            self.key_bindings = bindings_data.get('key_bindings', {})
            self.mouse_bindings = bindings_data.get('mouse_bindings', {})
            
        except (IOError, json.JSONDecodeError) as e:
            print(f"Could not load input bindings: {e}")
            self.setup_default_bindings()  # Fall back to defaults
