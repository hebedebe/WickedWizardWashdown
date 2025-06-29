#!/usr/bin/env python3
"""
Simple test to check lobby scene syntax and basic networking functionality.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(__file__))

try:
    print("Testing imports...")
    
    # Test engine imports
    from engine.networking import NetworkManager, get_network_manager, NetworkPriority, MessageType, NetworkMessage
    print("✅ NetworkManager imported successfully")
    
    # Test lobby scene import
    from game.scenes.lobby import LobbyScene
    print("✅ LobbyScene imported successfully")
    
    # Test basic network manager creation
    nm = get_network_manager()
    print(f"✅ Network manager created: {type(nm)}")
    
    # Test custom message handler registration
    def test_handler(event_data, sender_name, timestamp):
        print(f"Test handler called: {event_data}")
    
    nm.register_custom_handler("test", test_handler)
    print("✅ Custom handler registered successfully")
    
    # Test lobby scene creation
    lobby = LobbyScene()
    print(f"✅ Lobby scene created: {type(lobby)}")
    
    print("\n🎉 All basic imports and instantiation tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
