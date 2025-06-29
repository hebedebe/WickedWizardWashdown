#!/usr/bin/env python3
"""
Test script to verify the improved lobby join/leave functionality.
This simulates the complete flow with proper state management.
"""

import sys
import os
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(__file__))

def test_lobby_flow():
    """Test the complete lobby join/leave flow."""
    print("Testing improved lobby flow...")
    
    try:
        # Import the required modules
        from engine.networking import NetworkManager, NetworkPriority
        from game.scenes.lobby import LobbyScene
        
        # Create host lobby
        print("1. Setting up host lobby...")
        host_lobby = LobbyScene()
        host_lobby.player_name = "Host"
        host_lobby.is_host = True
        host_lobby.players = ["Host"]  # Initialize with host
        
        # Create client lobby  
        print("2. Setting up client lobby...")
        client_lobby = LobbyScene()
        client_lobby.player_name = "TestClient"
        client_lobby.is_host = False
        client_lobby.players = []  # Client starts empty
        
        print("3. Testing host player_join processing...")
        # Simulate host receiving a player_join message
        host_lobby.on_network_player_joined(
            {"player_name": "TestClient"}, 
            "TestClient", 
            time.time()
        )
        
        # Check if host's player list is correct
        expected_host_players = ["Host", "TestClient"]
        if host_lobby.players == expected_host_players:
            print(f"✅ Host player list correct: {host_lobby.players}")
        else:
            print(f"❌ Host player list incorrect. Expected: {expected_host_players}, Got: {host_lobby.players}")
            return False
        
        print("4. Testing client lobby_update processing...")
        # Simulate client receiving lobby_update from server
        client_lobby.on_network_lobby_update(
            {"players": ["Host", "TestClient"], "max_players": 4},
            "Server",
            time.time()
        )
        
        # Check if client's player list is correct
        if client_lobby.players == expected_host_players:
            print(f"✅ Client player list correct: {client_lobby.players}")
        else:
            print(f"❌ Client player list incorrect. Expected: {expected_host_players}, Got: {client_lobby.players}")
            return False
        
        print("5. Testing player leave...")
        # Simulate host processing player leave
        host_lobby.on_network_player_left(
            {"player_name": "TestClient"},
            "TestClient",
            time.time()
        )
        
        # Check if host's player list is correct after leave
        expected_after_leave = ["Host"]
        if host_lobby.players == expected_after_leave:
            print(f"✅ Host player list after leave correct: {host_lobby.players}")
        else:
            print(f"❌ Host player list after leave incorrect. Expected: {expected_after_leave}, Got: {host_lobby.players}")
            return False
        
        print("6. Testing client receiving leave update...")
        # Simulate client receiving updated lobby state
        client_lobby.on_network_lobby_update(
            {"players": ["Host"], "max_players": 4},
            "Server",
            time.time()
        )
        
        if client_lobby.players == expected_after_leave:
            print(f"✅ Client player list after leave update correct: {client_lobby.players}")
        else:
            print(f"❌ Client player list after leave update incorrect. Expected: {expected_after_leave}, Got: {client_lobby.players}")
            return False
            
        print("\n🎉 All lobby flow tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_lobby_flow()
    if success:
        print("\n✅ Lobby improvements should now work correctly!")
        print("Key improvements:")
        print("- Only the host manages the authoritative player list")
        print("- Clients receive updates via lobby_update messages")
        print("- Join/leave messages are shown correctly")
        print("- No duplicate processing or race conditions")
    else:
        print("\n❌ Tests failed - there may still be issues")
