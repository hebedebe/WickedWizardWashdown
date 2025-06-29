from engine.components import Component
from ..player_data import PlayerCosmeticData

class PlayerDataComponent(Component):    
    def __init__(self):
        super().__init__()
        self.cosmetics: PlayerCosmeticData