from engine import Game, Scene, Actor, Component, InputManager, AssetManager, NetworkManager
from engine.ui import UIManager, FPSDisplay, Button
from engine.particles import create_fire_emitter
import pygame

class SettingsScene(Scene):
    """Settings screen with volume controls and options."""
    
    def __init__(self):
        super().__init__("Settings")
        self.ui_manager = None
        self.master_volume = 1.0
        self.music_volume = 1.0
        self.sfx_volume = 1.0
        
    def on_enter(self) -> None:
        super().on_enter()
        
        # Setup UI
        screen_size = pygame.display.get_surface().get_size()
        self.ui_manager = UIManager(screen_size)
        
        # Create settings UI
        self.create_settings_ui()
        
    def create_settings_ui(self) -> None:
        """Create the settings UI elements."""
        from engine.ui import Label, Slider
        screen_size = pygame.display.get_surface().get_size()
        
        # Title label
        title_label = Label(
            pygame.Rect((screen_size[0] - 200) // 2, 50, 200, 40),
            "Settings",
            name="title_label"
        )
        self.ui_manager.add_widget(title_label)
        
        # Volume controls
        y_start = 150
        spacing = 60
        
        # Master Volume
        master_label = Label(
            pygame.Rect(100, y_start, 200, 30),
            f"Master Volume: {int(self.master_volume * 100)}%",
            name="master_label"
        )
        self.ui_manager.add_widget(master_label)
        
        master_slider = Slider(
            pygame.Rect(320, y_start, 200, 30),
            min_value=0.0,
            max_value=1.0,
            value=self.master_volume,
            name="master_slider"
        )
        master_slider.add_event_handler("value_changed", self.on_master_volume_changed)
        self.ui_manager.add_widget(master_slider)
        
        # Music Volume
        music_label = Label(
            pygame.Rect(100, y_start + spacing, 200, 30),
            f"Music Volume: {int(self.music_volume * 100)}%",
            name="music_label"
        )
        self.ui_manager.add_widget(music_label)
        
        music_slider = Slider(
            pygame.Rect(320, y_start + spacing, 200, 30),
            min_value=0.0,
            max_value=1.0,
            value=self.music_volume,
            name="music_slider"
        )
        music_slider.add_event_handler("value_changed", self.on_music_volume_changed)
        self.ui_manager.add_widget(music_slider)
        
        # SFX Volume
        sfx_label = Label(
            pygame.Rect(100, y_start + 2 * spacing, 200, 30),
            f"SFX Volume: {int(self.sfx_volume * 100)}%",
            name="sfx_label"
        )
        self.ui_manager.add_widget(sfx_label)
        
        sfx_slider = Slider(
            pygame.Rect(320, y_start + 2 * spacing, 200, 30),
            min_value=0.0,
            max_value=1.0,
            value=self.sfx_volume,
            name="sfx_slider"
        )
        sfx_slider.add_event_handler("value_changed", self.on_sfx_volume_changed)
        self.ui_manager.add_widget(sfx_slider)
        
        # Back button
        back_button = Button(
            pygame.Rect((screen_size[0] - 150) // 2, screen_size[1] - 100, 150, 50),
            "Back",
            name="back_button"
        )
        back_button.add_event_handler("clicked", self.on_back_clicked)
        self.ui_manager.add_widget(back_button)
        
    def on_master_volume_changed(self, event) -> None:
        """Handle master volume slider change."""
        self.master_volume = event.data
        # Update label
        master_label = self.ui_manager.find_widget("master_label")
        if master_label:
            master_label.set_text(f"Master Volume: {int(self.master_volume * 100)}%")
        print(f"Master volume set to {int(self.master_volume * 100)}%")
        
    def on_music_volume_changed(self, event) -> None:
        """Handle music volume slider change."""
        self.music_volume = event.data
        # Update label
        music_label = self.ui_manager.find_widget("music_label")
        if music_label:
            music_label.set_text(f"Music Volume: {int(self.music_volume * 100)}%")
        print(f"Music volume set to {int(self.music_volume * 100)}%")
        
    def on_sfx_volume_changed(self, event) -> None:
        """Handle SFX volume slider change."""
        self.sfx_volume = event.data
        # Update label
        sfx_label = self.ui_manager.find_widget("sfx_label")
        if sfx_label:
            sfx_label.set_text(f"SFX Volume: {int(self.sfx_volume * 100)}%")
        print(f"SFX volume set to {int(self.sfx_volume * 100)}%")
        
    def on_back_clicked(self, event) -> None:
        """Handle back button click."""
        if self.game:
            self.game.pop_scene()
            
    def update(self, dt: float) -> None:
        super().update(dt)
        
        # Update UI
        if self.ui_manager:
            self.ui_manager.update(dt)
            
    def render(self, screen: pygame.Surface) -> None:
        # Clear screen with dark background
        self.background_color = pygame.Color(30, 40, 50)
        super().render(screen)
        
        # Render UI
        if self.ui_manager:
            self.ui_manager.render(screen)
            
    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        
        # Handle UI events
        if self.ui_manager:
            if self.ui_manager.handle_event(event):
                return
                
        # Handle escape key to go back
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.game:
                    self.game.pop_scene()
