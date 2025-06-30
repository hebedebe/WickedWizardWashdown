#!/usr/bin/env python3
"""
Test script to verify that scene serialization works correctly with actor parent-child relationships.
"""

import pygame
import json
from engine.actor.actor import Actor
from engine.scene.scene import Scene
from engine.component.builtin.transformComponent import TransformComponent
from engine.component.builtin.spriteComponent import SpriteComponent

def test_scene_serialization():
    """Test complete scene serialization with parent-child relationships."""
    
    print("Testing Scene Serialization with Actor Hierarchies")
    print("=" * 55)
    
    # Create a scene with complex hierarchy
    print("\n1. Creating scene with actor hierarchies...")
    
    scene = Scene()
    
    # Create multiple hierarchies in the scene
    
    # Hierarchy 1: Vehicle with parts
    vehicle = Actor("Vehicle")
    vehicle.transform.setPosition(200, 200)
    vehicle_transform = TransformComponent()
    vehicle.addComponent(vehicle_transform)
    
    wheel1 = Actor("Wheel1")
    wheel1.setParent(vehicle)
    wheel1_transform = TransformComponent()
    wheel1_transform.local_position = pygame.Vector2(-30, 20)
    wheel1.addComponent(wheel1_transform)
    
    wheel2 = Actor("Wheel2")
    wheel2.setParent(vehicle)
    wheel2_transform = TransformComponent()
    wheel2_transform.local_position = pygame.Vector2(30, 20)
    wheel2.addComponent(wheel2_transform)
    
    # Hierarchy 2: Building with rooms
    building = Actor("Building")
    building.transform.setPosition(500, 100)
    building_transform = TransformComponent()
    building.addComponent(building_transform)
    
    room1 = Actor("Room1")
    room1.setParent(building)
    room1_transform = TransformComponent()
    room1_transform.local_position = pygame.Vector2(-50, 0)
    room1.addComponent(room1_transform)
    
    room2 = Actor("Room2")
    room2.setParent(building)
    room2_transform = TransformComponent()
    room2_transform.local_position = pygame.Vector2(50, 0)
    room2.addComponent(room2_transform)
    
    # Nested hierarchy: furniture in room
    furniture = Actor("Furniture")
    furniture.setParent(room1)
    furniture_transform = TransformComponent()
    furniture_transform.local_position = pygame.Vector2(10, 10)
    furniture.addComponent(furniture_transform)
    
    # Add some standalone actors too
    standalone1 = Actor("Standalone1")
    standalone1.transform.setPosition(100, 100)
    standalone1_transform = TransformComponent()
    standalone1.addComponent(standalone1_transform)
    
    standalone2 = Actor("Standalone2")
    standalone2.transform.setPosition(300, 400)
    
    # Add all actors to scene
    actors = [vehicle, wheel1, wheel2, building, room1, room2, furniture, standalone1, standalone2]
    for actor in actors:
        scene.addActor(actor)
    
    print(f"Created scene with {len(scene.actors)} actors:")
    for actor in scene.actors:
        parent_name = actor.parent.name if actor.parent else "None"
        children_names = [c.name for c in actor.children]
        print(f"  {actor.name}: parent={parent_name}, children={children_names}")
    
    # Record world positions before serialization
    print(f"\n2. Recording world positions before serialization...")
    world_positions_before = {}
    for actor in scene.actors:
        transform_comp = actor.getComponent(TransformComponent)
        if transform_comp:
            world_positions_before[actor.name] = transform_comp.get_world_position()
            print(f"  {actor.name}: {world_positions_before[actor.name]}")
    
    # Serialize the scene
    print(f"\n3. Serializing scene...")
    scene_data = scene.serialize()
    json_data = json.dumps(scene_data, indent=2)
    print(f"Scene serialized successfully ({len(json_data)} characters)")
    
    # Simulate network transmission or file save/load
    print(f"\n4. Simulating data transmission...")
    transmitted_data = json.loads(json_data)
    
    # Deserialize into a new scene
    print(f"\n5. Deserializing into new scene...")
    new_scene = Scene.createFromSerializedData(transmitted_data)
    
    print(f"New scene created with {len(new_scene.actors)} actors:")
    for actor in new_scene.actors:
        parent_name = actor.parent.name if actor.parent else "None"
        children_names = [c.name for c in actor.children]
        print(f"  {actor.name}: parent={parent_name}, children={children_names}")
    
    # Verify all relationships are correct
    print(f"\n6. Verifying relationships...")
    
    # Find actors in new scene
    new_vehicle = new_scene.actor_lookup["Vehicle"]
    new_wheel1 = new_scene.actor_lookup["Wheel1"]
    new_wheel2 = new_scene.actor_lookup["Wheel2"]
    new_building = new_scene.actor_lookup["Building"]
    new_room1 = new_scene.actor_lookup["Room1"]
    new_room2 = new_scene.actor_lookup["Room2"]
    new_furniture = new_scene.actor_lookup["Furniture"]
    new_standalone1 = new_scene.actor_lookup["Standalone1"]
    new_standalone2 = new_scene.actor_lookup["Standalone2"]
    
    # Verify vehicle hierarchy
    assert new_wheel1.parent == new_vehicle, "Wheel1-Vehicle relationship not restored!"
    assert new_wheel2.parent == new_vehicle, "Wheel2-Vehicle relationship not restored!"
    assert new_wheel1 in new_vehicle.children, "Wheel1 not in Vehicle children!"
    assert new_wheel2 in new_vehicle.children, "Wheel2 not in Vehicle children!"
    
    # Verify building hierarchy
    assert new_room1.parent == new_building, "Room1-Building relationship not restored!"
    assert new_room2.parent == new_building, "Room2-Building relationship not restored!"
    assert new_furniture.parent == new_room1, "Furniture-Room1 relationship not restored!"
    
    # Verify standalone actors have no parents
    assert new_standalone1.parent is None, "Standalone1 should have no parent!"
    assert new_standalone2.parent is None, "Standalone2 should have no parent!"
    
    print("  ✓ All relationships correctly restored!")
    
    # Verify world positions match
    print(f"\n7. Verifying world positions...")
    world_positions_after = {}
    for actor in new_scene.actors:
        transform_comp = actor.getComponent(TransformComponent)
        if transform_comp:
            world_positions_after[actor.name] = transform_comp.get_world_position()
    
    for actor_name in world_positions_before:
        pos_before = world_positions_before[actor_name]
        pos_after = world_positions_after[actor_name]
        diff = (pos_before - pos_after).length()
        print(f"  {actor_name}: before={pos_before}, after={pos_after}, diff={diff:.6f}")
        assert diff < 0.001, f"World position mismatch for {actor_name}!"
    
    print("  ✓ All world positions match perfectly!")
    
    # Verify scene state
    print(f"\n8. Verifying scene state...")
    assert new_scene.active == scene.active, "Scene active state not restored!"
    assert new_scene.paused == scene.paused, "Scene paused state not restored!"
    assert len(new_scene.actors) == len(scene.actors), "Actor count mismatch!"
    print("  ✓ Scene state correctly restored!")
    
    print(f"\n" + "=" * 55)
    print("All Scene Serialization Tests PASSED! ✓")
    print("Complete scene hierarchies preserved through serialization!")
    print("=" * 55)

if __name__ == "__main__":
    test_scene_serialization()
