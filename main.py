from engine.core.game import Game
from engine.core.scene import Scene

from engine.core.world.actor import Actor

from engine.builtin.components.circle_renderer_component import CircleRendererComponent
from engine.builtin.components.camera_component import CameraComponent
from engine.builtin.components.basic_movement_component import BasicMovementComponent
from engine.builtin.components.sprite_component import SpriteComponent
from engine.builtin.ui.button_widget import Button 

from engine.builtin.shaders import greyscale_shader, posterize_shader

from engine.core.asset_manager import AssetManager


def main(): 
    """Run main"""
    game: Game = Game(1280, 720)
    
    AssetManager().loadImage("colour_test")

    test_scene = Scene("Test Scene")
    test_scene.add_actor(Actor(components=[CircleRendererComponent(radius=50, color=(255, 0, 0, 255)), CameraComponent(interpolate=True), BasicMovementComponent(1000)]))
    test_scene.add_actor(Actor(components=[SpriteComponent(sprite_name="colour_test")]))
    game.add_scene(test_scene)
    game.set_current_scene("Test Scene")

    test_scene.ui_manager.add_element(Button(100, 100, 120, 25, "greyscale on", on_click_callback=lambda: game.add_postprocess_shader(greyscale_shader)))
    test_scene.ui_manager.add_element(Button(100, 130, 120, 25, "greyscale off", on_click_callback=lambda: game.remove_postprocess_shader(greyscale_shader)))

    test_scene.ui_manager.add_element(Button(100, 180, 120, 25, "posterize on", on_click_callback=lambda: game.add_postprocess_shader(posterize_shader)))
    test_scene.ui_manager.add_element(Button(100, 210, 120, 25, "posterize off", on_click_callback=lambda: game.remove_postprocess_shader(posterize_shader)))

    game.run()

if __name__ == "__main__":
    main()
