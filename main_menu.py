from engine.core.scene import Scene
from engine.core.game import Game
from engine.builtin.ui.button import Button
from engine.builtin.ui.label import Label
from engine.builtin.ui.panel import Panel
from engine.core.ui import UIManager
from engine.builtin.ui.fps_counter import FPSCounter
from engine.core.world.actor import Actor
from engine.builtin.components.sprite_component import SpriteComponent
from engine.builtin.components.animation_component import AnimationComponent
from engine.core.asset_manager import AssetManager
import pygame

class MainMenuScene(Scene):
    def __init__(self):
        super().__init__("MainMenu")

    def on_enter(self):
        print("Entering Main Menu Scene")
        self.panel = Panel((100, 100), 400, 300)

        self.title_label = Label((70, 20), 500, "Touching Jack 2: The Remake The Sequel (Complete Edition)", font_size=40, color=(255, 255, 255))
        self.menu_label = Label((150, 120), 100, "Main Menu", font_size=36, color=(255, 255, 255))
        self.start_button = Button((150, 200), 200, 50, "Start Game", font_size=24, on_click_callback=self.start_game)
        self.toggle_fullscreen_button = Button((150, 270), 200, 50, "Toggle Fullscreen", font_size=24, on_click_callback=Game().toggle_fullscreen)
        self.quit_button = Button((150, 340), 200, 50, "Quit", font_size=24, on_click_callback=self.quit_game)

        self.panel.add_child(self.menu_label)
        self.panel.add_child(self.start_button)
        self.panel.add_child(self.toggle_fullscreen_button)
        self.panel.add_child(self.quit_button)
        self.ui_manager.add_element(self.panel)
        self.ui_manager.add_element(self.title_label)

        self.ui_manager.add_element(FPSCounter())

        background = Actor("background")
        sprite = AnimationComponent(AssetManager().sliceSpritesheet("static_spritesheet", 640, 480))
        sprite.tint = (100, 100, 100)
        background.addComponent(sprite)
        self.add_actor(background)

        pygame.mixer.music.load("assets/sounds/ambient_menu.mp3")
        pygame.mixer.music.play(-1)

    def on_exit(self):
        print("Exiting Main Menu Scene")
        pygame.mixer.music.stop()

    def handle_event(self, event):
        self.ui_manager.handle_event(event)

    def start_game(self):
        print("Start Game")
        Game().load_scene("Game")

    def quit_game(self):
        print("Quit Game")
        Game().running = False