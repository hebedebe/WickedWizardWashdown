#Library imports
import pygame

# Core engine imports
from engine.core.game import Game
from engine.core.asset_manager import AssetManager

def main(): 
    """Run main"""
    game: Game = Game(640, 480, "Touching Jack 2: The Remake - The Sequel (Complete Edition)")

    AssetManager().autoloadAssets()

    game.run()

if __name__ == "__main__":
    main()
