from engine import *
from engine.actor import Actor

import pygame

def main():
    game = Game(1280, 720)

    scene = Scene()
    game.addScene("main", scene)
    game.loadScene("main")

    game.run()

if __name__ == "__main__":
    main()