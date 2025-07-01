from engine import *
from engine.component.builtin.physicsComponent import PhysicsComponent
from engine.component.builtin.circleRendererComponent import CircleRendererComponent
from engine.component.builtin.constraintComponent import DampedSpringComponent
from engine.component.builtin.inputComponent import InputComponent
import pymunk
import pygame

class SpringRendererComponent(Component):
    def __init__(self, get_other_actor, get_spring):
        super().__init__()
        self.get_other_actor = get_other_actor  # function returning the other actor
        self.get_spring = get_spring  # function returning the spring constraint

    def render(self, surface):
        other = self.get_other_actor()
        spring = self.get_spring()
        if not other or not spring:
            return
        pos1 = self.actor.transform.position
        pos2 = other.transform.position
        # Calculate spring stress (stretch/compression)
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        dist = (dx*dx + dy*dy) ** 0.5
        rest_length = spring.constraint.rest_length
        # Stress: 0 = rest, >0 = stretched, <0 = compressed
        stress = dist - rest_length
        # Color: blue (compressed), green (rest), red (stretched)
        if abs(stress) < 2:
            color = (0, 255, 0)
        elif stress > 0:
            # interpolate green to red
            t = min(stress / rest_length, 1)
            color = (int(0 + 255 * t), int(255 * (1-t)), 0)
        else:
            # interpolate green to blue
            t = min(-stress / rest_length, 1)
            color = (0, int(255 * (1-t)), int(255 * t))
        pygame.draw.line(surface, color, pos1, pos2, 4)

def create_spring_chain(scene, num_actors=5, start_pos=(200, 300), spacing=60):
    actors = []
    springs = []
    for i in range(num_actors):
        actor = Actor(f"SpringBall_{i}")
        x = start_pos[0] + i * spacing
        y = start_pos[1]
        actor.transform.setPosition(x, y)
        # Physics body
        body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 20))
        body.position = (x, y)
        shape = pymunk.Circle(body, 20)
        shape.elasticity = 0.8
        shape.friction = 0.5
        actor.addComponent(PhysicsComponent(body, [shape]))
        # Visual
        actor.addComponent(CircleRendererComponent(20, (100, 200, 255)))
        # Make every ball draggable
        actor.addComponent(DragComponent())
        actors.append(actor)
        scene.addActor(actor)
    # Chain with damped springs and add spring renderers
    for i in range(1, num_actors):
        a1 = actors[i-1]
        a2 = actors[i]
        spring = DampedSpringComponent(
            a1, a2,
            anchor_a=(0,0), anchor_b=(0,0),
            rest_length=spacing, stiffness=300, damping=20
        )
        a2.addComponent(spring)
        springs.append(spring)
        # Add a renderer to a2 to draw the spring from a1 to a2
        a2.addComponent(SpringRendererComponent(
            get_other_actor=lambda a1=a1: a1,
            get_spring=lambda spring=spring: spring
        ))
    return actors

class DragComponent(InputComponent):
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

def add_screen_bounds(scene, width, height, thickness=10):
    static_body = scene.physicsSpace.static_body
    edges = [
        # left
        pymunk.Segment(static_body, (0, 0), (0, height), thickness),
        # right
        pymunk.Segment(static_body, (width, 0), (width, height), thickness),
        # top
        pymunk.Segment(static_body, (0, 0), (width, 0), thickness),
        # bottom
        pymunk.Segment(static_body, (0, height), (width, height), thickness),
    ]
    for edge in edges:
        edge.elasticity = 0.8
        edge.friction = 0.5
    scene.physicsSpace.add(*edges)

def main():
    game = Game(800, 600, "Wicked Wizard Washdown")

    Logger.debug("Initializing game engine...")

    scene = Scene()
    game.addScene("test", scene)
    game.loadScene("test")

    # Add screen edge colliders
    add_screen_bounds(scene, 800, 600)

    # --- Damped Spring Chain Demo ---
    chain = create_spring_chain(scene, num_actors=15, start_pos=(100, 300), spacing=30)
    # Make the first ball draggable
    dragger = DragComponent()
    chain[0].addComponent(dragger)

    game.run()


if __name__ == "__main__":
    main()