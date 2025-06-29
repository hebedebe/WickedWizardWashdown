"""
Particle effects demonstration showing various particle systems.
"""

import pygame
import math
import random
from engine import *
from engine.particles import (
    create_explosion_emitter, create_fire_emitter, create_smoke_emitter,
    ParticleEmitter, Particle
)

class ParticleDemo(Scene):
    """Scene demonstrating various particle effects."""
    
    def __init__(self):
        super().__init__("ParticleDemo")
        self.ui_manager = None
        self.particle_actors = []
        self.demo_mode = 0  # Current demo mode
        self.demo_timer = 0.0
        self.demo_interval = 5.0  # Switch demos every 5 seconds
        
    def on_enter(self) -> None:
        super().on_enter()
        
        # Setup UI
        self.setup_ui()
        
        # Create initial particle effects
        self.setup_demo_effects()
        
    def setup_ui(self) -> None:
        """Setup UI elements."""
        screen_size = pygame.display.get_surface().get_size()
        self.ui_manager = UIManager(screen_size)
        
        # Title
        title = Label(
            pygame.Rect(screen_size[0] // 2 - 150, 20, 300, 40),
            "Particle Effects Demo",
            name="title"
        )
        title.text_color = pygame.Color(255, 255, 255)
        title.align_x = 'center'
        self.ui_manager.add_widget(title)
        
        # Current effect label
        effect_label = Label(
            pygame.Rect(20, 80, 300, 30),
            "Current Effect: Loading...",
            name="effect_label"
        )
        effect_label.text_color = pygame.Color(255, 255, 0)
        self.ui_manager.add_widget(effect_label)
        
        # Instructions
        instructions = Label(
            pygame.Rect(20, screen_size[1] - 120, 400, 100),
            "Click: Create explosion\nSpace: Switch effect\nR: Reset\nESC: Quit",
            name="instructions"
        )
        instructions.text_color = pygame.Color(200, 200, 200)
        self.ui_manager.add_widget(instructions)
        
        # Effect buttons
        button_y = 130
        button_height = 35
        button_spacing = 40
        
        effects = ["Explosion", "Fire", "Smoke", "Rain", "Magic", "Sparks"]
        
        for i, effect in enumerate(effects):
            button = Button(
                pygame.Rect(20, button_y + i * button_spacing, 100, button_height),
                effect,
                name=f"btn_{effect.lower()}"
            )
            button.add_event_handler("clicked", lambda e, idx=i: self.switch_to_demo(idx))
            self.ui_manager.add_widget(button)
            
    def setup_demo_effects(self) -> None:
        """Setup the initial demo effects."""
        self.switch_to_demo(0)
        
    def switch_to_demo(self, demo_index: int) -> None:
        """Switch to a specific demo."""
        self.demo_mode = demo_index
        self.demo_timer = 0.0
        
        # Clear existing effects
        for actor in self.particle_actors:
            self.destroy_actor(actor)
        self.particle_actors.clear()
        
        # Update UI
        effects = ["Explosion", "Fire", "Smoke", "Rain", "Magic", "Sparks"]
        if self.ui_manager:
            effect_label = self.ui_manager.find_widget("effect_label")
            if effect_label and demo_index < len(effects):
                effect_label.set_text(f"Current Effect: {effects[demo_index]}")
                
        # Create new effects based on demo mode
        screen_size = pygame.display.get_surface().get_size()
        center = pygame.Vector2(screen_size[0] // 2, screen_size[1] // 2)
        
        if demo_index == 0:  # Explosion
            self.create_explosion_demo(center)
        elif demo_index == 1:  # Fire
            self.create_fire_demo(center)
        elif demo_index == 2:  # Smoke
            self.create_smoke_demo(center)
        elif demo_index == 3:  # Rain
            self.create_rain_demo()
        elif demo_index == 4:  # Magic
            self.create_magic_demo(center)
        elif demo_index == 5:  # Sparks
            self.create_sparks_demo(center)
            
    def create_explosion_demo(self, position: pygame.Vector2) -> None:
        """Create explosion effect demo."""
        actor = self.create_actor("Explosion", position)
        particles = ParticleSystem()
        
        # Main explosion
        explosion = create_explosion_emitter(position, pygame.Color(255, 150, 0))
        particles.add_emitter(explosion)
        
        # Secondary explosion
        def create_secondary():
            if len(particles.emitters) == 1:  # Only main explosion left
                secondary = create_explosion_emitter(
                    position + pygame.Vector2(random.uniform(-30, 30), random.uniform(-30, 30)),
                    pygame.Color(255, 50, 0)
                )
                secondary.burst_count = 30
                particles.add_emitter(secondary)
                
        # Add timer behavior for secondary explosion
        timer = 0.8
        def update_explosion(dt):
            nonlocal timer
            timer -= dt
            if timer <= 0:
                create_secondary()
                
        # Store timer function (in real engine, you'd have a proper timer system)
        actor.explosion_timer = update_explosion
        
        actor.add_component(particles)
        self.particle_actors.append(actor)
        
    def create_fire_demo(self, position: pygame.Vector2) -> None:
        """Create fire effect demo."""
        # Main fire
        fire_actor = self.create_actor("Fire", position + pygame.Vector2(0, 50))
        fire_particles = ParticleSystem()
        
        fire_emitter = create_fire_emitter(position + pygame.Vector2(0, 50))
        fire_particles.add_emitter(fire_emitter)
        
        fire_actor.add_component(fire_particles)
        self.particle_actors.append(fire_actor)
        
        # Smoke from fire
        smoke_actor = self.create_actor("Smoke", position)
        smoke_particles = ParticleSystem()
        
        smoke_emitter = create_smoke_emitter(position)
        smoke_emitter.emission_rate = 8
        smoke_particles.add_emitter(smoke_emitter)
        
        smoke_actor.add_component(smoke_particles)
        self.particle_actors.append(smoke_actor)
        
    def create_smoke_demo(self, position: pygame.Vector2) -> None:
        """Create smoke effect demo."""
        actor = self.create_actor("SmokeDemo", position)
        particles = ParticleSystem()
        
        # Dense smoke
        smoke = create_smoke_emitter(position)
        smoke.emission_rate = 25
        smoke.max_particles = 80
        smoke.lifetime_range = (3.0, 6.0)
        smoke.size_range = (5.0, 20.0)
        
        particles.add_emitter(smoke)
        actor.add_component(particles)
        self.particle_actors.append(actor)
        
    def create_rain_demo(self) -> None:
        """Create rain effect demo."""
        screen_size = pygame.display.get_surface().get_size()
        
        # Rain emitter at top of screen
        rain_actor = self.create_actor("Rain", pygame.Vector2(screen_size[0] // 2, -20))
        particles = ParticleSystem()
        
        rain_emitter = ParticleEmitter(pygame.Vector2(screen_size[0] // 2, -20))
        rain_emitter.emission_rate = 100
        rain_emitter.max_particles = 200
        
        rain_emitter.lifetime_range = (3.0, 4.0)
        rain_emitter.speed_range = (200, 300)
        rain_emitter.direction_range = (85, 95)  # Mostly downward
        rain_emitter.size_range = (1.0, 3.0)
        
        # Blue rain color
        rain_emitter.start_color_range = (
            pygame.Color(150, 200, 255, 200),
            pygame.Color(100, 150, 255, 255)
        )
        rain_emitter.end_color_range = (
            pygame.Color(100, 150, 255, 100),
            pygame.Color(50, 100, 200, 0)
        )
        
        # Wide horizontal emission
        rain_emitter.emission_shape = 'line'
        rain_emitter.shape_data = {'length': screen_size[0], 'angle': 0}
        
        rain_emitter.gravity = pygame.Vector2(0, 300)
        
        particles.add_emitter(rain_emitter)
        rain_actor.add_component(particles)
        self.particle_actors.append(rain_actor)
        
    def create_magic_demo(self, position: pygame.Vector2) -> None:
        """Create magical effect demo."""
        actor = self.create_actor("Magic", position)
        particles = ParticleSystem()
        
        # Create magical sparkle emitter
        magic_emitter = ParticleEmitter(position)
        magic_emitter.emission_rate = 40
        magic_emitter.max_particles = 100
        
        magic_emitter.lifetime_range = (2.0, 4.0)
        magic_emitter.speed_range = (30, 80)
        magic_emitter.direction_range = (0, 360)
        magic_emitter.size_range = (2.0, 8.0)
        magic_emitter.angular_velocity_range = (-5.0, 5.0)
        
        # Purple and gold colors
        magic_emitter.start_color_range = (
            pygame.Color(255, 0, 255, 255),  # Magenta
            pygame.Color(255, 215, 0, 255)   # Gold
        )
        magic_emitter.end_color_range = (
            pygame.Color(128, 0, 128, 0),    # Purple fade
            pygame.Color(255, 165, 0, 0)     # Orange fade
        )
        
        # Circular emission
        magic_emitter.emission_shape = 'circle'
        magic_emitter.shape_data = {'radius': 15}
        
        # Add spiral behavior
        def spiral_behavior(particle: Particle, dt: float) -> None:
            if particle.age > 0:
                # Create spiral motion
                center = position
                radius = particle.age * 50
                angle = particle.age * 5
                
                spiral_pos = center + pygame.Vector2(
                    math.cos(angle) * radius,
                    math.sin(angle) * radius
                )
                
                # Blend with current position
                particle.position = particle.position.lerp(spiral_pos, dt * 2)
                
        magic_emitter.add_behavior(spiral_behavior)
        
        particles.add_emitter(magic_emitter)
        actor.add_component(particles)
        self.particle_actors.append(actor)
        
    def create_sparks_demo(self, position: pygame.Vector2) -> None:
        """Create sparks effect demo."""
        actor = self.create_actor("Sparks", position)
        particles = ParticleSystem()
        
        # Electric sparks
        sparks_emitter = ParticleEmitter(position)
        sparks_emitter.emission_rate = 60
        sparks_emitter.max_particles = 120
        
        sparks_emitter.lifetime_range = (0.5, 1.5)
        sparks_emitter.speed_range = (100, 250)
        sparks_emitter.direction_range = (0, 360)
        sparks_emitter.size_range = (1.0, 4.0)
        
        # Electric blue/white colors
        sparks_emitter.start_color_range = (
            pygame.Color(255, 255, 255, 255),  # White
            pygame.Color(0, 255, 255, 255)     # Cyan
        )
        sparks_emitter.end_color_range = (
            pygame.Color(0, 100, 255, 0),      # Blue fade
            pygame.Color(255, 255, 0, 0)       # Yellow fade
        )
        
        sparks_emitter.gravity = pygame.Vector2(0, 150)
        sparks_emitter.drag_range = (2.0, 4.0)
        
        particles.add_emitter(sparks_emitter)
        actor.add_component(particles)
        self.particle_actors.append(actor)
        
    def update(self, dt: float) -> None:
        super().update(dt)
        
        # Update UI
        if self.ui_manager:
            self.ui_manager.update(dt)
            
        # Auto-switch demos
        self.demo_timer += dt
        if self.demo_timer >= self.demo_interval:
            next_demo = (self.demo_mode + 1) % 6
            self.switch_to_demo(next_demo)
            
        # Update custom behaviors (explosion timer, etc.)
        for actor in self.particle_actors:
            if hasattr(actor, 'explosion_timer'):
                actor.explosion_timer(dt)
                
    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        
        # Handle UI events
        if self.ui_manager:
            self.ui_manager.handle_event(event)
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Create explosion at mouse position
                mouse_pos = pygame.Vector2(event.pos)
                explosion_actor = self.create_actor("ClickExplosion", mouse_pos)
                particles = ParticleSystem()
                
                explosion = create_explosion_emitter(mouse_pos)
                particles.add_emitter(explosion)
                
                explosion_actor.add_component(particles)
                
                # Auto-remove after 3 seconds
                def remove_later():
                    if explosion_actor in self.actors:
                        self.destroy_actor(explosion_actor)
                # In a real game, you'd use a timer system
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Switch to next demo
                next_demo = (self.demo_mode + 1) % 6
                self.switch_to_demo(next_demo)
            elif event.key == pygame.K_r:
                # Reset current demo
                self.switch_to_demo(self.demo_mode)
            elif event.key == pygame.K_ESCAPE:
                if self.game:
                    self.game.quit()
                    
    def render(self, screen: pygame.Surface) -> None:
        # Dark background
        self.background_color = pygame.Color(10, 10, 20)
        super().render(screen)
        
        # Render UI
        if self.ui_manager:
            self.ui_manager.render(screen)

def main():
    """Main function to run the particle demo."""
    # Create game
    game = Game(1000, 700, "Wicked Wizard Washdown - Particle Effects Demo")
    
    # Create and add the demo scene
    demo_scene = ParticleDemo()
    game.add_scene("demo", demo_scene)
    game.load_scene("demo")
    
    # Run the game
    game.run()

if __name__ == "__main__":
    main()
