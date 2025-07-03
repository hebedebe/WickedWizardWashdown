from .scene import Scene
from .. import Game

class SceneObject:
    @property
    def getGame(self):
        return Game._instance
    
    @property
    def getScene(self):
        return self.getGame.currentScene