"""
Network components for automatic synchronization of game objects.
Handles serialization, spawning, and synchronization of networked actors.
"""

import time
import uuid
from typing import Dict, Any, Optional, Set, List, Type
from ..core.actor import Actor, Component
from .networking import NetworkManager, NetworkMessage, MessageType, NetworkPriority, get_network_manager


class NetworkSerialization:
    """Handles serialization of game objects without pickle."""
    
    @staticmethod
    def serialize_component(component: Component) -> Dict[str, Any]:
        """Serialize a component to a dictionary."""
        data = {
            'type': component.__class__.__name__,
            'module': component.__class__.__module__,
            'enabled': component.enabled
        }
        
        # Use the component's built-in serialization method
        try:
            component_data = component.serialize_for_network()
            data['data'] = component_data
            return data
        except Exception as e:
            print(f"Error serializing component {component.__class__.__name__}: {e}")
            # Return minimal data on error
            data['data'] = {}
            return data
    
    @staticmethod
    def serialize_actor(actor: Actor) -> Dict[str, Any]:
        """Serialize an actor to a dictionary."""
        data = {
            'id': actor.id,
            'name': actor.name,
            'active': actor.active,
            'enabled': actor.enabled,
            'tags': actor.tags.copy(),
            'transform': {
                'local_position': [actor.transform.local_position.x, actor.transform.local_position.y],
                'local_rotation': actor.transform.local_rotation,
                'local_scale': [actor.transform.local_scale.x, actor.transform.local_scale.y]
            },
            'components': []
        }
        
        # Serialize components (excluding NetworkComponent to avoid recursion)
        for component in actor.component_list:
            if not isinstance(component, NetworkComponent):
                component_data = NetworkSerialization.serialize_component(component)
                data['components'].append(component_data)
        
        return data
    
    @staticmethod
    def _serialize_value(value: Any) -> Any:
        """Serialize a single value."""
        import pygame
        
        if value is None:
            return None
        elif isinstance(value, (bool, int, float, str)):
            return value
        elif isinstance(value, pygame.Vector2):
            return [value.x, value.y]
        elif isinstance(value, pygame.Color):
            return [value.r, value.g, value.b, value.a]
        elif isinstance(value, pygame.Rect):
            return [value.x, value.y, value.width, value.height]
        elif isinstance(value, (list, tuple)):
            return [NetworkSerialization._serialize_value(item) for item in value]
        elif isinstance(value, dict):
            return {k: NetworkSerialization._serialize_value(v) for k, v in value.items()}
        elif hasattr(value, '__dict__'):
            # Custom object - serialize its attributes
            return {k: NetworkSerialization._serialize_value(v) 
                   for k, v in value.__dict__.items() 
                   if not k.startswith('_')}
        else:
            # Cannot serialize this type
            return None
    
    @staticmethod
    def deserialize_actor(data: Dict[str, Any]) -> Actor:
        """Deserialize an actor from a dictionary."""
        import pygame
        
        actor = Actor(data['name'])
        actor.id = data['id']
        actor.active = data['active']
        actor.enabled = data['enabled']
        actor.tags = data['tags'].copy()
        
        # Restore transform
        transform_data = data['transform']
        actor.transform.local_position = pygame.Vector2(
            transform_data['local_position'][0],
            transform_data['local_position'][1]
        )
        actor.transform.local_rotation = transform_data['local_rotation']
        actor.transform.local_scale = pygame.Vector2(
            transform_data['local_scale'][0],
            transform_data['local_scale'][1]
        )
        
        # Deserialize components
        for component_data in data['components']:
            component = NetworkSerialization.deserialize_component(component_data)
            if component:
                actor.add_component(component)
        
        return actor
    
    @staticmethod
    def deserialize_component(data: Dict[str, Any]) -> Optional[Component]:
        """Deserialize a component from a dictionary."""
        try:
            # Import the component class
            module_name = data['module']
            class_name = data['type']
            
            # Dynamic import
            if module_name.startswith('engine.'):
                from engine import components
                component_class = getattr(components, class_name, None)
            elif module_name == '__main__':
                # Handle components defined in main module (like demo)
                import sys
                main_module = sys.modules['__main__']
                component_class = getattr(main_module, class_name, None)
            else:
                # Handle other modules
                import importlib
                module = importlib.import_module(module_name)
                component_class = getattr(module, class_name, None)
            
            if not component_class:
                print(f"Could not find component class: {class_name}")
                return None
            
            # Create component instance
            component = component_class()
            component.enabled = data['enabled']
            
            # Use the component's built-in deserialization method
            try:
                component.deserialize_from_network(data['data'])
                return component
            except Exception as e:
                print(f"Error deserializing component {class_name}: {e}")
                return component  # Return component even if deserialization failed
            
        except Exception as e:
            print(f"Error creating component {data.get('type', 'Unknown')}: {e}")
            return None
    
    @staticmethod
    def _deserialize_value(value: Any) -> Any:
        """Deserialize a single value."""
        import pygame
        
        if value is None:
            return None
        elif isinstance(value, (bool, int, float, str)):
            return value
        elif isinstance(value, list):
            if len(value) == 2 and all(isinstance(x, (int, float)) for x in value):
                # Assume it's a Vector2
                return pygame.Vector2(value[0], value[1])
            elif len(value) == 4 and all(isinstance(x, int) for x in value):
                # Could be Color or Rect - we'll assume Color for now
                return pygame.Color(value[0], value[1], value[2], value[3])
            else:
                # Regular list
                return [NetworkSerialization._deserialize_value(item) for item in value]
        elif isinstance(value, dict):
            return {k: NetworkSerialization._deserialize_value(v) for k, v in value.items()}
        else:
            return value


