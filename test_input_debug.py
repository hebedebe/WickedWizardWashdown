"""
Simple test to debug input handling.
"""

from engine import *
import pygame

def test_input_debug():
    """Simple test to debug input handling."""
    
    print("Testing input system...")
    
    game = Game(800, 600, "Input Debug Test")
    test_scene = Scene()
    game.addScene("test", test_scene)
    game.loadScene("test")
    
    # Create actor with input component
    input_actor = Actor("InputActor")
    input_actor.transform.setPosition(400, 300)
    
    input_comp = InputComponent()
    input_actor.addComponent(input_comp)
    
    # Add sprite to see the actor
    sprite_comp = SpriteComponent("default_cursor")
    sprite_comp.set_tint(pygame.Color(255, 255, 0))
    sprite_comp.scale_modifier = pygame.Vector2(3, 3)
    input_actor.addComponent(sprite_comp)
    
    test_scene.addActor(input_actor)
    
    # Test movement functions
    def move_up():
        print("MOVE UP called!")
        input_actor.transform.position.y -= 10
        
    def move_down():
        print("MOVE DOWN called!")
        input_actor.transform.position.y += 10
        
    def move_left():
        print("MOVE LEFT called!")
        input_actor.transform.position.x -= 10
        
    def move_right():
        print("MOVE RIGHT called!")
        input_actor.transform.position.x += 10
        
    def test_space():
        print("SPACE pressed!")
        
    # Bind keys
    print("Binding keys...")
    input_comp.bind_key(pygame.K_w, move_up)
    input_comp.bind_key(pygame.K_s, move_down)
    input_comp.bind_key(pygame.K_a, move_left)
    input_comp.bind_key(pygame.K_d, move_right)
    input_comp.bind_key(pygame.K_SPACE, test_space)
    
    print("Keys bound! Try WASD and SPACE")
    print("You should see the yellow cursor sprite move")
    
    # Add FPS display
    test_scene.uiManager.addWidget(FPSDisplay())
    
    # Run the game
    game.run()

if __name__ == "__main__":
    test_input_debug()
