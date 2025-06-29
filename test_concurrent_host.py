#!/usr/bin/env python3
"""
Quick test to verify that two hosts cannot run simultaneously.
"""

import time
from engine.networking import get_network_manager, reset_network_manager

def quick_host_test():
    """Quick test to try hosting."""
    reset_network_manager()
    network_manager = get_network_manager()
    
    print("Attempting to host on localhost:7777...")
    success = network_manager.host("localhost", 7777)
    
    if success:
        print("✅ Host started successfully!")
        print("Keeping server running for 60 seconds...")
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            print("Interrupted by user")
        finally:
            network_manager.disconnect()
            print("Host shut down")
    else:
        print("❌ Failed to host - port already in use!")

if __name__ == "__main__":
    quick_host_test()
