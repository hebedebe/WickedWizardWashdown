"""
Wicked Wizard Washdown - Main Entry Point
A 2D game engine demonstration.
"""

from engine import *

def main():
    print("Starting Wicked Wizard Washdown...")
    
    game = Game(800, 600, "Wicked Wizard Washdown")

    game.run()


if __name__ == "__main__":
    main()