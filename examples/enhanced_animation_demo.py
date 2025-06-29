"""
Example demonstrating the FileAnimationComponent with file-based animations.
"""

import pygame
import sys
import os
from typing import Dict
from engine import Game, Scene, Actor, SpriteComponent
from engine.enhanced_animation import FileAnimationComponent, create_animation_template


class AnimatedCharacter(Actor):
    """An actor with file-based animations."""
    
    def __init__(self, name: str, animation_file: str):
        super().__init__(name)
        
        # Add sprite component
        sprite = SpriteComponent(
            color=pygame.Color(255, 255, 255),
            size=pygame.Vector2(64, 64)
        )
        self.add_component(sprite)
        
        # Add file-based animation component
        self.animation = FileAnimationComponent(animation_file)
        self.add_component(self.animation)
        
        # Set up animation event callbacks
        self.animation.add_event_callback("attack_started", self.on_attack_started)
        self.animation.add_event_callback("attack_finished", self.on_attack_finished)
        self.animation.add_event_callback("deal_damage", self.on_deal_damage)
        self.animation.add_event_callback("screen_shake", self.on_screen_shake)
        
        # Character state
        self.is_attacking = False
        self.health = 100
    
    def on_attack_started(self):
        """Called when attack animation starts."""
        print(f"{self.name}: Attack started!")
        self.is_attacking = True
    
    def on_attack_finished(self):
        """Called when attack animation ends."""
        print(f"{self.name}: Attack finished!")
        self.is_attacking = False
    
    def on_deal_damage(self):
        """Called when damage should be dealt."""
        print(f"{self.name}: Dealing damage!")
    
    def on_screen_shake(self):
        """Called when screen should shake."""
        print(f"{self.name}: Screen shake!")
    
    def take_damage(self, amount: int):
        """Take damage and play hurt animation."""
        self.health -= amount
        print(f"{self.name}: Took {amount} damage! Health: {self.health}")
        if self.health > 0:
            self.animation.play("hurt")
        else:
            self.animation.play("death")


