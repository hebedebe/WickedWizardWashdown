"""
Wicked Wizard Washdown - Main Entry Point
A 2D game engine demonstration.
"""

from engine import *

class DrawCircleComponent(Component):
    def __init__(self, radius=50, color=(255, 0, 0)):
        super().__init__()
        self.radius = radius
        self.color = color

    def render(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.actor.transform.position.x), int(self.actor.transform.position.y)), self.radius)

class UpdateCircleComponent(Component):
    def __init__(self, amplitude=100):
        super().__init__()
        self.amplitude = amplitude

    def start(self):
        self.targetComponent = self.actor.getComponent(DrawCircleComponent)

    def update(self, dt):
        self.actor.transform.position.x = self.amplitude * sin(time.time() * 2) + 400
        self.targetComponent.radius = self.amplitude * (cos(time.time() * 2) + 1) + 50

def main():
    print("Starting Wicked Wizard Washdown...")
    
    game = Game(800, 600, "Wicked Wizard Washdown")

    testScene = Scene()
    game.addScene("test", testScene)
    game.loadScene("test")

    testActor = Actor("TestActor")
    testActor.transform.setPosition(400, 300)
    testActor.addComponent(DrawCircleComponent(radius=100, color=(0, 255, 0)))
    testActor.addComponent(UpdateCircleComponent(amplitude=100))
    testScene.addActor(testActor)

    testScene.uiManager.addWidget(FPSDisplay())

    print("Testing serialization:")
    print(testActor.serialize())

    print("testing creating a new actor with serialized data")
    serialized_data = testActor.serialize()
    newActor = Actor.createFromSerializedData(serialized_data)
    print("New Actor Serialized Data:")
    print(newActor.serialize())
    newActor.getComponent(DrawCircleComponent).color = (255, 0, 255)  # Change color to magenta
    testScene.addActor(newActor)

    game.run()


if __name__ == "__main__":
    main()