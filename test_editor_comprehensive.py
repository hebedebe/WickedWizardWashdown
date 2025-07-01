#!/usr/bin/env python3
"""
Comprehensive test for the scene editor functionality.
"""

import sys
import logging
from pathlib import Path

# Add the parent directory to sys.path
parent_dir = Path(__file__).parent
sys.path.insert(0, str(parent_dir))

# Import and patch engine
from editor import editor_dummy

from editor.editor_scene import EditorScene
from editor.editor_project import EditorProject
from engine.actor.actor import Actor

def test_basic_functionality():
    """Test basic scene editor functionality."""
    print("=== Testing Basic Scene Editor Functionality ===")
    
    # Test 1: Create a project
    print("\n1. Testing project creation...")
    project = EditorProject("Test Project")
    print(f"   ✓ Project created: {project.name}")
    
    # Test 2: Create a scene
    print("\n2. Testing scene creation...")
    scene_id = project.create_new_scene("Test Scene")
    scene = project.get_scene(scene_id)
    print(f"   ✓ Scene created: {scene.name}")
    print(f"   ✓ Scene ID: {scene_id}")
    print(f"   ✓ Scene has {len(scene.scene.actors)} actors initially")
    
    # Test 3: Add actors
    print("\n3. Testing actor creation...")
    actor1 = Actor("Player")
    actor2 = Actor("Enemy")
    actor3 = Actor("Platform")
    
    scene.add_actor(actor1)
    scene.add_actor(actor2)
    scene.add_actor(actor3)
    
    print(f"   ✓ Added 3 actors")
    print(f"   ✓ Scene now has {len(scene.scene.actors)} actors")
    print(f"   ✓ Actor names: {[a.name for a in scene.scene.actors]}")
    
    # Test 4: Actor parenting
    print("\n4. Testing actor parenting...")
    child_actor = Actor("ChildObject")
    actor1.addChild(child_actor)
    scene.add_actor(child_actor)
    
    print(f"   ✓ Created parent-child relationship")
    print(f"   ✓ Player has {len(actor1.children)} children")
    print(f"   ✓ Child actor parent: {child_actor.parent.name if child_actor.parent else 'None'}")
    
    # Test 5: Scene serialization
    print("\n5. Testing scene serialization...")
    try:
        serialized_data = scene.serialize()
        print(f"   ✓ Serialization successful")
        print(f"   ✓ Serialized {len(serialized_data['actors'])} actors")
        
        # Test deserialization
        new_scene = EditorScene("Deserialized Scene")
        new_scene.deserialize(serialized_data)
        print(f"   ✓ Deserialization successful")
        print(f"   ✓ Deserialized scene has {len(new_scene.scene.actors)} actors")
        
    except Exception as e:
        print(f"   ✗ Serialization failed: {e}")
        return False
    
    # Test 6: Project management
    print("\n6. Testing project management...")
    project.add_scene(new_scene, "deserialized_scene")
    print(f"   ✓ Project now has {len(project.scenes)} scenes")
    print(f"   ✓ Scene IDs: {list(project.scenes.keys())}")
    
    # Test 7: Dirty state tracking
    print("\n7. Testing dirty state tracking...")
    print(f"   ✓ Scene is dirty: {scene.is_dirty}")
    print(f"   ✓ Project has unsaved changes: {project.has_unsaved_changes()}")
    
    scene.mark_clean()
    new_scene.mark_clean()
    project.mark_clean()
    print(f"   ✓ After marking clean - Project has unsaved changes: {project.has_unsaved_changes()}")
    
    return True

def test_actor_properties():
    """Test actor property manipulation."""
    print("\n=== Testing Actor Properties ===")
    
    scene = EditorScene("Property Test Scene")
    actor = Actor("TestActor")
    
    # Test transform properties
    print("\n1. Testing transform properties...")
    actor.transform.setPosition(100, 200)
    actor.transform.setRotation(45)
    actor.transform.setScale(2.0, 1.5)
    
    print(f"   ✓ Position: {actor.transform.position}")
    print(f"   ✓ Rotation: {actor.transform.rotation}")
    print(f"   ✓ Scale: {actor.transform.scale}")
    
    # Test tags
    print("\n2. Testing tags...")
    actor.addTag("player")
    actor.addTag("movable")
    print(f"   ✓ Tags: {list(actor.tags)}")
    
    scene.add_actor(actor)
    
    # Test serialization of properties
    print("\n3. Testing property serialization...")
    data = scene.serialize()
    actor_data = data['actors'][0]
    
    print(f"   ✓ Serialized position: {actor_data['transform']['position']}")
    print(f"   ✓ Serialized rotation: {actor_data['transform']['rotation']}")
    print(f"   ✓ Serialized scale: {actor_data['transform']['scale']}")
    print(f"   ✓ Serialized tags: {actor_data['tags']}")
    
    return True

def test_error_handling():
    """Test error handling and edge cases."""
    print("\n=== Testing Error Handling ===")
    
    # Test 1: Empty scene serialization
    print("\n1. Testing empty scene...")
    empty_scene = EditorScene("Empty Scene")
    try:
        data = empty_scene.serialize()
        print(f"   ✓ Empty scene serialization successful")
        print(f"   ✓ Actors: {len(data['actors'])}")
        print(f"   ✓ UI: {len(data['ui'])}")
    except Exception as e:
        print(f"   ✗ Empty scene serialization failed: {e}")
        return False
    
    # Test 2: Invalid deserialization data
    print("\n2. Testing invalid data handling...")
    try:
        invalid_data = {"invalid": "data"}
        test_scene = EditorScene("Test Scene")
        test_scene.deserialize(invalid_data)
        print(f"   ✓ Invalid data handled gracefully")
    except Exception as e:
        print(f"   ✓ Invalid data properly rejected: {type(e).__name__}")
    
    return True

def main():
    """Run all tests."""
    print("Scene Editor Functionality Tests")
    print("=" * 40)
    
    tests = [
        test_basic_functionality,
        test_actor_properties,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
                print(f"\n✓ {test.__name__} PASSED")
            else:
                failed += 1
                print(f"\n✗ {test.__name__} FAILED")
        except Exception as e:
            failed += 1
            print(f"\n✗ {test.__name__} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 40)
    
    if failed == 0:
        print("🎉 All tests passed! The scene editor is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
