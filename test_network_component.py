"""
Simple test script for NetworkComponent functionality.
Tests basic serialization and networking without pygame.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time
from engine.actor import Actor, Component
from engine.network_component import NetworkComponent, NetworkOwnership
from engine.networking import NetworkManager
from engine.components import PhysicsComponent


class TestComponent(Component):
    """Simple test component for network testing."""
    
    def __init__(self):
        super().__init__()
        self.test_value = 42
        self.test_string = "hello"
        self.blacklisted_value = "should_not_sync"
    
    def update(self, dt: float) -> None:
        pass


def test_serialization():
    """Test basic serialization functionality."""
    print("Testing NetworkComponent serialization...")
    
    # Create test actor
    actor = Actor("TestActor")
    actor.add_tag("test")
    
    # Add test component
    test_comp = TestComponent()
    actor.add_component(test_comp)
    
    # Add physics component
    physics = PhysicsComponent()
    physics.velocity.x = 100.0
    physics.velocity.y = 50.0
    actor.add_component(physics)
    
    # Add network component
    network_comp = NetworkComponent()
    
    # Test blacklisting
    network_comp.blacklist_variable(TestComponent, 'blacklisted_value')
    
    actor.add_component(network_comp)
    
    # Test serialization
    state = network_comp._serialize_actor_state()
    
    print(f"Serialized state: {state}")
    
    # Verify expected fields are present
    assert 'network_id' in state
    assert 'actor_name' in state
    assert 'components' in state
    assert 'TestComponent' in state['components']
    assert 'PhysicsComponent' in state['components']
    
    # Verify blacklisted value is not included
    test_comp_data = state['components']['TestComponent']['data']
    assert 'test_value' in test_comp_data
    assert 'test_string' in test_comp_data
    assert 'blacklisted_value' not in test_comp_data
    
    print("✓ Serialization test passed!")
    
    # Test deserialization
    actor2 = Actor("TestActor2")
    test_comp2 = TestComponent()
    test_comp2.test_value = 0  # Different initial value
    test_comp2.test_string = "different"
    actor2.add_component(test_comp2)
    
    physics2 = PhysicsComponent()
    actor2.add_component(physics2)
    
    network_comp2 = NetworkComponent()
    actor2.add_component(network_comp2)
    
    # Apply state
    network_comp2._deserialize_actor_state(state)
    
    # Verify values were updated
    assert test_comp2.test_value == 42
    assert test_comp2.test_string == "hello"
    assert test_comp2.blacklisted_value == "should_not_sync"  # Should remain unchanged
    
    print("✓ Deserialization test passed!")


def test_blacklisting():
    """Test component and variable blacklisting."""
    print("\nTesting blacklisting functionality...")
    
    actor = Actor("BlacklistTest")
    
    # Add components
    test_comp = TestComponent()
    physics = PhysicsComponent()
    
    actor.add_component(test_comp)
    actor.add_component(physics)
    
    network_comp = NetworkComponent()
    
    # Blacklist entire physics component
    network_comp.blacklist_component(PhysicsComponent)
    
    actor.add_component(network_comp)
    
    # Serialize
    state = network_comp._serialize_actor_state()
    
    # Verify physics component is not included
    assert 'TestComponent' in state['components']
    assert 'PhysicsComponent' not in state['components']
    
    print("✓ Component blacklisting test passed!")


def test_ownership():
    """Test ownership and authority logic."""
    print("\nTesting ownership functionality...")
    
    # Test server ownership
    network_comp_server = NetworkComponent(
        owner_id="server",
        ownership=NetworkOwnership.SERVER
    )
    
    # Mock network manager as server
    network_manager = NetworkManager()
    network_manager.mode = 'server'
    NetworkComponent.set_network_manager(network_manager)
    
    # Should have authority as server
    assert network_comp_server._should_send_updates() == True
    
    # Test client ownership
    network_comp_client = NetworkComponent(
        owner_id="client_123",
        ownership=NetworkOwnership.CLIENT
    )
    
    # Should not have authority as server for client-owned object
    assert network_comp_client._should_send_updates() == False
    
    # Switch to client mode
    network_manager.mode = 'client'
    network_manager.client = type('MockClient', (), {'client_id': 'client_123'})()
    
    # Now should have authority for client-owned object
    assert network_comp_client._should_send_updates() == True
    
    # But not for server-owned object
    assert network_comp_server._should_send_updates() == False
    
    print("✓ Ownership test passed!")


def main():
    """Run all tests."""
    print("Running NetworkComponent tests...\n")
    
    try:
        test_serialization()
        test_blacklisting()
        test_ownership()
        
        print("\n✓ All tests passed!")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
