"""
Example custom components for the Scene Editor

This file demonstrates how to create custom components that can be imported
into the Scene Editor for use in your scenes.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.component.component import Component
import math


class HealthComponent(Component):
    """Component that manages actor health."""
    
    def __init__(self):
        super().__init__()
        self.max_health = 100
        self.current_health = 100
        self.regeneration_rate = 0.0  # Health per second
        
    def takeDamage(self, amount: float):
        """Apply damage to this component."""
        self.current_health = max(0, self.current_health - amount)
        
    def heal(self, amount: float):
        """Heal this component."""
        self.current_health = min(self.max_health, self.current_health + amount)
        
    def isDead(self) -> bool:
        """Check if the actor is dead."""
        return self.current_health <= 0
        
    def getHealthPercent(self) -> float:
        """Get health as a percentage."""
        return self.current_health / self.max_health if self.max_health > 0 else 0
        
    def update(self, delta_time):
        """Update the health component."""
        if self.regeneration_rate > 0 and self.current_health < self.max_health:
            self.heal(self.regeneration_rate * delta_time)


class InventoryComponent(Component):
    """Component that manages an actor's inventory."""
    
    def __init__(self):
        super().__init__()
        self.items = {}  # item_name: quantity
        self.max_slots = 20
        
    def addItem(self, item_name: str, quantity: int = 1) -> bool:
        """Add an item to the inventory."""
        if len(self.items) >= self.max_slots and item_name not in self.items:
            return False  # Inventory full
            
        self.items[item_name] = self.items.get(item_name, 0) + quantity
        return True
        
    def removeItem(self, item_name: str, quantity: int = 1) -> bool:
        """Remove an item from the inventory."""
        if item_name not in self.items or self.items[item_name] < quantity:
            return False
            
        self.items[item_name] -= quantity
        if self.items[item_name] <= 0:
            del self.items[item_name]
        return True
        
    def hasItem(self, item_name: str, quantity: int = 1) -> bool:
        """Check if the inventory contains an item."""
        return self.items.get(item_name, 0) >= quantity
        
    def getItemCount(self, item_name: str) -> int:
        """Get the count of a specific item."""
        return self.items.get(item_name, 0)


class MovementComponent(Component):
    """Component that handles various movement patterns."""
    
    def __init__(self):
        super().__init__()
        self.movement_type = "none"  # none, linear, circular, sine_wave
        self.speed = 100.0
        self.direction = (1, 0)  # normalized direction vector
        
        # For circular movement
        self.radius = 50.0
        self.center_offset = (0, 0)
        self.angle = 0.0
        
        # For sine wave movement
        self.amplitude = 30.0
        self.frequency = 1.0
        self.base_direction = (1, 0)
        
        self._time_elapsed = 0.0
        
    def update(self, delta_time):
        """Update movement based on type."""
        if not self.actor:
            return
            
        self._time_elapsed += delta_time
        
        if self.movement_type == "linear":
            self._updateLinearMovement(delta_time)
        elif self.movement_type == "circular":
            self._updateCircularMovement(delta_time)
        elif self.movement_type == "sine_wave":
            self._updateSineWaveMovement(delta_time)
            
    def _updateLinearMovement(self, delta_time):
        """Update linear movement."""
        current_pos = self.actor.transform.position
        new_x = current_pos[0] + self.direction[0] * self.speed * delta_time
        new_y = current_pos[1] + self.direction[1] * self.speed * delta_time
        self.actor.transform.setPosition(new_x, new_y)
        
    def _updateCircularMovement(self, delta_time):
        """Update circular movement."""
        self.angle += (self.speed / self.radius) * delta_time
        
        center_x = self.actor.transform.position[0] + self.center_offset[0]
        center_y = self.actor.transform.position[1] + self.center_offset[1]
        
        new_x = center_x + math.cos(self.angle) * self.radius
        new_y = center_y + math.sin(self.angle) * self.radius
        
        self.actor.transform.setPosition(new_x, new_y)
        
    def _updateSineWaveMovement(self, delta_time):
        """Update sine wave movement."""
        # Move forward
        current_pos = self.actor.transform.position
        forward_x = current_pos[0] + self.base_direction[0] * self.speed * delta_time
        
        # Apply sine wave to Y position
        sine_offset = math.sin(self._time_elapsed * self.frequency * 2 * math.pi) * self.amplitude
        new_y = current_pos[1] + sine_offset * delta_time
        
        self.actor.transform.setPosition(forward_x, new_y)


