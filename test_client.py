#!/usr/bin/env python3
"""
Simple test client to debug networking issues.
Run this to connect to a game server.
"""

import sys
import time
import socket
import json
import threading
from typing import Dict, Any

class TestNetworkClient:
    def __init__(self):
        self.socket = None
        self.connected = False
        self.client_id = f"test_client_{int(time.time())}"
        
    def connect(self, host: str = "localhost", port: int = 7777) -> bool:
        """Connect to the server."""
        try:
            print(f"Attempting to connect to {host}:{port}")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)  # 5 second timeout
            
            # Connect to server
            self.socket.connect((host, port))
            self.connected = True
            print(f"✓ Connected to server at {host}:{port}")
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            
            # Send connection request
            connect_msg = {
                'type': 'connect_request',
                'data': {'client_id': self.client_id},
                'sender_id': self.client_id,
                'timestamp': time.time(),
                'priority': 'medium',
                'id': f"msg_{int(time.time())}"
            }
            
            self._send_message(connect_msg)
            print(f"✓ Sent connection request with client_id: {self.client_id}")
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to connect: {e}")
            self.connected = False
            return False
    
    def _send_message(self, message: Dict[str, Any]):
        """Send a message to the server."""
        try:
            if self.socket and self.connected:
                msg_json = json.dumps(message) + '\n'
                self.socket.send(msg_json.encode('utf-8'))
                print(f"→ Sent: {message['type']}")
            else:
                print("✗ Cannot send message: not connected")
        except Exception as e:
            print(f"✗ Error sending message: {e}")
            self.connected = False
    
    def _receive_loop(self):
        """Receive messages from server."""
        buffer = ""
        print("🔄 Starting receive loop...")
        
        while self.connected:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    print("✗ Server closed connection")
                    break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            message = json.loads(line)
                            self._handle_message(message)
                        except json.JSONDecodeError as e:
                            print(f"✗ Failed to parse message: {e}")
                            print(f"   Raw data: {line}")
                            
            except Exception as e:
                print(f"✗ Receive error: {e}")
                break
        
        self.connected = False
        print("📴 Receive loop ended")
    
    def _handle_message(self, message: Dict[str, Any]):
        """Handle incoming messages."""
        msg_type = message.get('type', 'unknown')
        print(f"← Received: {msg_type}")
        
        if msg_type == 'connect_response':
            accepted = message.get('data', {}).get('accepted', False)
            if accepted:
                print("✓ Connection accepted by server!")
                # Send a test chat message
                self.send_chat_message("Hello from test client!")
            else:
                print("✗ Connection rejected by server")
                
        elif msg_type == 'custom_message':
            event_type = message.get('data', {}).get('event_type', 'unknown')
            event_data = message.get('data', {}).get('event_data', {})
            sender_name = message.get('data', {}).get('sender_name', 'Unknown')
            print(f"📨 Custom message: {event_type} from {sender_name}")
            print(f"   Data: {event_data}")
            
        else:
            print(f"📨 Message data: {message.get('data', {})}")
    
    def send_chat_message(self, message: str):
        """Send a chat message."""
        chat_msg = {
            'type': 'custom_message',
            'data': {
                'event_type': 'chat',
                'event_data': {'message': message},
                'sender_name': f'TestClient_{self.client_id[-4:]}',
                'timestamp': time.time()
            },
            'sender_id': self.client_id,
            'timestamp': time.time(),
            'priority': 'instant',
            'id': f"chat_{int(time.time())}"
        }
        self._send_message(chat_msg)
    
    def disconnect(self):
        """Disconnect from server."""
        if self.connected:
            disconnect_msg = {
                'type': 'disconnect',
                'data': {'client_id': self.client_id},
                'sender_id': self.client_id,
                'timestamp': time.time(),
                'priority': 'high',
                'id': f"disconnect_{int(time.time())}"
            }
            self._send_message(disconnect_msg)
            
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("📴 Disconnected from server")

def main():
    """Main test function."""
    print("🧪 Network Client Test Tool")
    print("=" * 40)
    
    # Parse command line arguments
    host = "localhost"
    port = 7777
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print(f"✗ Invalid port: {sys.argv[2]}")
            return
    
    print(f"Target: {host}:{port}")
    print()
    
    # Create and connect client
    client = TestNetworkClient()
    
    if not client.connect(host, port):
        print("Failed to connect. Exiting.")
        return
    
    # Keep client running for a bit
    try:
        print("🔄 Client running... Press Ctrl+C to quit")
        print("   Waiting for messages from server...")
        
        # Send periodic messages to test connection
        for i in range(5):
            time.sleep(2)
            if client.connected:
                client.send_chat_message(f"Test message #{i+1}")
            else:
                print("✗ Lost connection to server")
                break
        
        # Wait a bit more for any final messages
        if client.connected:
            print("⏳ Waiting 5 more seconds for final messages...")
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n⚡ Interrupted by user")
    
    # Clean disconnect
    client.disconnect()
    print("👋 Test completed")

if __name__ == "__main__":
    main()
