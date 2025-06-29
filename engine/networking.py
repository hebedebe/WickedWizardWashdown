"""
Networking system for multiplayer games.
"""

import socket
import threading
import pickle
import json
import time
from typing import Dict, List, Optional, Callable, Any, Tuple
from abc import ABC, abstractmethod
from enum import Enum
import pygame

class MessageType(Enum):
    """Types of network messages."""
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    GAME_STATE = "game_state"
    PLAYER_INPUT = "player_input"
    CHAT = "chat"
    CUSTOM = "custom"

class NetworkMessage:
    """
    Network message structure.
    """
    
    def __init__(self, msg_type: MessageType, data: Any = None, sender_id: str = None):
        self.type = msg_type
        self.data = data
        self.sender_id = sender_id
        self.timestamp = time.time()
        
    def serialize(self) -> bytes:
        """Serialize message to bytes."""
        try:
            return pickle.dumps(self)
        except pickle.PicklingError as e:
            print(f"Failed to serialize message: {e}")
            return b""
            
    @staticmethod
    def deserialize(data: bytes) -> Optional['NetworkMessage']:
        """Deserialize message from bytes."""
        try:
            return pickle.loads(data)
        except (pickle.UnpicklingError, EOFError) as e:
            print(f"Failed to deserialize message: {e}")
            return None