class TimerComponent(Component):
    """Component that manages multiple named timers."""
    
    def __init__(self):
        super().__init__()
        self.timers = {}  # timer_name: {"duration": float, "elapsed": float, "callback": callable, "repeat": bool}
        
    def addTimer(self, name: str, duration: float, callback=None, repeat: bool = False):
        """Add a new timer."""
        self.timers[name] = {
            "duration": duration,
            "elapsed": 0.0,
            "callback": callback,
            "repeat": repeat,
            "active": True
        }
        
    def removeTimer(self, name: str):
        """Remove a timer."""
        if name in self.timers:
            del self.timers[name]
            
    def pauseTimer(self, name: str):
        """Pause a timer."""
        if name in self.timers:
            self.timers[name]["active"] = False
            
    def resumeTimer(self, name: str):
        """Resume a timer."""
        if name in self.timers:
            self.timers[name]["active"] = True
            
    def getTimeRemaining(self, name: str) -> float:
        """Get time remaining for a timer."""
        if name in self.timers:
            timer = self.timers[name]
            return max(0, timer["duration"] - timer["elapsed"])
        return 0.0
        
    def isTimerFinished(self, name: str) -> bool:
        """Check if a timer has finished."""
        if name in self.timers:
            timer = self.timers[name]
            return timer["elapsed"] >= timer["duration"]
        return False
        
    def update(self, delta_time):
        """Update all timers."""
        finished_timers = []
        
        for name, timer in self.timers.items():
            if not timer["active"]:
                continue
                
            timer["elapsed"] += delta_time
            
            if timer["elapsed"] >= timer["duration"]:
                # Timer finished
                if timer["callback"]:
                    try:
                        timer["callback"]()
                    except Exception as e:
                        print(f"Timer callback error: {e}")
                        
                if timer["repeat"]:
                    timer["elapsed"] = 0.0  # Reset for repeat
                else:
                    finished_timers.append(name)
                    
        # Remove finished non-repeating timers
        for name in finished_timers:
            self.removeTimer(name)


class StateComponent(Component):
    """Component that manages state machines for actors."""
    
    def __init__(self):
        super().__init__()
        self.current_state = "idle"
        self.states = {
            "idle": {"enter": None, "update": None, "exit": None}
        }
        self.state_data = {}  # Persistent data across states
        
    def addState(self, name: str, enter_callback=None, update_callback=None, exit_callback=None):
        """Add a new state."""
        self.states[name] = {
            "enter": enter_callback,
            "update": update_callback,
            "exit": exit_callback
        }
        
    def changeState(self, new_state: str):
        """Change to a new state."""
        if new_state not in self.states:
            print(f"State '{new_state}' does not exist")
            return
            
        if new_state == self.current_state:
            return
            
        # Exit current state
        current_state_data = self.states[self.current_state]
        if current_state_data["exit"]:
            try:
                current_state_data["exit"](self.actor, self.state_data)
            except Exception as e:
                print(f"State exit error: {e}")
                
        # Enter new state
        old_state = self.current_state
        self.current_state = new_state
        
        new_state_data = self.states[new_state]
        if new_state_data["enter"]:
            try:
                new_state_data["enter"](self.actor, self.state_data)
            except Exception as e:
                print(f"State enter error: {e}")
                
    def update(self, delta_time):
        """Update current state."""
        state_data = self.states[self.current_state]
        if state_data["update"]:
            try:
                state_data["update"](self.actor, self.state_data, delta_time)
            except Exception as e:
                print(f"State update error: {e}")
