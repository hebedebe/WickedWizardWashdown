from engine import Game, NetworkComponent
from game import scenes


if __name__ == "__main__":
    game = Game(800, 600, "Wicked Wizard Washdown")
    
    game.add_scene("main_menu", scenes.MainMenuScene())
    game.add_scene("settings", scenes.SettingsScene())
    game.add_scene("game_select", scenes.GameSelectScene())
    game.add_scene("lobby_select", scenes.LobbySelectScene())
    game.add_scene("lobby", scenes.LobbyScene())
    game.add_scene("game", scenes.GameScene())
    
    NetworkComponent.set_network_manager(game.network_manager)

    game.load_scene("main_menu")

    game.run()