class NetworkComponent(Component):
    """
    Component that automatically synchronizes all other components on an actor.
    Only one NetworkComponent should be attached per networked actor.
    """
    
    def __init__(self, owner_id: str = None, sync_mode: str = "blacklist", network_manager=None):
        super().__init__()
        
        # Network identity
        self.network_id = str(uuid.uuid4())
        self.owner_id = owner_id or "server"  # Who owns this networked object
        
        # Synchronization settings
        self.sync_mode = sync_mode  # "blacklist" or "whitelist"
        self.sync_blacklist: Set[str] = set()  # Component types to NOT sync
        self.sync_whitelist: Set[str] = set()  # Component types to sync (whitelist mode)
        
        # State tracking
        self.last_sync_time = 0.0
        self.sync_rate = 20.0  # Updates per second
        self.last_component_states: Dict[str, Dict[str, Any]] = {}
        self.spawned_on_network = False
        
        # Network manager reference
        self.network_manager = network_manager or get_network_manager()
    
    def set_sync_mode(self, mode: str):
        """Set synchronization mode: 'blacklist' or 'whitelist'."""
        if mode in ['blacklist', 'whitelist']:
            self.sync_mode = mode
    
    def add_to_blacklist(self, component_type: str):
        """Add component type to sync blacklist."""
        self.sync_blacklist.add(component_type)
    
    def remove_from_blacklist(self, component_type: str):
        """Remove component type from sync blacklist."""
        self.sync_blacklist.discard(component_type)
    
    def add_to_whitelist(self, component_type: str):
        """Add component type to sync whitelist."""
        self.sync_whitelist.add(component_type)
    
    def remove_from_whitelist(self, component_type: str):
        """Remove component type from sync whitelist."""
        self.sync_whitelist.discard(component_type)
    
    def should_sync_component(self, component: Component) -> bool:
        """Check if a component should be synchronized."""
        component_type = component.__class__.__name__
        
        # Never sync NetworkComponent itself
        if isinstance(component, NetworkComponent):
            return False
        
        if self.sync_mode == "blacklist":
            return component_type not in self.sync_blacklist
        else:  # whitelist mode
            return component_type in self.sync_whitelist
    
    def on_added(self, actor: Actor):
        """Called when component is added to an actor."""
        super().on_added(actor)
        
        # Initialize component states
        self._capture_component_states()
    
    def update(self, dt: float):
        """Update network synchronization."""
        if not self.network_manager.is_connected:
            return
        
        current_time = time.time()
        
        # Throttle sync updates
        if current_time - self.last_sync_time < 1.0 / self.sync_rate:
            return
        
        self.last_sync_time = current_time
        
        # Check for component changes
        if self._has_components_changed():
            self._send_component_update()
            self._capture_component_states()
    
    def _capture_component_states(self):
        """Capture current state of all synchronized components."""
        self.last_component_states.clear()
        
        if not self.actor:
            return
        
        for component in self.actor.component_list:
            if self.should_sync_component(component):
                component_key = component.__class__.__name__
                self.last_component_states[component_key] = \
                    NetworkSerialization.serialize_component(component)
    
    def _has_components_changed(self) -> bool:
        """Check if any synchronized components have changed."""
        if not self.actor:
            return False
        
        current_states = {}
        for component in self.actor.component_list:
            if self.should_sync_component(component):
                component_key = component.__class__.__name__
                current_states[component_key] = \
                    NetworkSerialization.serialize_component(component)
        
        # Compare with last known states
        return current_states != self.last_component_states
    
    def _send_component_update(self):
        """Send component update message to network."""
        if not self.actor or not self.network_manager.is_connected:
            return
        
        # Collect data for all synchronized components
        component_data = []
        for component in self.actor.component_list:
            if self.should_sync_component(component):
                component_data.append(
                    NetworkSerialization.serialize_component(component)
                )
        
        # Send update message
        message = NetworkMessage(
            MessageType.COMPONENT_UPDATE,
            {
                'network_id': self.network_id,
                'actor_id': self.actor.id,
                'owner_id': self.owner_id,
                'components': component_data,
                'transform': {
                    'local_position': [self.actor.transform.local_position.x, 
                                     self.actor.transform.local_position.y],
                    'local_rotation': self.actor.transform.local_rotation,
                    'local_scale': [self.actor.transform.local_scale.x, 
                                  self.actor.transform.local_scale.y]
                }
            }
        )
        
        if self.network_manager.is_server:
            # Server broadcasts to all clients except owner
            self.network_manager.broadcast_message(message, exclude_client=self.owner_id)
        else:
            # Client sends to server
            self.network_manager.send_to_server(message)
    
    def apply_component_update(self, components_data: List[Dict[str, Any]], 
                             transform_data: Dict[str, Any]):
        """Apply received component update."""
        if not self.actor:
            return
        
        import pygame
        
        # Update transform
        self.actor.transform.local_position = pygame.Vector2(
            transform_data['local_position'][0],
            transform_data['local_position'][1]
        )
        self.actor.transform.local_rotation = transform_data['local_rotation']
        self.actor.transform.local_scale = pygame.Vector2(
            transform_data['local_scale'][0],
            transform_data['local_scale'][1]
        )
        
        # Update components
        for component_data in components_data:
            component_type = component_data['type']
            
            # Find existing component of this type
            existing_component = None
            for component in self.actor.component_list:
                if component.__class__.__name__ == component_type:
                    existing_component = component
                    break
            
            if existing_component and self.should_sync_component(existing_component):
                # Update existing component
                sprite_updated = False
                for attr_name, attr_value in component_data['data'].items():
                    if hasattr(existing_component, attr_name):
                        # Skip surface and rect - they'll be recreated
                        if component_type == 'SpriteComponent' and attr_name in ['surface', 'rect']:
                            continue
                        
                        deserialized_value = NetworkSerialization._deserialize_value(attr_value)
                        setattr(existing_component, attr_name, deserialized_value)
                        
                        # Track if sprite properties changed
                        if component_type == 'SpriteComponent' and attr_name in ['size', 'color', 'alpha']:
                            sprite_updated = True
                
                # Recreate sprite surface if SpriteComponent was updated
                if component_type == 'SpriteComponent' and sprite_updated:
                    if hasattr(existing_component, 'size') and hasattr(existing_component, 'color'):
                        existing_component.surface = pygame.Surface((int(existing_component.size.x), int(existing_component.size.y)))
                        existing_component.surface.fill(existing_component.color)
                        existing_component.rect = existing_component.surface.get_rect()
                        
                        # Apply alpha if it was set
                        if hasattr(existing_component, 'alpha') and existing_component.alpha != 255:
                            existing_component.surface.set_alpha(existing_component.alpha)
        
        # Update our state tracking
        self._capture_component_states()


