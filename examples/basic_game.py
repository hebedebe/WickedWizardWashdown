"""
Basic game example demonstrating the core features of the engine.
"""

import pygame
import random
from engine import *
from engine.particles import create_explosion_emitter, create_fire_emitter

class PlayerController(Component):
    """Player movement and input component."""
    
    def __init__(self, speed: float = 200.0):
        super().__init__()
        self.speed = speed
        
    def update(self, dt: float) -> None:
        if not self.actor:
            return
            
        # Get input from the game's input manager
        game = self.actor.transform.world_position  # Access to scene via actor would be better
        
        # For now, use pygame directly
        keys = pygame.key.get_pressed()
        movement = pygame.Vector2(0, 0)
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            movement.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            movement.x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            movement.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            movement.y += 1
            
        if movement.length() > 0:
            movement = movement.normalize()
            self.actor.transform.local_position += movement * self.speed * dt
            
        # Keep player on screen
        screen_width, screen_height = pygame.display.get_surface().get_size()
        pos = self.actor.transform.local_position
        pos.x = max(16, min(screen_width - 16, pos.x))
        pos.y = max(16, min(screen_height - 16, pos.y))

class EnemyAI(Component):
    """Simple enemy AI that follows the player."""
    
    def __init__(self, speed: float = 100.0, target: Actor = None):
        super().__init__()
        self.speed = speed
        self.target = target
        self.wander_time = 0.0
        self.wander_direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        
    def update(self, dt: float) -> None:
        if not self.actor:
            return
            
        if self.target:
            # Move towards target
            direction = self.target.transform.world_position - self.actor.transform.world_position
            if direction.length() > 0:
                direction = direction.normalize()
                self.actor.transform.local_position += direction * self.speed * dt
        else:
            # Wander randomly
            self.wander_time += dt
            if self.wander_time > 2.0:
                self.wander_direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                if self.wander_direction.length() > 0:
                    self.wander_direction = self.wander_direction.normalize()
                self.wander_time = 0.0
                
            self.actor.transform.local_position += self.wander_direction * self.speed * 0.5 * dt

class Projectile(Component):
    """Projectile component that moves in a direction."""
    
    def __init__(self, velocity: pygame.Vector2, lifetime: float = 3.0):
        super().__init__()
        self.velocity = velocity
        self.lifetime = lifetime
        self.age = 0.0
        
    def update(self, dt: float) -> None:
        if not self.actor:
            return
            
        self.age += dt
        if self.age >= self.lifetime:
            # Remove projectile
            if hasattr(self.actor, 'scene'):
                self.actor.scene.destroy_actor(self.actor)
            return
            
        # Move projectile
        self.actor.transform.local_position += self.velocity * dt

