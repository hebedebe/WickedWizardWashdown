#!/usr/bin/env python3
"""
Test script to verify lobby join/leave functionality works correctly.
This will test the networking and lobby scene improvements.
"""

import sys
import os
import threading
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(__file__))

from engine.networking import NetworkManager, get_network_manager, NetworkPriority

def test_lobby_messages():
    """Test that lobby join/leave messages work correctly."""
    print("Testing lobby join/leave message functionality...")
    
    # Create host
    host_manager = NetworkManager()
    success = host_manager.host("localhost", 7777)
    
    if not success:
        print("❌ Failed to create host - another server may be running")
        return False
    
    print("✅ Host started successfully")
    
    # Track received messages
    received_messages = []
    
    def capture_custom_message(event_type, event_data, sender_name, timestamp):
        received_messages.append({
            'type': event_type,
            'data': event_data,
            'sender': sender_name
        })
        print(f"Host received: {event_type} from {sender_name}: {event_data}")
    
    # Set up custom message handler
    host_manager.register_custom_handler("player_join", capture_custom_message)
    host_manager.register_custom_handler("player_leave", capture_custom_message)
    
    # Create client
    client_manager = NetworkManager()
    time.sleep(0.1)  # Small delay for host to be ready
    
    client_success = client_manager.connect("localhost", 7777)
    if not client_success:
        print("❌ Client failed to connect")
        host_manager.disconnect()
        return False
    
    print("✅ Client connected successfully")
    
    # Send player join message from client
    time.sleep(0.1)  # Let connection establish
    client_manager.send_custom_message(
        "player_join",
        {"player_name": "TestPlayer1"},
        NetworkPriority.HIGH,
        "TestPlayer1"
    )
    
    # Wait for messages to be processed
    time.sleep(0.5)
    
    # Send player leave message
    client_manager.send_custom_message(
        "player_leave", 
        {"player_name": "TestPlayer1"},
        NetworkPriority.HIGH,
        "TestPlayer1"
    )
    
    # Wait for messages to be processed
    time.sleep(0.5)
    
    # Cleanup
    client_manager.disconnect()
    host_manager.disconnect()
    
    # Check results
    if len(received_messages) >= 2:
        join_msg = next((msg for msg in received_messages if msg['type'] == 'player_join'), None)
        leave_msg = next((msg for msg in received_messages if msg['type'] == 'player_leave'), None)
        
        if join_msg and leave_msg:
            print("✅ Both join and leave messages received correctly")
            print(f"   Join: {join_msg}")
            print(f"   Leave: {leave_msg}")
            return True
        else:
            print(f"❌ Missing messages. Received: {received_messages}")
            return False
    else:
        print(f"❌ Expected at least 2 messages, got {len(received_messages)}: {received_messages}")
        return False

if __name__ == "__main__":
    try:
        success = test_lobby_messages()
        if success:
            print("\n🎉 Lobby networking test passed!")
        else:
            print("\n💥 Lobby networking test failed!")
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()
