import pygame
import pymunk
import random
from engine.actor.actor import Actor
from engine.component.component import Component
from engine.component.builtin.physicsComponent import PhysicsComponent
from engine.component.builtin.circleRendererComponent import CircleRendererComponent
from engine.component.builtin.textComponent import TextComponent

class BallSpawnerComponent(Component):
    def __init__(self, scene, debug_text, balls):
        super().__init__()
        self.scene = scene
        self.debug_text = debug_text
        self.balls = balls
        self.last_mouse_down = False

    def update(self, delta_time):
        mouse_pressed = pygame.mouse.get_pressed()[0]
        if mouse_pressed and not self.last_mouse_down:
            pos = pygame.mouse.get_pos()
            self.spawn_ball(pos)
        self.last_mouse_down = mouse_pressed
        # Update debug info
        fps = int(pygame.time.get_ticks() / 1000)  # fallback if no clock
        try:
            import engine
            fps = int(engine.Game._instance.clock.get_fps())
        except Exception:
            pass
        mouse_pos = pygame.mouse.get_pos()
        self.debug_text.set_text(f"Balls: {len(self.balls)}\nFPS: {fps}\nMouse: {mouse_pos}")

    def spawn_ball(self, pos):
        mass = 1
        radius = 30
        moment = pymunk.moment_for_circle(mass, 0, radius)
        body = pymunk.Body(mass, moment)
        shape = pymunk.Circle(body, radius)
        shape.elasticity = 0.8
        shape.friction = 0.5
        actor = Actor("Ball")
        actor.transform.setPosition(*pos)
        # Random color
        color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        actor.addComponent(PhysicsComponent(body, [shape]))
        actor.addComponent(CircleRendererComponent(radius, color))
        self.scene.addActor(actor)
        self.balls.append(actor)