class BasicGameScene(Scene):
    """Main game scene with player, enemies, and effects."""
    
    def __init__(self):
        super().__init__("BasicGame")
        self.player = None
        self.enemies = []
        self.ui_manager = None
        self.score = 0
        self.spawn_timer = 0.0
        
    def on_enter(self) -> None:
        super().on_enter()
        
        # Create UI
        screen_size = pygame.display.get_surface().get_size()
        self.ui_manager = UIManager(screen_size)
        
        # Score label
        score_label = Label(
            pygame.Rect(10, 10, 200, 30),
            f"Score: {self.score}",
            name="score_label"
        )
        score_label.text_color = pygame.Color(255, 255, 0)
        self.ui_manager.add_widget(score_label)
        
        # Instructions
        instructions = Label(
            pygame.Rect(10, screen_size[1] - 100, 400, 80),
            "WASD/Arrow Keys: Move\nSpace: Shoot\nESC: Quit",
            name="instructions"
        )
        instructions.text_color = pygame.Color(255, 255, 255)
        self.ui_manager.add_widget(instructions)
        
        # Create player
        self.create_player()
        
        # Create some initial enemies
        for _ in range(3):
            self.create_enemy()
            
    def create_player(self) -> None:
        """Create the player actor."""
        screen_size = pygame.display.get_surface().get_size()
        
        self.player = self.create_actor("Player", pygame.Vector2(screen_size[0] // 2, screen_size[1] // 2))
        
        # Add sprite component
        sprite = SpriteComponent(color=pygame.Color(0, 255, 0), size=pygame.Vector2(32, 32))
        self.player.add_component(sprite)
        
        # Add player controller
        controller = PlayerController(250.0)
        self.player.add_component(controller)
        
        # Add health
        health = HealthComponent(100.0)
        health.on_death = self.on_player_death
        self.player.add_component(health)
        
        # Add particle system for effects
        particles = ParticleSystem()
        self.player.add_component(particles)
        
        self.player.add_tag("player")
        
    def create_enemy(self) -> None:
        """Create an enemy actor."""
        screen_size = pygame.display.get_surface().get_size()
        
        # Random position on edges
        edge = random.randint(0, 3)
        if edge == 0:  # Top
            pos = pygame.Vector2(random.randint(0, screen_size[0]), 0)
        elif edge == 1:  # Right
            pos = pygame.Vector2(screen_size[0], random.randint(0, screen_size[1]))
        elif edge == 2:  # Bottom
            pos = pygame.Vector2(random.randint(0, screen_size[0]), screen_size[1])
        else:  # Left
            pos = pygame.Vector2(0, random.randint(0, screen_size[1]))
            
        enemy = self.create_actor(f"Enemy_{len(self.enemies)}", pos)
        
        # Add sprite component
        sprite = SpriteComponent(color=pygame.Color(255, 0, 0), size=pygame.Vector2(24, 24))
        enemy.add_component(sprite)
        
        # Add AI
        ai = EnemyAI(80.0, self.player)
        enemy.add_component(ai)
        
        # Add health
        health = HealthComponent(30.0)
        health.on_death = lambda: self.on_enemy_death(enemy)
        enemy.add_component(health)
        
        enemy.add_tag("enemy")
        self.enemies.append(enemy)
        
    def create_projectile(self, position: pygame.Vector2, direction: pygame.Vector2) -> None:
        """Create a projectile."""
        projectile = self.create_actor("Projectile", position)
        
        # Add sprite
        sprite = SpriteComponent(color=pygame.Color(255, 255, 0), size=pygame.Vector2(8, 8))
        projectile.add_component(sprite)
        
        # Add projectile behavior
        velocity = direction * 400.0  # Speed
        proj_component = Projectile(velocity, 2.0)
        projectile.add_component(proj_component)
        
        projectile.add_tag("projectile")
        
    def on_player_death(self) -> None:
        """Handle player death."""
        print("Game Over!")
        # Add explosion effect
        if self.player:
            particles = self.player.get_component(ParticleSystem)
            if particles:
                explosion = create_explosion_emitter(self.player.transform.world_position)
                particles.add_emitter(explosion)
                
    def on_enemy_death(self, enemy: Actor) -> None:
        """Handle enemy death."""
        self.score += 10
        
        # Update score display
        score_label = self.ui_manager.find_widget("score_label")
        if score_label:
            score_label.set_text(f"Score: {self.score}")
            
        # Add explosion effect
        particles_system = ParticleSystem()
        explosion = create_explosion_emitter(enemy.transform.world_position, pygame.Color(255, 100, 0))
        particles_system.add_emitter(explosion)
        
        # Create temporary actor for explosion
        explosion_actor = self.create_actor("Explosion", enemy.transform.world_position)
        explosion_actor.add_component(particles_system)
        
        # Remove explosion after 2 seconds
        def remove_explosion():
            self.destroy_actor(explosion_actor)
        # Note: In a real game, you'd want a timer system for this
        
        # Remove enemy
        if enemy in self.enemies:
            self.enemies.remove(enemy)
        self.destroy_actor(enemy)
        
    def update(self, dt: float) -> None:
        super().update(dt)
        
        # Update UI
        if self.ui_manager:
            self.ui_manager.update(dt)
            
        # Check for shooting input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.player:
            # Simple shooting - shoot up
            direction = pygame.Vector2(0, -1)
            self.create_projectile(self.player.transform.world_position, direction)
            
        # Spawn more enemies
        self.spawn_timer += dt
        if self.spawn_timer > 3.0 and len(self.enemies) < 5:
            self.create_enemy()
            self.spawn_timer = 0.0
            
        # Check collisions (simple distance-based)
        self.check_collisions()
        
    def check_collisions(self) -> None:
        """Simple collision detection."""
        if not self.player:
            return
            
        player_pos = self.player.transform.world_position
        projectiles = self.find_actors_with_tag("projectile")
        
        # Player vs enemies
        for enemy in list(self.enemies):
            enemy_pos = enemy.transform.world_position
            distance = (player_pos - enemy_pos).length()
            
            if distance < 25:  # Collision
                # Damage player
                player_health = self.player.get_component(HealthComponent)
                if player_health:
                    player_health.take_damage(20.0)
                    
                # Remove enemy
                self.on_enemy_death(enemy)
                
        # Projectiles vs enemies
        for projectile in projectiles:
            proj_pos = projectile.transform.world_position
            
            for enemy in list(self.enemies):
                enemy_pos = enemy.transform.world_position
                distance = (proj_pos - enemy_pos).length()
                
                if distance < 20:  # Collision
                    # Damage enemy
                    enemy_health = enemy.get_component(HealthComponent)
                    if enemy_health:
                        enemy_health.take_damage(50.0)
                        
                    # Remove projectile
                    self.destroy_actor(projectile)
                    break
                    
    def render(self, screen: pygame.Surface) -> None:
        # Set dark background
        self.background_color = pygame.Color(20, 20, 40)
        super().render(screen)
        
        # Render UI
        if self.ui_manager:
            self.ui_manager.render(screen)
            
    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        
        # Handle UI events
        if self.ui_manager:
            self.ui_manager.handle_event(event)
            
        # Handle game events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.game:
                    self.game.quit()

def main():
    """Main function to run the basic game."""
    # Create and configure the game
    game = Game(800, 600, "Wicked Wizard Washdown - Basic Game")
    
    # Create and add the game scene
    game_scene = BasicGameScene()
    game.add_scene("game", game_scene)
    game.load_scene("game")
    
    # Setup input bindings
    game.input_manager.setup_default_bindings()
    
    # Run the game
    game.run()

if __name__ == "__main__":
    main()
