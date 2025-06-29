from engine import Actor
from engine import SpriteComponent, HealthComponent, RigidBodyComponent, InputComponent

from ..components.physics_player_controller import PhysicsPlayerController

import pygame

class Player(Actor):    
    def __init__(self, player_id: str, is_owner: bool = False):
        super().__init__(name="Player")
        
        # Add sprite component with reasonable size
        sprite = SpriteComponent(
            color=pygame.Color(255, 255, 255),  # Default white, will be changed later
            size=pygame.Vector2(32, 48)  # 32x48 pixel player
        )
        self.add_component(sprite)
        self.add_component(HealthComponent(max_health=100))
        self.add_component(RigidBodyComponent())
        
        # Add player controller
        self.player_controller = PhysicsPlayerController(300, 500)  # Reasonable values
        self.add_component(self.player_controller)
        
        # Add input component if this is the local player
        if is_owner:
            input_comp = InputComponent()
            input_comp.update = self._handle_input
            self.add_component(input_comp)
        
    def _handle_input(self, dt: float) -> None:
        """Handle player input and pass it to the physics controller."""        
        keys = pygame.key.get_pressed()
        
        # Calculate horizontal input
        horizontal = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            horizontal -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            horizontal += 1.0
            
        # Check jump input
        jump_pressed = keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]
        jump_held = jump_pressed
        
        # Set input on player controller
        self.player_controller.set_input(horizontal, jump_pressed, jump_held)