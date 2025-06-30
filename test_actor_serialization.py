#!/usr/bin/env python3
"""
Test script to verify that actor parent-child serialization works correctly.
"""

import pygame
import json
from engine.actor.actor import Actor
from engine.component.builtin.transformComponent import TransformComponent
from engine.component.builtin.spriteComponent import SpriteComponent

def test_actor_serialization():
    """Test actor serialization with parent-child relationships."""
    
    print("Testing Actor Serialization with Parent-Child Relationships")
    print("=" * 60)
    
    # Create a hierarchy: Grandparent -> Parent -> Child
    print("\n1. Creating actor hierarchy...")
    
    grandparent = Actor("Grandparent")
    grandparent.transform.setPosition(100, 100)
    grandparent_transform = TransformComponent()
    grandparent_transform.local_position = pygame.Vector2(10, 20)
    grandparent.addComponent(grandparent_transform)
    
    parent = Actor("Parent") 
    parent.setParent(grandparent)
    parent_transform = TransformComponent()
    parent_transform.local_position = pygame.Vector2(30, 40)
    parent.addComponent(parent_transform)
    
    child1 = Actor("Child1")
    child1.setParent(parent)
    child1_transform = TransformComponent()
    child1_transform.local_position = pygame.Vector2(5, 5)
    child1.addComponent(child1_transform)
    
    child2 = Actor("Child2")
    child2.setParent(parent)
    child2_transform = TransformComponent()
    child2_transform.local_position = pygame.Vector2(-5, 10)
    child2.addComponent(child2_transform)
    
    actors = [grandparent, parent, child1, child2]
    
    print(f"Created hierarchy:")
    print(f"  Grandparent '{grandparent.name}' (children: {[c.name for c in grandparent.children]})")
    print(f"  Parent '{parent.name}' (parent: {parent.parent.name if parent.parent else None}, children: {[c.name for c in parent.children]})")
    print(f"  Child1 '{child1.name}' (parent: {child1.parent.name if child1.parent else None})")
    print(f"  Child2 '{child2.name}' (parent: {child2.parent.name if child2.parent else None})")
    
    # Test world positions before serialization
    print(f"\n2. World positions before serialization:")
    child1_world_before = child1_transform.get_world_position()
    child2_world_before = child2_transform.get_world_position()
    print(f"  Child1 world position: {child1_world_before}")
    print(f"  Child2 world position: {child2_world_before}")
    
    # Serialize all actors
    print(f"\n3. Serializing actors...")
    serialized_data = []
    for actor in actors:
        actor_data = actor.serialize()
        serialized_data.append(actor_data)
        print(f"  Serialized '{actor.name}': parent_name={actor_data.get('parent_name')}, children_names={actor_data.get('children_names')}")
    
    # Convert to JSON to simulate network transmission or file save
    json_data = json.dumps(serialized_data, indent=2)
    print(f"\n4. JSON serialization successful ({len(json_data)} characters)")
    
    # Deserialize back
    print(f"\n5. Deserializing actors...")
    deserialized_data = json.loads(json_data)
    new_actors = []
    
    for actor_data in deserialized_data:
        new_actor = Actor.createFromSerializedData(actor_data)
        new_actors.append(new_actor)
        print(f"  Deserialized '{new_actor.name}'")
    
    # Re-establish relationships
    print(f"\n6. Re-establishing parent-child relationships...")
    Actor.establishRelationshipsFromSerialization(new_actors)
    
    # Find the deserialized actors
    new_grandparent = next(a for a in new_actors if a.name == "Grandparent")
    new_parent = next(a for a in new_actors if a.name == "Parent")
    new_child1 = next(a for a in new_actors if a.name == "Child1")
    new_child2 = next(a for a in new_actors if a.name == "Child2")
    
    print(f"Re-established hierarchy:")
    print(f"  Grandparent '{new_grandparent.name}' (children: {[c.name for c in new_grandparent.children]})")
    print(f"  Parent '{new_parent.name}' (parent: {new_parent.parent.name if new_parent.parent else None}, children: {[c.name for c in new_parent.children]})")
    print(f"  Child1 '{new_child1.name}' (parent: {new_child1.parent.name if new_child1.parent else None})")
    print(f"  Child2 '{new_child2.name}' (parent: {new_child2.parent.name if new_child2.parent else None})")
    
    # Verify relationships are correct
    print(f"\n7. Verifying relationships...")
    assert new_parent.parent == new_grandparent, "Parent-grandparent relationship not restored!"
    assert new_child1.parent == new_parent, "Child1-parent relationship not restored!"
    assert new_child2.parent == new_parent, "Child2-parent relationship not restored!"
    assert new_child1 in new_parent.children, "Child1 not in parent's children!"
    assert new_child2 in new_parent.children, "Child2 not in parent's children!"
    assert new_parent in new_grandparent.children, "Parent not in grandparent's children!"
    print("  ✓ All relationships correctly restored!")
    
    # Test world positions after deserialization
    print(f"\n8. Verifying transform calculations...")
    new_child1_transform = new_child1.getComponent(TransformComponent)
    new_child2_transform = new_child2.getComponent(TransformComponent)
    
    child1_world_after = new_child1_transform.get_world_position()
    child2_world_after = new_child2_transform.get_world_position()
    
    print(f"  Child1 world position before: {child1_world_before}")
    print(f"  Child1 world position after:  {child1_world_after}")
    print(f"  Child2 world position before: {child2_world_before}")
    print(f"  Child2 world position after:  {child2_world_after}")
    
    # Check if positions match (allowing for small floating point differences)
    pos1_diff = (child1_world_before - child1_world_after).length()
    pos2_diff = (child2_world_before - child2_world_after).length()
    
    assert pos1_diff < 0.001, f"Child1 world position mismatch! Difference: {pos1_diff}"
    assert pos2_diff < 0.001, f"Child2 world position mismatch! Difference: {pos2_diff}"
    print("  ✓ World positions match perfectly!")
    
    print(f"\n" + "=" * 60)
    print("All Actor Serialization Tests PASSED! ✓")
    print("Parent-child relationships are preserved through serialization!")
    print("=" * 60)

if __name__ == "__main__":
    test_actor_serialization()