class AnimationDemoScene(Scene):
    """Scene demonstrating enhanced animations."""
    
    def __init__(self):
        super().__init__("AnimationDemo")
        self.characters: Dict[str, AnimatedCharacter] = {}
        self.current_character = 0
        self.character_names = []
    
    def start(self) -> None:
        """Initialize the scene."""
        super().start()
        
        # Create animation template files if they don't exist
        self._create_sample_animations()
        
        # Create animated characters
        try:
            # Player character
            player = AnimatedCharacter(
                "Player", 
                "assets/data/player_animations.yaml"
            )
            player.transform.local_position = pygame.Vector2(200, 300)
            self.add_actor(player)
            self.characters["player"] = player
            
            # Enemy character (if exists)
            if os.path.exists("assets/data/goblin_animations.json"):
                goblin = AnimatedCharacter(
                    "Goblin",
                    "assets/data/goblin_animations.json"
                )
                goblin.transform.local_position = pygame.Vector2(400, 300)
                self.add_actor(goblin)
                self.characters["goblin"] = goblin
            
            self.character_names = list(self.characters.keys())
            
            print("Animation Demo Controls:")
            print("  1-9: Play different animations")
            print("  TAB: Switch between characters")
            print("  SPACE: Play attack animation")
            print("  H: Take damage")
            print("  P: Pause/Resume animation")
            print("  S: Stop animation")
            print("  ESC: Quit")
            
        except Exception as e:
            print(f"Error loading animations: {e}")
    
    def _create_sample_animations(self):
        """Create sample animation files if they don't exist."""
        # Create simple template for testing
        if not os.path.exists("assets/data/simple_test.yaml"):
            os.makedirs("assets/data", exist_ok=True)
            
            simple_template = """name: "Simple Test Character"
base_path: "assets/images/"
default_animation: "idle"

animations:
  idle:
    loop: true
    frames:
      - source: "default_cursor.png"  # Using existing image
        duration: 0.5
      - source: "default_cursor.png"
        duration: 0.5
        offset_y: -2

  bounce:
    loop: true
    ping_pong: true
    frames:
      - source: "default_cursor.png"
        duration: 0.1
      - source: "default_cursor.png"
        duration: 0.1
        offset_y: -5
      - source: "default_cursor.png"
        duration: 0.1
        offset_y: -10
      - source: "default_cursor.png"
        duration: 0.1
        offset_y: -15

  spin:
    loop: true
    frames:
      - source: "default_cursor.png"
        duration: 0.1
      - source: "default_cursor.png"
        duration: 0.1
        flip_x: true
      - source: "default_cursor.png"
        duration: 0.1
        flip_y: true
      - source: "default_cursor.png"
        duration: 0.1
        flip_x: true
        flip_y: true
"""
            
            with open("assets/data/simple_test.yaml", "w") as f:
                f.write(simple_template)
            
            # Create a test character with the simple animations
            test_char = AnimatedCharacter(
                "TestChar",
                "assets/data/simple_test.yaml"
            )
            test_char.transform.local_position = pygame.Vector2(100, 200)
            self.add_actor(test_char)
            self.characters["test"] = test_char
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            current_char = self._get_current_character()
            if not current_char:
                return
            
            if event.key == pygame.K_ESCAPE:
                self.game.quit()
            
            elif event.key == pygame.K_TAB:
                # Switch character
                self.current_character = (self.current_character + 1) % len(self.character_names)
                char_name = self.character_names[self.current_character]
                print(f"Switched to: {char_name}")
            
            elif event.key == pygame.K_SPACE:
                # Attack
                current_char.animation.play("attack")
            
            elif event.key == pygame.K_h:
                # Take damage
                current_char.take_damage(20)
            
            elif event.key == pygame.K_p:
                # Pause/Resume
                if current_char.animation.paused:
                    current_char.animation.resume()
                    print("Resumed animation")
                else:
                    current_char.animation.pause()
                    print("Paused animation")
            
            elif event.key == pygame.K_s:
                # Stop
                current_char.animation.stop()
                print("Stopped animation")
            
            # Number keys for different animations
            elif event.key == pygame.K_1:
                current_char.animation.play("idle")
            elif event.key == pygame.K_2:
                current_char.animation.play("walk")
            elif event.key == pygame.K_3:
                current_char.animation.play("run")
            elif event.key == pygame.K_4:
                current_char.animation.play("jump")
            elif event.key == pygame.K_5:
                current_char.animation.play("fall")
            elif event.key == pygame.K_6:
                current_char.animation.play("spell_cast")
            elif event.key == pygame.K_7:
                current_char.animation.play("hurt")
            elif event.key == pygame.K_8:
                current_char.animation.play("death")
            elif event.key == pygame.K_9:
                # For test character
                if "test" in self.characters:
                    test_char = self.characters["test"]
                    animations = test_char.animation.get_animation_names()
                    if "bounce" in animations:
                        test_char.animation.play("bounce")
                    elif "spin" in animations:
                        test_char.animation.play("spin")
    
    def _get_current_character(self) -> AnimatedCharacter:
        """Get the currently selected character."""
        if not self.character_names:
            return None
        
        char_name = self.character_names[self.current_character]
        return self.characters.get(char_name)
    
    def update(self, dt: float) -> None:
        """Update the scene."""
        super().update(dt)
        
        # Display current character and animation info
        current_char = self._get_current_character()
        if current_char:
            char_name = self.character_names[self.current_character]
            current_anim = current_char.animation.current_animation or "None"
            playing = "Playing" if current_char.animation.playing else "Stopped"
            paused = " (Paused)" if current_char.animation.paused else ""
            
            # You could display this on screen in a real implementation
            # For now, we'll just update the window title
            if hasattr(self.game, 'screen'):
                title = f"Animation Demo - {char_name}: {current_anim} {playing}{paused}"
                pygame.display.set_caption(title)


class AnimationDemoGame(Game):
    """Game demonstrating enhanced animations."""
    
    def __init__(self):
        super().__init__(
            title="Enhanced Animation Demo",
            window_size=(800, 600),
            target_fps=60
        )
    
    def initialize(self) -> bool:
        """Initialize the game."""
        if not super().initialize():
            return False
        
        # Create and start the demo scene
        demo_scene = AnimationDemoScene()
        self.scene_manager.add_scene(demo_scene)
        self.scene_manager.set_active_scene("AnimationDemo")
        
        return True


def main():
    """Main function."""
    # Create sample animation files
    print("Creating sample animation files...")
    
    os.makedirs("assets/data", exist_ok=True)
    
    # Create a basic template
    create_animation_template("assets/data/template.yaml", "Template Character")
    print("Created template.yaml")
    
    # Run the demo
    game = AnimationDemoGame()
    
    if game.initialize():
        print("Starting Enhanced Animation Demo...")
        game.run()
    else:
        print("Failed to initialize game")
        sys.exit(1)


if __name__ == "__main__":
    main()
