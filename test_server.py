#!/usr/bin/env python3
"""
Simple test server to debug networking issues.
Run this to start a test server.
"""

import sys
import time
from engine.networking import get_network_manager, NetworkPriority

class TestServer:
    def __init__(self):
        self.network_manager = get_network_manager()
        self.running = False
        
    def setup_callbacks(self):
        """Setup network callbacks."""
        self.network_manager.on_client_connected = self.on_client_connected
        self.network_manager.on_client_disconnected = self.on_client_disconnected
        
        # Register custom message handlers
        self.network_manager.register_custom_handler("chat", self.on_chat_message)
        
    def on_client_connected(self, client_id: str):
        """Handle client connection."""
        print(f"✓ Client connected: {client_id}")
        
        # Send a welcome message
        self.network_manager.send_custom_message(
            "chat",
            {"message": f"Welcome {client_id}!"},
            NetworkPriority.INSTANT,
            "Server"
        )
        
    def on_client_disconnected(self, client_id: str):
        """Handle client disconnection."""
        print(f"✗ Client disconnected: {client_id}")
        
    def on_chat_message(self, event_data, sender_name, timestamp):
        """Handle chat messages."""
        message = event_data.get("message", "")
        print(f"💬 Chat from {sender_name}: {message}")
        
        # Echo the message back to all clients
        self.network_manager.send_custom_message(
            "chat",
            {"message": f"Echo: {message}"},
            NetworkPriority.INSTANT,
            "Server"
        )
    
    def start(self, host: str = "localhost", port: int = 7777):
        """Start the test server."""
        print(f"🚀 Starting test server on {host}:{port}")
        
        self.setup_callbacks()
        
        if self.network_manager.host(host, port):
            print("✓ Server started successfully")
            print(f"📡 Listening for connections on {host}:{port}")
            print("🔄 Server running... Press Ctrl+C to stop")
            
            self.running = True
            
            try:
                while self.running:
                    # Update network manager
                    self.network_manager.update()
                    
                    # Small delay to prevent busy waiting
                    time.sleep(0.016)  # ~60 FPS
                    
            except KeyboardInterrupt:
                print("\n⚡ Server interrupted by user")
            
        else:
            print("✗ Failed to start server")
        
        # Clean shutdown
        self.stop()
    
    def stop(self):
        """Stop the server."""
        self.running = False
        print("📴 Shutting down server...")
        self.network_manager.disconnect()
        print("👋 Server stopped")

def main():
    """Main function."""
    print("🧪 Network Server Test Tool")
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
    
    # Create and start server
    server = TestServer()
    server.start(host, port)

if __name__ == "__main__":
    main()
