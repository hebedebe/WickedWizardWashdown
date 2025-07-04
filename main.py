from engine.core.game import Game
from engine.builtin.shaders import greyscale_shader


def main():
    """Run main"""
    game = Game(1280, 720)

    game.add_postprocess_shader(greyscale_shader.get())

    game.run()

if __name__ == "__main__":
    main()
