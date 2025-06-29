from engine import Game, Scene, Actor, Component, InputManager, AssetManager, NetworkManager
from engine.ui import UIManager, FPSDisplay, Button
from engine.particles import create_fire_emitter
import pygame

from game.actors.player import Player

class GameScene(Scene):
    def on_enter(self):
        super().on_enter()
        player = Player("player", True)
        self.add_actor(player)