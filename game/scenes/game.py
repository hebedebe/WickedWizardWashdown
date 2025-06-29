from engine import Game, Scene
import pygame
from game.actors.player import Player


class GameScene(Scene):
    """Main gameplay scene."""
    
    def __init__(self):
        super().__init__("Game")
        
    def on_enter(self):
        super().on_enter()
        
        # Create player
        player = Player("player", True)
        self.add_actor(player)
        
        # Set background color
        self.background_color = pygame.Color(50, 50, 100)
        
    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.game:
                    self.game.pop_scene()