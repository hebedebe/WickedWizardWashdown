from dataclasses import dataclass

COSMETIC_DEFAULT = "default"

@dataclass
class PlayerCosmeticData:
    """Data class to hold cosmetic data for a player."""
    skin: str = COSMETIC_DEFAULT
    hat: str = COSMETIC_DEFAULT
    glasses: str = COSMETIC_DEFAULT