class NetworkClient:
    """
    Network client for connecting to a game server.
    """
    
    def __init__(self, client_id: str = None):
        self.client_id = client_id or f"client_{int(time.time())}"
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.running = False
        
        # Threading
        self.receive_thread: Optional[threading.Thread] = None
        self.send_queue: List[NetworkMessage] = []
        self.receive_queue: List[NetworkMessage] = []
        self.queue_lock = threading.Lock()
        
        # Event handlers
        self.message_handlers: Dict[MessageType, List[Callable]] = {}
        
        # Connection info
        self.server_address: Optional[Tuple[str, int]] = None
        
    def add_message_handler(self, msg_type: MessageType, handler: Callable) -> None:
        """Add a message handler for a specific message type."""
        if msg_type not in self.message_handlers:
            self.message_handlers[msg_type] = []
        self.message_handlers[msg_type].append(handler)
        
    def remove_message_handler(self, msg_type: MessageType, handler: Callable) -> None:
        """Remove a message handler."""
        if msg_type in self.message_handlers:
            if handler in self.message_handlers[msg_type]:
                self.message_handlers[msg_type].remove(handler)
                
    def connect(self, host: str, port: int) -> bool:
        """Connect to a server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.server_address = (host, port)
            self.connected = True
            self.running = True
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            
            # Send connection message
            connect_msg = NetworkMessage(MessageType.CONNECT, {"client_id": self.client_id})
            self.send_message(connect_msg)
            
            return True
            
        except socket.error as e:
            print(f"Failed to connect to server: {e}")
            self.connected = False
            return False
            
    def disconnect(self) -> None:
        """Disconnect from the server."""
        if self.connected:
            # Send disconnect message
            disconnect_msg = NetworkMessage(MessageType.DISCONNECT, {"client_id": self.client_id})
            self.send_message(disconnect_msg)
            
        self.running = False
        self.connected = False
        
        if self.socket:
            self.socket.close()
            self.socket = None
            
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=1.0)
            
    def send_message(self, message: NetworkMessage) -> None:
        """Queue a message to be sent."""
        message.sender_id = self.client_id
        with self.queue_lock:
            self.send_queue.append(message)
            
    def _receive_loop(self) -> None:
        """Main receive loop running in a separate thread."""
        buffer = b""
        
        while self.running and self.connected:
            try:
                # Receive data
                data = self.socket.recv(4096)
                if not data:
                    print("Server disconnected")
                    self.connected = False
                    break
                    
                buffer += data
                
                # Process complete messages
                while len(buffer) >= 4:  # At least 4 bytes for message length
                    # First 4 bytes contain message length
                    msg_length = int.from_bytes(buffer[:4], byteorder='big')
                    
                    if len(buffer) >= 4 + msg_length:
                        # Extract message
                        msg_data = buffer[4:4 + msg_length]
                        buffer = buffer[4 + msg_length:]
                        
                        # Deserialize and queue message
                        message = NetworkMessage.deserialize(msg_data)
                        if message:
                            with self.queue_lock:
                                self.receive_queue.append(message)
                    else:
                        break  # Wait for more data
                        
            except socket.error as e:
                if self.running:
                    print(f"Receive error: {e}")
                break
                
        self.connected = False
        
    def update(self, dt: float) -> None:
        """Update client and process messages."""
        # Send queued messages
        self._send_queued_messages()
        
        # Process received messages
        self._process_received_messages()
        
    def _send_queued_messages(self) -> None:
        """Send all queued messages."""
        if not self.connected or not self.socket:
            return
            
        with self.queue_lock:
            messages_to_send = self.send_queue.copy()
            self.send_queue.clear()
            
        for message in messages_to_send:
            try:
                # Serialize message
                msg_data = message.serialize()
                
                # Send message length followed by message data
                msg_length = len(msg_data)
                length_bytes = msg_length.to_bytes(4, byteorder='big')
                
                self.socket.sendall(length_bytes + msg_data)
                
            except socket.error as e:
                print(f"Send error: {e}")
                self.connected = False
                break
                
    def _process_received_messages(self) -> None:
        """Process all received messages."""
        with self.queue_lock:
            messages_to_process = self.receive_queue.copy()
            self.receive_queue.clear()
            
        for message in messages_to_process:
            # Call message handlers
            if message.type in self.message_handlers:
                for handler in self.message_handlers[message.type]:
                    handler(message)

class NetworkServer:
    """
    Network server for hosting multiplayer games.
    """
    
    def __init__(self, port: int = 12345):
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.running = False
        
        # Client management
        self.clients: Dict[str, socket.socket] = {}
        self.client_addresses: Dict[str, Tuple[str, int]] = {}
        
        # Threading
        self.accept_thread: Optional[threading.Thread] = None
        self.client_threads: Dict[str, threading.Thread] = {}
        
        # Message handling
        self.message_handlers: Dict[MessageType, List[Callable]] = {}
        self.message_queue: List[Tuple[str, NetworkMessage]] = []
        self.queue_lock = threading.Lock()
        
    def add_message_handler(self, msg_type: MessageType, handler: Callable) -> None:
        """Add a message handler for a specific message type."""
        if msg_type not in self.message_handlers:
            self.message_handlers[msg_type] = []
        self.message_handlers[msg_type].append(handler)
        
    def remove_message_handler(self, msg_type: MessageType, handler: Callable) -> None:
        """Remove a message handler."""
        if msg_type in self.message_handlers:
            if handler in self.message_handlers[msg_type]:
                self.message_handlers[msg_type].remove(handler)
                
    def start(self) -> bool:
        """Start the server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('localhost', self.port))
            self.socket.listen(5)
            
            self.running = True
            
            # Start accept thread
            self.accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
            self.accept_thread.start()
            
            print(f"Server started on port {self.port}")
            return True
            
        except socket.error as e:
            print(f"Failed to start server: {e}")
            return False
            
    def stop(self) -> None:
        """Stop the server."""
        self.running = False
        
        # Close all client connections
        for client_id in list(self.clients.keys()):
            self.disconnect_client(client_id)
            
        # Close server socket
        if self.socket:
            self.socket.close()
            self.socket = None
            
        # Wait for threads to finish
        if self.accept_thread and self.accept_thread.is_alive():
            self.accept_thread.join(timeout=1.0)
            
        for thread in self.client_threads.values():
            if thread.is_alive():
                thread.join(timeout=1.0)
                
    def _accept_loop(self) -> None:
        """Main accept loop for new connections."""
        while self.running:
            try:
                client_socket, address = self.socket.accept()
                print(f"New connection from {address}")
                
                # Generate temporary client ID
                temp_id = f"temp_{int(time.time())}_{len(self.clients)}"
                
                # Store client info
                self.clients[temp_id] = client_socket
                self.client_addresses[temp_id] = address
                
                # Start client thread
                client_thread = threading.Thread(
                    target=self._client_loop, 
                    args=(temp_id, client_socket),
                    daemon=True
                )
                self.client_threads[temp_id] = client_thread
                client_thread.start()
                
            except socket.error as e:
                if self.running:
                    print(f"Accept error: {e}")
                break
                
    def _client_loop(self, client_id: str, client_socket: socket.socket) -> None:
        """Handle communication with a specific client."""
        buffer = b""
        
        while self.running:
            try:
                data = client_socket.recv(4096)
                if not data:
                    print(f"Client {client_id} disconnected")
                    break
                    
                buffer += data
                
                # Process complete messages
                while len(buffer) >= 4:
                    msg_length = int.from_bytes(buffer[:4], byteorder='big')
                    
                    if len(buffer) >= 4 + msg_length:
                        msg_data = buffer[4:4 + msg_length]
                        buffer = buffer[4 + msg_length:]
                        
                        message = NetworkMessage.deserialize(msg_data)
                        if message:
                            # Handle client ID assignment
                            if message.type == MessageType.CONNECT and "client_id" in message.data:
                                new_id = message.data["client_id"]
                                if new_id != client_id and new_id not in self.clients:
                                    # Update client ID
                                    self.clients[new_id] = self.clients.pop(client_id)
                                    self.client_addresses[new_id] = self.client_addresses.pop(client_id)
                                    self.client_threads[new_id] = self.client_threads.pop(client_id)
                                    client_id = new_id
                                    
                            message.sender_id = client_id
                            
                            with self.queue_lock:
                                self.message_queue.append((client_id, message))
                    else:
                        break
                        
            except socket.error as e:
                print(f"Client {client_id} error: {e}")
                break
                
        # Clean up disconnected client
        self.disconnect_client(client_id)
        
    def disconnect_client(self, client_id: str) -> None:
        """Disconnect a specific client."""
        if client_id in self.clients:
            try:
                self.clients[client_id].close()
            except:
                pass
            del self.clients[client_id]
            
        if client_id in self.client_addresses:
            del self.client_addresses[client_id]
            
        if client_id in self.client_threads:
            del self.client_threads[client_id]
            
    def send_to_client(self, client_id: str, message: NetworkMessage) -> bool:
        """Send a message to a specific client."""
        if client_id not in self.clients:
            return False
            
        try:
            msg_data = message.serialize()
            msg_length = len(msg_data)
            length_bytes = msg_length.to_bytes(4, byteorder='big')
            
            self.clients[client_id].sendall(length_bytes + msg_data)
            return True
            
        except socket.error as e:
            print(f"Failed to send to client {client_id}: {e}")
            self.disconnect_client(client_id)
            return False
            
    def broadcast_message(self, message: NetworkMessage, exclude: List[str] = None) -> None:
        """Send a message to all connected clients."""
        exclude = exclude or []
        
        for client_id in list(self.clients.keys()):
            if client_id not in exclude:
                self.send_to_client(client_id, message)
                
    def update(self, dt: float) -> None:
        """Update server and process messages."""
        # Process received messages
        with self.queue_lock:
            messages_to_process = self.message_queue.copy()
            self.message_queue.clear()
            
        for client_id, message in messages_to_process:
            # Handle disconnect messages
            if message.type == MessageType.DISCONNECT:
                self.disconnect_client(client_id)
                continue
                
            # Call message handlers
            if message.type in self.message_handlers:
                for handler in self.message_handlers[message.type]:
                    handler(client_id, message)
                    
    def get_connected_clients(self) -> List[str]:
        """Get list of connected client IDs."""
        return list(self.clients.keys())
        
    def get_client_count(self) -> int:
        """Get number of connected clients."""
        return len(self.clients)

