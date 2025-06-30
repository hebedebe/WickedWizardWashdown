#!/usr/bin/env python3
"""
Test script to verify that actor parent-child transform hierarchy works correctly,
including the case where a parent actor has no TransformComponent.
"""

import pygame
from engine.actor.actor import Actor
from engine.component.builtin.transformComponent import TransformComponent

def test_transform_hierarchy():
    """Test the transform hierarchy system."""
    
    print("Testing Transform Hierarchy System")
    print("=" * 40)
    
    # Test Case 1: Normal parent-child with both having TransformComponents
    print("\nTest Case 1: Both parent and child have TransformComponent")
    parent1 = Actor("Parent1")
    parent1.transform.setPosition(100, 100)
    parent_transform1 = TransformComponent()
    parent1.addComponent(parent_transform1)
    
    child1 = Actor("Child1")
    child1.setParent(parent1)
    child_transform1 = TransformComponent()
    child_transform1.local_position = pygame.Vector2(50, 25)
    child1.addComponent(child_transform1)
    
    world_pos1 = child_transform1.get_world_position()
    print(f"Parent position: {parent1.transform.position}")
    print(f"Child local position: {child_transform1.local_position}")
    print(f"Child world position: {world_pos1}")
    print(f"Expected: (150, 125), Got: ({world_pos1.x}, {world_pos1.y})")
    assert abs(world_pos1.x - 150) < 0.1 and abs(world_pos1.y - 125) < 0.1, "World position calculation failed!"
    print("✓ PASSED")
    
    # Test Case 2: Parent has no TransformComponent, child has one
    print("\nTest Case 2: Parent has NO TransformComponent, child has one")
    parent2 = Actor("Parent2")
    parent2.transform.setPosition(200, 200)
    # Note: parent2 has NO TransformComponent
    
    child2 = Actor("Child2")
    child2.setParent(parent2)
    child_transform2 = TransformComponent()
    child_transform2.local_position = pygame.Vector2(30, 40)
    child2.addComponent(child_transform2)
    
    # This should NOT crash and should return a reasonable result
    try:
        world_pos2 = child_transform2.get_world_position()
        print(f"Parent position: {parent2.transform.position} (no TransformComponent)")
        print(f"Child local position: {child_transform2.local_position}")
        print(f"Child world position: {world_pos2}")
        print(f"✓ PASSED - No crash when parent lacks TransformComponent")
    except Exception as e:
        print(f"✗ FAILED - Crashed when parent lacks TransformComponent: {e}")
        raise
    
    # Test Case 3: Multiple levels of hierarchy
    print("\nTest Case 3: Multi-level hierarchy")
    grandparent = Actor("Grandparent")
    grandparent.transform.setPosition(10, 10)
    grandparent_transform = TransformComponent()
    grandparent.addComponent(grandparent_transform)
    
    parent3 = Actor("Parent3")
    parent3.setParent(grandparent)
    parent_transform3 = TransformComponent()
    parent_transform3.local_position = pygame.Vector2(20, 30)
    parent3.addComponent(parent_transform3)
    
    child3 = Actor("Child3")
    child3.setParent(parent3)
    child_transform3 = TransformComponent()
    child_transform3.local_position = pygame.Vector2(5, 5)
    child3.addComponent(child_transform3)
    
    world_pos3 = child_transform3.get_world_position()
    print(f"Grandparent position: {grandparent.transform.position}")
    print(f"Parent local position: {parent_transform3.local_position}")
    print(f"Child local position: {child_transform3.local_position}")
    print(f"Child world position: {world_pos3}")
    # Expected: (10 + 20 + 5, 10 + 30 + 5) = (35, 45)
    print(f"Expected: (35, 45), Got: ({world_pos3.x}, {world_pos3.y})")
    assert abs(world_pos3.x - 35) < 0.1 and abs(world_pos3.y - 45) < 0.1, "Multi-level hierarchy failed!"
    print("✓ PASSED")
    
    # Test Case 4: Test rotation inheritance
    print("\nTest Case 4: Rotation inheritance")
    rot_parent = Actor("RotParent")
    rot_parent.transform.setPosition(0, 0)
    rot_parent.transform.rotation = 90  # 90 degrees
    rot_parent_transform = TransformComponent()
    rot_parent.addComponent(rot_parent_transform)
    
    rot_child = Actor("RotChild")
    rot_child.setParent(rot_parent)
    rot_child_transform = TransformComponent()
    rot_child_transform.local_position = pygame.Vector2(10, 0)  # 10 units to the right
    rot_child_transform.local_rotation = 45  # Additional 45 degrees
    rot_child.addComponent(rot_child_transform)
    
    world_rot = rot_child_transform.get_world_rotation()
    print(f"Parent rotation: {rot_parent.transform.rotation}°")
    print(f"Child local rotation: {rot_child_transform.local_rotation}°")
    print(f"Child world rotation: {world_rot}°")
    print(f"Expected: 135°, Got: {world_rot}°")
    assert abs(world_rot - 135) < 0.1, "Rotation inheritance failed!"
    
    # Test world position with rotation (should be rotated 90 degrees)
    world_pos_rot = rot_child_transform.get_world_position()
    print(f"Child world position with rotation: {world_pos_rot}")
    print(f"Expected approximately: (0, 10), Got: ({world_pos_rot.x:.1f}, {world_pos_rot.y:.1f})")
    # Due to rotation, (10, 0) rotated 90° should become approximately (0, 10)
    assert abs(world_pos_rot.x) < 1.0 and abs(world_pos_rot.y - 10) < 1.0, "Rotated position calculation failed!"
    print("✓ PASSED")
    
    print("\n" + "=" * 40)
    print("All Transform Hierarchy Tests PASSED! ✓")
    print("=" * 40)

if __name__ == "__main__":
    test_transform_hierarchy()
