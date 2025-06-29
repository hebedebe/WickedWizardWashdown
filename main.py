from engine import Game, Scene, Actor, Component, InputManager, AssetManager, NetworkManager
from engine.ui import UIManager, FPSDisplay, Button
from engine.particles import create_fire_emitter
import pygame

from game import scenes


if __name__ == "__main__":
    game = Game(800, 600, "Wicked Wizard Washdown")
    
    game.add_scene("main", scenes.MainMenuScene())
    game.add_scene("settings", scenes.SettingsScene())
    game.add_scene("game_select", scenes.GameSelectScene())
    game.add_scene("lobby_select", scenes.LobbySelectScene())
    game.add_scene("lobby", scenes.LobbyScene())
    game.add_scene("game", scenes.GameScene())
    
    # Start with the main scene
    game.load_scene("main")
    
    game.run()