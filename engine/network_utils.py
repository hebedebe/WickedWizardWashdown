"""
Network utilities for advanced networking features.
Includes scene synchronization, player management, and optimization utilities.
"""

from typing import Dict, Any, Optional, List
from .networking import NetworkManager, NetworkMessage, MessageType, get_network_manager
from .network_components import NetworkedActorManager, get_networked_actor_manager
from .scene import Scene


class NetworkedSceneManager:
    """Manages networked scene changes and synchronization."""
    
    def __init__(self):
        self.network_manager = get_network_manager()
        self.networked_actor_manager = get_networked_actor_manager()
        
        # Setup network callbacks
        self.network_manager.on_scene_changed = self._on_scene_changed
    
    def change_scene_networked(self, scene_name: str) -> bool:
        """Change scene and synchronize across network."""
        if not self.network_manager.is_connected:
            return False
        
        # Only server can initiate scene changes
        if not self.network_manager.is_server:
            return False
        
        # Send scene change message
        message = NetworkMessage(
            MessageType.SCENE_CHANGE,
            {'scene_name': scene_name}
        )
        
        self.network_manager.broadcast_message(message)
        
        # Change scene locally
        if self.network_manager.game:
            self.network_manager.game.load_scene(scene_name)
        
        return True
    
    def _on_scene_changed(self, scene_name: str):
        """Handle scene change from network."""
        if self.network_manager.game:
            self.network_manager.game.load_scene(scene_name)
            
            # Request full sync after scene change
            if self.network_manager.is_client:
                self.networked_actor_manager.request_full_sync()


