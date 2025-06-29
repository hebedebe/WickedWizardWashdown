"""
Demo showcasing the FileAnimationComponent with property animations.
Shows how to animate component properties, transforms, and create smooth effects.
"""

import pygame
import sys
import os
import math
from typing import Dict
from engine import Game, Scene, Actor, SpriteComponent
from engine.enhanced_animation import FileAnimationComponent, EasingType


class PropertyAnimatedCharacter(Actor):
    """Character that demonstrates property animations."""
    
    def __init__(self, name: str, animation_file: str):
        super().__init__(name)
        
        # Add sprite component
        sprite = SpriteComponent(
            color=pygame.Color(100, 150, 255),
            size=pygame.Vector2(64, 64)
        )
        self.add_component(sprite)
        
        # Add animation component
        self.animation = FileAnimationComponent(animation_file)
        self.add_component(self.animation)
        
        # Set up callbacks
        self.animation.add_event_callback("attack_started", self.on_attack_started)
        self.animation.add_event_callback("attack_finished", self.on_attack_finished)
        self.animation.add_event_callback("deal_damage", self.on_deal_damage)
        self.animation.add_event_callback("screen_shake", self.on_screen_shake)
        self.animation.add_event_callback("spell_completed", self.on_spell_completed)
        
        # Store original position for effects
        self.original_position = pygame.Vector2(0, 0)
        
    def setup_position(self, x: float, y: float):
        """Set up the character's position."""
        self.transform.local_position = pygame.Vector2(x, y)
        self.original_position = pygame.Vector2(x, y)
    
    def on_attack_started(self):
        print(f"{self.name}: Attack started!")
    
    def on_attack_finished(self):
        print(f"{self.name}: Attack finished!")
    
    def on_deal_damage(self):
        print(f"{self.name}: WHAM! Dealing damage!")
    
    def on_screen_shake(self):
        print(f"{self.name}: *Screen shakes*")
    
    def on_spell_completed(self):
        print(f"{self.name}: ✨ Spell cast! ✨")


