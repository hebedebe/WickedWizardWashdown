from engine.components import Component
from engine.network_component import NetworkComponent, NetworkOwnership
from ..player_data import PlayerCosmeticData

class PlayerDataComponent(Component):    
    def __init__(self):
        super().__init__()
        self.cosmetics: PlayerCosmeticData = PlayerCosmeticData()
        
        # Player stats that should be networked
        self.player_name: str = "Player"
        self.level: int = 1
        self.experience: int = 0
        self.gold: int = 0
        
        # Local-only data (not synced)
        self.input_buffer = []  # Input history for lag compensation
        self.local_settings = {}  # Client-specific settings
    
    def update(self, dt: float) -> None:
        """Update player data component."""
        pass
    
    def setup_networking(self, player_id: str, is_owner: bool = False) -> NetworkComponent:
        """
        Set up networking for this player data.
        
        Args:
            player_id: The ID of the player who owns this data
            is_owner: Whether the local client owns this player
            
        Returns:
            The NetworkComponent added to the actor
        """
        if not self.actor:
            raise RuntimeError("Component must be added to an actor before setting up networking")
        
        # Create network component
        ownership = NetworkOwnership.CLIENT if is_owner else NetworkOwnership.SERVER
        network_comp = NetworkComponent(
            owner_id=player_id,
            ownership=ownership,
            sync_transform=False,  # Player data doesn't need transform sync
            sync_rate=10.0  # Lower rate for player data
        )
        
        # Blacklist local-only data
        network_comp.blacklist_variable(PlayerDataComponent, 'input_buffer')
        network_comp.blacklist_variable(PlayerDataComponent, 'local_settings')
        
        # Add to actor
        self.actor.add_component(network_comp)
        
        return network_comp