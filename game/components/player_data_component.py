from engine.components import Component
from ..player_data import PlayerCosmeticData

class PlayerDataComponent(Component):    
    def __init__(self):
        super().__init__()
        self.cosmetics: PlayerCosmeticData = PlayerCosmeticData()
        
        # Player stats
        self.player_name: str = "Player"
        self.level: int = 1
        self.experience: int = 0
        self.gold: int = 0
        
        # Local-only data
        self.input_buffer = []  # Input history for lag compensation
        self.local_settings = {}  # Client-specific settings
    
    def update(self, dt: float) -> None:
        """Update player data component."""
        pass