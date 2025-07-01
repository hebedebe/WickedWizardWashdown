import pymunk
from engine.component.component import Component
from engine.component.builtin.physicsComponent import PhysicsComponent

class ConstraintComponent(Component):
    def __init__(self, actor_a, actor_b, constraint):
        super().__init__()
        self.actor_a = actor_a
        self.actor_b = actor_b
        self.constraint = constraint
        self._enabled = True

    def start(self, actor):
        # Add the constraint to the scene's physics space
        scene = actor.scene
        if scene and hasattr(scene, 'physicsSpace') and self._enabled:
            scene.physicsSpace.add(self.constraint)

    def onRemoved(self, actor):
        scene = actor.scene
        if scene and hasattr(scene, 'physicsSpace'):
            if self.constraint in scene.physicsSpace.constraints:
                scene.physicsSpace.remove(self.constraint)

    def onEnabled(self, actor):
        self._enabled = True
        scene = actor.scene
        if scene and hasattr(scene, 'physicsSpace'):
            if self.constraint not in scene.physicsSpace.constraints:
                scene.physicsSpace.add(self.constraint)

    def onDisabled(self, actor):
        self._enabled = False
        scene = actor.scene
        if scene and hasattr(scene, 'physicsSpace'):
            if self.constraint in scene.physicsSpace.constraints:
                scene.physicsSpace.remove(self.constraint)

class PinJointComponent(ConstraintComponent):
    def __init__(self, actor_a, actor_b, anchor_a=(0,0), anchor_b=(0,0)):
        body_a = actor_a.getComponent(PhysicsComponent).body
        body_b = actor_b.getComponent(PhysicsComponent).body
        constraint = pymunk.PinJoint(body_a, body_b, anchor_a, anchor_b)
        super().__init__(actor_a, actor_b, constraint)

class PivotJointComponent(ConstraintComponent):
    def __init__(self, actor_a, actor_b, pivot):
        body_a = actor_a.getComponent(PhysicsComponent).body
        body_b = actor_b.getComponent(PhysicsComponent).body
        constraint = pymunk.PivotJoint(body_a, body_b, pivot)
        super().__init__(actor_a, actor_b, constraint)

class DampedSpringComponent(ConstraintComponent):
    def __init__(self, actor_a, actor_b, anchor_a, anchor_b, rest_length, stiffness, damping):
        body_a = actor_a.getComponent(PhysicsComponent).body
        body_b = actor_b.getComponent(PhysicsComponent).body
        constraint = pymunk.DampedSpring(body_a, body_b, anchor_a, anchor_b, rest_length, stiffness, damping)
        super().__init__(actor_a, actor_b, constraint)
