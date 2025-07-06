#Library imports
import pygame

# Core engine imports
from engine.core.game import Game
from engine.core.asset_manager import AssetManager

# Builtin engine imports
from engine.builtin.shaders import vignette_shader

# Local scene imports
from main_menu import MainMenuScene
from game import GameScene
from nosleep import NoSleepScene
from jumpscare import JumpscareScene
from gameover import GameOverScene

def main(): 
    """Run main"""
    game: Game = Game(640, 480, "Touching Jack 2: The Remake - The Sequel (Complete Edition)")

    AssetManager().autoloadAssets()
    AssetManager().setDefaultFont("vcrosdmono")

    game.add_postprocess_shader(vignette_shader)

    game.add_scene(MainMenuScene())
    game.add_scene(GameScene())
    game.add_scene(NoSleepScene())
    game.add_scene(JumpscareScene())
    game.add_scene(GameOverScene())

    game.load_scene("MainMenu")

    game.run()

if __name__ == "__main__":
    main()
