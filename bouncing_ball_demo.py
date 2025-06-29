"""
Bouncing Ball Physics Demo
Showcases physics with walls, ceiling, floor, and mouse-controlled ball spawning.
"""

import pygame
import random
import math
from engine import Game
from engine.core.scene import Scene
from engine.core.actor import Actor
from engine.components import (
    create_box_rigidbody, 
    create_circle_rigidbody,
    PhysicsBodyType
)


class BouncingBallDemo(Scene):
    """
    Demo scene with bouncing balls and boundary walls.
    Click to spawn bouncing balls!
    """
    
    def __init__(self, width: int = 800, height: int = 600):
        super().__init__("Bouncing Ball Demo", enable_physics=True, gravity=(0, 500))
        self.width = width
        self.height = height
        self.ball_count = 0
        self.setup_scene()
        
    def setup_scene(self):
        """Setup the demo scene with walls and boundaries."""
        wall_thickness = 20
        
        # Create floor
        floor = self.create_actor("Floor", pygame.Vector2(self.width // 2, self.height - wall_thickness // 2))
        floor_physics = create_box_rigidbody(
            size=pygame.Vector2(self.width, wall_thickness),
            mass=0,
            body_type="static"
        )
        floor_physics.friction = 0.7
        floor_physics.elasticity = 0.8
        floor.add_component(floor_physics)
        
        # Create ceiling
        ceiling = self.create_actor("Ceiling", pygame.Vector2(self.width // 2, wall_thickness // 2))
        ceiling_physics = create_box_rigidbody(
            size=pygame.Vector2(self.width, wall_thickness),
            mass=0,
            body_type="static"
        )
        ceiling_physics.friction = 0.7
        ceiling_physics.elasticity = 0.8
        ceiling.add_component(ceiling_physics)
        
        # Create left wall
        left_wall = self.create_actor("LeftWall", pygame.Vector2(wall_thickness // 2, self.height // 2))
        left_wall_physics = create_box_rigidbody(
            size=pygame.Vector2(wall_thickness, self.height),
            mass=0,
            body_type="static"
        )
        left_wall_physics.friction = 0.7
        left_wall_physics.elasticity = 0.8
        left_wall.add_component(left_wall_physics)
        
        # Create right wall
        right_wall = self.create_actor("RightWall", pygame.Vector2(self.width - wall_thickness // 2, self.height // 2))
        right_wall_physics = create_box_rigidbody(
            size=pygame.Vector2(wall_thickness, self.height),
            mass=0,
            body_type="static"
        )
        right_wall_physics.friction = 0.7
        right_wall_physics.elasticity = 0.8
        right_wall.add_component(right_wall_physics)
        
        # Create some initial bouncing balls
        self.spawn_ball(pygame.Vector2(200, 100), initial_velocity=pygame.Vector2(200, -300))
        self.spawn_ball(pygame.Vector2(600, 150), initial_velocity=pygame.Vector2(-150, -250))
        self.spawn_ball(pygame.Vector2(400, 200), initial_velocity=pygame.Vector2(100, -400))
        
        # Debug: Print number of physics objects
        print(f"Physics objects in world: {len(self.physics_world.physics_objects)}")
        for obj in self.physics_world.physics_objects:
            if hasattr(obj, 'actor') and obj.actor:
                print(f"  - {obj.actor.name}: {obj.actor.transform.world_position}")
        
    def spawn_ball(self, position: pygame.Vector2, initial_velocity: pygame.Vector2 = None):
        """Spawn a new bouncing ball at the given position."""
        self.ball_count += 1
        
        print(f"Spawning ball {self.ball_count} at position {position}")
        
        # Create ball actor
        ball = self.create_actor(f"Ball_{self.ball_count}", position)
        
        # Debug: Check actor position after creation
        print(f"Actor created at: {ball.transform.local_position}, world: {ball.transform.world_position}")
        
        # Random ball properties
        radius = random.uniform(10, 25)
        mass = radius / 10.0  # Smaller balls are lighter
        
        # Create physics component
        ball_physics = create_circle_rigidbody(
            radius=radius,
            mass=mass,
            body_type="dynamic"
        )
        
        # Set physics properties for bouncy behavior
        ball_physics.friction = 0.3
        ball_physics.elasticity = random.uniform(0.7, 0.95)  # Random bounciness
        
        ball.add_component(ball_physics)
        
        # Debug: Check physics body position after component added
        if ball_physics.body:
            print(f"Physics body position: {ball_physics.body.position}")
        
        # Set initial velocity if provided
        if initial_velocity and ball_physics.body:
            ball_physics.set_velocity(initial_velocity)
        elif ball_physics.body:
            # Random initial velocity
            vel_x = random.uniform(-200, 200)
            vel_y = random.uniform(-300, -100)
            ball_physics.set_velocity(pygame.Vector2(vel_x, vel_y))
            
        # Store ball properties for rendering
        ball.ball_radius = radius
        ball.ball_color = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255)
        )
        
    def handle_event(self, event: pygame.event.Event):
        """Handle input events."""
        super().handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_pos = pygame.Vector2(event.pos)
                # Add some upward velocity for more interesting bouncing
                initial_vel = pygame.Vector2(
                    random.uniform(-100, 100),
                    random.uniform(-200, -50)
                )
                self.spawn_ball(mouse_pos, initial_vel)
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Spawn a ball at random position
                pos = pygame.Vector2(
                    random.uniform(50, self.width - 50),
                    random.uniform(50, self.height // 2)
                )
                self.spawn_ball(pos)
                
            elif event.key == pygame.K_c:
                # Clear all balls (keep walls)
                balls_to_remove = []
                for actor in self.actors:
                    if actor.name.startswith("Ball_"):
                        balls_to_remove.append(actor)
                        
                for ball in balls_to_remove:
                    self.destroy_actor(ball)
                    
                self.ball_count = 0
                
            elif event.key == pygame.K_d:
                # Toggle debug drawing
                self.toggle_physics_debug_draw()
                
            elif event.key == pygame.K_g:
                # Toggle gravity
                if self.physics_gravity[1] > 0:
                    self.set_physics_gravity((0, 0))  # Zero gravity
                else:
                    self.set_physics_gravity((0, 500))  # Normal gravity
                    
            elif event.key == pygame.K_r:
                # Reset scene
                self.clear()
                self.setup_scene()
                
    def update(self, dt: float):
        """Update the demo scene."""
        super().update(dt)
        
        # Remove balls that have fallen too far below the screen
        balls_to_remove = []
        for actor in self.actors:
            if actor.name.startswith("Ball_"):
                if actor.transform.world_position.y > self.height + 100:
                    balls_to_remove.append(actor)
                    
        for ball in balls_to_remove:
            self.destroy_actor(ball)
            
    def render(self, screen: pygame.Surface):
        """Render the demo scene."""
        # Set background gradient
        for y in range(self.height):
            color_intensity = int(30 + (y / self.height) * 50)
            pygame.draw.line(screen, (color_intensity, color_intensity, color_intensity + 20), 
                           (0, y), (self.width, y))
        
        # Draw walls
        wall_color = (100, 100, 100)
        wall_thickness = 20
        
        # Floor
        pygame.draw.rect(screen, wall_color, 
                        (0, self.height - wall_thickness, self.width, wall_thickness))
        
        # Ceiling
        pygame.draw.rect(screen, wall_color, 
                        (0, 0, self.width, wall_thickness))
        
        # Left wall
        pygame.draw.rect(screen, wall_color, 
                        (0, 0, wall_thickness, self.height))
        
        # Right wall
        pygame.draw.rect(screen, wall_color, 
                        (self.width - wall_thickness, 0, wall_thickness, self.height))
        
        # Draw balls
        for actor in self.actors:
            if actor.name.startswith("Ball_") and hasattr(actor, 'ball_radius'):
                pos = actor.transform.world_position
                
                # Draw ball with slight glow effect
                glow_radius = int(actor.ball_radius + 3)
                glow_color = tuple(max(0, c - 50) for c in actor.ball_color)
                pygame.draw.circle(screen, glow_color, 
                                 (int(pos.x), int(pos.y)), glow_radius)
                
                # Draw main ball
                pygame.draw.circle(screen, actor.ball_color, 
                                 (int(pos.x), int(pos.y)), int(actor.ball_radius))
                
                # Draw highlight
                highlight_pos = (int(pos.x - actor.ball_radius * 0.3), 
                               int(pos.y - actor.ball_radius * 0.3))
                highlight_radius = max(2, int(actor.ball_radius * 0.3))
                highlight_color = tuple(min(255, c + 100) for c in actor.ball_color)
                pygame.draw.circle(screen, highlight_color, highlight_pos, highlight_radius)
                
        # Draw instructions
        font = pygame.font.Font(None, 28)
        instructions = [
            "Bouncing Ball Physics Demo",
            "",
            "Click - Spawn ball at mouse",
            "SPACE - Spawn random ball",
            "C - Clear all balls",
            "D - Toggle debug draw",
            "G - Toggle gravity",
            "R - Reset scene",
            "",
            f"Balls: {len([a for a in self.actors if a.name.startswith('Ball_')])}"
        ]
        
        y_offset = 10
        for instruction in instructions:
            if instruction:  # Skip empty lines for spacing
                text = font.render(instruction, True, (255, 255, 255))
                # Add text shadow
                shadow = font.render(instruction, True, (0, 0, 0))
                screen.blit(shadow, (12, y_offset + 2))
                screen.blit(text, (10, y_offset))
            y_offset += 25
            
        # Draw performance info
        if self.physics_world:
            stats = self.physics_world.get_performance_stats()
            perf_text = f"Physics: {stats['object_count']} objects, {stats['last_step_time']:.3f}s"
            perf_surface = font.render(perf_text, True, (200, 200, 200))
            screen.blit(perf_surface, (10, self.height - 30))


def run_bouncing_ball_demo():
    """Run the bouncing ball demo."""
    # Create game instance
    game = Game(800, 600, "Bouncing Ball Physics Demo")
    
    # Create and add the demo scene
    demo_scene = BouncingBallDemo(800, 600)
    game.add_scene("demo", demo_scene)
    game.load_scene("demo")
    
    # Enable debug drawing by default (can be toggled with D key)
    demo_scene.set_physics_debug_draw(False)
    
    # Run the game
    game.run()


if __name__ == "__main__":
    run_bouncing_ball_demo()