class PlayerManager:
    """Manages player connections and data."""
    
    def __init__(self):
        self.network_manager = get_network_manager()
        self.players: Dict[str, Dict[str, Any]] = {}  # client_id -> player_data
        
        # Setup callbacks
        self.network_manager.on_client_connected = self._on_client_connected
        self.network_manager.on_client_disconnected = self._on_client_disconnected
    
    def get_player_count(self) -> int:
        """Get current number of players."""
        if self.network_manager.is_server:
            return len(self.players) + 1  # +1 for server
        elif self.network_manager.is_client:
            return len(self.players)
        return 0
    
    def get_max_players(self) -> int:
        """Get maximum number of players."""
        return self.network_manager.max_players
    
    def is_room_full(self) -> bool:
        """Check if the room is full."""
        return self.get_player_count() >= self.get_max_players()
    
    def get_player_list(self) -> List[str]:
        """Get list of connected player IDs."""
        player_ids = list(self.players.keys())
        if self.network_manager.is_server:
            player_ids.append("server")
        return player_ids
    
    def set_player_data(self, player_id: str, data: Dict[str, Any]):
        """Set data for a player."""
        if player_id in self.players:
            self.players[player_id].update(data)
        else:
            self.players[player_id] = data.copy()
    
    def get_player_data(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Get data for a player."""
        return self.players.get(player_id)
    
    def _on_client_connected(self, client_id: str):
        """Handle client connection."""
        self.players[client_id] = {
            'id': client_id,
            'connected_at': time.time(),
            'ping': 0.0
        }
        print(f"Player {client_id} connected. Total players: {self.get_player_count()}")
    
    def _on_client_disconnected(self, client_id: str):
        """Handle client disconnection."""
        if client_id in self.players:
            del self.players[client_id]
        print(f"Player {client_id} disconnected. Total players: {self.get_player_count()}")


class NetworkOptimizer:
    """Optimizes network traffic and performance."""
    
    def __init__(self):
        self.network_manager = get_network_manager()
        
        # Traffic statistics
        self.bytes_sent = 0
        self.bytes_received = 0
        self.messages_sent = 0
        self.messages_received = 0
        
        # Optimization settings
        self.compression_enabled = False
        self.delta_compression = True  # Only send changed data
        self.priority_queue = []  # High priority messages
        
    def enable_compression(self, enabled: bool = True):
        """Enable/disable message compression."""
        self.compression_enabled = enabled
    
    def enable_delta_compression(self, enabled: bool = True):
        """Enable/disable delta compression (only send changes)."""
        self.delta_compression = enabled
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics."""
        return {
            'bytes_sent': self.bytes_sent,
            'bytes_received': self.bytes_received,
            'messages_sent': self.messages_sent,
            'messages_received': self.messages_received,
            'connected_clients': len(self.network_manager.clients) if self.network_manager.is_server else 1,
            'is_server': self.network_manager.is_server,
            'is_connected': self.network_manager.is_connected
        }
    
    def optimize_message(self, message: NetworkMessage) -> NetworkMessage:
        """Optimize a message before sending."""
        # Apply compression if enabled
        if self.compression_enabled:
            message = self._compress_message(message)
        
        # Apply delta compression for component updates
        if self.delta_compression and message.type == MessageType.COMPONENT_UPDATE:
            message = self._delta_compress_components(message)
        
        return message
    
    def _compress_message(self, message: NetworkMessage) -> NetworkMessage:
        """Apply compression to message data."""
        # Simple compression - remove redundant data
        # In a real implementation, you might use zlib or similar
        return message
    
    def _delta_compress_components(self, message: NetworkMessage) -> NetworkMessage:
        """Apply delta compression to component updates."""
        # Only include changed component data
        # This would require tracking previous states
        return message


class NetworkDebugger:
    """Debugging tools for network issues."""
    
    def __init__(self):
        self.network_manager = get_network_manager()
        self.message_log: List[Dict[str, Any]] = []
        self.max_log_size = 1000
        
    def log_message(self, message: NetworkMessage, direction: str, peer: str):
        """Log a network message."""
        log_entry = {
            'timestamp': time.time(),
            'direction': direction,  # 'sent' or 'received'
            'peer': peer,
            'type': message.type.value,
            'size': len(str(message.to_dict())),
            'data': message.data
        }
        
        self.message_log.append(log_entry)
        
        # Trim log if too large
        if len(self.message_log) > self.max_log_size:
            self.message_log = self.message_log[-self.max_log_size:]
    
    def get_recent_messages(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent network messages."""
        return self.message_log[-count:]
    
    def get_message_stats(self) -> Dict[str, Any]:
        """Get statistics about network messages."""
        if not self.message_log:
            return {}
        
        sent_count = sum(1 for msg in self.message_log if msg['direction'] == 'sent')
        received_count = sum(1 for msg in self.message_log if msg['direction'] == 'received')
        total_size = sum(msg['size'] for msg in self.message_log)
        
        return {
            'total_messages': len(self.message_log),
            'sent_messages': sent_count,
            'received_messages': received_count,
            'total_bytes': total_size,
            'average_message_size': total_size / len(self.message_log) if self.message_log else 0
        }
    
    def diagnose_connection_issues(self) -> List[str]:
        """Diagnose potential connection issues."""
        issues = []
        
        if not self.network_manager.is_connected:
            issues.append("Not connected to network")
        
        # Check for high message frequency
        recent_messages = self.get_recent_messages(50)
        if len(recent_messages) >= 50:
            time_span = recent_messages[-1]['timestamp'] - recent_messages[0]['timestamp']
            if time_span > 0:
                message_rate = len(recent_messages) / time_span
                if message_rate > 100:  # More than 100 messages per second
                    issues.append(f"High message rate: {message_rate:.1f} msg/sec")
        
        # Check for large messages
        large_messages = [msg for msg in recent_messages if msg['size'] > 1024]
        if large_messages:
            issues.append(f"Found {len(large_messages)} large messages (>1KB)")
        
        # Check ping times
        if self.network_manager.is_client and self.network_manager.server_client:
            last_ping = time.time() - self.network_manager.server_client.last_ping
            if last_ping > 10.0:
                issues.append(f"High ping: {last_ping:.1f}s since last response")
        
        return issues


# Global instances
_networked_scene_manager = NetworkedSceneManager()
_player_manager = PlayerManager()
_network_optimizer = NetworkOptimizer()
_network_debugger = NetworkDebugger()

def get_networked_scene_manager() -> NetworkedSceneManager:
    """Get the global networked scene manager."""
    return _networked_scene_manager

def get_player_manager() -> PlayerManager:
    """Get the global player manager."""
    return _player_manager

def get_network_optimizer() -> NetworkOptimizer:
    """Get the global network optimizer."""
    return _network_optimizer

def get_network_debugger() -> NetworkDebugger:
    """Get the global network debugger."""
    return _network_debugger

def change_scene_networked(scene_name: str) -> bool:
    """Change scene across the network."""
    return _networked_scene_manager.change_scene_networked(scene_name)

import time
