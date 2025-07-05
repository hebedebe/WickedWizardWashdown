import pygame
from copy import copy
import math

from engine.core.scene import Scene
from engine.core.game import Game
from engine.core.world.actor import Actor
from engine.core.world.component import Component

from engine.builtin.ui.button import Button

from engine.builtin.components.sprite_component import SpriteComponent
from engine.builtin.components.camera_component import CameraComponent

class GameScene(Scene):
    def __init__(self):
        super().__init__("Game")

    def on_enter(self):
        pygame.mixer.music.load("assets/sounds/ambient_game.mp3")
        pygame.mixer.music.play(-1)

        interior_brightness = 200  # Adjust this value to change the brightness of the interior

        monitor = Actor("monitor")
        monitor_sprite = SpriteComponent("monitor", tint_color=(interior_brightness, interior_brightness, interior_brightness))
        monitor.transform.scale = pygame.Vector2(1)  # Adjust scale as needed
        monitor.transform.position = pygame.Vector2(-640//2, 0)
        monitor.addComponent(monitor_sprite)
        self.add_actor(monitor)

        fireman_poster = Actor("fireman_poster")
        fireman_poster_sprite = SpriteComponent("fireman_poster", tint_color=(interior_brightness, interior_brightness, interior_brightness))
        fireman_poster.transform.scale = pygame.Vector2(0.2)  # Adjust scale as needed
        fireman_poster.transform.position = pygame.Vector2(-640//2+230, -150)
        fireman_poster.addComponent(fireman_poster_sprite)
        self.add_actor(fireman_poster)

        outside = Actor("outside")
        outside_sprite = SpriteComponent("outside", tint_color=(100, 100, 100))
        outside.transform.scale = pygame.Vector2(0.9)  # Adjust scale as needed
        outside.transform.position = pygame.Vector2(640//2, 0)
        outside.transform.rotation = 90
        outside.addComponent(outside_sprite)
        self.add_actor(outside)

        window = Actor("window")
        window_sprite = SpriteComponent("window", tint_color=(interior_brightness, interior_brightness, interior_brightness))
        window.transform.scale = pygame.Vector2(1)  # Adjust scale as needed
        window.transform.position = pygame.Vector2(640//2, 0)
        window.addComponent(window_sprite)
        self.add_actor(window)

        camera = Actor("camera")
        camera.addComponent(CameraComponent(interpolate=True, smoothing=20))
        camera.transform.position = pygame.Vector2(-640//2, 0)
        self.add_actor(camera)

        self.cam_left_button = Button([0, Game().height//2], 50, 50, "<<<", font_size=24, on_click_callback=self.move_camera_left)
        self.cam_right_button = Button([Game().width - 50, Game().height//2], 50, 50, ">>>", font_size=24, on_click_callback=self.move_camera_right)

        self.cam_left_button.visible = False
        self.ui_manager.add_element(self.cam_left_button)
        self.ui_manager.add_element(self.cam_right_button)

    def on_exit(self):
        pygame.mixer.music.stop()
        return super().on_exit()

    def move_camera_left(self):
        camera = self.get_actor("camera")
        if camera:
            camera.transform.position.x = -640//2
            self.cam_left_button.visible = False
            self.cam_right_button.visible = True

    def move_camera_right(self):
        camera = self.get_actor("camera")
        if camera:
            camera.transform.position.x = 640//2
            self.cam_left_button.visible = True
            self.cam_right_button.visible = False