class NetworkManager:
    """
    High-level network manager that can act as client or server.
    """
    
    def __init__(self):
        self.mode = None  # 'client' or 'server'
        self.client: Optional[NetworkClient] = None
        self.server: Optional[NetworkServer] = None
        
        # Game state synchronization
        self.game_state: Dict[str, Any] = {}
        self.state_handlers: Dict[str, Callable] = {}
        
    def start_server(self, port: int = 12345) -> bool:
        """Start as a server."""
        if self.mode is not None:
            self.cleanup()
            
        self.server = NetworkServer(port)
        if self.server.start():
            self.mode = 'server'
            self._setup_server_handlers()
            return True
        return False
        
    def connect_to_server(self, host: str, port: int, client_id: str = None) -> bool:
        """Connect as a client."""
        if self.mode is not None:
            self.cleanup()
            
        self.client = NetworkClient(client_id)
        if self.client.connect(host, port):
            self.mode = 'client'
            self._setup_client_handlers()
            return True
        return False
        
    def _setup_server_handlers(self) -> None:
        """Set up default server message handlers."""
        if self.server:
            self.server.add_message_handler(MessageType.CONNECT, self._handle_client_connect)
            self.server.add_message_handler(MessageType.GAME_STATE, self._handle_client_state)
            
    def _setup_client_handlers(self) -> None:
        """Set up default client message handlers."""
        if self.client:
            self.client.add_message_handler(MessageType.GAME_STATE, self._handle_server_state)
            
    def _handle_client_connect(self, client_id: str, message: NetworkMessage) -> None:
        """Handle client connection on server."""
        print(f"Client {client_id} connected")
        
        # Send current game state to new client
        if self.game_state:
            state_msg = NetworkMessage(MessageType.GAME_STATE, self.game_state)
            self.server.send_to_client(client_id, state_msg)
            
    def _handle_client_state(self, client_id: str, message: NetworkMessage) -> None:
        """Handle game state update from client."""
        if isinstance(message.data, dict):
            self.game_state.update(message.data)
            
            # Broadcast to other clients
            if self.server:
                self.server.broadcast_message(message, exclude=[client_id])
                
    def _handle_server_state(self, message: NetworkMessage) -> None:
        """Handle game state update from server."""
        if isinstance(message.data, dict):
            self.game_state.update(message.data)
            
    def send_game_state(self, state_data: Dict[str, Any]) -> None:
        """Send game state update."""
        message = NetworkMessage(MessageType.GAME_STATE, state_data)
        
        if self.mode == 'client' and self.client:
            self.client.send_message(message)
        elif self.mode == 'server' and self.server:
            self.server.broadcast_message(message)
            
    def update(self, dt: float) -> None:
        """Update network manager."""
        if self.mode == 'client' and self.client:
            self.client.update(dt)
        elif self.mode == 'server' and self.server:
            self.server.update(dt)
            
    def cleanup(self) -> None:
        """Clean up network resources."""
        if self.client:
            self.client.disconnect()
            self.client = None
            
        if self.server:
            self.server.stop()
            self.server = None
            
        self.mode = None
        self.game_state.clear()
        
    def is_connected(self) -> bool:
        """Check if connected to network."""
        if self.mode == 'client' and self.client:
            return self.client.connected
        elif self.mode == 'server' and self.server:
            return self.server.running
        return False
        
    def get_network_info(self) -> Dict[str, Any]:
        """Get network status information."""
        info = {
            'mode': self.mode,
            'connected': self.is_connected()
        }
        
        if self.mode == 'server' and self.server:
            info['port'] = self.server.port
            info['client_count'] = self.server.get_client_count()
            info['clients'] = self.server.get_connected_clients()
        elif self.mode == 'client' and self.client:
            info['client_id'] = self.client.client_id
            info['server_address'] = self.client.server_address
            
        return info
