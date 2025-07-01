from engine import *
import pymunk
import pygame
from ballSpawnerComponent import BallSpawnerComponent


def main():
    game = Game(800, 600, "Wicked Wizard Washdown")
    game.assetManager.setDefaultFont("alagard.ttf", 24)
    Logger.debug("Initializing game engine...")
    scene = Scene()
    game.addScene("test", scene)
    game.loadScene("test")

    # Add static boundaries (walls, floor, ceiling)
    width, height = 800, 600
    thickness = 1
    static_lines = [
        pymunk.Segment(scene.physicsSpace.static_body, (0, thickness), (width, thickness), thickness),  # ceiling
        pymunk.Segment(scene.physicsSpace.static_body, (0, height-thickness), (width, height-thickness), thickness),  # floor
        pymunk.Segment(scene.physicsSpace.static_body, (thickness, 0), (thickness, height), thickness),  # left wall
        pymunk.Segment(scene.physicsSpace.static_body, (width-thickness, 0), (width-thickness, height), thickness),  # right wall
    ]
    for line in static_lines:
        line.elasticity = 0.8
        line.friction = 0.5
    scene.physicsSpace.add(*static_lines)

    # Store balls for debug info
    balls = []

    # UI widgets (FPS and debug info)
    fps_widget = FPSDisplay(x=10, y=10, width=100, height=30)
    debug_widget = DebugInfo(scene, balls, x=10, y=40, width=300, height=60)
    scene.uiManager.addWidget(fps_widget)
    scene.uiManager.addWidget(debug_widget)

    # Initial ball
    def spawn_ball(pos):
        mass = 1
        radius = 30
        moment = pymunk.moment_for_circle(mass, 0, radius)
        body = pymunk.Body(mass, moment)
        body.position = pos
        shape = pymunk.Circle(body, radius)
        shape.elasticity = 0.8
        shape.friction = 0.5
        actor = Actor("Ball")
        actor.addComponent(PhysicsComponent(body, [shape]))
        actor.addComponent(CircleRendererComponent(radius, (0, 200, 255)))
        scene.addActor(actor)
        balls.append(actor)
    spawn_ball((400, 100))

    # Add BallSpawnerComponent to handle input and debug info
    spawner_actor = Actor("BallSpawner")
    spawner_actor.addComponent(BallSpawnerComponent(scene, debug_widget, balls))
    scene.addActor(spawner_actor)

    game.run()


if __name__ == "__main__":
    main()