"""
Particle system for creating visual effects.
"""

import pygame
import math
import random
from typing import List, Optional, Callable, Dict, Any
from .actor import Component

class Particle:
    """
    Individual particle with physics and rendering properties.
    """
    
    def __init__(self, position: pygame.Vector2):
        # Transform
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)
        
        # Visual properties
        self.color = pygame.Color(255, 255, 255, 255)
        self.size = 2.0
        self.rotation = 0.0
        self.scale = pygame.Vector2(1, 1)
        
        # Life properties
        self.lifetime = 1.0
        self.age = 0.0
        self.alive = True
        
        # Animation properties
        self.start_color = pygame.Color(255, 255, 255, 255)
        self.end_color = pygame.Color(255, 255, 255, 0)
        self.start_size = 2.0
        self.end_size = 0.0
        self.start_rotation = 0.0
        self.angular_velocity = 0.0
        
        # Physics
        self.drag = 0.0
        self.bounce = 0.0
        self.gravity = pygame.Vector2(0, 0)
        
        # Custom data
        self.user_data: Dict[str, Any] = {}
        
    def update(self, dt: float) -> None:
        """Update particle physics and properties."""
        if not self.alive:
            return
            
        # Update age
        self.age += dt
        if self.age >= self.lifetime:
            self.alive = False
            return
            
        # Physics
        self.acceleration += self.gravity
        
        # Apply drag
        if self.drag > 0:
            drag_force = self.velocity * -self.drag
            self.acceleration += drag_force
            
        # Update velocity and position
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt
        
        # Update rotation
        self.rotation += self.angular_velocity * dt
        
        # Interpolate properties based on age
        t = self.age / self.lifetime if self.lifetime > 0 else 1.0
        t = max(0, min(1, t))  # Clamp to 0-1
        
        # Color interpolation
        self.color.r = int(self.start_color.r + (self.end_color.r - self.start_color.r) * t)
        self.color.g = int(self.start_color.g + (self.end_color.g - self.start_color.g) * t)
        self.color.b = int(self.start_color.b + (self.end_color.b - self.start_color.b) * t)
        self.color.a = int(self.start_color.a + (self.end_color.a - self.start_color.a) * t)
        
        # Size interpolation
        self.size = self.start_size + (self.end_size - self.start_size) * t
        
        # Reset acceleration for next frame
        self.acceleration = pygame.Vector2(0, 0)
        
    def render(self, screen: pygame.Surface) -> None:
        """Render the particle."""
        if not self.alive or self.size <= 0:
            return
            
        # Create particle surface
        size = max(1, int(self.size * 2))
        particle_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw particle (simple circle for now)
        center = (size // 2, size // 2)
        radius = max(1, int(self.size))
        pygame.draw.circle(particle_surface, self.color, center, radius)
        
        # Apply rotation if needed
        if self.rotation != 0:
            particle_surface = pygame.transform.rotate(particle_surface, math.degrees(self.rotation))
            
        # Draw to screen
        rect = particle_surface.get_rect()
        rect.center = (int(self.position.x), int(self.position.y))
        screen.blit(particle_surface, rect)

class ParticleEmitter:
    """
    Emits and manages particles with configurable properties.
    """
    
    def __init__(self, position: pygame.Vector2 = None):
        self.position = position or pygame.Vector2(0, 0)
        self.particles: List[Particle] = []
        
        # Emission properties
        self.emission_rate = 10.0  # particles per second
        self.burst_count = 0  # particles to emit immediately
        self.max_particles = 100
        self.auto_emit = True
        
        # Particle properties (ranges)
        self.lifetime_range = (1.0, 2.0)
        self.speed_range = (50.0, 100.0)
        self.direction_range = (0.0, 360.0)  # degrees
        self.size_range = (1.0, 5.0)
        self.angular_velocity_range = (0.0, 0.0)
        
        # Color properties
        self.start_color_range = (pygame.Color(255, 255, 255, 255), pygame.Color(255, 255, 255, 255))
        self.end_color_range = (pygame.Color(255, 255, 255, 0), pygame.Color(255, 255, 255, 0))
        
        # Physics properties
        self.gravity = pygame.Vector2(0, 0)
        self.drag_range = (0.0, 0.0)
        
        # Shape properties
        self.emission_shape = 'point'  # 'point', 'circle', 'rectangle', 'line'
        self.shape_data = {}  # Additional shape-specific data
        
        # Timing
        self.emission_timer = 0.0
        self.active = True
        
        # Custom behaviors
        self.custom_behaviors: List[Callable[[Particle, float], None]] = []
        
    def add_behavior(self, behavior: Callable[[Particle, float], None]) -> None:
        """Add a custom particle behavior function."""
        self.custom_behaviors.append(behavior)
        
    def remove_behavior(self, behavior: Callable[[Particle, float], None]) -> None:
        """Remove a custom particle behavior function."""
        if behavior in self.custom_behaviors:
            self.custom_behaviors.remove(behavior)
            
    def emit_particle(self) -> Particle:
        """Create and emit a single particle."""
        # Determine spawn position based on emission shape
        spawn_pos = self._get_spawn_position()
        
        particle = Particle(spawn_pos)
        
        # Set random properties within ranges
        particle.lifetime = random.uniform(*self.lifetime_range)
        
        # Set velocity based on speed and direction
        speed = random.uniform(*self.speed_range)
        direction = math.radians(random.uniform(*self.direction_range))
        particle.velocity = pygame.Vector2(
            math.cos(direction) * speed,
            math.sin(direction) * speed
        )
        
        # Set size
        particle.start_size = random.uniform(*self.size_range)
        particle.end_size = particle.start_size * 0.1  # Default shrink
        particle.size = particle.start_size
        
        # Set angular velocity
        particle.angular_velocity = random.uniform(*self.angular_velocity_range)
        
        # Set colors
        particle.start_color = self._interpolate_color(*self.start_color_range, random.random())
        particle.end_color = self._interpolate_color(*self.end_color_range, random.random())
        particle.color = pygame.Color(particle.start_color)
        
        # Set physics
        particle.gravity = pygame.Vector2(self.gravity)
        particle.drag = random.uniform(*self.drag_range)
        
        return particle
        
    def _get_spawn_position(self) -> pygame.Vector2:
        """Get spawn position based on emission shape."""
        if self.emission_shape == 'point':
            return pygame.Vector2(self.position)
        elif self.emission_shape == 'circle':
            radius = self.shape_data.get('radius', 10.0)
            angle = random.uniform(0, 2 * math.pi)
            offset = pygame.Vector2(
                math.cos(angle) * random.uniform(0, radius),
                math.sin(angle) * random.uniform(0, radius)
            )
            return self.position + offset
        elif self.emission_shape == 'rectangle':
            width = self.shape_data.get('width', 20.0)
            height = self.shape_data.get('height', 20.0)
            offset = pygame.Vector2(
                random.uniform(-width/2, width/2),
                random.uniform(-height/2, height/2)
            )
            return self.position + offset
        elif self.emission_shape == 'line':
            length = self.shape_data.get('length', 20.0)
            angle = self.shape_data.get('angle', 0.0)
            t = random.uniform(-0.5, 0.5)
            offset = pygame.Vector2(
                math.cos(math.radians(angle)) * length * t,
                math.sin(math.radians(angle)) * length * t
            )
            return self.position + offset
        else:
            return pygame.Vector2(self.position)
            
    def _interpolate_color(self, color1: pygame.Color, color2: pygame.Color, t: float) -> pygame.Color:
        """Interpolate between two colors."""
        return pygame.Color(
            int(color1.r + (color2.r - color1.r) * t),
            int(color1.g + (color2.g - color1.g) * t),
            int(color1.b + (color2.b - color1.b) * t),
            int(color1.a + (color2.a - color1.a) * t)
        )
        
    def emit_burst(self, count: int) -> None:
        """Emit a burst of particles immediately."""
        for _ in range(count):
            if len(self.particles) < self.max_particles:
                self.particles.append(self.emit_particle())
                
    def update(self, dt: float) -> None:
        """Update emitter and all particles."""
        if not self.active:
            return
            
        # Handle burst emission
        if self.burst_count > 0:
            self.emit_burst(self.burst_count)
            self.burst_count = 0
            
        # Handle continuous emission
        if self.auto_emit and self.emission_rate > 0:
            self.emission_timer += dt
            particles_to_emit = int(self.emission_timer * self.emission_rate)
            
            if particles_to_emit > 0:
                self.emission_timer -= particles_to_emit / self.emission_rate
                for _ in range(particles_to_emit):
                    if len(self.particles) < self.max_particles:
                        self.particles.append(self.emit_particle())
                        
        # Update particles
        for particle in list(self.particles):
            particle.update(dt)
            
            # Apply custom behaviors
            for behavior in self.custom_behaviors:
                behavior(particle, dt)
                
            # Remove dead particles
            if not particle.alive:
                self.particles.remove(particle)
                
    def render(self, screen: pygame.Surface) -> None:
        """Render all particles."""
        for particle in self.particles:
            particle.render(screen)
            
    def clear(self) -> None:
        """Remove all particles."""
        self.particles.clear()
        
    def get_particle_count(self) -> int:
        """Get the current number of active particles."""
        return len(self.particles)

class ParticleSystem(Component):
    """
    Component that manages multiple particle emitters.
    """
    
    def __init__(self):
        super().__init__()
        self.emitters: List[ParticleEmitter] = []
        self.active = True
        
    def add_emitter(self, emitter: ParticleEmitter) -> None:
        """Add a particle emitter."""
        self.emitters.append(emitter)
        
    def remove_emitter(self, emitter: ParticleEmitter) -> None:
        """Remove a particle emitter."""
        if emitter in self.emitters:
            self.emitters.remove(emitter)
            
    def create_emitter(self, position: pygame.Vector2 = None) -> ParticleEmitter:
        """Create and add a new emitter."""
        if not position and self.actor:
            position = pygame.Vector2(self.actor.transform.world_position)
        emitter = ParticleEmitter(position)
        self.add_emitter(emitter)
        return emitter
        
    def update(self, dt: float) -> None:
        """Update all emitters."""
        if not self.active:
            return
            
        # Update emitter positions to follow actor
        if self.actor:
            for emitter in self.emitters:
                emitter.position = pygame.Vector2(self.actor.transform.world_position)
                
        # Update all emitters
        for emitter in self.emitters:
            emitter.update(dt)
            
    def render(self, screen: pygame.Surface) -> None:
        """Render all emitters."""
        if not self.active:
            return
            
        for emitter in self.emitters:
            emitter.render(screen)
            
    def clear_all(self) -> None:
        """Clear all particles from all emitters."""
        for emitter in self.emitters:
            emitter.clear()
            
    def get_total_particle_count(self) -> int:
        """Get total particle count across all emitters."""
        return sum(emitter.get_particle_count() for emitter in self.emitters)

# Predefined particle effect functions
def create_explosion_emitter(position: pygame.Vector2, color: pygame.Color = None) -> ParticleEmitter:
    """Create an explosion particle effect."""
    emitter = ParticleEmitter(position)
    emitter.emission_rate = 0  # Burst only
    emitter.burst_count = 50
    emitter.auto_emit = False
    emitter.max_particles = 50
    
    emitter.lifetime_range = (0.5, 1.5)
    emitter.speed_range = (100, 300)
    emitter.direction_range = (0, 360)
    emitter.size_range = (2, 8)
    
    if color:
        emitter.start_color_range = (color, color)
        end_color = pygame.Color(color)
        end_color.a = 0
        emitter.end_color_range = (end_color, end_color)
    else:
        emitter.start_color_range = (pygame.Color(255, 100, 0), pygame.Color(255, 255, 0))
        emitter.end_color_range = (pygame.Color(255, 0, 0, 0), pygame.Color(100, 0, 0, 0))
        
    emitter.drag_range = (1.0, 2.0)
    emitter.gravity = pygame.Vector2(0, 200)
    
    return emitter

def create_fire_emitter(position: pygame.Vector2) -> ParticleEmitter:
    """Create a fire particle effect."""
    emitter = ParticleEmitter(position)
    emitter.emission_rate = 30
    emitter.max_particles = 100
    
    emitter.lifetime_range = (1.0, 2.0)
    emitter.speed_range = (20, 60)
    emitter.direction_range = (260, 280)  # Mostly upward
    emitter.size_range = (2, 6)
    
    emitter.start_color_range = (pygame.Color(255, 100, 0), pygame.Color(255, 255, 0))
    emitter.end_color_range = (pygame.Color(255, 0, 0, 0), pygame.Color(100, 0, 0, 0))
    
    emitter.emission_shape = 'circle'
    emitter.shape_data = {'radius': 5}
    emitter.gravity = pygame.Vector2(0, -50)  # Upward force
    emitter.drag_range = (0.5, 1.0)
    
    return emitter

def create_smoke_emitter(position: pygame.Vector2) -> ParticleEmitter:
    """Create a smoke particle effect."""
    emitter = ParticleEmitter(position)
    emitter.emission_rate = 15
    emitter.max_particles = 50
    
    emitter.lifetime_range = (2.0, 4.0)
    emitter.speed_range = (10, 30)
    emitter.direction_range = (260, 280)
    emitter.size_range = (3, 12)
    
    emitter.start_color_range = (pygame.Color(100, 100, 100, 200), pygame.Color(150, 150, 150, 255))
    emitter.end_color_range = (pygame.Color(200, 200, 200, 0), pygame.Color(100, 100, 100, 0))
    
    emitter.emission_shape = 'circle'
    emitter.shape_data = {'radius': 8}
    emitter.gravity = pygame.Vector2(0, -20)
    emitter.drag_range = (0.2, 0.5)
    
    return emitter

def create_magical_orb_emitter(position: pygame.Vector2, 
                              orb_color: pygame.Color = pygame.Color(100, 150, 255)) -> 'ParticleEmitter':
    """Create a floating magical orb particle emitter."""
    emitter = ParticleEmitter(position)
    emitter.emission_rate = 15
    emitter.max_particles = 30
    emitter.lifetime_range = (3.0, 5.0)
    emitter.speed_range = (20, 40)
    emitter.size_range = (4, 12)
    emitter.emission_shape = 'circle'
    emitter.emission_radius = 15
    
    def setup_orb_particle(particle: Particle):
        # Magical blue-purple colors
        base_colors = [
            pygame.Color(100, 150, 255),  # Light blue
            pygame.Color(150, 100, 255),  # Purple
            pygame.Color(200, 150, 255),  # Light purple
            pygame.Color(50, 200, 255),   # Cyan
        ]
        
        start_color = random.choice(base_colors)
        particle.start_color = start_color
        particle.color = start_color
        particle.end_color = pygame.Color(start_color.r, start_color.g, start_color.b, 0)
        
        # Floating motion
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(15, 25)
        particle.velocity = pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
        
        # Gentle gravity upward (magical floating)
        particle.gravity = pygame.Vector2(0, -10)
        particle.drag = 0.5
        
        # Rotation
        particle.angular_velocity = random.uniform(-90, 90)
        
        # Size animation
        particle.start_size = random.uniform(3, 8)
        particle.end_size = 0
        
    emitter.particle_setup = setup_orb_particle
    return emitter

def create_sparkle_emitter(position: pygame.Vector2) -> 'ParticleEmitter':
    """Create sparkling magical particles."""
    emitter = ParticleEmitter(position)
    emitter.emission_rate = 25
    emitter.max_particles = 50
    emitter.lifetime_range = (1.0, 2.5)
    emitter.speed_range = (30, 80)
    emitter.size_range = (1, 4)
    emitter.emission_shape = 'circle'
    emitter.emission_radius = 20
    
    def setup_sparkle_particle(particle: Particle):
        # Golden sparkle colors
        sparkle_colors = [
            pygame.Color(255, 255, 100),  # Gold
            pygame.Color(255, 200, 100),  # Orange-gold
            pygame.Color(255, 255, 200),  # Light gold
            pygame.Color(255, 255, 255),  # White
        ]
        
        start_color = random.choice(sparkle_colors)
        particle.start_color = start_color
        particle.color = start_color
        particle.end_color = pygame.Color(start_color.r, start_color.g, start_color.b, 0)
        
        # Random sparkle motion
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(20, 60)
        particle.velocity = pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
        
        # Light gravity
        particle.gravity = pygame.Vector2(0, 20)
        particle.drag = 0.8
        
        # Twinkling rotation
        particle.angular_velocity = random.uniform(-180, 180)
        
        # Size animation
        particle.start_size = random.uniform(1, 3)
        particle.end_size = random.uniform(0, 1)
        
    emitter.particle_setup = setup_sparkle_particle
    return emitter

def create_mystical_energy_emitter(position: pygame.Vector2) -> 'ParticleEmitter':
    """Create mystical energy swirls."""
    emitter = ParticleEmitter(position)
    emitter.emission_rate = 8
    emitter.max_particles = 20
    emitter.lifetime_range = (4.0, 6.0)
    emitter.speed_range = (10, 30)
    emitter.size_range = (6, 15)
    emitter.emission_shape = 'circle'
    emitter.emission_radius = 5
    
    def setup_energy_particle(particle: Particle):
        # Mystical purple/green energy colors
        energy_colors = [
            pygame.Color(150, 50, 255),   # Purple
            pygame.Color(100, 255, 150),  # Green
            pygame.Color(50, 255, 200),   # Cyan
            pygame.Color(200, 100, 255),  # Light purple
        ]
        
        start_color = random.choice(energy_colors)
        particle.start_color = start_color
        particle.color = start_color
        particle.end_color = pygame.Color(start_color.r, start_color.g, start_color.b, 0)
        
        # Spiral motion
        particle.user_data['spiral_time'] = 0
        particle.user_data['spiral_radius'] = random.uniform(20, 60)
        particle.user_data['spiral_speed'] = random.uniform(0.5, 2.0)
        particle.user_data['center'] = pygame.Vector2(position)
        
        # Initial velocity
        particle.velocity = pygame.Vector2(0, random.uniform(-20, -40))
        particle.drag = 0.2
        
        # Size animation
        particle.start_size = random.uniform(4, 10)
        particle.end_size = 0
        
    def update_energy_particle(particle: Particle, dt: float):
        # Custom spiral motion
        particle.user_data['spiral_time'] += dt * particle.user_data['spiral_speed']
        
        spiral_x = math.cos(particle.user_data['spiral_time']) * particle.user_data['spiral_radius']
        spiral_y = math.sin(particle.user_data['spiral_time']) * particle.user_data['spiral_radius'] * 0.5
        
        center = particle.user_data['center']
        target_pos = center + pygame.Vector2(spiral_x, spiral_y - particle.age * 30)
        
        # Move towards spiral position
        direction = target_pos - particle.position
        if direction.length() > 0:
            particle.velocity += direction.normalize() * 50 * dt
            
    emitter.particle_setup = setup_energy_particle
    emitter.particle_update = update_energy_particle
    return emitter

def create_floating_runes_emitter(position: pygame.Vector2) -> 'ParticleEmitter':
    """Create floating magical rune symbols."""
    emitter = ParticleEmitter(position)
    emitter.emission_rate = 3
    emitter.max_particles = 8
    emitter.lifetime_range = (8.0, 12.0)
    emitter.speed_range = (5, 15)
    emitter.size_range = (12, 20)
    emitter.emission_shape = 'rectangle'
    emitter.emission_width = 100
    emitter.emission_height = 50
    
    def setup_rune_particle(particle: Particle):
        # Mystical rune colors
        rune_colors = [
            pygame.Color(255, 215, 0),    # Gold
            pygame.Color(147, 112, 219),  # Medium slate blue
            pygame.Color(138, 43, 226),   # Blue violet
            pygame.Color(255, 20, 147),   # Deep pink
        ]
        
        start_color = random.choice(rune_colors)
        particle.start_color = start_color
        particle.color = start_color
        particle.end_color = pygame.Color(start_color.r, start_color.g, start_color.b, 0)
        
        # Slow floating motion
        particle.velocity = pygame.Vector2(random.uniform(-10, 10), random.uniform(-20, -5))
        particle.gravity = pygame.Vector2(0, -5)  # Float upward
        particle.drag = 0.3
        
        # Slow rotation
        particle.angular_velocity = random.uniform(-30, 30)
        
        # Pulsing size
        particle.user_data['pulse_time'] = 0
        particle.user_data['base_size'] = random.uniform(8, 16)
        particle.start_size = particle.user_data['base_size']
        particle.end_size = 0
        
    def update_rune_particle(particle: Particle, dt: float):
        # Pulsing effect
        particle.user_data['pulse_time'] += dt * 2
        pulse = math.sin(particle.user_data['pulse_time']) * 0.3 + 1.0
        particle.size = particle.user_data['base_size'] * pulse
        
        # Fade out near end of life
        life_ratio = particle.age / particle.lifetime
        if life_ratio > 0.7:
            fade = 1.0 - (life_ratio - 0.7) / 0.3
            particle.color.a = int(particle.start_color.a * fade)
            
    emitter.particle_setup = setup_rune_particle
    emitter.particle_update = update_rune_particle
    return emitter
