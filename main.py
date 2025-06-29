"""
Wicked Wizard Washdown - Main Entry Point
A 2D game engine demonstration.
"""

from engine import Game
from game import scenes


def main():
    """Initialize and run the game."""
    # Create the game instance
    game = Game(800, 600, "Wicked Wizard Washdown")
    
    # Add all game scenes
    game.add_scene("main_menu", scenes.MainMenuScene())
    game.add_scene("settings", scenes.SettingsScene())
    game.add_scene("multiplayer_select", scenes.MultiplayerSelectScene())
    game.add_scene("join_lobby", scenes.JoinLobbyScene())
    game.add_scene("lobby", scenes.LobbyScene())
    game.add_scene("game", scenes.GameScene())

    # Start with the main menu
    game.load_scene("main_menu")

    # Run the game
    game.run()


if __name__ == "__main__":
    main()