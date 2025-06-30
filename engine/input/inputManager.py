import pygame


class InputManager:
    """
    InputManager handles keyboard and mouse input for the game.
    It provides methods to check for key presses, releases, and mouse button states.
    """

    def __init__(self):
        self.keys = pygame.key.get_pressed()
        self.mouse_buttons = pygame.mouse.get_pressed()
        self.mouse_position = pygame.mouse.get_pos()

    def update(self):
        """Update the input state."""
        self.keys = pygame.key.get_pressed()
        self.mouse_buttons = pygame.mouse.get_pressed()
        self.mouse_position = pygame.mouse.get_pos()

    def is_key_pressed(self, key: int) -> bool:
        """Check if a specific key is currently pressed."""
        return self.keys[key]

    def is_mouse_button_pressed(self, button: int) -> bool:
        """Check if a specific mouse button is currently pressed."""
        return self.mouse_buttons[button]