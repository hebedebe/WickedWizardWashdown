import pygame
from copy import copy
import math

from engine.core.scene import Scene
from engine.core.game import Game
from engine.core.world.actor import Actor
from engine.core.world.component import Component
from engine.core.asset_manager import AssetManager

from engine.builtin.ui.button import Button
from engine.builtin.ui.label import Label
from engine.builtin.ui.fps_counter import FPSCounter
from engine.builtin.ui.panel import Panel

from engine.builtin.components.sprite_component import SpriteComponent
from engine.builtin.components.camera_component import CameraComponent
from engine.builtin.components.clickable_component import ClickableComponent
from engine.builtin.components.audio_component import AudioComponent

class GameScene(Scene):
    def __init__(self):
        super().__init__("Game")
        self.position = 1
        self.positions = [
            pygame.Vector2(-640, 0),  # Left position
            pygame.Vector2(0, 0),     # Middle position
            pygame.Vector2(640, 0)    # Right position
        ]
        self.monitor_on = False

        self.power = 100
        self.power_drain_rate = 1.7

        self.time = 0
        self.hour_length = 60  # Length of an hour in seconds

        self.sleep = 100
        self.sleep_drain_rate = 1  # Rate at which sleep decreases
        self.asleep = False
        self.sleep_timer = 0
        self.sleep_timer_max = 8  # Maximum time before waking up in seconds

    def on_enter(self):
        pygame.mixer.music.load("assets/sounds/ambient_game.mp3")
        pygame.mixer.music.play(-1)

        interior_brightness = 200  # Adjust this value to change the brightness of the interior

        monitor = Actor("monitor")
        monitor_sprite = SpriteComponent("monitor", tint_color=(interior_brightness, interior_brightness, interior_brightness))
        monitor.transform.scale = pygame.Vector2(1)  # Adjust scale as needed
        monitor.transform.position = self.positions[1]
        monitor.addComponent(monitor_sprite)
        self.add_actor(monitor)

        power_button = Actor("power_button")
        power_button_sprite = SpriteComponent("power_button", tint_color=(interior_brightness, interior_brightness, interior_brightness))
        power_button_click = ClickableComponent(20, 20, (0, 0))
        power_button_click_audio = AudioComponent("click")
        power_button_start_audio = AudioComponent("startup", volume=2)
        def toggle_monitor():
            power_button_click_audio.play()
            self.monitor_on = not self.monitor_on
            if self.monitor_on:
                power_button_start_audio.play()
            else:
                power_button_start_audio.stop()
        power_button_click.set_click_callback(lambda: toggle_monitor())
        power_button.transform.scale = pygame.Vector2(0.03)  # Adjust scale as needed
        power_button.transform.position = pygame.Vector2(self.positions[1].x+125, 102)
        power_button.addComponent(power_button_sprite)
        power_button.addComponent(power_button_click)
        self.add_actor(power_button)

        fireman_poster = Actor("fireman_poster")
        fireman_poster_sprite = SpriteComponent("fireman_poster", tint_color=(interior_brightness, interior_brightness, interior_brightness))
        fireman_poster_click = ClickableComponent(70, 100, (5, 0))
        fireman_poster_audio = AudioComponent("grunt")
        fireman_poster_click.set_click_callback(lambda: fireman_poster_audio.play())
        fireman_poster.transform.scale = pygame.Vector2(0.2)  # Adjust scale as needed
        fireman_poster.transform.position = pygame.Vector2(self.positions[1].x+230, -150)
        fireman_poster.addComponent(fireman_poster_sprite)
        fireman_poster.addComponent(fireman_poster_click)
        fireman_poster.addComponent(fireman_poster_audio)
        self.add_actor(fireman_poster)

        bed = Actor("bed")
        bed_sprite = SpriteComponent("bed", tint_color=(interior_brightness, interior_brightness, interior_brightness))
        bed.transform.scale = pygame.Vector2(1.5)  # Adjust scale as needed
        bed.transform.position = self.positions[0]
        bed.transform.position.x -= 130
        bed.addComponent(bed_sprite)
        self.add_actor(bed)

        outside = Actor("outside")
        outside_sprite = SpriteComponent("outside", tint_color=(100, 100, 100))
        outside.transform.scale = pygame.Vector2(0.9)  # Adjust scale as needed
        outside.transform.position = self.positions[2]
        outside.transform.rotation = 90
        outside.addComponent(outside_sprite)
        self.add_actor(outside)

        window = Actor("window")
        window_sprite = SpriteComponent("window", tint_color=(interior_brightness, interior_brightness, interior_brightness))
        window.transform.scale = pygame.Vector2(1)  # Adjust scale as needed
        window.transform.position = self.positions[2]
        window.addComponent(window_sprite)
        self.add_actor(window)

        camera = Actor("camera")
        camera.addComponent(CameraComponent(interpolate=True, smoothing=20))
        camera.transform.position = self.positions[1]
        self.add_actor(camera)

        self.look_left_button = Button([0, Game().height//2], 50, 50, "<<<", font_size=24, on_click_callback=self.look_left)
        self.look_right_button = Button([Game().width - 50, Game().height//2], 50, 50, ">>>", font_size=24, on_click_callback=self.look_right)
        self.lower_panel = Panel((0,430), Game().width, 100)
        self.time_label = Label([Game().width//2+200, 440], 1000, text=f"Time: ", font_size=36, color=(255, 255, 255))
        self.power_label = Label([Game().width//2-310, 440], 1000, text=f"Power: {self.power}", font_size=24, color=(200, 0, 0))
        self.sleep_label = Label([Game().width//2-310, 460], 1000, text=f"Sleep: {self.sleep}", font_size=24, color=(200, 0, 0))
        self.lower_panel.add_child(self.power_label)
        self.lower_panel.add_child(self.sleep_label)
        self.lower_panel.add_child(self.time_label)

        def _sleep():
            self.asleep = True
            self.sleep_timer = 0
            print("Sleeping...")

        self.sleep_button = Button((Game().width//2, 440), 100, 50, "Sleep", font_size=24, on_click_callback=_sleep)

        self.next_cam_button = Button((Game().width//2-55, 440), 50, 50, "<", font_size=24, on_click_callback=lambda: print("Not yet implemented!"))
        self.previous_cam_button = Button((Game().width//2+55, 440), 50, 50, ">", font_size=24, on_click_callback=lambda: print("Not yet implemented!"))

        self.touch_jack_button = Button((Game().width//2, 440), 100, 50, "Touch Jack", font_size=24, on_click_callback=lambda: print("Not yet implemented!"))

        self.lower_panel.add_child(self.sleep_button)
        self.lower_panel.add_child(self.next_cam_button)
        self.lower_panel.add_child(self.previous_cam_button)
        self.lower_panel.add_child(self.touch_jack_button)

        self.look_left_button.visible = False
        self.ui_manager.add_element(self.look_left_button)
        self.ui_manager.add_element(self.look_right_button)
        self.ui_manager.add_element(FPSCounter())
        self.ui_manager.add_element(self.lower_panel)

    def on_exit(self):
        pygame.mixer.music.stop()
        return super().on_exit()
    
    def update(self, delta_time):
        # Update camera position based on the current position
        self.get_actor("camera").transform.position = self.positions[self.position]

        # Show or hide camera buttons based on position
        self.look_left_button.set_active(self.position > 0 and not self.asleep)
        self.look_right_button.set_active(self.position < 2 and not self.asleep)

        self.sleep_button.set_active(self.position == 0 and not self.asleep)
        self.next_cam_button.set_active(self.position == 1 and not self.asleep)
        self.previous_cam_button.set_active(self.position == 1 and not self.asleep)
        self.touch_jack_button.set_active(self.position == 2 and not self.asleep)


        if self.monitor_on:
            self.power -= delta_time * self.power_drain_rate

        if self.asleep:
            self.sleep_timer += delta_time
            if self.sleep_timer >= self.sleep_timer_max:
                self.asleep = False
                self.sleep_timer = 0
                self.sleep = 100
        else:
            self.sleep -= delta_time * self.sleep_drain_rate

        self.sleep = max(0, self.sleep)
        self.power = max(0, self.power)

        self.time += delta_time
        time = (self.time // 60)
        if time <= 0:
            time = 12
        self.time_label.text = f"{int(time)} AM"
        self.power_label.text = f"Power: {math.ceil(self.power)}%"
        self.sleep_label.text = f"Sleep: {math.ceil(self.sleep)}%"

        super().update(delta_time)

    def look_left(self):
        self.position = max(0, self.position - 1)
        AssetManager().getSound("woosh").play()

    def look_right(self):
        self.position = min(2, self.position + 1)
        AssetManager().getSound("woosh").play()
