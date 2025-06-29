"""
Physics-based player controller component.
Provides platformer-style movement using the physics engine.
"""

import pygame
from typing import Optional
from engine import Component, RigidBodyComponent
import math

class PhysicsPlayerController(Component):
    """
    Physics-based player controller for platformer-style movement.
    Uses physics engine for realistic movement with jumping, ground detection, etc.
    """
    
    def __init__(self, move_speed: float = 300.0, jump_force: float = 500.0):
        super().__init__()
        
        # Movement parameters
        self.move_speed = move_speed
        self.jump_force = jump_force
        self.air_control = 0.3  # How much control player has in air (0-1)
        self.max_speed = 400.0  # Maximum horizontal speed
        self.friction_ground = 0.8  # Ground friction multiplier
        self.friction_air = 0.95   # Air friction multiplier
        self.lock_rotation = True  # Prevent player from falling over
        
        # State tracking
        self.is_grounded = False
        self.is_jumping = False
        self.jump_buffer_time = 0.1  # Seconds to buffer jump input
        self.coyote_time = 0.1       # Seconds to allow jumping after leaving platform
        self.jump_buffer_timer = 0.0
        self.coyote_timer = 0.0
        self.was_grounded = False
        
        # Input state
        self.horizontal_input = 0.0  # -1 to 1
        self.jump_pressed = False
        self.jump_held = False
        
        # Ground detection
        self.ground_check_distance = 5.0
        self.ground_layers = [0]  # Collision types that count as ground
        
        # Physics component reference
        self.physics_component: Optional[RigidBodyComponent] = None
        
    def on_added(self, actor) -> None:
        """Called when component is added to an actor."""
        super().on_added(actor)
        
        # Get the physics component
        self.physics_component = self.actor.get_component(RigidBodyComponent)
        if not self.physics_component:
            raise ValueError("PhysicsPlayerController requires a RigidBodyComponent on the same actor")
            
        # Set up physics properties for character movement
        self.physics_component.friction = 0.1  # Low friction for responsive movement
        self.physics_component.elasticity = 0.0  # No bouncing
        
        # Lock rotation to prevent falling over
        if self.lock_rotation and self.physics_component.body:
            self.physics_component.body.moment = float('inf')  # Infinite moment of inertia
            
    def set_input(self, horizontal: float, jump_pressed: bool, jump_held: bool) -> None:
        """Set input state for the controller."""
        self.horizontal_input = max(-1.0, min(1.0, horizontal))
        
        # Handle jump buffering
        if jump_pressed and not self.jump_pressed:
            self.jump_buffer_timer = self.jump_buffer_time
            
        self.jump_pressed = jump_pressed
        self.jump_held = jump_held
        
    def update(self, dt: float) -> None:
        """Update player movement."""
        if not self.physics_component or not self.physics_component.body:
            return
            
        # Update timers
        self.jump_buffer_timer = max(0, self.jump_buffer_timer - dt)
        self.coyote_timer = max(0, self.coyote_timer - dt)
        
        # Check if grounded
        self._check_grounded()
        
        # Update coyote timer
        if self.was_grounded and not self.is_grounded:
            self.coyote_timer = self.coyote_time
        self.was_grounded = self.is_grounded
        
        # Handle horizontal movement
        self._handle_horizontal_movement(dt)
        
        # Handle jumping
        self._handle_jumping()
        
        # Apply friction
        self._apply_friction()
        
        # Lock rotation if enabled
        if self.lock_rotation:
            self._lock_rotation()
        
    def _lock_rotation(self) -> None:
        """Keep the player upright by locking rotation."""
        if not self.physics_component or not self.physics_component.body:
            return
            
        # Reset rotation to upright
        self.physics_component.body.angle = 0
        self.physics_component.body.angular_velocity = 0
        
    def _check_grounded(self) -> None:
        """Check if the player is on the ground using physics queries."""
        if not self.physics_component or not self.physics_component.body:
            return
            
        # Get current position
        body_pos = self.physics_component.body.position
        
        # Cast a ray downward to check for ground
        start_point = (body_pos[0], body_pos[1])
        end_point = (body_pos[0], body_pos[1] + self.ground_check_distance)
        
        # Query physics world for ground
        physics_world = self.physics_component.physics_world
        hit_info = physics_world.query_segment(start_point, end_point)
        
        # Check if we hit something that counts as ground
        self.is_grounded = False
        for hit in hit_info:
            if hit.shape.collision_type in self.ground_layers:
                # Check if we're actually touching (not just close)
                if hit.alpha < 1.0:  # Hit something along the ray
                    self.is_grounded = True
                    break
                    
        # Alternative: check velocity for more responsive ground detection
        if self.physics_component.body.velocity[1] >= -10:  # Not falling fast
            velocity_y = self.physics_component.body.velocity[1]
            if abs(velocity_y) < 50:  # Nearly stopped vertically
                self.is_grounded = True
                
    def _handle_horizontal_movement(self, dt: float) -> None:
        """Handle left/right movement."""
        if not self.physics_component or not self.physics_component.body:
            return
            
        current_velocity = self.physics_component.body.velocity
        
        # Calculate desired horizontal velocity
        target_velocity_x = self.horizontal_input * self.move_speed
        
        # Apply movement force based on whether we're grounded or in air
        control_factor = 1.0 if self.is_grounded else self.air_control
        
        # Calculate force needed to reach target velocity
        velocity_diff = target_velocity_x - current_velocity[0]
        force_needed = velocity_diff * self.physics_component.mass * control_factor * 10
        
        # Limit maximum force to prevent super-fast acceleration
        max_force = self.physics_component.mass * 2000 * control_factor
        force_needed = max(-max_force, min(max_force, force_needed))
        
        # Apply the force
        if abs(self.horizontal_input) > 0.1:  # Only apply force if actually trying to move
            self.physics_component.apply_force((force_needed, 0))
            
        # Clamp to maximum speed
        if abs(current_velocity[0]) > self.max_speed:
            clamped_velocity_x = math.copysign(self.max_speed, current_velocity[0])
            self.physics_component.set_velocity((clamped_velocity_x, current_velocity[1]))
            
    def _handle_jumping(self) -> None:
        """Handle jumping mechanics."""
        if not self.physics_component or not self.physics_component.body:
            return
            
        # Check if we can jump (grounded, coyote time, or jump buffering)
        can_jump = (self.is_grounded or self.coyote_timer > 0) and self.jump_buffer_timer > 0
        
        if can_jump and not self.is_jumping:
            # Perform jump
            current_velocity = self.physics_component.body.velocity
            
            # Set upward velocity for jump
            jump_velocity = -self.jump_force  # Negative Y is up in most coordinate systems
            self.physics_component.set_velocity((current_velocity[0], jump_velocity))
            
            # Reset timers
            self.jump_buffer_timer = 0.0
            self.coyote_timer = 0.0
            self.is_jumping = True
            
        # Variable jump height (cut jump short if button released)
        if self.is_jumping and not self.jump_held:
            current_velocity = self.physics_component.body.velocity
            if current_velocity[1] < 0:  # Moving upward
                # Reduce upward velocity for shorter jump
                reduced_velocity = current_velocity[1] * 0.5
                self.physics_component.set_velocity((current_velocity[0], reduced_velocity))
                
        # Reset jumping state when grounded
        if self.is_grounded and self.physics_component.body.velocity[1] >= 0:
            self.is_jumping = False
            
    def _apply_friction(self) -> None:
        """Apply friction to the physics body."""
        if not self.physics_component or not self.physics_component.body:
            return
            
        current_velocity = self.physics_component.body.velocity
        
        # Only apply horizontal friction when not actively moving
        if abs(self.horizontal_input) < 0.1:
            friction_factor = self.friction_ground if self.is_grounded else self.friction_air
            new_velocity_x = current_velocity[0] * friction_factor
            self.physics_component.set_velocity((new_velocity_x, current_velocity[1]))
            
    def get_debug_info(self) -> dict:
        """Get debug information about the controller state."""
        return {
            "is_grounded": self.is_grounded,
            "is_jumping": self.is_jumping,
            "horizontal_input": self.horizontal_input,
            "jump_buffer_timer": self.jump_buffer_timer,
            "coyote_timer": self.coyote_timer,
            "velocity": self.physics_component.body.velocity if self.physics_component and self.physics_component.body else (0, 0)
        }
        
    def set_rotation_lock(self, locked: bool) -> None:
        """Enable or disable rotation locking."""
        self.lock_rotation = locked
        
        if self.physics_component and self.physics_component.body:
            if locked:
                # Set infinite moment of inertia to prevent rotation
                self.physics_component.body.moment = float('inf')
                self.physics_component.body.angle = 0
                self.physics_component.body.angular_velocity = 0
            else:
                # Restore normal moment of inertia
                # Calculate appropriate moment for the shape
                if hasattr(self.physics_component, 'moment'):
                    self.physics_component.body.moment = self.physics_component.moment
                else:
                    # Default moment calculation for a box
                    import pymunk
                    mass = self.physics_component.mass
                    # Assume a 30x30 box for default moment calculation
                    self.physics_component.body.moment = pymunk.moment_for_box(mass, (30, 30))
                    
    def toggle_rotation_lock(self) -> None:
        """Toggle rotation locking on/off."""
        self.set_rotation_lock(not self.lock_rotation)
        
    def is_rotation_locked(self) -> bool:
        """Check if rotation is currently locked."""
        return self.lock_rotation
