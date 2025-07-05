from engine.core.game import Game
from engine.core.scene import Scene

from engine.core.world.actor import Actor

from engine.builtin.components.circle_renderer_component import CircleRendererComponent
from engine.builtin.components.camera_component import CameraComponent
from engine.builtin.components.basic_movement_component import BasicMovementComponent
from engine.builtin.components.sprite_component import SpriteComponent

from engine.builtin.ui.button import Button 
from engine.builtin.ui.fps_counter import FPSCounter

from engine.builtin.shaders import greyscale_shader, posterize_shader, invert_shader, blur_shader, sepia_shader, bloom_shader, chromatic_aberration_shader, vignette_shader

from engine.core.asset_manager import AssetManager


def main(): 
    """Run main"""
    game: Game = Game(1280, 720)
    
    AssetManager().loadImage("colour_test")

    test_scene = Scene("Test Scene")
    test_scene.add_actor(Actor(components=[
        CircleRendererComponent(radius=50, color=(255, 255, 255, 255)), 
        CameraComponent(interpolate=True), 
        BasicMovementComponent(1000)
    ]))
    game.add_scene(test_scene)
    game.load_scene("Test Scene")

    test_scene.ui_manager.add_element(FPSCounter())

    game.run()

if __name__ == "__main__":
    main()
