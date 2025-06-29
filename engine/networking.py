"""
Core networking system for multiplayer game synchronization.
Handles client-server communication, actor spawning, and component synchronization.
"""

import socket
import threading
import time
import json
import queue
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
import uuid

from .actor import Actor, Component


class NetworkRole(Enum):
    """Network role of the current instance."""
    SERVER = "server"
    CLIENT = "client"
    NONE = "none"


class MessageType(Enum):
    """Types of network messages."""
    # Connection
    CONNECT_REQUEST = "connect_request"
    CONNECT_RESPONSE = "connect_response"
    DISCONNECT = "disconnect"
    
    # Actor management
    SPAWN_ACTOR = "spawn_actor"
    DESTROY_ACTOR = "destroy_actor"
    ACTOR_UPDATE = "actor_update"
    
    # Component synchronization
    COMPONENT_UPDATE = "component_update"
    COMPONENT_ADD = "component_add"
    COMPONENT_REMOVE = "component_remove"
    
    # Scene management
    SCENE_CHANGE = "scene_change"
    
    # Synchronization
    FULL_SYNC_REQUEST = "full_sync_request"
    FULL_SYNC_DATA = "full_sync_data"
    
    # Heartbeat
    PING = "ping"
    PONG = "pong"


class NetworkMessage:
    """Network message container."""
    
    def __init__(self, msg_type: MessageType, data: Dict[str, Any], 
                 sender_id: str = None, timestamp: float = None):
        self.type = msg_type
        self.data = data
        self.sender_id = sender_id
        self.timestamp = timestamp or time.time()
        self.id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for JSON serialization."""
        return {
            'type': self.type.value,
            'data': self.data,
            'sender_id': self.sender_id,
            'timestamp': self.timestamp,
            'id': self.id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NetworkMessage':
        """Create message from dictionary."""
        return cls(
            MessageType(data['type']),
            data['data'],
            data.get('sender_id'),
            data.get('timestamp')
        )


class NetworkClient:
    """Handles network communication for a single client."""
    
    def __init__(self, socket_obj: socket.socket, client_id: str, address: tuple):
        self.socket = socket_obj
        self.client_id = client_id
        self.address = address
        self.connected = True
        self.last_ping = time.time()
        
        # Message queues
        self.outbound_queue = queue.Queue()
        self.receive_thread = None
        self.send_thread = None
        
        # Known actors and components for this client
        self.known_actors: Set[str] = set()
        self.last_sync_time = 0.0
    
    def start_threads(self, manager: 'NetworkManager'):
        """Start receive and send threads."""
        self.receive_thread = threading.Thread(
            target=self._receive_loop, 
            args=(manager,), 
            daemon=True
        )
        self.send_thread = threading.Thread(
            target=self._send_loop, 
            daemon=True
        )
        self.receive_thread.start()
        self.send_thread.start()
    
    def _receive_loop(self, manager: 'NetworkManager'):
        """Receive messages from client."""
        buffer = ""
        while self.connected:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            msg_data = json.loads(line.strip())
                            message = NetworkMessage.from_dict(msg_data)
                            manager._handle_message(message, self)
                        except (json.JSONDecodeError, ValueError) as e:
                            print(f"Error parsing message from {self.client_id}: {e}")
                            
            except (ConnectionResetError, ConnectionAbortedError, OSError):
                break
        
        self.connected = False
        manager._on_client_disconnected(self)
    
    def _send_loop(self):
        """Send messages to client."""
        while self.connected:
            try:
                message = self.outbound_queue.get(timeout=0.1)
                if message is None:  # Shutdown signal
                    break
                
                msg_json = json.dumps(message.to_dict()) + '\n'
                self.socket.send(msg_json.encode('utf-8'))
                
            except queue.Empty:
                continue
            except (ConnectionResetError, ConnectionAbortedError, OSError):
                break
    
    def send_message(self, message: NetworkMessage):
        """Queue a message to be sent."""
        if self.connected:
            self.outbound_queue.put(message)
    
    def disconnect(self):
        """Disconnect the client."""
        self.connected = False
        self.outbound_queue.put(None)  # Shutdown signal
        try:
            self.socket.close()
        except:
            pass


class NetworkManager:
    """Central network manager for client-server communication."""
    
    def __init__(self):
        self.role = NetworkRole.NONE
        self.max_players = 4  # Including host
        
        # Server-specific
        self.server_socket: Optional[socket.socket] = None
        self.clients: Dict[str, NetworkClient] = {}
        self.listen_thread: Optional[threading.Thread] = None
        
        # Client-specific
        self.client_socket: Optional[socket.socket] = None
        self.server_client: Optional[NetworkClient] = None
        self.client_id = str(uuid.uuid4())
        
        # Network state
        self.is_running = False
        self.last_update_time = 0.0
        self.update_rate = 20.0  # 20 updates per second
        
        # Callbacks
        self.on_client_connected: Optional[Callable[[str], None]] = None
        self.on_client_disconnected: Optional[Callable[[str], None]] = None
        self.on_actor_spawned: Optional[Callable[[Actor], None]] = None
        self.on_actor_destroyed: Optional[Callable[[str], None]] = None
        self.on_scene_changed: Optional[Callable[[str], None]] = None
        
        # Game reference
        self.game = None
    
    @property
    def is_server(self) -> bool:
        """Check if this instance is the server."""
        return self.role == NetworkRole.SERVER
    
    @property
    def is_client(self) -> bool:
        """Check if this instance is a client."""
        return self.role == NetworkRole.CLIENT
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to network."""
        if self.is_server:
            return self.is_running
        elif self.is_client:
            return self.server_client and self.server_client.connected
        return False
    
    def set_max_players(self, max_players: int):
        """Set maximum number of players."""
        self.max_players = max_players
    
    def host(self, ip: str = "localhost", port: int = 8888) -> bool:
        """Start hosting a server."""
        if self.role != NetworkRole.NONE:
            return False
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((ip, port))
            self.server_socket.listen(self.max_players - 1)  # -1 for host
            
            self.role = NetworkRole.SERVER
            self.is_running = True
            
            # Start listening for connections
            self.listen_thread = threading.Thread(
                target=self._listen_for_connections, 
                daemon=True
            )
            self.listen_thread.start()
            
            print(f"Server started on {ip}:{port}")
            return True
            
        except Exception as e:
            print(f"Failed to start server: {e}")
            return False
    
    def connect(self, ip: str = "localhost", port: int = 8888) -> bool:
        """Connect to a server as a client."""
        if self.role != NetworkRole.NONE:
            return False
        
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip, port))
            
            # Create client wrapper for server communication
            self.server_client = NetworkClient(
                self.client_socket, 
                "server", 
                (ip, port)
            )
            
            self.role = NetworkRole.CLIENT
            self.is_running = True
            
            # Start communication threads
            self.server_client.start_threads(self)
            
            # Send connection request
            connect_msg = NetworkMessage(
                MessageType.CONNECT_REQUEST,
                {"client_id": self.client_id}
            )
            self.server_client.send_message(connect_msg)
            
            print(f"Connected to server at {ip}:{port}")
            return True
            
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from network."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.is_server:
            # Disconnect all clients
            for client in list(self.clients.values()):
                client.disconnect()
            self.clients.clear()
            
            # Close server socket
            if self.server_socket:
                self.server_socket.close()
                self.server_socket = None
                
        elif self.is_client:
            # Disconnect from server
            if self.server_client:
                disconnect_msg = NetworkMessage(
                    MessageType.DISCONNECT,
                    {"client_id": self.client_id}
                )
                self.server_client.send_message(disconnect_msg)
                self.server_client.disconnect()
                self.server_client = None
            
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
        
        self.role = NetworkRole.NONE
        print("Disconnected from network")
    
    def _listen_for_connections(self):
        """Listen for incoming client connections (server only)."""
        while self.is_running:
            try:
                client_socket, address = self.server_socket.accept()
                
                # Check if we have room for more clients
                if len(self.clients) >= self.max_players - 1:
                    client_socket.close()
                    continue
                
                # Create client wrapper
                client_id = str(uuid.uuid4())
                client = NetworkClient(client_socket, client_id, address)
                
                self.clients[client_id] = client
                client.start_threads(self)
                
                print(f"Client {client_id} connected from {address}")
                
            except OSError:
                break
    
    def _handle_message(self, message: NetworkMessage, sender: NetworkClient):
        """Handle incoming network messages."""
        if message.type == MessageType.CONNECT_REQUEST:
            self._handle_connect_request(message, sender)
        elif message.type == MessageType.DISCONNECT:
            self._handle_disconnect(message, sender)
        elif message.type == MessageType.SPAWN_ACTOR:
            self._handle_spawn_actor(message, sender)
        elif message.type == MessageType.DESTROY_ACTOR:
            self._handle_destroy_actor(message, sender)
        elif message.type == MessageType.ACTOR_UPDATE:
            self._handle_actor_update(message, sender)
        elif message.type == MessageType.COMPONENT_UPDATE:
            self._handle_component_update(message, sender)
        elif message.type == MessageType.SCENE_CHANGE:
            self._handle_scene_change(message, sender)
        elif message.type == MessageType.FULL_SYNC_REQUEST:
            self._handle_full_sync_request(message, sender)
        elif message.type == MessageType.FULL_SYNC_DATA:
            self._handle_full_sync_data(message, sender)
        elif message.type == MessageType.PING:
            self._handle_ping(message, sender)
        elif message.type == MessageType.PONG:
            self._handle_pong(message, sender)
    
    def _handle_connect_request(self, message: NetworkMessage, sender: NetworkClient):
        """Handle client connection request."""
        if not self.is_server:
            return
        
        client_id = message.data.get("client_id")
        if client_id:
            sender.client_id = client_id
            
            # Send connection response
            response = NetworkMessage(
                MessageType.CONNECT_RESPONSE,
                {
                    "accepted": True,
                    "server_id": "server",
                    "client_id": client_id
                }
            )
            sender.send_message(response)
            
            # Notify game of new client
            if self.on_client_connected:
                self.on_client_connected(client_id)
            
            # Send full sync to new client
            self._send_full_sync(sender)
    
    def _handle_disconnect(self, message: NetworkMessage, sender: NetworkClient):
        """Handle client disconnect."""
        client_id = message.data.get("client_id")
        if client_id and client_id in self.clients:
            self._on_client_disconnected(self.clients[client_id])
    
    def _on_client_disconnected(self, client: NetworkClient):
        """Handle client disconnection."""
        if client.client_id in self.clients:
            del self.clients[client.client_id]
        
        if self.on_client_disconnected:
            self.on_client_disconnected(client.client_id)
        
        print(f"Client {client.client_id} disconnected")
    
    def _handle_spawn_actor(self, message: NetworkMessage, sender: NetworkClient):
        """Handle networked actor spawning."""
        # Implementation will be in network_components.py
        pass
    
    def _handle_destroy_actor(self, message: NetworkMessage, sender: NetworkClient):
        """Handle networked actor destruction."""
        # Implementation will be in network_components.py
        pass
    
    def _handle_actor_update(self, message: NetworkMessage, sender: NetworkClient):
        """Handle actor updates."""
        # Implementation will be in network_components.py
        pass
    
    def _handle_component_update(self, message: NetworkMessage, sender: NetworkClient):
        """Handle component updates."""
        # Implementation will be in network_components.py
        pass
    
    def _handle_scene_change(self, message: NetworkMessage, sender: NetworkClient):
        """Handle scene changes."""
        scene_name = message.data.get("scene_name")
        if scene_name and self.game:
            if self.on_scene_changed:
                self.on_scene_changed(scene_name)
    
    def _handle_full_sync_request(self, message: NetworkMessage, sender: NetworkClient):
        """Handle full synchronization request."""
        if self.is_server:
            self._send_full_sync(sender)
    
    def _handle_full_sync_data(self, message: NetworkMessage, sender: NetworkClient):
        """Handle full synchronization data."""
        # Implementation will be in network_components.py
        pass
    
    def _handle_ping(self, message: NetworkMessage, sender: NetworkClient):
        """Handle ping message."""
        pong = NetworkMessage(MessageType.PONG, {"timestamp": message.timestamp})
        sender.send_message(pong)
    
    def _handle_pong(self, message: NetworkMessage, sender: NetworkClient):
        """Handle pong message."""
        sender.last_ping = time.time()
    
    def _send_full_sync(self, client: NetworkClient):
        """Send full synchronization data to a client."""
        if not self.game or not self.game.current_scene:
            return
        
        # This will be implemented in network_components.py
        # Will send all networked actors and their components
        pass
    
    def broadcast_message(self, message: NetworkMessage, exclude_client: str = None):
        """Broadcast a message to all connected clients."""
        if self.is_server:
            for client_id, client in self.clients.items():
                if client_id != exclude_client:
                    client.send_message(message)
        elif self.is_client and self.server_client:
            self.server_client.send_message(message)
    
    def send_to_server(self, message: NetworkMessage):
        """Send message to server (client only)."""
        if self.is_client and self.server_client:
            self.server_client.send_message(message)
    
    def send_to_client(self, client_id: str, message: NetworkMessage):
        """Send message to specific client (server only)."""
        if self.is_server and client_id in self.clients:
            self.clients[client_id].send_message(message)
    
    def update(self):
        """Update network manager."""
        current_time = time.time()
        
        # Throttle updates
        if current_time - self.last_update_time < 1.0 / self.update_rate:
            return
        
        self.last_update_time = current_time
        
        # Send periodic pings
        if self.is_server:
            for client in self.clients.values():
                if current_time - client.last_ping > 5.0:  # 5 second ping interval
                    ping = NetworkMessage(MessageType.PING, {"timestamp": current_time})
                    client.send_message(ping)
        elif self.is_client and self.server_client:
            if current_time - self.server_client.last_ping > 5.0:
                ping = NetworkMessage(MessageType.PING, {"timestamp": current_time})
                self.server_client.send_message(ping)


# Global network manager instance
_network_manager = NetworkManager()

def get_network_manager() -> NetworkManager:
    """Get the global network manager instance."""
    return _network_manager
