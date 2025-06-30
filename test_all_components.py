"""
Comprehensive test for all implemented builti    # === TransformComponent Test ===
    transform_actor = Actor("TransformActor")
    transform_actor.transform.setPosition(300, 300)
    
    transform_comp = TransformComponent()
    transform_actor.addComponent(transform_comp)nents.
"""

from engine import *
import pygame

def test_all_components():
    """Test all implemented builtin components."""
    
    print("Testing all builtin components...")
    
    # Create a game instance
    game = Game(1000, 700, "All Components Test")
    
    # Create a test scene
    test_scene = Scene()
    game.addScene("test", test_scene)
    game.loadScene("test")
    
    # === SpriteComponent Test ===
    sprite_actor = Actor("SpriteActor")
    sprite_actor.transform.setPosition(200, 150)
    
    sprite_comp = SpriteComponent("default_cursor")
    sprite_comp.set_tint(pygame.Color(100, 200, 255))
    sprite_comp.scale_modifier = pygame.Vector2(2, 2)
    sprite_actor.addComponent(sprite_comp)
    
    test_scene.addActor(sprite_actor)
    
    # === TextComponent Test ===
    text_actor = Actor("TextActor")
    text_actor.transform.setPosition(500, 100)
    
    text_comp = TextComponent("Hello, World!\nMulti-line text!", font_size=24)
    text_comp.set_color(pygame.Color(255, 255, 0))
    text_comp.set_alignment('center', 'center')
    text_actor.addComponent(text_comp)
    
    test_scene.addActor(text_actor)
    
    # === AudioComponent Test ===
    audio_actor = Actor("AudioActor")
    # Note: We don't have audio files in assets/sounds, so this will fail gracefully
    audio_comp = AudioComponent("test_sound", volume=0.7, loop=True)
    audio_actor.addComponent(audio_comp)
    
    test_scene.addActor(audio_actor)
    
    # === TransformComponent Test ===
    transform_actor = Actor("TransformActor")
    transform_actor.transform.setPosition(300, 300)
    
    transform_comp = TransformComponent()
    # Test some constraints
    transform_comp.lock_rotation = False  # Allow rotation for demo
    transform_actor.addComponent(transform_comp)
    
    # Add a sprite to visualize the transform
    transform_sprite = SpriteComponent("default_cursor")
    transform_sprite.set_tint(pygame.Color(255, 100, 100))
    transform_actor.addComponent(transform_sprite)
    
    test_scene.addActor(transform_actor)
    
    # === ColliderComponent Test ===
    collider_actor = Actor("ColliderActor")
    collider_actor.transform.setPosition(600, 300)
    
    collider_comp = ColliderComponent(ColliderType.RECTANGLE, width=64, height=64)
    collider_comp.debug_render = True
    collider_comp.collision_layer = 1
    collider_actor.addComponent(collider_comp)
    
    # Add sprite for visualization
    collider_sprite = SpriteComponent("default_cursor")
    collider_sprite.set_tint(pygame.Color(100, 255, 100))
    collider_sprite.scale_modifier = pygame.Vector2(3, 3)
    collider_actor.addComponent(collider_sprite)
    
    test_scene.addActor(collider_actor)
    
    # === InputComponent Test ===
    input_actor = Actor("InputActor")
    input_actor.transform.setPosition(400, 500)
    
    input_comp = InputComponent()
    input_actor.addComponent(input_comp)
    
    # Add sprite for visualization
    input_sprite = SpriteComponent("default_cursor")
    input_sprite.set_tint(pygame.Color(255, 255, 100))
    input_actor.addComponent(input_sprite)
    
    # Add input bindings
    def move_up():
        input_actor.transform.position.y -= 5
        print("Moving up!")
        
    def move_down():
        input_actor.transform.position.y += 5
        print("Moving down!")
        
    def move_left():
        input_actor.transform.position.x -= 5
        print("Moving left!")
        
    def move_right():
        input_actor.transform.position.x += 5
        print("Moving right!")
        
    def transform_test():
        # Test movement using the TransformComponent
        current_pos = transform_actor.transform.position
        target = pygame.Vector2(
            current_pos.x + 100 if current_pos.x < 500 else 300,  # Move back and forth
            current_pos.y
        )
        transform_comp.move_to(target)
        print(f"Moving to {target} from {current_pos}")
        
    def test_audio():
        # Try to play audio (will print message if no sound file)
        print("Testing audio playback...")
        audio_comp.play()
        
    # Bind keys
    input_comp.bind_movement_keys(move_up, move_down, move_left, move_right)
    input_comp.bind_key(pygame.K_SPACE, transform_test)
    input_comp.bind_key(pygame.K_p, test_audio)
    
    test_scene.addActor(input_actor)
    
    # === Animation Component (using TransformComponent) ===
    class AnimationComponent(Component):
        def __init__(self):
            super().__init__()
            self.time = 0
            
        def update(self, dt):
            self.time += dt
            # Animate the sprite actor in a circle
            radius = 50
            center_x, center_y = 200, 150
            self.actor.transform.position.x = center_x + radius * sin(self.time * 2)
            self.actor.transform.position.y = center_y + radius * cos(self.time * 2)
            self.actor.transform.rotation = self.time * 180 / 3.14159 * 2
    
    sprite_actor.addComponent(AnimationComponent())
    
    # === Actor Parent/Child Transform Hierarchy Test ===
    # Create a parent actor with a transform component
    parent_actor = Actor("ParentActor")
    parent_actor.transform.setPosition(400, 400)
    parent_transform_comp = TransformComponent()
    parent_actor.addComponent(parent_transform_comp)
    
    # Add a sprite to visualize the parent
    parent_sprite = SpriteComponent("default_cursor")
    parent_sprite.set_tint(pygame.Color(0, 255, 255))  # Cyan
    parent_sprite.scale_modifier = pygame.Vector2(1.5, 1.5)  # Make it bigger to distinguish
    parent_actor.addComponent(parent_sprite)
    
    # Create a child actor with a local offset
    child_actor = Actor("ChildActor")
    child_actor.setParent(parent_actor)  # Set parent relationship
    child_transform_comp = TransformComponent()
    child_transform_comp.local_position = pygame.Vector2(50, 0)  # Offset from parent
    child_actor.addComponent(child_transform_comp)
    
    # Add a sprite to visualize the child
    child_sprite = SpriteComponent("default_cursor")
    child_sprite.set_tint(pygame.Color(255, 0, 255))  # Magenta
    child_actor.addComponent(child_sprite)
    
    # Animate the parent to show hierarchical transformation
    class ParentAnimationComponent(Component):
        def __init__(self):
            super().__init__()
            self.time = 0
            
        def update(self, dt):
            self.time += dt
            # Rotate the parent, child should follow
            self.actor.transform.rotation = self.time * 50  # Degrees per second
    
    parent_actor.addComponent(ParentAnimationComponent())
    
    test_scene.addActor(parent_actor)
    test_scene.addActor(child_actor)
    
    # === UI Elements ===
    test_scene.uiManager.addWidget(FPSDisplay())
    
    # Instructions
    instructions_text = """
    Component Test Demo:
    
    • Rotating blue sprite (SpriteComponent + Animation)
    • Yellow text (TextComponent) 
    • Red sprite with TransformComponent
    • Green sprite with ColliderComponent (debug visible)
    • Yellow controllable sprite (InputComponent)
    • Cyan parent with magenta child (Actor parent/child hierarchy)
    
    Controls:
    • WASD: Move yellow sprite
    • SPACE: Test transform movement (red sprite)
    • P: Test audio component
    
    Press ESC or close window to exit
    """
    
    print(instructions_text)
    
    # Run the game
    game.run()

if __name__ == "__main__":
    test_all_components()
