"""
Physics demo showing how to use the physics system.
"""

import pygame
from engine import Game
from engine.core.scene import Scene
from engine.core.actor import Actor
from engine.components import (
    SpriteComponent, 
    create_box_rigidbody, 
    create_circle_rigidbody, 
    create_box_trigger,
    PhysicsBodyType
)


class PhysicsDemo(Scene):
    """
    Demo scene showing physics components in action.
    """
    
    def __init__(self):
        super().__init__("Physics Demo", enable_physics=True, gravity=(0, 981))
        self.setup_scene()
        
    def setup_scene(self):
        """Setup the physics demo scene."""
        # Create ground
        ground = self.create_actor("Ground", pygame.Vector2(400, 550))
        ground_physics = create_box_rigidbody(
            size=pygame.Vector2(800, 50),
            mass=0,  # Static body
            body_type="static"
        )
        ground_physics.friction = 0.8
        ground.add_component(ground_physics)
        
        # Create some falling boxes
        for i in range(5):
            box = self.create_actor(f"Box_{i}", pygame.Vector2(200 + i * 100, 100 + i * 50))
            box_physics = create_box_rigidbody(
                size=pygame.Vector2(40, 40),
                mass=1.0,
                body_type="dynamic"
            )
            box_physics.friction = 0.5
            box_physics.elasticity = 0.3
            box.add_component(box_physics)
            
        # Create some falling circles
        for i in range(3):
            circle = self.create_actor(f"Circle_{i}", pygame.Vector2(100 + i * 150, 50))
            circle_physics = create_circle_rigidbody(
                radius=20,
                mass=0.8,
                body_type="dynamic"
            )
            circle_physics.friction = 0.4
            circle_physics.elasticity = 0.6
            circle.add_component(circle_physics)
            
        # Create a kinematic platform
        platform = self.create_actor("Platform", pygame.Vector2(600, 300))
        platform_physics = create_box_rigidbody(
            size=pygame.Vector2(150, 20),
            mass=0,
            body_type="kinematic"
        )
        platform.add_component(platform_physics)
        
        # Make platform move up and down
        self.platform_time = 0.0
        self.platform_actor = platform
        
        # Create a trigger zone
        trigger = self.create_actor("Trigger", pygame.Vector2(300, 400))
        trigger_component = create_box_trigger(pygame.Vector2(100, 100))
        trigger_component.on_trigger_enter = self.on_trigger_enter
        trigger_component.on_trigger_exit = self.on_trigger_exit
        trigger.add_component(trigger_component)
        
        # Create walls
        self.create_wall("LeftWall", pygame.Vector2(25, 300), pygame.Vector2(50, 600))
        self.create_wall("RightWall", pygame.Vector2(775, 300), pygame.Vector2(50, 600))
        
    def create_wall(self, name: str, position: pygame.Vector2, size: pygame.Vector2):
        """Create a static wall."""
        wall = self.create_actor(name, position)
        wall_physics = create_box_rigidbody(
            size=size,
            mass=0,
            body_type="static"
        )
        wall_physics.friction = 0.7
        wall.add_component(wall_physics)
        
    def on_trigger_enter(self, trigger, other):
        """Handle trigger enter event."""
        print(f"Object {other.actor.name} entered trigger!")
        
    def on_trigger_exit(self, trigger, other):
        """Handle trigger exit event."""
        print(f"Object {other.actor.name} exited trigger!")
        
    def update(self, dt: float):
        """Update the demo scene."""
        super().update(dt)
        
        # Move the kinematic platform
        self.platform_time += dt
        
        # Find physics component by checking for body attribute
        platform_physics = None
        for comp in self.platform_actor.component_list:
            if hasattr(comp, 'body') and comp.body:
                platform_physics = comp
                break
                
        if platform_physics:
            import math
            new_y = 300 + math.sin(self.platform_time) * 100
            platform_physics.body.position = (600, new_y)
            
    def handle_event(self, event: pygame.event.Event):
        """Handle input events."""
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Spawn a new box at random position
                import random
                box = self.create_actor(f"Box_{len(self.actors)}", 
                                      pygame.Vector2(random.randint(100, 700), 50))
                box_physics = create_box_rigidbody(
                    size=pygame.Vector2(30, 30),
                    mass=1.0,
                    body_type="dynamic"
                )
                box_physics.friction = 0.5
                box_physics.elasticity = 0.4
                box.add_component(box_physics)
                
            elif event.key == pygame.K_r:
                # Reset scene
                self.clear()
                self.setup_scene()
                
            elif event.key == pygame.K_d:
                # Toggle debug drawing
                self.toggle_physics_debug_draw()
                
    def render(self, screen: pygame.Surface):
        """Render the demo scene."""
        # Set background
        screen.fill((50, 50, 100))
        
        # Draw simple representations of physics objects
        for actor in self.actors:
            physics_comp = None
            for comp in actor.component_list:
                if hasattr(comp, 'shape') and comp.shape:
                    physics_comp = comp
                    break
                    
            if physics_comp and physics_comp.shape:
                import pymunk
                pos = physics_comp.body.position
                
                if isinstance(physics_comp.shape, pymunk.Circle):
                    # Draw circle
                    pygame.draw.circle(screen, (255, 255, 255), 
                                     (int(pos.x), int(pos.y)), 
                                     int(physics_comp.shape.radius), 2)
                elif isinstance(physics_comp.shape, pymunk.Poly):
                    # Draw polygon
                    vertices = []
                    for vertex in physics_comp.shape.get_vertices():
                        x = vertex.rotated(physics_comp.body.angle).x + pos.x
                        y = vertex.rotated(physics_comp.body.angle).y + pos.y
                        vertices.append((int(x), int(y)))
                    if len(vertices) > 2:
                        pygame.draw.polygon(screen, (255, 255, 255), vertices, 2)
                        
        # Draw trigger zone outline
        trigger_actor = self.find_actor("Trigger")
        if trigger_actor:
            pos = trigger_actor.transform.world_position
            trigger_rect = pygame.Rect(pos.x - 50, pos.y - 50, 100, 100)
            pygame.draw.rect(screen, (255, 255, 0), trigger_rect, 2)
            
        # Draw instructions
        font = pygame.font.Font(None, 36)
        instructions = [
            "Physics Demo",
            "SPACE - Spawn box",
            "R - Reset scene", 
            "D - Toggle debug draw"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font.render(instruction, True, (255, 255, 255))
            screen.blit(text, (10, 10 + i * 30))


def run_physics_demo():
    """Run the physics demo."""
    # Create game instance
    game = Game(800, 600, "Physics Demo")
    
    # Create and add the demo scene
    demo_scene = PhysicsDemo()
    game.add_scene("demo", demo_scene)
    game.load_scene("demo")
    
    # Enable debug drawing by default
    demo_scene.set_physics_debug_draw(True)
    
    # Run the game
    game.run()


if __name__ == "__main__":
    run_physics_demo()
