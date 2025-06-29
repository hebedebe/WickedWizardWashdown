"""
Test script to verify physics component transform fixes.
This test creates a physics object with a parent to verify the transform hierarchy works correctly.
"""

import pygame
import sys
import os
import math

# Add parent directory to path so we can import the engine
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import (
    Game, Scene, Actor, Transform, SpriteComponent,
    RigidBodyComponent, StaticBodyComponent, PhysicsWorld
)

class PhysicsTransformTest(Scene):
    """Test scene for physics transform fixes."""
    
    def __init__(self):
        super().__init__()
        self.physics_world = PhysicsWorld.get_instance()
        
    def on_enter(self):
        """Set up the test."""
        super().on_enter()
        
        # Set gravity
        self.physics_world.set_gravity((0, 400))
        
        # Create a parent actor that will move
        self.parent_container = Actor("ParentContainer")
        self.parent_container.transform.local_position = pygame.Vector2(100, 100)
        self.parent_container.add_component(SpriteComponent(color=pygame.Color(100, 100, 255), 
                                                           size=pygame.Vector2(200, 200)))
        self.add_actor(self.parent_container)
        
        # Create a child actor with physics
        child_with_physics = Actor("ChildWithPhysics")
        child_with_physics.transform.local_position = pygame.Vector2(50, 50)  # Relative to parent
        child_with_physics.add_component(SpriteComponent(color=pygame.Color(255, 100, 100), 
                                                        size=pygame.Vector2(30, 30)))
        
        # Add physics to the child
        rigid_body = RigidBodyComponent(mass=1.0, shape_type="box", size=(30, 30))
        rigid_body.friction = 0.7
        rigid_body.elasticity = 0.5
        child_with_physics.add_component(rigid_body)
        
        # Make it a child of the parent
        self.parent_container.add_child(child_with_physics)
        
        # Create ground
        ground = Actor("Ground")
        ground.transform.local_position = pygame.Vector2(400, 550)
        ground.add_component(SpriteComponent(color=pygame.Color(100, 100, 100), 
                                           size=pygame.Vector2(800, 40)))
        ground.add_component(StaticBodyComponent(shape_type="box", size=(800, 40)))
        self.add_actor(ground)
        
        # Create some independent physics objects for comparison
        for i in range(3):
            box = Actor(f"IndependentBox{i}")
            box.transform.local_position = pygame.Vector2(300 + i * 40, 100)
            box.add_component(SpriteComponent(color=pygame.Color(100, 255, 100), 
                                            size=pygame.Vector2(25, 25)))
            rigid_body = RigidBodyComponent(mass=1.0, shape_type="box", size=(25, 25))
            rigid_body.friction = 0.7
            rigid_body.elasticity = 0.3
            box.add_component(rigid_body)
            self.add_actor(box)
        
        # Variables for parent movement
        self.parent_move_time = 0.0
        self.initial_parent_pos = pygame.Vector2(self.parent_container.transform.local_position)
        
        print("Physics Transform Test")
        print("- Blue box: Parent container (will move in a circle)")
        print("- Red box: Child with physics (should maintain physics while following parent)")
        print("- Green boxes: Independent physics objects for comparison")
        print("- Press SPACE to teleport the child physics object")
        print("- ESC to quit")
        
    def handle_event(self, event):
        """Handle input events."""
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.quit()
            elif event.key == pygame.K_SPACE:
                # Test teleporting the child physics object
                child = self.parent_container.find_child("ChildWithPhysics")
                if child:
                    physics_comp = child.get_component(RigidBodyComponent)
                    if physics_comp:
                        # Teleport to a new local position within the parent
                        new_local_pos = pygame.Vector2(100, 20)
                        # Calculate world position for physics
                        self.parent_container.update_transform()
                        world_pos = self.parent_container.transform.world_position + new_local_pos
                        physics_comp.teleport_to((world_pos.x, world_pos.y))
                        print(f"Teleported child to local pos {new_local_pos}, world pos {world_pos}")
    
    def update(self, dt):
        """Update the scene."""
        super().update(dt)
        
        # Move the parent in a circle to test transform hierarchy
        self.parent_move_time += dt
        radius = 50
        center_x = self.initial_parent_pos.x + 200
        center_y = self.initial_parent_pos.y + 100
        
        new_x = center_x + radius * math.cos(self.parent_move_time)
        new_y = center_y + radius * math.sin(self.parent_move_time * 0.5)
        
        self.parent_container.transform.local_position = pygame.Vector2(new_x, new_y)
        self.parent_container.transform.mark_dirty()
    
    def render(self, screen):
        """Render the scene with debug physics visualization."""
        super().render(screen)
        
        # Render physics debug info
        self.game.physics_system.render_debug(screen)
        
        # Add some UI text
        font = pygame.font.Font(None, 24)
        
        text_lines = [
            "Physics Transform Test",
            "Blue: Parent (moving in circle)",
            "Red: Child with physics", 
            "Green: Independent physics",
            "SPACE: Teleport child",
            "ESC: Quit"
        ]
        
        for i, line in enumerate(text_lines):
            text_surface = font.render(line, True, pygame.Color(255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))


def main():
    """Run the physics transform test."""
    # Create game instance
    game = Game(800, 600, "Physics Transform Test")
    
    # Create and add the test scene
    test_scene = PhysicsTransformTest()
    game.add_scene("test", test_scene)
    game.load_scene("test")
    
    # Run the game
    game.run()


if __name__ == "__main__":
    main()
