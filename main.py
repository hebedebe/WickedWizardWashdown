#Library imports
import pygame

# Core engine imports
from engine.core.game import Game
from engine.core.asset_manager import AssetManager
from test_pano_scene import PanoScene

def main(): 
    """Run main"""
    game: Game = Game()

    AssetManager().autoloadAssets()

    game.add_scene(PanoScene())
    game.load_scene("Pano Scene")

    game.run()

if __name__ == "__main__":
    main()
