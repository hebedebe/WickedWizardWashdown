import pygame
from .physicsComponent import PhysicsComponent
from .inputComponent import InputComponent
import pymunk

class PhysicsDragComponent(InputComponent):
    def __init__(self):
        super().__init__()
        self.dragging = False
        self.mouse_joint = None
        self.mouse_body = None

    def start(self):
        self.bind_mouse(1, self.on_mouse_down, on_press=True)
        self.bind_mouse(1, self.on_mouse_up, on_press=False, on_release=True)

    def on_mouse_down(self):
        mouse_pos = pygame.mouse.get_pos()
        actor_pos = self.actor.transform.position
        dx = mouse_pos[0] - actor_pos[0]
        dy = mouse_pos[1] - actor_pos[1]
        if dx*dx + dy*dy < 400:  # within 20px
            self.dragging = True
            # Create a kinematic body at the mouse position
            self.mouse_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
            self.mouse_body.position = mouse_pos
            # Create a pivot joint between mouse and actor
            phys = self.actor.getComponent(PhysicsComponent)
            if phys:
                self.mouse_joint = pymunk.PivotJoint(self.mouse_body, phys.body, (0,0), (0,0))
                self.mouse_joint.max_force = 10000
                self.actor.scene.physicsSpace.add(self.mouse_body, self.mouse_joint)

    def on_mouse_up(self):
        self.dragging = False
        if self.mouse_joint:
            self.actor.scene.physicsSpace.remove(self.mouse_joint)
            self.mouse_joint = None
        if self.mouse_body:
            self.actor.scene.physicsSpace.remove(self.mouse_body)
            self.mouse_body = None

    def update(self, delta_time):
        if self.dragging and self.mouse_body:
            mouse_pos = pygame.mouse.get_pos()
            self.mouse_body.position = mouse_pos
            self.mouse_joint.max_force = abs(2000*(pygame.Vector2.distance_to(pygame.Vector2(mouse_pos), pygame.Vector2(self.actor.transform.position))))