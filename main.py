from engine import *

def main():
    game = Game(800, 600, "Wicked Wizard Washdown")

    Logger.log("Initializing game engine...", LogType.INFO)

    scene = Scene()
    game.addScene("test", scene)
    game.loadScene("test")

    ### add actors here ###

    actor = Actor("Test Actor")
    scene.addActor(actor)

    #######################

    game.run()


if __name__ == "__main__":
    main()