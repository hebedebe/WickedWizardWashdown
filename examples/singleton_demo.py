"""
Example demonstrating the Game singleton pattern and easy access from actors/components.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
from engine import Game, Scene, Actor, Component, SpriteComponent
from engine.ui import UIManager, Label, FPSDisplay

class PlayerComponent(Component):
    """Example component that uses game singleton for easy access."""
    
    def __init__(self):
        super().__init__()
        self.speed = 200.0
        
    def update(self, dt: float) -> None:
        """Move player and demonstrate game access."""
        if not self.actor:
            return
            
        # Easy access to game systems via singleton
        input_mgr = self.game.input_manager
        
        # Move player based on input
        movement = pygame.Vector2(0, 0)
        if input_mgr.is_key_down(pygame.K_a) or input_mgr.is_key_down(pygame.K_LEFT):
            movement.x -= 1
        if input_mgr.is_key_down(pygame.K_d) or input_mgr.is_key_down(pygame.K_RIGHT):
            movement.x += 1
        if input_mgr.is_key_down(pygame.K_w) or input_mgr.is_key_down(pygame.K_UP):
            movement.y -= 1
        if input_mgr.is_key_down(pygame.K_s) or input_mgr.is_key_down(pygame.K_DOWN):
            movement.y += 1
            
        if movement.length() > 0:
            movement.normalize_ip()
            self.actor.transform.local_position += movement * self.speed * dt
            
        # Example: Access asset manager
        # asset_mgr = self.game.asset_manager
        
        # Example: Access network manager
        # network = self.game.network_manager
        
        # Example: Change scenes based on game logic
        if input_mgr.is_key_pressed(pygame.K_m):
            print("Switching to menu scene (if it existed)...")
            # self.game.load_scene("menu")

class GameManagerActor(Actor):
    """Example actor that manages game state using singleton access."""
    
    def __init__(self):
        super().__init__("GameManager")
        self.score = 0
        
    def update(self, dt: float) -> None:
        super().update(dt)
        
        # Example of using game singleton from actor
        input_mgr = self.game.input_manager
        
        # Quit game on ESC
        if input_mgr.is_key_pressed(pygame.K_ESCAPE):
            print("Quitting game via game manager...")
            self.game.quit()
            
        # Example: Add score and check for win condition
        if input_mgr.is_key_pressed(pygame.K_SPACE):
            self.score += 10
            print(f"Score: {self.score}")
            
            if self.score >= 100:
                print("You win! (This could load a victory scene)")
                # self.game.load_scene("victory")

class SingletonDemoScene(Scene):
    """Scene demonstrating singleton access patterns."""
    
    def __init__(self):
        super().__init__("SingletonDemo")
        self.ui_manager = None
        
    def on_enter(self) -> None:
        super().on_enter()
        
        # Setup UI (FPS display using singleton)
        screen_size = pygame.display.get_surface().get_size()
        self.ui_manager = UIManager(screen_size)
        
        # FPS display
        fps_display = FPSDisplay(
            pygame.Rect(10, 10, 120, 25),
            name="fps_display",
            update_interval=0.25
        )
        fps_display.text_color = pygame.Color(0, 255, 0)
        self.ui_manager.add_widget(fps_display)
        
        # Info label
        info_label = Label(
            pygame.Rect(10, 40, 400, 80),
            "Singleton Demo:\n• WASD/Arrows: Move player\n• Space: Add score\n• M: Menu message\n• ESC: Quit",
            name="info"
        )
        info_label.text_color = pygame.Color(255, 255, 255)
        info_label.align_y = 'top'
        self.ui_manager.add_widget(info_label)
        
        # Create game manager
        game_manager = GameManagerActor()
        self.add_actor(game_manager)
        
        # Create player
        player = self.create_actor("Player", pygame.Vector2(400, 300))
        
        # Add visual representation (simple sprite)
        sprite_comp = SpriteComponent()
        sprite_comp.color = pygame.Color(0, 100, 255)  # Blue player
        sprite_comp.size = pygame.Vector2(32, 32)
        player.add_component(sprite_comp)
        
        # Add player controller
        player_controller = PlayerComponent()
        player.add_component(player_controller)
        
        print("Singleton Demo Scene loaded!")
        print("Game instance ID:", id(self.game))
        
    def update(self, dt: float) -> None:
        super().update(dt)
        
        # Update UI
        if self.ui_manager:
            self.ui_manager.update(dt)
            
    def render(self, screen: pygame.Surface) -> None:
        # Dark blue background
        self.background_color = pygame.Color(20, 30, 50)
        super().render(screen)
        
        # Render UI
        if self.ui_manager:
            self.ui_manager.render(screen)
            
    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        
        # Handle UI events
        if self.ui_manager:
            if self.ui_manager.handle_event(event):
                return

def main():
    """Main function demonstrating singleton pattern."""
    print("Creating game instance...")
    
    # Create the first (and only) game instance
    game1 = Game(800, 600, "Singleton Pattern Demo")
    print(f"Game1 instance ID: {id(game1)}")
    
    # Try to create another instance - should return the same one
    game2 = Game(1024, 768, "This should be ignored")
    print(f"Game2 instance ID: {id(game2)}")
    print(f"Are they the same instance? {game1 is game2}")
    print(f"Game title: {game1.title}")  # Should still be the original title
    
    # Access game from anywhere
    game3 = Game.get_instance()
    print(f"Game3 instance ID: {id(game3)}")
    print(f"All instances are the same: {game1 is game2 is game3}")
    
    # Create and add the demo scene
    demo_scene = SingletonDemoScene()
    game1.add_scene("singleton_demo", demo_scene)
    game1.load_scene("singleton_demo")
    
    print("Starting game loop...")
    game1.run()

if __name__ == "__main__":
    main()
