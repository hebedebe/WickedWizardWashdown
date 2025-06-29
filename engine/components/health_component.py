"""
Health component for actors.
"""

from typing import Optional, Callable
from ..core.actor import Component


class HealthComponent(Component):
    """
    Component for managing actor health/hit points.
    """
    
    def __init__(self, max_health: float = 100.0):
        super().__init__()
        self.max_health = max_health
        self.current_health = max_health
        self.invulnerable = False
        self.invulnerability_time = 0.0
        
        # Events
        self.on_damage_taken: Optional[Callable] = None
        self.on_health_changed: Optional[Callable] = None
        self.on_death: Optional[Callable] = None
        
    def take_damage(self, amount: float) -> None:
        """Apply damage to this component."""
        if self.invulnerable:
            return
            
        self.current_health -= amount
        self.current_health = max(0, self.current_health)
        
        if self.on_damage_taken:
            self.on_damage_taken(amount)
        if self.on_health_changed:
            self.on_health_changed(self.current_health, self.max_health)
            
        if self.current_health <= 0 and self.on_death:
            self.on_death()
            
    def heal(self, amount: float) -> None:
        """Heal this component."""
        self.current_health += amount
        self.current_health = min(self.max_health, self.current_health)
        
        if self.on_health_changed:
            self.on_health_changed(self.current_health, self.max_health)
            
    def set_invulnerable(self, duration: float) -> None:
        """Make temporarily invulnerable."""
        self.invulnerable = True
        self.invulnerability_time = duration
        
    def update(self, dt: float) -> None:
        """Update health component."""
        if self.invulnerable:
            self.invulnerability_time -= dt
            if self.invulnerability_time <= 0:
                self.invulnerable = False
                
    @property
    def health_percentage(self) -> float:
        """Get health as a percentage (0-1)."""
        return self.current_health / self.max_health if self.max_health > 0 else 0
        
    @property
    def is_alive(self) -> bool:
        """Check if actor is alive."""
        return self.current_health > 0
