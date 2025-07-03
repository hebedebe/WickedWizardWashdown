# This component creates a simple 2D human-shaped active ragdoll player controller
# Requires Pymunk and your engine's Component system

import pymunk
from engine import *

class RagdollPlayerComponent(Component):
    def __init__(self, position=(300, 300)):
        super().__init__()
        self.space = self.getScene.physicsSpace
        self.position = position
        self.balance_strength = 5000
        self.move_strength = 10000
        self.joints = []
        self.motors = []
        self.parts = {}
        self.create_ragdoll()

    def create_segment(self, name, offset, size, mass=1):
        body = pymunk.Body(mass, pymunk.moment_for_box(mass, size))
        body.position = self.position[0] + offset[0], self.position[1] + offset[1]
        shape = pymunk.Poly.create_box(body, size)
        shape.friction = 1.0
        self.space.add(body, shape)
        self.parts[name] = body
        return body

    def create_ragdoll(self):
        torso = self.create_segment("torso", (0, 0), (20, 60))
        head = self.create_segment("head", (0, -50), (20, 20))
        upper_arm_r = self.create_segment("upper_arm_r", (25, -20), (10, 30))
        lower_arm_r = self.create_segment("lower_arm_r", (25, 10), (10, 30))
        upper_arm_l = self.create_segment("upper_arm_l", (-25, -20), (10, 30))
        lower_arm_l = self.create_segment("lower_arm_l", (-25, 10), (10, 30))
        upper_leg_r = self.create_segment("upper_leg_r", (10, 50), (15, 35))
        lower_leg_r = self.create_segment("lower_leg_r", (10, 90), (15, 35))
        upper_leg_l = self.create_segment("upper_leg_l", (-10, 50), (15, 35))
        lower_leg_l = self.create_segment("lower_leg_l", (-10, 90), (15, 35))

        def add_joint(a, b, anchor_a, anchor_b, limits=(-0.5, 0.5)):
            joint = pymunk.PinJoint(a, b, anchor_a, anchor_b)
            limit = pymunk.RotaryLimitJoint(a, b, *limits)
            self.space.add(joint, limit)
            self.joints.append((joint, limit))

        # Joints
        add_joint(torso, head, (0, -30), (0, 10), (-0.2, 0.2))
        add_joint(torso, upper_arm_r, (10, -20), (0, -15), (-1.5, 1.5))
        add_joint(upper_arm_r, lower_arm_r, (0, 15), (0, -15), (-1.5, 0))
        add_joint(torso, upper_arm_l, (-10, -20), (0, -15), (-1.5, 1.5))
        add_joint(upper_arm_l, lower_arm_l, (0, 15), (0, -15), (-1.5, 0))
        add_joint(torso, upper_leg_r, (5, 30), (0, -17), (-1, 1))
        add_joint(upper_leg_r, lower_leg_r, (0, 17), (0, -17), (-1, 0))
        add_joint(torso, upper_leg_l, (-5, 30), (0, -17), (-1, 1))
        add_joint(upper_leg_l, lower_leg_l, (0, 17), (0, -17), (-1, 0))

    def apply_torque_to_joint(self, body_a, body_b, target_angle, strength):
        current_angle = body_b.angle - body_a.angle
        delta = (target_angle - current_angle + 3.14) % (2 * 3.14) - 3.14  # Normalize angle
        torque = delta * strength
        body_b.torque += torque
        body_a.torque -= torque

    def update(self, delta_time):
        keys = self.actor.scene.engine.input.keys

        # Basic input-based pose
        move_right = keys.get("d", False)
        move_left = keys.get("a", False)
        raise_arms = keys.get("w", False)

        # Torso balance
        self.apply_torque_to_joint(self.parts["torso"], self.parts["head"], 0, self.balance_strength)

        if raise_arms:
            self.apply_torque_to_joint(self.parts["torso"], self.parts["upper_arm_r"], -1.0, self.move_strength)
            self.apply_torque_to_joint(self.parts["torso"], self.parts["upper_arm_l"], 1.0, self.move_strength)
        else:
            self.apply_torque_to_joint(self.parts["torso"], self.parts["upper_arm_r"], 0.0, self.move_strength)
            self.apply_torque_to_joint(self.parts["torso"], self.parts["upper_arm_l"], 0.0, self.move_strength)

        if move_right:
            self.apply_torque_to_joint(self.parts["torso"], self.parts["upper_leg_r"], 0.5, self.move_strength)
            self.apply_torque_to_joint(self.parts["torso"], self.parts["upper_leg_l"], -0.5, self.move_strength)
        elif move_left:
            self.apply_torque_to_joint(self.parts["torso"], self.parts["upper_leg_r"], -0.5, self.move_strength)
            self.apply_torque_to_joint(self.parts["torso"], self.parts["upper_leg_l"], 0.5, self.move_strength)
        else:
            self.apply_torque_to_joint(self.parts["torso"], self.parts["upper_leg_r"], 0.0, self.move_strength)
            self.apply_torque_to_joint(self.parts["torso"], self.parts["upper_leg_l"], 0.0, self.move_strength)

        # Keep knees and elbows bent slightly
        self.apply_torque_to_joint(self.parts["upper_leg_r"], self.parts["lower_leg_r"], -0.5, self.move_strength)
        self.apply_torque_to_joint(self.parts["upper_leg_l"], self.parts["lower_leg_l"], -0.5, self.move_strength)
        self.apply_torque_to_joint(self.parts["upper_arm_r"], self.parts["lower_arm_r"], -0.5, self.move_strength)
        self.apply_torque_to_joint(self.parts["upper_arm_l"], self.parts["lower_arm_l"], -0.5, self.move_strength)

