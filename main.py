from engine import *

def main():
    game = Game(800, 600, "Wicked Wizard Washdown")

    scene = Scene("Test Scene")
    game.addScene(scene)
    game.loadScene(scene)

    ### add actors here ###

    actor = Actor("Test Actor")
    scene.addActor(actor)

    #######################

    game.run()


if __name__ == "__main__":
    main()