class PriorityNetworkComponent(Component):
    """Network component with configurable update priority."""
    
    def __init__(self, update_priority: NetworkPriority = None):
        super().__init__()
        self.update_priority = update_priority or NetworkPriority.MEDIUM
        self.last_sync_time = 0.0
        self.sync_interval = 0.05  # Default 20 FPS
        self.force_update = False
        
        # Set sync interval based on priority
        priority_intervals = {
            NetworkPriority.INSTANT: 0.0,     # Immediate
            NetworkPriority.HIGH: 1.0/60.0,   # 60 FPS
            NetworkPriority.MEDIUM: 1.0/20.0, # 20 FPS  
            NetworkPriority.LOW: 1.0/5.0      # 5 FPS
        }
        self.sync_interval = priority_intervals.get(self.update_priority, 0.05)
        
    def should_sync(self) -> bool:
        """Check if this component should sync based on priority and timing."""
        current_time = time.time()
        
        # Instant priority or forced updates always sync
        if self.update_priority.value == "instant" or self.force_update:
            self.force_update = False
            return True
            
        # Check if enough time has passed based on priority
        return (current_time - self.last_sync_time) >= self.sync_interval
    
    def mark_for_sync(self):
        """Mark this component for immediate synchronization."""
        self.force_update = True
        
    def on_sync_completed(self):
        """Called after synchronization is completed."""
        self.last_sync_time = time.time()
        
    def serialize_for_network(self) -> Dict[str, Any]:
        """Serialize component data for network transmission."""
        return {
            'update_priority': self.update_priority.value,
            'last_sync_time': self.last_sync_time
        }
        
    def deserialize_from_network(self, data: Dict[str, Any]) -> None:
        """Deserialize component data from network."""
        priority_str = data.get('update_priority', 'medium')
        try:
            self.update_priority = NetworkPriority(priority_str)
        except ValueError:
            self.update_priority = NetworkPriority.MEDIUM
        self.last_sync_time = data.get('last_sync_time', 0.0)


