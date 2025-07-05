from engine.core.game import Game
from engine.core.scene import Scene

from engine.core.world.actor import Actor

from engine.builtin.components.circle_renderer_component import CircleRendererComponent
from engine.builtin.components.camera_component import CameraComponent
from engine.builtin.components.basic_movement_component import BasicMovementComponent

from engine.builtin.shaders import greyscale_shader


def main(): 
    """Run main"""
    game: Game = Game(1280, 720)
    # game.init()  # Initialize the default shader

    # game.add_postprocess_shader(greyscale_shader)

    test_scene = Scene("Test Scene")
    test_scene.add_actor(Actor(components=[CircleRendererComponent(radius=50, color=(255, 0, 0, 255)), CameraComponent(interpolate=True), BasicMovementComponent(1000)]))
    test_scene.add_actor(Actor(components=[CircleRendererComponent(radius=40, color=(0, 255, 0, 255))]))
    game.add_scene(test_scene)
    game.set_current_scene("Test Scene")

    game.run()

if __name__ == "__main__":
    main()
