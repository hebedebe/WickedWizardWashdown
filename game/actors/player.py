from engine import Actor
from engine import SpriteComponent, NetworkComponent, HealthComponent
from engine import NetworkOwnership

class Player(Actor):    
    def __init__(self, player_id: str, is_owner: bool = False):
        super().__init__(name="Player")
        
        self.add_component(SpriteComponent())
        self.add_component(HealthComponent(max_health=100))

        # add this component last
        self.add_component(NetworkComponent(
            owner_id=player_id,
            ownership=NetworkOwnership.CLIENT if is_owner else NetworkOwnership.SERVER,
            sync_transform=True  # Sync transform for player movement
        ))