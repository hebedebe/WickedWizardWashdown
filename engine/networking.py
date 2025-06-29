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


class NetworkPriority(Enum):
    """Network message priority levels."""
    INSTANT = "instant"      # Chat messages, critical events
    HIGH = "high"           # Player actions, game state changes
    MEDIUM = "medium"       # Regular updates, position sync
    LOW = "low"             # Background data, statistics


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
    
    # Custom/Application messages
    CUSTOM_MESSAGE = "custom_message"
    
    # Synchronization
    FULL_SYNC_REQUEST = "full_sync_request"
    FULL_SYNC_DATA = "full_sync_data"
    
    # Heartbeat
    PING = "ping"
    PONG = "pong"


class NetworkMessage:
    """Network message container with priority support."""
    
    def __init__(self, msg_type: MessageType, data: Dict[str, Any], 
                 sender_id: str = None, timestamp: float = None, 
                 priority: NetworkPriority = NetworkPriority.MEDIUM):
        self.type = msg_type
        self.data = data
        self.sender_id = sender_id
        self.timestamp = timestamp or time.time()
        self.priority = priority
        self.id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for JSON serialization."""
        return {
            'type': self.type.value,
            'data': self.data,
            'sender_id': self.sender_id,
            'timestamp': self.timestamp,
            'priority': self.priority.value,
            'id': self.id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NetworkMessage':
        """Create message from dictionary."""
        priority = NetworkPriority(data.get('priority', NetworkPriority.MEDIUM.value))
        return cls(
            MessageType(data['type']),
            data['data'],
            data.get('sender_id'),
            data.get('timestamp'),
            priority
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
        """Disconnect the client with proper thread cleanup."""
        if not self.connected:
            return
            
        print(f"Disconnecting client {self.client_id}")
        self.connected = False
        
        # Send shutdown signal to send thread
        try:
            self.outbound_queue.put(None, timeout=0.1)
        except queue.Full:
            pass
        
        # Close socket to break receive thread
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            self.socket.close()
        except:
            pass
        
        # Wait for threads to finish
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=1.0)
        if self.send_thread and self.send_thread.is_alive():
            self.send_thread.join(timeout=1.0)
            
        print(f"Client {self.client_id} disconnected cleanly")


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
        
        # Priority-based message queues
        self.instant_queue = queue.PriorityQueue()  # For chat and critical messages
        self.high_queue = queue.PriorityQueue()     # For player actions
        self.medium_queue = queue.PriorityQueue()   # For regular updates
        self.low_queue = queue.PriorityQueue()      # For background data
        
        # Counter for unique priority queue ordering
        self.message_counter = 0
        self.counter_lock = threading.Lock()
        
        # Update rate control per priority
        self.priority_rates = {
            NetworkPriority.INSTANT: 0.0,    # No delay - immediate
            NetworkPriority.HIGH: 1.0/60.0,  # 60 FPS
            NetworkPriority.MEDIUM: 1.0/20.0, # 20 FPS
            NetworkPriority.LOW: 1.0/5.0      # 5 FPS
        }
        self.last_priority_update = {priority: 0.0 for priority in NetworkPriority}
        
        # Callbacks
        self.on_client_connected: Optional[Callable[[str], None]] = None
        self.on_client_disconnected: Optional[Callable[[str], None]] = None
        self.on_actor_spawned: Optional[Callable[[Actor], None]] = None
        self.on_actor_destroyed: Optional[Callable[[str], None]] = None
        self.on_scene_changed: Optional[Callable[[str], None]] = None
        self.on_custom_message: Optional[Callable[[str, Dict[str, Any], str, float], None]] = None
        
        # Custom message handlers by event type
        self.custom_message_handlers: Dict[str, List[Callable]] = {}
        
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
            print(f"Cannot host: NetworkManager already in role {self.role.value}")
            return False
        
        if self.is_running:
            print("Cannot host: NetworkManager is already running")
            return False
        
        # Check if another instance is already hosting on this port
        if self._is_port_in_use(ip, port):
            print(f"Cannot host: Another server is already running on {ip}:{port}")
            return False
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # DO NOT use SO_REUSEADDR for hosting - we want exclusive port access
            # This prevents multiple hosts on the same port
            # self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Set socket to non-blocking to allow proper error handling
            self.server_socket.settimeout(5.0)  # 5 second timeout for bind
            
            self.server_socket.bind((ip, port))
            self.server_socket.listen(self.max_players - 1)  # -1 for host
            
            # Reset to blocking after successful bind
            self.server_socket.settimeout(None)
            
            self.role = NetworkRole.SERVER
            self.is_running = True
            
            # Start listening for connections
            self.listen_thread = threading.Thread(
                target=self._listen_for_connections, 
                daemon=True
            )
            self.listen_thread.start()
            
            print(f"Server started successfully on {ip}:{port}")
            return True
            
        except OSError as e:
            if e.errno == 10048:  # Windows: Address already in use
                print(f"Cannot host: Port {port} is already in use by another application")
            elif e.errno == 98:  # Linux: Address already in use
                print(f"Cannot host: Port {port} is already in use by another application")
            else:
                print(f"Failed to start server on {ip}:{port}: {e}")
            
            if self.server_socket:
                self.server_socket.close()
                self.server_socket = None
            self.role = NetworkRole.NONE
            self.is_running = False
            return False
            
        except socket.error as e:
            print(f"Socket error starting server on {ip}:{port}: {e}")
            if self.server_socket:
                self.server_socket.close()
                self.server_socket = None
            self.role = NetworkRole.NONE
            self.is_running = False
            return False
            
        except Exception as e:
            print(f"Unexpected error starting server: {e}")
            if self.server_socket:
                self.server_socket.close()
                self.server_socket = None
            self.role = NetworkRole.NONE
            self.is_running = False
            return False
    
    def _is_port_in_use(self, ip: str, port: int) -> bool:
        """Check if a port is already in use."""
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(1.0)
            result = test_socket.connect_ex((ip, port))
            test_socket.close()
            
            # If connect_ex returns 0, the port is in use
            return result == 0
        except Exception:
            # If we can't test, assume it's not in use
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
        """Disconnect from network with proper cleanup."""
        if not self.is_running:
            return
        
        print("Shutting down network...")
        self.is_running = False
        
        if self.is_server:
            # Disconnect all clients first
            for client in list(self.clients.values()):
                try:
                    client.disconnect()
                except Exception as e:
                    print(f"Error disconnecting client: {e}")
            self.clients.clear()
            
            # Close server socket
            if self.server_socket:
                try:
                    self.server_socket.shutdown(socket.SHUT_RDWR)
                except:
                    pass  # Socket might already be closed
                self.server_socket.close()
                self.server_socket = None
            
            # Wait for listen thread to finish
            if self.listen_thread and self.listen_thread.is_alive():
                print("Waiting for server thread to finish...")
                self.listen_thread.join(timeout=2.0)
                if self.listen_thread.is_alive():
                    print("Warning: Server thread did not shutdown cleanly")
                
        elif self.is_client:
            # Disconnect from server
            if self.server_client:
                try:
                    disconnect_msg = NetworkMessage(
                        MessageType.DISCONNECT,
                        {"client_id": self.client_id}
                    )
                    self.server_client.send_message(disconnect_msg)
                    self.server_client.disconnect()
                except Exception as e:
                    print(f"Error sending disconnect message: {e}")
                self.server_client = None
            
            if self.client_socket:
                try:
                    self.client_socket.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                self.client_socket.close()
                self.client_socket = None
        
        self.role = NetworkRole.NONE
        print("Network disconnected cleanly")
    
    def _listen_for_connections(self):
        """Listen for incoming client connections (server only)."""
        print("Server listening for connections...")
        while self.is_running and self.server_socket:
            try:
                # Set a timeout so we can check is_running periodically
                self.server_socket.settimeout(1.0)
                client_socket, address = self.server_socket.accept()
                
                # Reset to blocking mode for the client socket
                client_socket.settimeout(None)
                
                # Check if we have room for more clients
                if len(self.clients) >= self.max_players - 1:
                    print(f"Server full, rejecting connection from {address}")
                    try:
                        client_socket.close()
                    except:
                        pass
                    continue
                
                # Create client wrapper with temporary ID
                # The real client_id will be set when we receive the connect request
                temp_client_id = f"temp_{int(time.time())}_{len(self.clients)}"
                client = NetworkClient(client_socket, temp_client_id, address)
                
                # Store with temporary ID for now
                self.clients[temp_client_id] = client
                client.start_threads(self)
                
                print(f"New connection from {address}, waiting for connect request...")
                
            except socket.timeout:
                # Timeout is expected, just continue the loop to check is_running
                continue
            except OSError as e:
                if self.is_running:
                    print(f"Server socket error: {e}")
                break
            except Exception as e:
                if self.is_running:
                    print(f"Unexpected error in server listen thread: {e}")
                break
        
        print("Server listen thread ended")
    
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
        elif message.type == MessageType.CUSTOM_MESSAGE:
            self._handle_custom_message(message, sender)
    
    def _handle_connect_request(self, message: NetworkMessage, sender: NetworkClient):
        """Handle client connection request."""
        if not self.is_server:
            return
        
        client_id = message.data.get("client_id")
        if not client_id:
            print("Connect request missing client_id")
            return
        
        # Get the old temporary ID
        old_temp_id = sender.client_id
        
        # Update the client with the real ID
        sender.client_id = client_id
        
        # Update the clients dictionary with the new ID
        if old_temp_id in self.clients:
            del self.clients[old_temp_id]
        self.clients[client_id] = sender
        
        print(f"Client {client_id} connected (was {old_temp_id})")
        
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
    
    def _handle_custom_message(self, message: NetworkMessage, sender: NetworkClient):
        """Handle custom messages with priority-based processing."""
        # For instant messages, process immediately
        if message.priority == NetworkPriority.INSTANT:
            self._handle_custom_message_locally(message)
            
            # Broadcast to other clients immediately if we're the server
            if self.is_server:
                self.broadcast_message(message, exclude_client=sender.client_id)
        else:
            # Queue for priority-based processing
            self._queue_message_by_priority(message)
    
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
    
    def send_custom_message(self, event_type: str, data: Dict[str, Any], 
                           priority: NetworkPriority = NetworkPriority.MEDIUM, 
                           sender_name: str = None):
        """Send a custom application message with specified priority."""
        custom_msg = NetworkMessage(
            MessageType.CUSTOM_MESSAGE,
            {
                "event_type": event_type,
                "event_data": data,
                "sender_name": sender_name or "Unknown",
                "timestamp": time.time()
            },
            sender_id=self.client_id,
            priority=priority
        )
        
        if self.is_server:
            # Broadcast to all clients
            self.broadcast_message(custom_msg)
            # Also handle locally for the host
            self._handle_custom_message_locally(custom_msg)
        elif self.is_client:
            # Send to server
            self.send_to_server(custom_msg)
    
    def register_custom_handler(self, event_type: str, handler: Callable[[Dict[str, Any], str, float], None]):
        """Register a handler for a specific custom message event type."""
        if event_type not in self.custom_message_handlers:
            self.custom_message_handlers[event_type] = []
        self.custom_message_handlers[event_type].append(handler)
    
    def unregister_custom_handler(self, event_type: str, handler: Callable):
        """Unregister a custom message handler."""
        if event_type in self.custom_message_handlers:
            if handler in self.custom_message_handlers[event_type]:
                self.custom_message_handlers[event_type].remove(handler)
    
    def _handle_custom_message_locally(self, message: NetworkMessage):
        """Handle custom message locally without broadcasting."""
        data = message.data
        event_type = data.get("event_type", "unknown")
        event_data = data.get("event_data", {})
        sender_name = data.get("sender_name", "Unknown")
        timestamp = data.get("timestamp", time.time())
        
        # Call the general custom message callback
        if self.on_custom_message:
            self.on_custom_message(event_type, event_data, sender_name, timestamp)
        
        # Call specific handlers for this event type
        if event_type in self.custom_message_handlers:
            for handler in self.custom_message_handlers[event_type]:
                try:
                    handler(event_data, sender_name, timestamp)
                except Exception as e:
                    print(f"Error in custom message handler for {event_type}: {e}")
    
    # Convenience methods for common message types
    def send_chat_message(self, sender_name: str, message: str):
        """Send a chat message (convenience method using custom messages)."""
        self.send_custom_message(
            "chat", 
            {"message": message}, 
            NetworkPriority.INSTANT, 
            sender_name
        )
    
    def announce_player_joined(self, player_name: str):
        """Announce that a player joined (convenience method)."""
        self.send_custom_message(
            "player_join", 
            {"player_name": player_name}, 
            NetworkPriority.HIGH
        )
        
    def announce_player_left(self, player_name: str):
        """Announce that a player left (convenience method)."""
        self.send_custom_message(
            "player_leave", 
            {"player_name": player_name}, 
            NetworkPriority.HIGH
        )
    
    def update_lobby_info(self, lobby_data: Dict[str, Any]):
        """Update lobby information (convenience method)."""
        self.send_custom_message(
            "lobby_update", 
            lobby_data, 
            NetworkPriority.MEDIUM
        )
    
    def _process_priority_queues(self):
        """Process messages based on priority and timing."""
        current_time = time.time()
        
        # Process instant messages immediately (chat, critical events)
        self._process_queue_with_priority(NetworkPriority.INSTANT, current_time)
        
        # Process other queues based on their update rates
        for priority in [NetworkPriority.HIGH, NetworkPriority.MEDIUM, NetworkPriority.LOW]:
            if current_time - self.last_priority_update[priority] >= self.priority_rates[priority]:
                self._process_queue_with_priority(priority, current_time)
                self.last_priority_update[priority] = current_time
    
    def _process_queue_with_priority(self, priority: NetworkPriority, current_time: float):
        """Process a specific priority queue."""
        queue_map = {
            NetworkPriority.INSTANT: self.instant_queue,
            NetworkPriority.HIGH: self.high_queue,
            NetworkPriority.MEDIUM: self.medium_queue,
            NetworkPriority.LOW: self.low_queue
        }
        
        target_queue = queue_map.get(priority)
        if not target_queue:
            return
        
        # Process a batch of messages from this priority queue
        batch_size = 10 if priority == NetworkPriority.INSTANT else 5
        processed = 0
        
        while not target_queue.empty() and processed < batch_size:
            try:
                # Unpack the tuple: (timestamp, counter, message)
                _, _, message = target_queue.get_nowait()
                self._handle_priority_message(message)
                processed += 1
            except queue.Empty:
                break
    
    def _handle_priority_message(self, message: NetworkMessage):
        """Handle a message from the priority queue system."""
        # Route the message based on its type
        if message.type == MessageType.CUSTOM_MESSAGE:
            self._handle_custom_message_locally(message)
        # Add more message type handlers as needed
    
    def _queue_message_by_priority(self, message: NetworkMessage):
        """Queue a message based on its priority."""
        queue_map = {
            NetworkPriority.INSTANT: self.instant_queue,
            NetworkPriority.HIGH: self.high_queue,
            NetworkPriority.MEDIUM: self.medium_queue,
            NetworkPriority.LOW: self.low_queue
        }
        
        target_queue = queue_map.get(message.priority, self.medium_queue)
        
        # Use timestamp as primary priority, counter as tiebreaker to avoid comparison issues
        with self.counter_lock:
            counter = self.message_counter
            self.message_counter += 1
        
        # Create tuple: (timestamp, counter, message) - no direct message comparison needed
        priority_item = (message.timestamp, counter, message)
        target_queue.put(priority_item)

    def update(self):
        """Update network manager with priority-based processing."""
        current_time = time.time()
        
        # Always process instant priority messages (chat, critical events)
        self._process_priority_queues()
        
        # Throttle regular updates
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
_network_manager = None

def get_network_manager() -> NetworkManager:
    """Get the global network manager instance."""
    global _network_manager
    if _network_manager is None:
        _network_manager = NetworkManager()
    return _network_manager

def reset_network_manager():
    """Reset the global network manager (for testing/cleanup)."""
    global _network_manager
    if _network_manager:
        _network_manager.disconnect()
        _network_manager = None
