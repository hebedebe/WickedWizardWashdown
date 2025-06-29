#!/usr/bin/env python3
"""
Test script to demonstrate that only one host can exist per port.
Run this script multiple times simultaneously to test the fix.
"""

import sys
import time
from engine.networking import get_network_manager, reset_network_manager

def test_hosting():
    """Test hosting functionality."""
    print("Testing network hosting functionality...")
    
    # Reset any existing network manager
    reset_network_manager()
    
    # Get a fresh network manager
    network_manager = get_network_manager()
    
    print(f"Process PID: {sys.exc_info}")
    print(f"Network manager role: {network_manager.role.value}")
    print(f"Network manager running: {network_manager.is_running}")
    
    # Try to start hosting
    print("\nAttempting to host on localhost:7777...")
    success = network_manager.host("localhost", 7777)
    
    if success:
        print("✅ SUCCESS: Hosting started successfully!")
        print("This process is now the host.")
        print("Try running this script again in another terminal - it should fail.")
        
        # Keep the server running for a while
        try:
            for i in range(30):
                print(f"Server running... {30-i} seconds remaining")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down server...")
        
        # Cleanup
        network_manager.disconnect()
        print("Server shut down.")
        
    else:
        print("❌ FAILED: Could not start hosting!")
        print("This means another process is already hosting on port 7777.")
        print("The fix is working correctly - only one host per port is allowed.")

if __name__ == "__main__":
    test_hosting()
