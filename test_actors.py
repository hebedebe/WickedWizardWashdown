#!/usr/bin/env python3
"""
Test script for the scene editor actor spawning functionality.
"""

import sys
import os
from pathlib import Path

# Add the project directory to sys.path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Import pygame first to initialize it
import pygame
pygame.init()

# Import and patch engine
from editor import editor_dummy

from editor.editor_scene import EditorScene
from engine.actor.actor import Actor

def test_actor_creation():
    """Test creating and adding actors to a scene."""
    print("Testing actor creation...")
    
    # Create a scene
    scene = EditorScene("Test Scene")
    
    # Create an actor
    actor1 = Actor("TestActor1")
    print(f"Created actor: {actor1.name}")
    
    # Add actor to scene
    scene.add_actor(actor1)
    print(f"Added actor to scene. Scene has {len(scene.scene.actors)} actors")
    
    # Create another actor with parent
    actor2 = Actor("TestActor2")
    actor1.addChild(actor2)
    scene.add_actor(actor2)
    print(f"Added child actor. Scene has {len(scene.scene.actors)} actors")
    
    # Test serialization
    print("\nTesting serialization...")
    try:
        data = scene.serialize()
        print("Serialization successful!")
        print(f"Serialized {len(data['actors'])} actors")
        
        # Test deserialization
        new_scene = EditorScene("New Test Scene")
        new_scene.deserialize(data)
        print(f"Deserialization successful! New scene has {len(new_scene.scene.actors)} actors")
        
    except Exception as e:
        print(f"Serialization/Deserialization failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("Actor creation test completed!")

if __name__ == "__main__":
    test_actor_creation()
