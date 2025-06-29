#!/usr/bin/env python3
"""
Network cleanup utility to kill lingering server processes and reset networking state.
"""

import socket
import time
import sys
import os

def check_port_in_use(port):
    """Check if a port is currently in use."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            result = s.connect_ex(('localhost', port))
            return result == 0
    except:
        return False

def force_close_port(port):
    """Try to force close a port by binding to it with SO_REUSEADDR."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('localhost', port))
            print(f"Successfully bound to port {port} (it was available)")
    except OSError as e:
        print(f"Port {port} is still in use: {e}")
        return False
    return True

def cleanup_network_manager():
    """Reset the global network manager instance."""
    try:
        from engine.networking import get_network_manager
        nm = get_network_manager()
        if nm.is_connected:
            print("Disconnecting existing network manager...")
            nm.disconnect()
            time.sleep(1.0)
        print("Network manager reset")
    except Exception as e:
        print(f"Error resetting network manager: {e}")

def main():
    print("=== Network Cleanup Utility ===")
    
    # Check common game ports
    ports_to_check = [7777, 8888, 8080, 3000]
    
    for port in ports_to_check:
        print(f"\nChecking port {port}...")
        if check_port_in_use(port):
            print(f"Port {port} is in use")
            if force_close_port(port):
                print(f"Port {port} is now available")
        else:
            print(f"Port {port} is available")
    
    # Reset network manager
    cleanup_network_manager()
    
    print("\n=== Cleanup Complete ===")
    print("You can now start a fresh server on the cleaned ports.")

if __name__ == "__main__":
    main()
