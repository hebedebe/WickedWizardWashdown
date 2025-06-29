from dataclasses import dataclass
from enum import Enum, auto

class CosmeticKind(Enum):
    """Enum to define different kinds of cosmetics."""
    SKIN = auto()
    HAT = auto()
    GLASSES = auto()

@dataclass
class Cosmetic:
    name: str
    description: str
    type: CosmeticKind
    texture: str
    
@dataclass
class PlayerCosmeticData:
    """Data class to hold cosmetic data for a player."""
    skin: Cosmetic
    hat: Cosmetic
    glasses: Cosmetic
