import pygame
from engine.builtin.components.camera_component import CameraComponent
from engine.builtin.components.sprite_component import SpriteComponent
from engine.core.game import Game
from engine.core.scene import Scene
from engine.core.world.actor import Actor
from engine.core.world.component import Component

def clamp(value, min_value, max_value):
    """Clamp a value between min_value and max_value."""
    return max(min_value, min(value, max_value))

class PanoramaCameraControllerComponent(Component):
    def __init__(self, speed=600, margin_distance=50):
        super().__init__()
        self.speed = speed
        self.margin_distance = margin_distance
        self.max_left = -Game().width
        self.max_right = Game().width

    def update(self, delta_time):
        """Update the camera position based on user input."""
        mousepos = pygame.mouse.get_pos()
        dir = 0
        if mousepos[0] < self.margin_distance:
            dir = -1
        if mousepos[0] > Game().width - self.margin_distance:
            dir = 1
        
        self.actor.transform.position.x = clamp(self.actor.transform.position.x + dir * self.speed * delta_time, self.max_left, self.max_right)

class PanoScene(Scene):
    def __init__(self):
        super().__init__("Pano Scene")

    def on_enter(self):
        background_actor = Actor("Background")
        background_actor.add_component(SpriteComponent("test_panorama"))
        self.add_actor(background_actor)

        camera_actor = Actor("Camera")
        camera_actor.add_component(CameraComponent())
        camera_actor.add_component(PanoramaCameraControllerComponent())
        self.add_actor(camera_actor)