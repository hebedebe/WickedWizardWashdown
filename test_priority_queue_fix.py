#!/usr/bin/env python3
"""
Test script to verify the priority queue fix works correctly.
"""

import sys
import os
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(__file__))

def test_priority_queue_fix():
    """Test that the priority queue no longer crashes on message comparison."""
    print("Testing priority queue fix...")
    
    try:
        from engine.networking import NetworkManager, NetworkMessage, MessageType, NetworkPriority
        
        # Create a network manager
        nm = NetworkManager()
        print("✅ NetworkManager created successfully")
        
        # Create some test messages with the same timestamp (this would cause the original error)
        timestamp = time.time()
        
        msg1 = NetworkMessage(
            MessageType.CUSTOM_MESSAGE,
            {"event_type": "test1", "event_data": {"value": 1}},
            "client1",
            timestamp,
            NetworkPriority.HIGH
        )
        
        msg2 = NetworkMessage(
            MessageType.CUSTOM_MESSAGE,
            {"event_type": "test2", "event_data": {"value": 2}},
            "client2", 
            timestamp,  # Same timestamp
            NetworkPriority.HIGH
        )
        
        msg3 = NetworkMessage(
            MessageType.CUSTOM_MESSAGE,
            {"event_type": "test3", "event_data": {"value": 3}},
            "client3",
            timestamp,  # Same timestamp
            NetworkPriority.HIGH
        )
        
        print("✅ Test messages created with identical timestamps")
        
        # Try to queue them (this would fail in the original code)
        nm._queue_message_by_priority(msg1)
        nm._queue_message_by_priority(msg2)
        nm._queue_message_by_priority(msg3)
        
        print("✅ Messages queued successfully - no comparison errors!")
        
        # Try to process them
        nm._process_queue_with_priority(NetworkPriority.HIGH, time.time())
        
        print("✅ Messages processed successfully!")
        
        # Test with different priorities and same timestamps
        msg4 = NetworkMessage(
            MessageType.CUSTOM_MESSAGE,
            {"event_type": "instant", "event_data": {}},
            "client1",
            timestamp,
            NetworkPriority.INSTANT
        )
        
        msg5 = NetworkMessage(
            MessageType.CUSTOM_MESSAGE,
            {"event_type": "medium", "event_data": {}},
            "client1", 
            timestamp,
            NetworkPriority.MEDIUM
        )
        
        nm._queue_message_by_priority(msg4)
        nm._queue_message_by_priority(msg5)
        
        print("✅ Mixed priority messages queued successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_priority_queue_fix()
    if success:
        print("\n🎉 Priority queue fix successful!")
        print("The NetworkMessage comparison error should be resolved.")
    else:
        print("\n💥 Priority queue test failed!")
