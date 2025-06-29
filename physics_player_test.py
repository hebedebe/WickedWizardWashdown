"""
Test program for the physics-based player controller.
Creates a platformer-style test level with physics-based player movement.
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
from physics_player_controller import PhysicsPlayerController

class PlayerControllerTest(Scene):
    """Test scene for the physics player controller."""
    
    def __init__(self):
        super().__init__()
        self.physics_world = PhysicsWorld.get_instance()
        self.player = None
        self.player_controller = None
        
    def on_enter(self):
        """Set up the test level."""
        super().on_enter()
        
        # Set gravity
        self.physics_world.set_gravity((0, 800))  # Standard platformer gravity
        
        # Create player
        self.player = Actor("Player")
        self.player.transform.local_position = pygame.Vector2(100, 300)
        
        # Add visual component
        self.player.add_component(SpriteComponent(color=pygame.Color(0, 150, 255), 
                                                 size=pygame.Vector2(32, 48)))
        
        # Add physics component
        player_physics = RigidBodyComponent(mass=1.0, shape_type="box", size=(32, 48))
        player_physics.friction = 0.1
        player_physics.elasticity = 0.0
        self.player.add_component(player_physics)
        
        # Add player controller
        self.player_controller = PhysicsPlayerController(move_speed=300, jump_force=600)
        self.player.add_component(self.player_controller)
        
        self.add_actor(self.player)
        
        # Create ground platforms
        self._create_platforms()
        
        # Create some moving platforms
        self._create_moving_platforms()
        
        # Create walls
        self._create_walls()
        
        print("Physics Player Controller Test")
        print("- Arrow keys or WASD: Move")
        print("- Space: Jump")
        print("- R: Toggle rotation lock (try falling off platforms!)")
        print("- ESC: Quit")
        print("- Player starts with rotation locked (can't fall over)")
        
    def _create_platforms(self):
        """Create static platforms for the test level."""
        platforms = [
            # Ground level
            {"pos": (400, 550), "size": (800, 40), "color": (100, 100, 100)},
            # Lower platforms
            {"pos": (150, 450), "size": (150, 20), "color": (120, 120, 120)},
            {"pos": (400, 400), "size": (120, 20), "color": (120, 120, 120)},
            {"pos": (650, 450), "size": (150, 20), "color": (120, 120, 120)},
            # Mid-level platforms
            {"pos": (200, 320), "size": (100, 20), "color": (140, 140, 140)},
            {"pos": (500, 280), "size": (150, 20), "color": (140, 140, 140)},
            {"pos": (700, 320), "size": (80, 20), "color": (140, 140, 140)},
            # Higher platforms
            {"pos": (150, 200), "size": (100, 20), "color": (160, 160, 160)},
            {"pos": (400, 150), "size": (120, 20), "color": (160, 160, 160)},
            {"pos": (650, 180), "size": (100, 20), "color": (160, 160, 160)},
            # Top platforms
            {"pos": (300, 80), "size": (200, 20), "color": (180, 180, 180)},
        ]
        
        for i, platform_data in enumerate(platforms):
            platform = Actor(f"Platform{i}")
            platform.transform.local_position = pygame.Vector2(platform_data["pos"])
            
            platform.add_component(SpriteComponent(
                color=pygame.Color(platform_data["color"]),
                size=pygame.Vector2(platform_data["size"])
            ))
            
            platform.add_component(StaticBodyComponent(
                shape_type="box", 
                size=platform_data["size"]
            ))
            
            self.add_actor(platform)
            
    def _create_moving_platforms(self):
        """Create moving platforms for added challenge."""
        # Horizontal moving platform
        self.moving_platform_h = Actor("MovingPlatformH")
        self.moving_platform_h.transform.local_position = pygame.Vector2(250, 360)
        self.moving_platform_h.add_component(SpriteComponent(
            color=pygame.Color(100, 200, 100),
            size=pygame.Vector2(80, 15)
        ))
        
        platform_physics_h = StaticBodyComponent(shape_type="box", size=(80, 15))
        self.moving_platform_h.add_component(platform_physics_h)
        self.add_actor(self.moving_platform_h)
        
        # Vertical moving platform
        self.moving_platform_v = Actor("MovingPlatformV")
        self.moving_platform_v.transform.local_position = pygame.Vector2(550, 240)
        self.moving_platform_v.add_component(SpriteComponent(
            color=pygame.Color(200, 100, 100),
            size=pygame.Vector2(80, 15)
        ))
        
        platform_physics_v = StaticBodyComponent(shape_type="box", size=(80, 15))
        self.moving_platform_v.add_component(platform_physics_v)
        self.add_actor(self.moving_platform_v)
        
        # Movement tracking
        self.platform_h_time = 0.0
        self.platform_v_time = 0.0
        
    def _create_walls(self):
        """Create boundary walls."""
        # Left wall
        left_wall = Actor("LeftWall")
        left_wall.transform.local_position = pygame.Vector2(10, 300)
        left_wall.add_component(SpriteComponent(
            color=pygame.Color(80, 80, 80),
            size=pygame.Vector2(20, 600)
        ))
        left_wall.add_component(StaticBodyComponent(shape_type="box", size=(20, 600)))
        self.add_actor(left_wall)
        
        # Right wall
        right_wall = Actor("RightWall")
        right_wall.transform.local_position = pygame.Vector2(790, 300)
        right_wall.add_component(SpriteComponent(
            color=pygame.Color(80, 80, 80),
            size=pygame.Vector2(20, 600)
        ))
        right_wall.add_component(StaticBodyComponent(shape_type="box", size=(20, 600)))
        self.add_actor(right_wall)
        
    def handle_event(self, event):
        """Handle input events."""
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.quit()
                
    def update(self, dt):
        """Update the scene."""
        super().update(dt)
        
        # Handle player input
        if self.player_controller:
            self._handle_player_input()
            
        # Move platforms
        self._update_moving_platforms(dt)
        
    def _handle_player_input(self):
        """Handle continuous player input."""
        keys = pygame.key.get_pressed()
        
        # Horizontal movement
        horizontal = 0.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            horizontal = -1.0
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            horizontal = 1.0
            
        # Jump input
        jump_pressed = keys[pygame.K_w] or keys[pygame.K_SPACE] or keys[pygame.K_UP]
        jump_held = jump_pressed
        
        # Set input on controller
        self.player_controller.set_input(horizontal, jump_pressed, jump_held)
        
    def _update_moving_platforms(self, dt):
        """Update moving platform positions."""
        # Horizontal platform
        self.platform_h_time += dt
        base_x = 250
        offset_x = 100 * math.sin(self.platform_h_time * 2)
        new_pos_h = pygame.Vector2(base_x + offset_x, 360)
        
        # Move the platform
        platform_physics_h = self.moving_platform_h.get_component(StaticBodyComponent)
        if platform_physics_h and platform_physics_h.body:
            platform_physics_h.body.position = (new_pos_h.x, new_pos_h.y)
            
        # Vertical platform
        self.platform_v_time += dt
        base_y = 240
        offset_y = 60 * math.sin(self.platform_v_time * 1.5)
        new_pos_v = pygame.Vector2(550, base_y + offset_y)
        
        # Move the platform
        platform_physics_v = self.moving_platform_v.get_component(StaticBodyComponent)
        if platform_physics_v and platform_physics_v.body:
            platform_physics_v.body.position = (new_pos_v.x, new_pos_v.y)
            
    def render(self, screen):
        """Render the scene with debug info."""
        super().render(screen)
        
        # Render physics debug
        self.game.physics_system.render_debug(screen)
        
        # Render UI and debug info
        self._render_ui(screen)
        
    def _render_ui(self, screen):
        """Render UI and debug information."""
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 20)
        
        # Title and controls
        title_lines = [
            "Physics Player Controller Test",
            "A/D/Arrows: Move | W/Space/Up: Jump | ESC: Quit"
        ]
        
        for i, line in enumerate(title_lines):
            text_surface = font.render(line, True, pygame.Color(255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))
            
        # Debug info
        if self.player_controller:
            debug_info = self.player_controller.get_debug_info()
            debug_y = 70
            
            debug_lines = [
                f"Grounded: {debug_info['is_grounded']}",
                f"Jumping: {debug_info['is_jumping']}",
                f"Input: {debug_info['horizontal_input']:.2f}",
                f"Velocity: ({debug_info['velocity'][0]:.1f}, {debug_info['velocity'][1]:.1f})",
                f"Jump Buffer: {debug_info['jump_buffer_timer']:.2f}",
                f"Coyote Time: {debug_info['coyote_timer']:.2f}"
            ]
            
            for i, line in enumerate(debug_lines):
                color = pygame.Color(200, 200, 200)
                text_surface = small_font.render(line, True, color)
                screen.blit(text_surface, (10, debug_y + i * 20))


def main():
    """Run the physics player controller test."""
    # Create game instance
    game = Game(800, 600, "Physics Player Controller Test")
    
    # Create and add the test scene
    test_scene = PlayerControllerTest()
    game.add_scene("test", test_scene)
    game.load_scene("test")
    
    # Run the game
    game.run()


if __name__ == "__main__":
    main()
