from engine import *
from engine.component.builtin.physicsComponent import PhysicsComponent
from engine.component.builtin.circleRendererComponent import CircleRendererComponent
from engine.component.builtin.constraintComponent import DampedSpringComponent
from engine.component.builtin.inputComponent import InputComponent
import pymunk
import pygame
import math

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
            self.mouse_joint.max_force = abs(2000*(pygame.Vector2.distance_to(pygame.Vector2(mouse_pos), pygame.Vector2(self.actor.transform.position))))

def add_screen_bounds(scene, width, height, thickness=100):
    static_body = scene.physicsSpace.static_body
    edges = [
        # left
        pymunk.Segment(static_body, (0-thickness, 0-thickness), (0-thickness, height+thickness), thickness),
        # right
        pymunk.Segment(static_body, (width+thickness, 0-thickness), (width+thickness, height+thickness), thickness),
        # top
        pymunk.Segment(static_body, (0-thickness, 0-thickness), (width+thickness, 0-thickness), thickness),
        # bottom
        pymunk.Segment(static_body, (0-thickness, height+thickness), (width+thickness, height+thickness), thickness),
    ]
    for edge in edges:
        edge.elasticity = 0.1
        edge.friction = 0
    scene.physicsSpace.add(*edges)

class SoftbodyControlComponent(InputComponent):
    def __init__(self, force_strength=500000):
        super().__init__()
        self.force_strength = force_strength

    def update(self, dt):
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT]:
            direction.x -= 1
        if keys[pygame.K_RIGHT]:
            direction.x += 1
        if keys[pygame.K_UP]:
            direction.y -= 1
        if keys[pygame.K_DOWN]:
            direction.y += 1

        if direction.length_squared() > 0:
            direction = direction.normalize()
            phys = self.actor.getComponent(PhysicsComponent)
            if phys:
                phys.body.apply_force_at_world_point(tuple((direction * self.force_strength) * dt), (0, 0))


def create_softbody_circle(scene, num_points=12, center=(500, 400), radius=100):
    actors = []
    springs = []
    angle_step = 2 * math.pi / num_points

        # --- Central anchor particle ---
    center_actor = Actor("SoftBody_Center")
    center_actor.transform.setPosition(*center)
    center_body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 5))
    center_body.position = center
    center_shape = pymunk.Circle(center_body, 5)
    center_shape.sensor = True  # Optional: remove collision

    center_actor.addComponent(PhysicsComponent(center_body, [center_shape]))
    center_actor.addComponent(SoftbodyControlComponent())
    center_actor.addComponent(CircleRendererComponent(5, (255, 255, 0)))  # visible core
    scene.addActor(center_actor)


    # --- Outer particles ---
    for i in range(num_points):
        angle = i * angle_step
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        actor = Actor(f"SoftPoint_{i}")
        actor.transform.setPosition(x, y)

        body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 10))
        body.position = (x, y)
        shape = pymunk.Circle(body, 10)
        shape.elasticity = 0.8
        shape.friction = 0.5

        actor.addComponent(PhysicsComponent(body, [shape]))
        actor.addComponent(CircleRendererComponent(10, (200, 100, 255)))
        actor.addComponent(DragComponent())
        actor.addComponent(SoftbodyControlComponent())


        scene.addActor(actor)
        actors.append(actor)

    # --- Perimeter springs (loop) ---
    for i in range(num_points):
        a1 = actors[i]
        a2 = actors[(i + 1) % num_points]
        rest = (a1.transform.position - a2.transform.position).length()
        spring = DampedSpringComponent(a1, a2, (0, 0), (0, 0), rest_length=rest, stiffness=3000, damping=1)
        a2.addComponent(spring)
        a2.addComponent(SpringRendererComponent(lambda a1=a1: a1, lambda spring=spring: spring))
        springs.append(spring)

    # --- Cross-link springs (chords) ---
    for i in range(num_points):
        a1 = actors[i]
        for j in range(i + 2, i + num_points - 1):
            # Skip adjacent and opposite (avoid clutter)
            a2 = actors[j % num_points]
            rest = (a1.transform.position - a2.transform.position).length()
            spring = DampedSpringComponent(a1, a2, (0, 0), (0, 0), rest_length=rest, stiffness=50, damping=1)
            a2.addComponent(spring)
            springs.append(spring)

    # --- Radial springs to center ---
    for actor in actors:
        rest = (actor.transform.position - center_actor.transform.position).length()
        spring = DampedSpringComponent(actor, center_actor, (0, 0), (0, 0), rest_length=rest, stiffness=10, damping=1)
        actor.addComponent(spring)
        actor.addComponent(SpringRendererComponent(lambda a1=center_actor: a1, lambda spring=spring: spring))
        springs.append(spring)

    return actors

def add_static_box(scene, pos, size, name="StaticBox"):
    actor = Actor(name)
    actor.transform.setPosition(*pos)

    body = scene.physicsSpace.static_body
    x, y = pos
    w, h = size[0] / 2, size[1] / 2
    shape = pymunk.Poly.create_box(body, size)
    shape.elasticity = 0.4
    shape.friction = 0.8

    scene.physicsSpace.add(shape)

    # For visual feedback only (optional)
    class BoxRenderer(Component):
        def render(self, surface):
            rect = pygame.Rect(x - w, y - h, size[0], size[1])
            pygame.draw.rect(surface, (100, 255, 100), rect, 0)

    actor.addComponent(BoxRenderer())
    scene.addActor(actor)

def add_dynamic_box(scene, pos, size=(60, 60), name="Box"):
    actor = Actor(name)
    actor.transform.setPosition(*pos)

    mass = 3
    moment = pymunk.moment_for_box(mass, size)
    body = pymunk.Body(mass, moment)
    body.position = pos
    shape = pymunk.Poly.create_box(body, size)
    shape.elasticity = 0.4
    shape.friction = 0.8

    actor.addComponent(PhysicsComponent(body, [shape]))
    actor.addComponent(CircleRendererComponent(min(size)//2, (200, 200, 100)))  # crude circle to represent box
    scene.addActor(actor)


def main():
    game = Game(1920, 1080, "Wicked Wizard Washdown")
    pygame.display.toggle_fullscreen()

    Logger.debug("Initializing game engine...")

    scene = Scene()
    # scene.physicsSpace.gravity = (0, 0)
    game.addScene("test", scene)
    game.loadScene("test")

    # Add screen edge colliders
    add_screen_bounds(scene, game.width, game.height, 10000)

    # --- Damped Spring Chain Demo ---
    # chain = create_spring_chain(scene, num_actors=15, start_pos=(100, 300), spacing=30)
    softbody = create_softbody_circle(scene, num_points=40, center=(960, 540), radius=150)

    # Add a dynamic pushable box
    add_dynamic_box(scene, (960, 500))
    add_dynamic_box(scene, (960, 500))
    add_dynamic_box(scene, (960, 500))
    add_dynamic_box(scene, (960, 500))
    add_dynamic_box(scene, (960, 500))

    # Make the first ball draggable
    dragger = DragComponent()
    softbody[0].addComponent(dragger)

    scene.uiManager.addWidget(FPSDisplay())

    game.run()


if __name__ == "__main__":
    main()