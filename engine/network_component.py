"""
Network component for automatic synchronization of actors and components across network.
"""

import pickle
import time
import uuid
from typing import Dict, List, Set, Any, Optional, Type, Union
from enum import Enum
import pygame

from .actor import Component, Actor
from .networking import NetworkMessage, MessageType, NetworkManager


class NetworkOwnership(Enum):
    """Who has authority over this networked object."""
    SERVER = "server"
    CLIENT = "client"
    LOCAL = "local"  # Only exists locally


class NetworkComponent(Component):
    """
    Component that automatically synchronizes its parent actor and all components
    across the network. Supports selective blacklisting of components/variables.
    """
    
    # Class-level tracking
    _networked_actors: Dict[str, 'NetworkComponent'] = {}
    _network_manager: Optional[NetworkManager] = None
    _sync_rate = 20.0  # Updates per second
    _last_sync_time = 0.0
    
    def __init__(self, 
                 owner_id: str = "server",
                 ownership: NetworkOwnership = NetworkOwnership.SERVER,
                 sync_transform: bool = True,
                 sync_rate: float = 20.0):
        super().__init__()
        
        # Network identity
        self.network_id = str(uuid.uuid4())
        self.owner_id = owner_id  # Which client/server owns this object
        self.ownership = ownership
        
        # Sync settings
        self.sync_transform = sync_transform
        self.sync_rate = sync_rate
        self.last_sync_time = 0.0
        self.force_sync = False  # Force sync on next update
        
        # Blacklists for selective synchronization
        self.blacklisted_components: Set[Type[Component]] = set()
        self.blacklisted_variables: Dict[Type[Component], Set[str]] = {}
        
        # State tracking for efficient sync
        self.last_synced_state: Dict[str, Any] = {}
        self.dirty_components: Set[Type[Component]] = set()
        
        # Spawn/destroy tracking
        self.is_spawned = False
        self.pending_destroy = False
        
    @classmethod
    def set_network_manager(cls, network_manager: NetworkManager) -> None:
        """Set the global network manager for all network components."""
        cls._network_manager = network_manager
        if network_manager:
            # Set up message handlers
            if network_manager.mode == 'server' and network_manager.server:
                network_manager.server.add_message_handler(
                    MessageType.ACTOR_SYNC, cls._handle_actor_sync_server
                )
                network_manager.server.add_message_handler(
                    MessageType.ACTOR_SPAWN, cls._handle_actor_spawn_server
                )
                network_manager.server.add_message_handler(
                    MessageType.ACTOR_DESTROY, cls._handle_actor_destroy_server
                )
            elif network_manager.mode == 'client' and network_manager.client:
                network_manager.client.add_message_handler(
                    MessageType.ACTOR_SYNC, cls._handle_actor_sync_client
                )
                network_manager.client.add_message_handler(
                    MessageType.ACTOR_SPAWN, cls._handle_actor_spawn_client
                )
                network_manager.client.add_message_handler(
                    MessageType.ACTOR_DESTROY, cls._handle_actor_destroy_client
                )
    
    def on_added(self, actor: Actor) -> None:
        """Called when component is added to an actor."""
        super().on_added(actor)
        self._networked_actors[self.network_id] = self
        
        # If we have authority and network manager, spawn on network
        if self._should_send_updates() and self._network_manager:
            self._spawn_on_network()
    
    def on_removed(self) -> None:
        """Called when component is removed from an actor."""
        # Destroy on network if we have authority
        if self._should_send_updates() and self._network_manager:
            self._destroy_on_network()
        
        if self.network_id in self._networked_actors:
            del self._networked_actors[self.network_id]
        super().on_removed()
    
    def blacklist_component(self, component_type: Type[Component]) -> None:
        """Blacklist an entire component type from being synced."""
        self.blacklisted_components.add(component_type)
    
    def blacklist_variable(self, component_type: Type[Component], variable_name: str) -> None:
        """Blacklist a specific variable from a component type."""
        if component_type not in self.blacklisted_variables:
            self.blacklisted_variables[component_type] = set()
        self.blacklisted_variables[component_type].add(variable_name)
    
    def whitelist_component(self, component_type: Type[Component]) -> None:
        """Remove a component type from blacklist."""
        self.blacklisted_components.discard(component_type)
    
    def whitelist_variable(self, component_type: Type[Component], variable_name: str) -> None:
        """Remove a variable from blacklist."""
        if component_type in self.blacklisted_variables:
            self.blacklisted_variables[component_type].discard(variable_name)
    
    def force_sync_next_update(self) -> None:
        """Force a sync on the next update regardless of sync rate."""
        self.force_sync = True
    
    def mark_component_dirty(self, component_type: Type[Component]) -> None:
        """Mark a component as needing sync."""
        self.dirty_components.add(component_type)
    
    def _should_send_updates(self) -> bool:
        """Check if this component should send updates to the network."""
        if not self._network_manager:
            return False
        
        # Server always has authority unless specifically set to client
        if self._network_manager.mode == 'server':
            return self.ownership in [NetworkOwnership.SERVER, NetworkOwnership.LOCAL]
        
        # Client only has authority if specifically owned by this client
        if self._network_manager.mode == 'client':
            client_id = self._network_manager.client.client_id if self._network_manager.client else ""
            return (self.ownership == NetworkOwnership.CLIENT and 
                   self.owner_id == client_id)
        
        return False
    
    def _serialize_actor_state(self) -> Dict[str, Any]:
        """Serialize the actor and its components to a dictionary."""
        if not self.actor:
            return {}
        
        state = {
            'network_id': self.network_id,
            'actor_id': self.actor.id,
            'actor_name': self.actor.name,
            'active': self.actor.active,
            'enabled': self.actor.enabled,
            'tags': self.actor.tags.copy(),
            'components': {}
        }
        
        # Serialize transform if enabled
        if self.sync_transform:
            state['transform'] = {
                'position': (self.actor.transform.local_position.x, self.actor.transform.local_position.y),
                'rotation': self.actor.transform.local_rotation,
                'scale': (self.actor.transform.local_scale.x, self.actor.transform.local_scale.y)
            }
        
        # Serialize components
        for component in self.actor.component_list:
            component_type = type(component)
            component_name = component_type.__name__
            
            # Skip blacklisted components
            if component_type in self.blacklisted_components:
                continue
            
            # Skip network component itself to avoid recursion
            if isinstance(component, NetworkComponent):
                continue
            
            # Serialize component state
            component_data = self._serialize_component(component)
            if component_data:
                state['components'][component_name] = {
                    'type': component_name,
                    'module': component_type.__module__,
                    'data': component_data
                }
        
        return state
    
    def _serialize_component(self, component: Component) -> Dict[str, Any]:
        """Serialize a single component to a dictionary."""
        component_type = type(component)
        blacklisted_vars = self.blacklisted_variables.get(component_type, set())
        
        # Get all public attributes
        data = {}
        for attr_name in dir(component):
            if (attr_name.startswith('_') or 
                attr_name in blacklisted_vars or
                attr_name in ['actor', 'game'] or  # Skip references to avoid circular serialization
                callable(getattr(component, attr_name))):
                continue
            
            try:
                value = getattr(component, attr_name)
                # Convert pygame types to serializable forms
                if isinstance(value, pygame.Vector2):
                    data[attr_name] = (value.x, value.y)
                elif isinstance(value, pygame.Color):
                    data[attr_name] = (value.r, value.g, value.b, value.a)
                elif isinstance(value, pygame.Rect):
                    data[attr_name] = (value.x, value.y, value.width, value.height)
                elif isinstance(value, pygame.Surface):
                    # Skip surfaces as they can't be easily serialized
                    continue
                else:
                    # Try to serialize the value
                    pickle.dumps(value)  # Test if it's serializable
                    data[attr_name] = value
            except (pickle.PicklingError, TypeError, AttributeError):
                # Skip non-serializable attributes
                continue
        
        return data
    
    def _deserialize_actor_state(self, state: Dict[str, Any]) -> None:
        """Apply received state to the actor."""
        if not self.actor:
            return
        
        # Update basic actor properties
        self.actor.active = state.get('active', True)
        self.actor.enabled = state.get('enabled', True)
        self.actor.tags = state.get('tags', [])
        
        # Update transform
        if self.sync_transform and 'transform' in state:
            transform_data = state['transform']
            pos = transform_data.get('position', (0, 0))
            self.actor.transform.local_position = pygame.Vector2(pos[0], pos[1])
            self.actor.transform.local_rotation = transform_data.get('rotation', 0)
            scale = transform_data.get('scale', (1, 1))
            self.actor.transform.local_scale = pygame.Vector2(scale[0], scale[1])
            self.actor.transform.mark_dirty()
        
        # Update components
        components_data = state.get('components', {})
        for component_name, component_info in components_data.items():
            self._update_component_from_data(component_name, component_info)
    
    def _update_component_from_data(self, component_name: str, component_info: Dict[str, Any]) -> None:
        """Update or create a component from network data."""
        # Find existing component by type name
        target_component = None
        for component in self.actor.component_list:
            if type(component).__name__ == component_name:
                target_component = component
                break
        
        if not target_component:
            # Component doesn't exist, skip for now
            # In a full implementation, you could dynamically create components
            return
        
        # Update component data
        component_data = component_info.get('data', {})
        self._apply_component_data(target_component, component_data)
    
    def _apply_component_data(self, component: Component, data: Dict[str, Any]) -> None:
        """Apply data to a component."""
        component_type = type(component)
        blacklisted_vars = self.blacklisted_variables.get(component_type, set())
        
        for attr_name, value in data.items():
            if attr_name in blacklisted_vars:
                continue
            
            try:
                # Convert back from serialized forms
                if hasattr(component, attr_name):
                    current_value = getattr(component, attr_name)
                    
                    # Handle pygame types
                    if isinstance(current_value, pygame.Vector2) and isinstance(value, (list, tuple)):
                        setattr(component, attr_name, pygame.Vector2(value[0], value[1]))
                    elif isinstance(current_value, pygame.Color) and isinstance(value, (list, tuple)):
                        setattr(component, attr_name, pygame.Color(value[0], value[1], value[2], value[3]))
                    elif isinstance(current_value, pygame.Rect) and isinstance(value, (list, tuple)):
                        setattr(component, attr_name, pygame.Rect(value[0], value[1], value[2], value[3]))
                    else:
                        setattr(component, attr_name, value)
            except (AttributeError, TypeError, ValueError):
                # Skip attributes that can't be set
                continue
    
    def _spawn_on_network(self) -> None:
        """Spawn this actor on the network."""
        if not self._network_manager or self.is_spawned:
            return
        
        actor_state = self._serialize_actor_state()
        spawn_data = {
            'network_id': self.network_id,
            'owner_id': self.owner_id,
            'ownership': self.ownership.value,
            'actor_state': actor_state
        }
        
        message = NetworkMessage(MessageType.ACTOR_SPAWN, spawn_data)
        
        if self._network_manager.mode == 'server' and self._network_manager.server:
            self._network_manager.server.broadcast_message(message)
        elif self._network_manager.mode == 'client' and self._network_manager.client:
            self._network_manager.client.send_message(message)
        
        self.is_spawned = True
    
    def _destroy_on_network(self) -> None:
        """Destroy this actor on the network."""
        if not self._network_manager or not self.is_spawned:
            return
        
        destroy_data = {
            'network_id': self.network_id
        }
        
        message = NetworkMessage(MessageType.ACTOR_DESTROY, destroy_data)
        
        if self._network_manager.mode == 'server' and self._network_manager.server:
            self._network_manager.server.broadcast_message(message)
        elif self._network_manager.mode == 'client' and self._network_manager.client:
            self._network_manager.client.send_message(message)
        
        self.is_spawned = False
    
    def update(self, dt: float) -> None:
        """Update the network component."""
        if not self._should_send_updates() or not self._network_manager:
            return
        
        current_time = time.time()
        
        # Check if it's time to sync
        should_sync = (
            self.force_sync or
            (current_time - self.last_sync_time) >= (1.0 / self.sync_rate) or
            len(self.dirty_components) > 0
        )
        
        if should_sync:
            # Get current state
            current_state = self._serialize_actor_state()
            
            # Check if state has changed
            if self.force_sync or current_state != self.last_synced_state:
                # Send sync message
                sync_data = {
                    'network_id': self.network_id,
                    'actor_state': current_state,
                    'timestamp': current_time
                }
                
                message = NetworkMessage(MessageType.ACTOR_SYNC, sync_data)
                
                if self._network_manager.mode == 'server' and self._network_manager.server:
                    self._network_manager.server.broadcast_message(message)
                elif self._network_manager.mode == 'client' and self._network_manager.client:
                    self._network_manager.client.send_message(message)
                
                # Update tracking
                self.last_synced_state = current_state
                self.last_sync_time = current_time
                self.force_sync = False
                self.dirty_components.clear()
    
    # Static message handlers
    @classmethod
    def _handle_actor_sync_server(cls, client_id: str, message: NetworkMessage) -> None:
        """Handle actor sync message on server."""
        data = message.data
        network_id = data.get('network_id')
        
        if network_id in cls._networked_actors:
            network_comp = cls._networked_actors[network_id]
            
            # Only accept updates from the owner
            if network_comp.owner_id == client_id:
                network_comp._deserialize_actor_state(data['actor_state'])
                
                # Broadcast to other clients
                if cls._network_manager and cls._network_manager.server:
                    cls._network_manager.server.broadcast_message(message, exclude=[client_id])
    
    @classmethod
    def _handle_actor_sync_client(cls, message: NetworkMessage) -> None:
        """Handle actor sync message on client."""
        data = message.data
        network_id = data.get('network_id')
        
        if network_id in cls._networked_actors:
            network_comp = cls._networked_actors[network_id]
            # Only accept updates if we don't own this object
            if not network_comp._should_send_updates():
                network_comp._deserialize_actor_state(data['actor_state'])
    
    @classmethod
    def _handle_actor_spawn_server(cls, client_id: str, message: NetworkMessage) -> None:
        """Handle actor spawn message on server."""
        # For now, just forward to all clients
        if cls._network_manager and cls._network_manager.server:
            cls._network_manager.server.broadcast_message(message, exclude=[client_id])
    
    @classmethod
    def _handle_actor_spawn_client(cls, message: NetworkMessage) -> None:
        """Handle actor spawn message on client."""
        data = message.data
        network_id = data.get('network_id')
        
        # Don't spawn if we already have this actor
        if network_id in cls._networked_actors:
            return
        
        # Create new actor with network component
        # This is a simplified implementation - in practice you'd want
        # more sophisticated actor factory system
        from .actor import Actor
        
        actor_state = data.get('actor_state', {})
        actor = Actor(actor_state.get('actor_name', f'NetworkedActor_{network_id[:8]}'))
        
        # Add network component
        network_comp = NetworkComponent(
            owner_id=data.get('owner_id', 'server'),
            ownership=NetworkOwnership(data.get('ownership', 'server'))
        )
        network_comp.network_id = network_id
        network_comp.is_spawned = True
        actor.add_component(network_comp)
        
        # Apply initial state
        network_comp._deserialize_actor_state(actor_state)
        
        # Add to scene - this would need to be handled by your scene system
        # For now, just mark as spawned
        print(f"Spawned networked actor: {actor.name} (ID: {network_id})")
    
    @classmethod
    def _handle_actor_destroy_server(cls, client_id: str, message: NetworkMessage) -> None:
        """Handle actor destroy message on server."""
        data = message.data
        network_id = data.get('network_id')
        
        if network_id in cls._networked_actors:
            network_comp = cls._networked_actors[network_id]
            
            # Only accept destroy from owner
            if network_comp.owner_id == client_id:
                # Broadcast to other clients
                if cls._network_manager and cls._network_manager.server:
                    cls._network_manager.server.broadcast_message(message, exclude=[client_id])
    
    @classmethod
    def _handle_actor_destroy_client(cls, message: NetworkMessage) -> None:
        """Handle actor destroy message on client."""
        data = message.data
        network_id = data.get('network_id')
        
        if network_id in cls._networked_actors:
            network_comp = cls._networked_actors[network_id]
            if network_comp.actor:
                network_comp.actor.destroy()
    
    @classmethod
    def spawn_networked_actor(cls, actor: Actor, owner_id: str = "server", 
                            ownership: NetworkOwnership = NetworkOwnership.SERVER) -> 'NetworkComponent':
        """Convenience method to spawn an actor on the network."""
        network_comp = NetworkComponent(owner_id=owner_id, ownership=ownership)
        actor.add_component(network_comp)
        return network_comp
    
    @classmethod
    def get_networked_actor(cls, network_id: str) -> Optional[Actor]:
        """Get a networked actor by its network ID."""
        if network_id in cls._networked_actors:
            return cls._networked_actors[network_id].actor
        return None
