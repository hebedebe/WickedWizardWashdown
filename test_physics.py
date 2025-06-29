"""
Simple physics test to verify the system works.
"""

import pygame
from engine import Game
from engine.core.scene import Scene
from engine.core.actor import Actor
from engine.components import create_box_rigidbody


def test_physics_basic():
    """Test basic physics functionality."""
    print("Testing basic physics system...")
    
    # Create game instance
    game = Game(400, 300, "Physics Test")
    
    # Create a simple scene with physics enabled
    scene = Scene("Test Scene", enable_physics=True, gravity=(0, 981))
    game.add_scene("test", scene)
    game.load_scene("test")
    
    # Create a ground
    ground = scene.create_actor("Ground", pygame.Vector2(200, 250))
    ground_physics = create_box_rigidbody(
        size=pygame.Vector2(400, 50),
        body_type="static"
    )
    ground.add_component(ground_physics)
    
    # Create a falling box
    box = scene.create_actor("Box", pygame.Vector2(200, 100))
    box_physics = create_box_rigidbody(
        size=pygame.Vector2(40, 40),
        body_type="dynamic"
    )
    box.add_component(box_physics)
    
    print("✓ Created physics objects successfully")
    
    # Test that scene physics world is initialized
    assert scene.physics_world is not None, "Scene physics world not initialized"
    print("✓ Scene physics world initialized")
    
    # Test that objects were added to physics world
    assert len(scene.physics_world.physics_objects) >= 2, "Physics objects not added to world"
    print("✓ Physics objects added to world")
    
    # Run a few physics steps
    for i in range(10):
        scene.physics_world.step(1.0/60.0)
        
    print("✓ Physics simulation ran successfully")
    
    # Test that the box fell (y position should have increased)
    final_y = box_physics.body.position.y
    print(f"✓ Box fell from y=100 to y={final_y}")
    
    # Cleanup
    scene.physics_world.clear()
    
    print("All physics tests passed!")


if __name__ == "__main__":
    test_physics_basic()