class NetworkedActorManager:
    """Manages networked actor spawning and synchronization."""
    
    def __init__(self, network_manager=None):
        self.network_manager = network_manager or get_network_manager()
        self.networked_actors: Dict[str, Actor] = {}  # network_id -> actor
        self.actor_owners: Dict[str, str] = {}  # network_id -> owner_id
        
        # Setup network callbacks
        self.network_manager.on_actor_spawned = self._on_actor_spawned
        self.network_manager.on_actor_destroyed = self._on_actor_destroyed
        
        # Hook into message handlers
        self._setup_message_handlers()
    
    def _setup_message_handlers(self):
        """Setup message handlers for networked actors."""
        original_handle_message = self.network_manager._handle_message
        
        def enhanced_handle_message(message, sender):
            # Handle our messages first
            if message.type == MessageType.SPAWN_ACTOR:
                self._handle_spawn_actor(message, sender)
            elif message.type == MessageType.DESTROY_ACTOR:
                self._handle_destroy_actor(message, sender)
            elif message.type == MessageType.COMPONENT_UPDATE:
                self._handle_component_update(message, sender)
            elif message.type == MessageType.FULL_SYNC_DATA:
                self._handle_full_sync_data(message, sender)
            elif message.type == MessageType.FULL_SYNC_REQUEST:
                self._handle_full_sync_request(message, sender)
            else:
                # Let original handler deal with other messages
                original_handle_message(message, sender)
        
        self.network_manager._handle_message = enhanced_handle_message
        
        # Also hook into full sync
        original_send_full_sync = self.network_manager._send_full_sync
        
        def enhanced_send_full_sync(client):
            self._send_full_sync_to_client(client)
        
        self.network_manager._send_full_sync = enhanced_send_full_sync
    
    def spawn_network_actor(self, actor: Actor, owner_id: str = None) -> bool:
        """Spawn an actor on the network."""
        if not self.network_manager.is_connected:
            return False
        
        # Determine owner
        if owner_id is None:
            if self.network_manager.is_server:
                owner_id = "server"
            else:
                owner_id = self.network_manager.client_id
        
        # Add NetworkComponent if not already present
        network_component = actor.get_component(NetworkComponent)
        if not network_component:
            network_component = NetworkComponent(owner_id, network_manager=self.network_manager)
            actor.add_component(network_component)
        else:
            network_component.owner_id = owner_id
            network_component.network_manager = self.network_manager
        
        # Register the actor
        self.networked_actors[network_component.network_id] = actor
        self.actor_owners[network_component.network_id] = owner_id
        
        # Add to current scene if we have a game instance
        if self.network_manager.game and self.network_manager.game.current_scene:
            self.network_manager.game.current_scene.add_actor(actor)
        
        # Send spawn message
        message = NetworkMessage(
            MessageType.SPAWN_ACTOR,
            {
                'network_id': network_component.network_id,
                'owner_id': owner_id,
                'actor_data': NetworkSerialization.serialize_actor(actor)
            }
        )
        
        if self.network_manager.is_server:
            # Server broadcasts to all clients
            self.network_manager.broadcast_message(message)
        else:
            # Client sends to server
            self.network_manager.send_to_server(message)
        
        network_component.spawned_on_network = True
        return True
    
    def destroy_network_actor(self, actor: Actor) -> bool:
        """Destroy a networked actor."""
        network_component = actor.get_component(NetworkComponent)
        if not network_component or not network_component.spawned_on_network:
            return False
        
        # Send destroy message
        message = NetworkMessage(
            MessageType.DESTROY_ACTOR,
            {
                'network_id': network_component.network_id,
                'actor_id': actor.id
            }
        )
        
        if self.network_manager.is_server:
            self.network_manager.broadcast_message(message)
        else:
            self.network_manager.send_to_server(message)
        
        # Remove from tracking
        if network_component.network_id in self.networked_actors:
            del self.networked_actors[network_component.network_id]
        if network_component.network_id in self.actor_owners:
            del self.actor_owners[network_component.network_id]
        
        # Destroy the actor
        actor.destroy()
        return True
    
    def request_full_sync(self):
        """Request full synchronization from server (client only)."""
        if self.network_manager.is_client:
            message = NetworkMessage(
                MessageType.FULL_SYNC_REQUEST,
                {'client_id': self.network_manager.client_id}
            )
            self.network_manager.send_to_server(message)
    
    def _handle_spawn_actor(self, message, sender):
        """Handle actor spawn message."""
        network_id = message.data['network_id']
        owner_id = message.data['owner_id']
        actor_data = message.data['actor_data']
        
        # Don't spawn if we already have this actor
        if network_id in self.networked_actors:
            return
        
        # Deserialize and create actor
        actor = NetworkSerialization.deserialize_actor(actor_data)
        if not actor:
            return
        
        # Add NetworkComponent with correct network_id and owner
        network_component = NetworkComponent(owner_id, network_manager=self.network_manager)
        network_component.network_id = network_id
        network_component.spawned_on_network = True
        actor.add_component(network_component)
        
        # Register the actor
        self.networked_actors[network_id] = actor
        self.actor_owners[network_id] = owner_id
        
        # Add to current scene
        if self.network_manager.game and self.network_manager.game.current_scene:
            self.network_manager.game.current_scene.add_actor(actor)
        
        # If we're server, relay to other clients
        if self.network_manager.is_server:
            self.network_manager.broadcast_message(message, exclude_client=sender.client_id)
        
        # Notify callback
        if self.network_manager.on_actor_spawned:
            self.network_manager.on_actor_spawned(actor)
    
    def _handle_destroy_actor(self, message, sender):
        """Handle actor destroy message."""
        network_id = message.data['network_id']
        
        if network_id in self.networked_actors:
            actor = self.networked_actors[network_id]
            
            # Remove from tracking
            del self.networked_actors[network_id]
            if network_id in self.actor_owners:
                del self.actor_owners[network_id]
            
            # Destroy the actor
            actor.destroy()
            
            # If we're server, relay to other clients
            if self.network_manager.is_server:
                self.network_manager.broadcast_message(message, exclude_client=sender.client_id)
            
            # Notify callback
            if self.network_manager.on_actor_destroyed:
                self.network_manager.on_actor_destroyed(network_id)
    
    def _handle_component_update(self, message, sender):
        """Handle component update message."""
        network_id = message.data['network_id']
        components_data = message.data['components']
        transform_data = message.data['transform']
        
        if network_id in self.networked_actors:
            actor = self.networked_actors[network_id]
            network_component = actor.get_component(NetworkComponent)
            
            if network_component:
                # Only apply update if we're not the owner
                if network_component.owner_id != self.network_manager.client_id:
                    network_component.apply_component_update(components_data, transform_data)
        
        # If we're server, relay to other clients
        if self.network_manager.is_server:
            self.network_manager.broadcast_message(message, exclude_client=sender.client_id)
    
    def _handle_full_sync_request(self, message, sender):
        """Handle full sync request."""
        if self.network_manager.is_server:
            self._send_full_sync_to_client(sender)
    
    def _handle_full_sync_data(self, message, sender):
        """Handle full sync data."""
        actors_data = message.data.get('actors', [])
        
        # Clear existing networked actors
        for actor in list(self.networked_actors.values()):
            actor.destroy()
        self.networked_actors.clear()
        self.actor_owners.clear()
        
        # Recreate all actors
        for actor_data in actors_data:
            network_id = actor_data['network_id']
            owner_id = actor_data['owner_id']
            serialized_actor = actor_data['actor_data']
            
            actor = NetworkSerialization.deserialize_actor(serialized_actor)
            if actor:
                # Add NetworkComponent
                network_component = NetworkComponent(owner_id, network_manager=self.network_manager)
                network_component.network_id = network_id
                network_component.spawned_on_network = True
                actor.add_component(network_component)
                
                # Register and add to scene
                self.networked_actors[network_id] = actor
                self.actor_owners[network_id] = owner_id
                
                if self.network_manager.game and self.network_manager.game.current_scene:
                    self.network_manager.game.current_scene.add_actor(actor)
    
    def _send_full_sync_to_client(self, client):
        """Send full synchronization data to a client."""
        actors_data = []
        
        for network_id, actor in self.networked_actors.items():
            actors_data.append({
                'network_id': network_id,
                'owner_id': self.actor_owners.get(network_id, "server"),
                'actor_data': NetworkSerialization.serialize_actor(actor)
            })
        
        message = NetworkMessage(
            MessageType.FULL_SYNC_DATA,
            {'actors': actors_data}
        )
        
        client.send_message(message)
    
    def _on_actor_spawned(self, actor):
        """Callback for when an actor is spawned."""
        pass
    
    def _on_actor_destroyed(self, network_id):
        """Callback for when an actor is destroyed."""
        pass


# Global networked actor manager
_networked_actor_manager = NetworkedActorManager()

def spawn_network_actor(actor: Actor, owner_id: str = None) -> bool:
    """Spawn an actor on the network."""
    return _networked_actor_manager.spawn_network_actor(actor, owner_id)

def destroy_network_actor(actor: Actor) -> bool:
    """Destroy a networked actor."""
    return _networked_actor_manager.destroy_network_actor(actor)

def request_full_sync():
    """Request full synchronization from server."""
    _networked_actor_manager.request_full_sync()

def get_networked_actor_manager() -> NetworkedActorManager:
    """Get the global networked actor manager."""
    return _networked_actor_manager