class PropertyAnimationDemoScene(Scene):
    """Scene demonstrating property animations."""
    
    def __init__(self):
        super().__init__("PropertyAnimationDemo")
        self.characters: Dict[str, PropertyAnimatedCharacter] = {}
        self.current_character = 0
        self.character_names = []
        self.demo_time = 0.0
    
    def start(self) -> None:
        """Initialize the scene."""
        super().start()
        
        # Create simple test animation file
        self._create_test_animations()
        
        # Create test characters
        try:
            # Character 1: Simple test
            char1 = PropertyAnimatedCharacter("TestChar1", "assets/data/simple_property_test.yaml")
            char1.setup_position(150, 200)
            self.add_actor(char1)
            self.characters["test1"] = char1
            
            # Character 2: Enhanced animations (if available)
            if os.path.exists("assets/data/enhanced_player_animations.yaml"):
                char2 = PropertyAnimatedCharacter("EnhancedChar", "assets/data/enhanced_player_animations.yaml")
                char2.setup_position(400, 200)
                self.add_actor(char2)
                self.characters["enhanced"] = char2
            
            # Character 3: Manual property animations
            char3 = PropertyAnimatedCharacter("ManualChar", "assets/data/simple_property_test.yaml")
            char3.setup_position(650, 200)
            self.add_actor(char3)
            self.characters["manual"] = char3
            
            # Set up manual animations for char3
            self._setup_manual_animations(char3)
            
            self.character_names = list(self.characters.keys())
            
            print("Property Animation Demo Controls:")
            print("  1: Idle animation")
            print("  2: Bobbing animation")
            print("  3: Attack animation")
            print("  4: Floating animation")
            print("  5: Spell cast animation")
            print("  6: Hurt animation")
            print("  7: Power up animation")
            print("  8: Death animation")
            print("  TAB: Switch character")
            print("  R: Reset position")
            print("  M: Add manual sine wave")
            print("  C: Clear property animations")
            print("  ESC: Quit")
            
        except Exception as e:
            print(f"Error setting up demo: {e}")
    
    def _create_test_animations(self):
        """Create simple test animation files."""
        os.makedirs("assets/data", exist_ok=True)
        
        # Simple property animation test
        simple_test = """name: "Property Animation Test"
base_path: "assets/images/"
default_animation: "idle"

animations:
  idle:
    loop: true
    frames:
      - source: "default_cursor.png"
        duration: 0.5
    property_animations:
      - target: "transform.position.y"
        base_value: 0
        amplitude: 5
        frequency: 1.0
        easing: "sine_wave"

  bobbing:
    loop: true
    frames:
      - source: "default_cursor.png"
        duration: 1.0
    property_animations:
      - target: "transform.position.y"
        base_value: 0
        amplitude: 15
        frequency: 0.8
        easing: "sine_wave"
      - target: "transform.rotation"
        base_value: 0
        amplitude: 10
        frequency: 0.5
        easing: "sine_wave"

  attack:
    loop: false
    next_animation: "idle"
    on_start: "attack_started"
    on_end: "attack_finished"
    frame_events:
      1: "deal_damage"
    frames:
      - source: "default_cursor.png"
        duration: 0.1
      - source: "default_cursor.png"
        duration: 0.2
        flip_x: true
      - source: "default_cursor.png"
        duration: 0.1
    property_animations:
      - target: "transform.scale.x"
        start_value: 1.0
        end_value: 1.5
        duration: 0.2
        easing: "ease_out"
        ping_pong: true
      - target: "SpriteComponent.alpha"
        start_value: 255
        end_value: 100
        duration: 0.1
        easing: "pulse"
        loop: true

  floating:
    loop: true
    frames:
      - source: "default_cursor.png"
        duration: 2.0
    property_animations:
      - target: "transform.position.y"
        base_value: 0
        amplitude: 20
        frequency: 0.3
        easing: "sine_wave"
      - target: "transform.scale.x"
        start_value: 1.0
        end_value: 1.1
        duration: 3.0
        easing: "ease_in_out"
        ping_pong: true
        loop: true
      - target: "transform.rotation"
        base_value: 0
        amplitude: 15
        frequency: 0.2
        easing: "sine_wave"

  spell:
    loop: false
    next_animation: "idle"
    on_end: "spell_completed"
    frames:
      - source: "default_cursor.png"
        duration: 0.5
        flip_y: true
      - source: "default_cursor.png"
        duration: 0.5
        flip_x: true
        flip_y: true
      - source: "default_cursor.png"
        duration: 0.5
    property_animations:
      - target: "transform.position.y"
        start_value: 0
        end_value: -30
        duration: 1.0
        easing: "ease_out"
      - target: "transform.rotation"
        start_value: 0
        end_value: 360
        duration: 1.5
        easing: "ease_in_out"
      - target: "transform.scale.x"
        start_value: 1.0
        end_value: 2.0
        duration: 1.5
        easing: "elastic"

  hurt:
    loop: false
    next_animation: "idle"
    frames:
      - source: "default_cursor.png"
        duration: 0.1
      - source: "default_cursor.png"
        duration: 0.1
        offset_x: -3
      - source: "default_cursor.png"
        duration: 0.1
        offset_x: 3
      - source: "default_cursor.png"
        duration: 0.1
    property_animations:
      - target: "transform.position.x"
        start_value: 0
        end_value: -15
        duration: 0.2
        easing: "ease_out"
      - target: "SpriteComponent.alpha"
        start_value: 255
        end_value: 128
        duration: 0.05
        easing: "linear"
        ping_pong: true
        loop: true

  powerup:
    loop: false
    next_animation: "idle"
    frames:
      - source: "default_cursor.png"
        duration: 0.3
      - source: "default_cursor.png"
        duration: 0.3
        flip_x: true
      - source: "default_cursor.png"
        duration: 0.4
    property_animations:
      - target: "transform.scale.x"
        start_value: 1.0
        end_value: 2.0
        duration: 0.5
        easing: "bounce"
      - target: "transform.scale.y"
        start_value: 1.0
        end_value: 2.0
        duration: 0.5
        easing: "bounce"
      - target: "SpriteComponent.alpha"
        start_value: 255
        end_value: 100
        duration: 0.1
        easing: "pulse"
        loop: true

  death:
    loop: false
    frames:
      - source: "default_cursor.png"
        duration: 0.5
      - source: "default_cursor.png"
        duration: 1.0
        flip_y: true
    property_animations:
      - target: "transform.position.y"
        start_value: 0
        end_value: 30
        duration: 1.0
        easing: "ease_in"
      - target: "transform.rotation"
        start_value: 0
        end_value: 90
        duration: 1.0
        easing: "ease_in"
      - target: "SpriteComponent.alpha"
        start_value: 255
        end_value: 0
        duration: 1.5
        easing: "ease_out"
"""
        
        with open("assets/data/simple_property_test.yaml", "w") as f:
            f.write(simple_test)
    
    def _setup_manual_animations(self, character: PropertyAnimatedCharacter):
        """Set up manual property animations."""
        # Add a continuous sine wave for Y position
        character.animation.add_sine_wave_animation(
            "transform.position.y", 
            base_value=0, 
            amplitude=8, 
            frequency=2.0
        )
        
        # Add a scaling animation
        character.animation.add_property_animation(
            "transform.scale.x",
            start_value=1.0,
            end_value=1.2,
            duration=2.0,
            easing=EasingType.EASE_IN_OUT
        )
    
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
                self.current_character = (self.current_character + 1) % len(self.character_names)
                char_name = self.character_names[self.current_character]
                print(f"Switched to: {char_name}")
            
            elif event.key == pygame.K_r:
                # Reset position
                current_char.transform.local_position = pygame.Vector2(current_char.original_position)
                current_char.transform.local_rotation = 0
                current_char.transform.local_scale = pygame.Vector2(1, 1)
                sprite = current_char.get_component(SpriteComponent)
                if sprite:
                    sprite.alpha = 255
                print("Reset character")
            
            elif event.key == pygame.K_m:
                # Add manual sine wave
                current_char.animation.add_sine_wave_animation(
                    "transform.rotation",
                    base_value=0,
                    amplitude=45,
                    frequency=1.0
                )
                print("Added manual sine wave rotation")
            
            elif event.key == pygame.K_c:
                # Clear property animations
                current_char.animation.stop_property_animations()
                print("Cleared property animations")
            
            # Animation keys
            elif event.key == pygame.K_1:
                current_char.animation.play("idle")
            elif event.key == pygame.K_2:
                current_char.animation.play("bobbing")
            elif event.key == pygame.K_3:
                current_char.animation.play("attack")
            elif event.key == pygame.K_4:
                current_char.animation.play("floating")
            elif event.key == pygame.K_5:
                current_char.animation.play("spell")
            elif event.key == pygame.K_6:
                current_char.animation.play("hurt")
            elif event.key == pygame.K_7:
                current_char.animation.play("powerup")
            elif event.key == pygame.K_8:
                current_char.animation.play("death")
    
    def _get_current_character(self) -> PropertyAnimatedCharacter:
        """Get the currently selected character."""
        if not self.character_names:
            return None
        
        char_name = self.character_names[self.current_character]
        return self.characters.get(char_name)
    
    def update(self, dt: float) -> None:
        """Update the scene."""
        super().update(dt)
        self.demo_time += dt
        
        # Update window title with current character info
        current_char = self._get_current_character()
        if current_char:
            char_name = self.character_names[self.current_character]
            current_anim = current_char.animation.current_animation or "None"
            playing = "Playing" if current_char.animation.playing else "Stopped"
            paused = " (Paused)" if current_char.animation.paused else ""
            
            title = f"Property Animation Demo - {char_name}: {current_anim} {playing}{paused}"
            pygame.display.set_caption(title)


class PropertyAnimationDemoGame(Game):
    """Game demonstrating property animations."""
    
    def __init__(self):
        super().__init__(
            title="Property Animation Demo",
            window_size=(800, 600),
            target_fps=60
        )
    
    def initialize(self) -> bool:
        """Initialize the game."""
        if not super().initialize():
            return False
        
        # Create and start the demo scene
        demo_scene = PropertyAnimationDemoScene()
        self.scene_manager.add_scene(demo_scene)
        self.scene_manager.set_active_scene("PropertyAnimationDemo")
        
        return True


def main():
    """Main function."""
    game = PropertyAnimationDemoGame()
    
    if game.initialize():
        print("Starting Property Animation Demo...")
        print("Watch the characters animate with property animations!")
        game.run()
    else:
        print("Failed to initialize game")
        sys.exit(1)


if __name__ == "__main__":
    main()
