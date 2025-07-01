import pygame
import pymunk

from ..component import Component
from engine.logger import Logger

class PhysicsComponent(Component):
    def __init__(self, body, shapes):
        super().__init__()
        self.body = body
        self.shapes = [*shapes]

    def update(self, delta_time):
        self.body.position = (*self.actor.transform.position,)
        return super().update(delta_time)
    
    def lateUpdate(self, delta_time):
        self.actor.transform.setPosition(self.body.position.x, self.body.position.y)
        return super().lateUpdate(delta_time)