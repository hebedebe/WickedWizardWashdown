from pygame import Vector2

class Transform:
    """
    Transform handles the position, rotation, and scale of an actor.
    It allows for transformations in 2D or 3D space.
    """
    
    def __init__(self):
        self.position = Vector2(0.0, 0.0)  # x, y position in 2D space
        self.rotation = 0
        self.scale = Vector2(1.0, 1.0)  # scale factors for x, y in 2D space

    def setPosition(self, x: float, y: float) -> None:
        """Set the position of the actor."""
        self.position = Vector2(x, y)

    def setRotation(self, angle: float) -> None:
        """Set the rotation of the actor."""
        self.rotation = angle

    def setScale(self, x: float, y: float) -> None:
        """Set the scale of the actor."""
        self.scale = Vector2(x, y)

    def serialize(self) -> dict:
        """Serialize the transform data to a dictionary."""
        return {
            "position": [self.position.x, self.position.y],
            "rotation": self.rotation,
            "scale": [self.scale.x, self.scale.y]
        }
    
    def deserialize(self, data: dict) -> None:
        """Deserialize the transform data from a dictionary."""
        self.position = Vector2(*data["position"])
        self.rotation = data["rotation"]
        self.scale = Vector2(*data["scale"])