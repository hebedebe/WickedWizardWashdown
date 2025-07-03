from engine import *
from engine.actor import Actor

import pygame

from ragdollComponent import RagdollPlayerComponent

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

    # player = Actor("Player")
    # player.addComponent(CircleRendererComponent(color=(255, 255, 255)))
    # player.addComponent(PhysicsCircleComponent(bodyType=pymunk.Body.DYNAMIC, mass=10))
    # player.addComponent(CameraComponent())
    # player.addComponent(PhysicsDragComponent(10000))
    # scene.addActor(player)

    camera = Actor("Camera")
    camera.addComponent(CameraComponent())
    # camera.addComponent(BasicMovementComponent(1000))
    camera.addComponent(RagdollPlayerComponent())
    scene.addActor(camera)

    spritesheet = game.assetManager.loadImage("testanim")
    frames = game.assetManager.sliceSpritesheet("testanim", 16, 16)
    animationActor = Actor("test")
    animationActor.transform.position = pygame.Vector2(100, 100)
    animationActor.addComponent(AnimationComponent(frames))
    scene.addActor(animationActor)

    game.run()

if __name__ == "__main__":
    main()