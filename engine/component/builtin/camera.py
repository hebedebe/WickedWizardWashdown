from ..component import Component

class CameraComponent(Component):
    def __init__(self):
        super().__init__()

    def lateUpdate(self, delta_time):
        self.getScene.worldOffset = -self.actor.transform.position
        return super().lateUpdate(delta_time)