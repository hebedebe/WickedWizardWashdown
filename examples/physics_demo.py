"""
Physics demo showcasing the new Pymunk-based physics system.
Demonstrates rigid bodies, static bodies, constraints, and collision detection.
"""

import pygame
import sys
import os

# Add parent directory to path so we can import the engine
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import (
    Game, Scene, Actor, Transform, SpriteComponent,
    RigidBodyComponent, StaticBodyComponent, KinematicBodyComponent,
    PhysicsConstraintComponent, PhysicsWorld
)

class PhysicsDemo(Scene):
    """Demo scene showing physics features."""
    
    def __init__(self):
        super().__init__()
        self.physics_world = PhysicsWorld.get_instance()
        
    def on_enter(self):
        """Set up the physics demo."""
        super().on_enter()
        
        # Set gravity
        self.physics_world.set_gravity((0, 500))  # Downward gravity
        
        # Create ground platform
        ground = Actor(Transform(pygame.Vector2(400, 550)))
        ground.add_component(SpriteComponent(color=pygame.Color(100, 100, 100), 
                                           size=pygame.Vector2(600, 40)))
        ground.add_component(StaticBodyComponent(shape_type="box", size=(600, 40)))
        self.add_actor(ground)
        
        # Create walls
        left_wall = Actor(Transform(pygame.Vector2(50, 300)))
        left_wall.add_component(SpriteComponent(color=pygame.Color(80, 80, 80), 
                                               size=pygame.Vector2(20, 400)))
        left_wall.add_component(StaticBodyComponent(shape_type="box", size=(20, 400)))
        self.add_actor(left_wall)
        
        right_wall = Actor(Transform(pygame.Vector2(750, 300)))
        right_wall.add_component(SpriteComponent(color=pygame.Color(80, 80, 80), 
                                                size=pygame.Vector2(20, 400)))
        right_wall.add_component(StaticBodyComponent(shape_type="box", size=(20, 400)))
        self.add_actor(right_wall)
        
        # Create dynamic boxes
        for i in range(5):
            for j in range(3):
                box = Actor(Transform(pygame.Vector2(300 + i * 35, 100 + j * 35)))
                box.add_component(SpriteComponent(color=pygame.Color(255, 100, 100), 
                                                size=pygame.Vector2(30, 30)))
                rigid_body = RigidBodyComponent(mass=1.0, shape_type="box", size=(30, 30))
                rigid_body.friction = 0.7
                rigid_body.elasticity = 0.3
                box.add_component(rigid_body)
                self.add_actor(box)
        
        # Create some circles
        for i in range(3):
            circle = Actor(Transform(pygame.Vector2(200 + i * 40, 150)))
            circle.add_component(SpriteComponent(color=pygame.Color(100, 255, 100), 
                                               size=pygame.Vector2(25, 25)))
            rigid_body = RigidBodyComponent(mass=1.0, shape_type="circle", size=(25, 25))
            rigid_body.friction = 0.5
            rigid_body.elasticity = 0.8  # Bouncy balls
            circle.add_component(rigid_body)
            self.add_actor(circle)
        
        # Create a kinematic platform that moves
        self.moving_platform = Actor(Transform(pygame.Vector2(400, 350)))
        self.moving_platform.add_component(SpriteComponent(color=pygame.Color(100, 100, 255), 
                                                          size=pygame.Vector2(100, 20)))
        kinematic_body = KinematicBodyComponent(shape_type="box", size=(100, 20))
        kinematic_body.friction = 1.0
        self.moving_platform.add_component(kinematic_body)
        self.add_actor(self.moving_platform)
        
        # Set up platform movement
        self.platform_direction = 1
        self.platform_speed = 100
        
        # Create pendulum with constraint
        # Anchor point (static)
        anchor = Actor(Transform(pygame.Vector2(600, 100)))
        anchor.add_component(SpriteComponent(color=pygame.Color(255, 255, 255), 
                                           size=pygame.Vector2(10, 10)))
        anchor.add_component(StaticBodyComponent(shape_type="circle", size=(5, 5)))
        self.add_actor(anchor)
        
        # Pendulum bob
        bob = Actor(Transform(pygame.Vector2(600, 200)))
        bob.add_component(SpriteComponent(color=pygame.Color(255, 255, 0), 
                                        size=pygame.Vector2(20, 20)))
        bob_rigid_body = RigidBodyComponent(mass=2.0, shape_type="circle", size=(20, 20))
        bob_rigid_body.friction = 0.1
        bob.add_component(bob_rigid_body)
        self.add_actor(bob)
        
        # Connect with pin joint constraint
        constraint = PhysicsConstraintComponent(constraint_type="pin_joint")
        constraint.anchor_a = (0, 0)  # Center of anchor
        constraint.anchor_b = (0, 0)  # Center of bob
        constraint.set_other_actor(anchor)
        bob.add_component(constraint)
        
        print("Physics Demo Controls:")
        print("- Left click to spawn a bouncy ball")
        print("- Right click to spawn a heavy box")
        print("- ESC to quit")
        
    def handle_event(self, event):
        """Handle input events."""
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.quit()
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if event.button == 1:  # Left click - spawn bouncy ball
                ball = Actor(Transform(pygame.Vector2(mouse_pos[0], mouse_pos[1])))
                ball.add_component(SpriteComponent(color=pygame.Color(255, 200, 0), 
                                                 size=pygame.Vector2(20, 20)))
                rigid_body = RigidBodyComponent(mass=0.5, shape_type="circle", size=(20, 20))
                rigid_body.friction = 0.3
                rigid_body.elasticity = 0.9  # Very bouncy
                ball.add_component(rigid_body)
                self.add_actor(ball)
                
            elif event.button == 3:  # Right click - spawn heavy box
                box = Actor(Transform(pygame.Vector2(mouse_pos[0], mouse_pos[1])))
                box.add_component(SpriteComponent(color=pygame.Color(150, 75, 0), 
                                                size=pygame.Vector2(40, 40)))
                rigid_body = RigidBodyComponent(mass=5.0, shape_type="box", size=(40, 40))
                rigid_body.friction = 0.8
                rigid_body.elasticity = 0.1
                box.add_component(rigid_body)
                self.add_actor(box)
    
    def update(self, dt):
        """Update the scene."""
        super().update(dt)
        
        # Move the kinematic platform back and forth
        kinematic_comp = self.moving_platform.get_component(KinematicBodyComponent)
        if kinematic_comp:
            current_pos = self.moving_platform.transform.local_position
            
            # Change direction at boundaries
            if current_pos.x <= 150:
                self.platform_direction = 1
            elif current_pos.x >= 650:
                self.platform_direction = -1
                
            # Set velocity for smooth movement
            velocity = (self.platform_speed * self.platform_direction, 0)
            kinematic_comp.set_velocity(velocity)
    
    def render(self, screen):
        """Render the scene with debug physics visualization."""
        super().render(screen)
        
        # Render physics debug info
        self.game.physics_system.render_debug(screen)
        
        # Add some UI text
        font = pygame.font.Font(None, 24)
        
        text_lines = [
            "Physics Demo - Pymunk Integration",
            "Left click: Spawn bouncy ball",
            "Right click: Spawn heavy box",
            "ESC: Quit"
        ]
        
        for i, line in enumerate(text_lines):
            text_surface = font.render(line, True, pygame.Color(255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))


def main():
    """Run the physics demo."""
    # Create game instance
    game = Game(800, 600, "Physics Demo - Pymunk Integration")
    
    # Create and add the demo scene
    demo_scene = PhysicsDemo()
    game.add_scene("demo", demo_scene)
    game.load_scene("demo")
    
    # Run the game
    game.run()


if __name__ == "__main__":
    main()
