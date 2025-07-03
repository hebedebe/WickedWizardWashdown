from engine import *

def main():
    game = Game(1280, 720)

    scene = Scene()
    game.addScene("main", scene)
    game.loadScene("main")

    radius = 10

    actors: List[Actor] = []
    for i in range(30):
        actors.append(Actor(components=[CircleRendererComponent(color=(0, 0, 255), radius=radius),]))
        actors[i].transform.setPosition(600, 25 + (i+2) * radius)

    scene.addActors(*actors)
    lastactor = Actor(components=[CircleRendererComponent(color=(255, 0, 0), radius=radius),])
    lastactor.addComponent(PhysicsCircleComponent(radius=radius, bodyType=pymunk.Body.STATIC))
    lastactor.transform.setPosition(600, 25)
    scene.addActor(lastactor)

    for actor in actors:
        actor.addComponent(PhysicsCircleComponent(radius=radius, bodyType=pymunk.Body.DYNAMIC))
        actor.addComponent(DampedSpringComponent(actor, lastactor, rest_length=radius+5, stiffness=4000, damping=100))
        actor.addComponent(SpringRendererComponent(lastactor))
        actor.addComponent(PhysicsDragComponent(1000))
        lastactor = actor

    scene.addWidget(FPSDisplay())


    game.run()

if __name__ == "__main__":
    main()