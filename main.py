import pygame

from engine import *
from engine.actor import Actor


def main():
    """Run main"""
    game = Game(1280, 720)

    scene = Scene()
    game.addScene("main", scene)
    game.loadScene("main")

    scene.addActor(Actor(components=[CircleRendererComponent()]))
    scene.addActor(Actor(components=[CircleRendererComponent(color=(255,0,0)),BasicMovementComponent(speed=1000),CameraComponent(interpolate=True)]))

    game.run()

if __name__ == "__main__":
    main()
