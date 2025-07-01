import pygame
import pymunk

from ..component import Component
from engine.logger import Logger

class PhysicsComponent(Component):
    def __init__(self, body, shapes):
        super().__init__()
        self.body = body
        self.shapes = [*shapes]

    def start(self):
        from ... import Game
        Game._instance.currentScene.addPhysics(self.actor)
        self.body.position = (*self.actor.transform.position,)
        self.body.rotation = self.actor.transform.rotation
        return super().start()

    def update(self, delta_time):
        self.body.position = (*self.actor.transform.position,)
        self.body.rotation = self.actor.transform.rotation
        return super().update(delta_time)
    
    def lateUpdate(self, delta_time):
        self.actor.transform.setPosition(self.body.position.x, self.body.position.y)
        self.actor.transform.setRotation(self.body.angle)
        return super().lateUpdate(delta_time)