from engine import Game, Scene
from engine.rendering.ui import UIManager, Label, Button
from engine.rendering.particles import create_fire_emitter
import pygame
import random
import math

class GameScene(Scene):
    """Main game scene where the action happens."""

    def __init__(self):
        super().__init__("GameScene")
        self.ui_manager = None
        self.player_pos = pygame.Vector2(400, 300)
        self.player_speed = 200.0
        self.wizard_particles = []
        self.enemies = []
        self.score = 0
        self.health = 100
        self.max_health = 100
        self.game_time = 0.0
        self.enemy_spawn_timer = 0.0
        self.enemy_spawn_interval = 3.0
        
    def on_enter(self) -> None:
        super().on_enter()
        
        # Setup UI
        screen_size = pygame.display.get_surface().get_size()
        self.ui_manager = UIManager(screen_size)
        
        # Create game UI
        self.create_game_ui()
        
        # Initialize player position
        self.player_pos = pygame.Vector2(screen_size[0] // 2, screen_size[1] // 2)
        
        # Create initial wizard particles
        self.setup_wizard_effects()
        
        # Spawn some initial enemies
        self.spawn_enemy()
        
    def create_game_ui(self) -> None:
        """Create the game UI elements."""
        screen_size = pygame.display.get_surface().get_size()
        
        # Health bar background
        health_bg = Label(
            pygame.Rect(20, 20, 200, 25),
            "",
            name="health_bg"
        )
        self.ui_manager.add_widget(health_bg)
        
        # Health bar
        health_bar = Label(
            pygame.Rect(20, 20, 200, 25),
            f"Health: {self.health}/{self.max_health}",
            name="health_bar"
        )
        self.ui_manager.add_widget(health_bar)
        
        # Score display
        score_label = Label(
            pygame.Rect(screen_size[0] - 150, 20, 130, 25),
            f"Score: {self.score}",
            name="score_label"
        )
        self.ui_manager.add_widget(score_label)
        
        # Time display
        time_label = Label(
            pygame.Rect(screen_size[0] - 150, 50, 130, 25),
            f"Time: {int(self.game_time)}s",
            name="time_label"
        )
        self.ui_manager.add_widget(time_label)
        
        # Controls hint
        controls_label = Label(
            pygame.Rect(20, screen_size[1] - 80, 300, 50),
            "WASD: Move | Space: Cast Spell | ESC: Pause",
            name="controls_label"
        )
        self.ui_manager.add_widget(controls_label)
        
        # Pause button
        pause_button = Button(
            pygame.Rect(screen_size[0] - 100, screen_size[1] - 60, 80, 40),
            "Pause",
            name="pause_button"
        )
        pause_button.add_event_handler("clicked", self.on_pause_clicked)
        self.ui_manager.add_widget(pause_button)
        
    def setup_wizard_effects(self) -> None:
        """Setup magical effects around the wizard."""
        # Create particle emitter for wizard
        self.wizard_emitter = create_fire_emitter(self.player_pos)
        
    def spawn_enemy(self) -> None:
        """Spawn a new enemy at a random edge of the screen."""
        screen_size = pygame.display.get_surface().get_size()
        
        # Choose a random edge
        edge = random.randint(0, 3)
        if edge == 0:  # Top
            pos = pygame.Vector2(random.randint(0, screen_size[0]), 0)
        elif edge == 1:  # Right
            pos = pygame.Vector2(screen_size[0], random.randint(0, screen_size[1]))
        elif edge == 2:  # Bottom
            pos = pygame.Vector2(random.randint(0, screen_size[0]), screen_size[1])
        else:  # Left
            pos = pygame.Vector2(0, random.randint(0, screen_size[1]))
            
        enemy = {
            'pos': pos,
            'speed': random.uniform(50, 100),
            'health': random.randint(1, 3),
            'radius': random.randint(15, 25),
            'color': pygame.Color(random.randint(100, 200), random.randint(50, 150), random.randint(50, 150))
        }
        self.enemies.append(enemy)
        
    def update_player(self, dt: float) -> None:
        """Update player movement and actions."""
        keys = pygame.key.get_pressed()
        
        # Movement
        movement = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            movement.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            movement.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            movement.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            movement.x += 1
            
        if movement.length() > 0:
            movement = movement.normalize()
            self.player_pos += movement * self.player_speed * dt
            
        # Keep player on screen
        screen_size = pygame.display.get_surface().get_size()
        self.player_pos.x = max(20, min(screen_size[0] - 20, self.player_pos.x))
        self.player_pos.y = max(20, min(screen_size[1] - 20, self.player_pos.y))
        
    def update_enemies(self, dt: float) -> None:
        """Update enemy movement and behavior."""
        for enemy in self.enemies[:]:  # Copy list to avoid modification during iteration
            # Move towards player
            direction = self.player_pos - enemy['pos']
            if direction.length() > 0:
                direction = direction.normalize()
                enemy['pos'] += direction * enemy['speed'] * dt
                
            # Check collision with player
            distance = (enemy['pos'] - self.player_pos).length()
            if distance < enemy['radius'] + 15:  # Player radius is ~15
                # Damage player
                self.health -= 10
                self.enemies.remove(enemy)
                
                # Update health display
                health_bar = self.ui_manager.find_widget("health_bar")
                if health_bar:
                    health_bar.set_text(f"Health: {max(0, self.health)}/{self.max_health}")
                    
                # Check game over
                if self.health <= 0:
                    self.game_over()
                    
    def cast_spell(self) -> None:
        """Cast a spell to destroy nearby enemies."""
        spell_range = 100
        destroyed_enemies = []
        
        for enemy in self.enemies:
            distance = (enemy['pos'] - self.player_pos).length()
            if distance < spell_range:
                destroyed_enemies.append(enemy)
                
        # Remove destroyed enemies and add score
        for enemy in destroyed_enemies:
            self.enemies.remove(enemy)
            self.score += 10
            
        # Update score display
        score_label = self.ui_manager.find_widget("score_label")
        if score_label:
            score_label.set_text(f"Score: {self.score}")
            
        # Create spell effect (visual feedback)
        print(f"Spell cast! Destroyed {len(destroyed_enemies)} enemies")
        
    def game_over(self) -> None:
        """Handle game over."""
        print(f"Game Over! Final Score: {self.score}")
        # TODO: Show game over screen
        if self.game:
            self.game.pop_scene()
            
    def on_pause_clicked(self, event) -> None:
        """Handle pause button click."""
        print("Game paused")
        # TODO: Implement pause menu
        if self.game:
            self.game.pop_scene()
            
    def update(self, dt: float) -> None:
        super().update(dt)
        
        # Update game time
        self.game_time += dt
        
        # Update time display
        time_label = self.ui_manager.find_widget("time_label")
        if time_label:
            time_label.set_text(f"Time: {int(self.game_time)}s")
        
        # Update player
        self.update_player(dt)
        
        # Update enemies
        self.update_enemies(dt)
        
        # Spawn new enemies
        self.enemy_spawn_timer += dt
        if self.enemy_spawn_timer >= self.enemy_spawn_interval:
            self.spawn_enemy()
            self.enemy_spawn_timer = 0.0
            # Make enemies spawn faster over time
            self.enemy_spawn_interval = max(1.0, self.enemy_spawn_interval - 0.05)
        
        # Update particle effects
        if hasattr(self, 'wizard_emitter'):
            self.wizard_emitter.position = self.player_pos
            self.wizard_emitter.update(dt)
        
        # Update UI
        if self.ui_manager:
            self.ui_manager.update(dt)
            
    def render(self, screen: pygame.Surface) -> None:
        # Clear screen with dark blue background
        self.background_color = pygame.Color(10, 15, 25)
        super().render(screen)
        
        # Render game elements
        self.render_game_world(screen)
        
        # Render UI
        if self.ui_manager:
            self.ui_manager.render(screen)
            
    def render_game_world(self, screen: pygame.Surface) -> None:
        """Render the game world (player, enemies, effects)."""
        
        # Render enemies
        for enemy in self.enemies:
            pygame.draw.circle(screen, enemy['color'], 
                             (int(enemy['pos'].x), int(enemy['pos'].y)), 
                             enemy['radius'])
            # Add a darker border
            pygame.draw.circle(screen, pygame.Color(50, 50, 50), 
                             (int(enemy['pos'].x), int(enemy['pos'].y)), 
                             enemy['radius'], 2)
        
        # Render player wizard
        # Main body
        pygame.draw.circle(screen, pygame.Color(100, 150, 255), 
                         (int(self.player_pos.x), int(self.player_pos.y)), 15)
        # Wizard hat
        hat_points = [
            (int(self.player_pos.x), int(self.player_pos.y - 15)),
            (int(self.player_pos.x - 8), int(self.player_pos.y - 25)),
            (int(self.player_pos.x + 8), int(self.player_pos.y - 25))
        ]
        pygame.draw.polygon(screen, pygame.Color(80, 50, 150), hat_points)
        
        # Render wizard particle effects
        if hasattr(self, 'wizard_emitter'):
            self.wizard_emitter.render(screen)
            
        # Render health bar visual
        health_bg = self.ui_manager.find_widget("health_bg")
        if health_bg:
            # Background
            pygame.draw.rect(screen, pygame.Color(100, 50, 50), 
                           pygame.Rect(20, 20, 200, 25))
            # Health bar
            health_width = int((self.health / self.max_health) * 200)
            health_color = pygame.Color(50, 200, 50) if self.health > 30 else pygame.Color(200, 50, 50)
            pygame.draw.rect(screen, health_color,
                           pygame.Rect(20, 20, health_width, 25))
            # Border
            pygame.draw.rect(screen, pygame.Color(255, 255, 255),
                           pygame.Rect(20, 20, 200, 25), 2)
            
    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        
        # Handle UI events
        if self.ui_manager:
            if self.ui_manager.handle_event(event):
                return
                
        # Handle game events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.cast_spell()
            elif event.key == pygame.K_ESCAPE:
                # Pause/return to lobby
                if self.game:
                    self.game.pop_scene()
            elif event.key == pygame.K_r and self.health <= 0:
                # Restart game
                self.restart_game()
                
    def restart_game(self) -> None:
        """Restart the game."""
        self.health = self.max_health
        self.score = 0
        self.game_time = 0.0
        self.enemies.clear()
        self.enemy_spawn_timer = 0.0
        self.enemy_spawn_interval = 3.0
        
        # Reset UI
        health_bar = self.ui_manager.find_widget("health_bar")
        if health_bar:
            health_bar.set_text(f"Health: {self.health}/{self.max_health}")
            
        score_label = self.ui_manager.find_widget("score_label")
        if score_label:
            score_label.set_text(f"Score: {self.score}")
            
        print("Game restarted!")