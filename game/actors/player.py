from engine import Actor
from engine import SpriteComponent, NetworkComponent, HealthComponent, RigidBodyComponent, InputComponent
from engine import NetworkOwnership

from ..components.physics_player_controller import PhysicsPlayerController

import pygame

class Player(Actor):    
    def __init__(self, player_id: str, is_owner: bool = False):
        super().__init__(name="Player")
        
        self.add_component(SpriteComponent())
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

        # add this component last
        self.add_component(NetworkComponent(
            owner_id=player_id,
            ownership=NetworkOwnership.CLIENT if is_owner else NetworkOwnership.SERVER,
            sync_transform=True  # Sync transform for player movement
        ))
        
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