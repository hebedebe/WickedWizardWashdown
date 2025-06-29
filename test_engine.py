#!/usr/bin/env python3
"""
Test script to validate the Wicked Wizard Washdown game engine.
"""

import sys
import os
import traceback
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all engine modules import correctly."""
    print("Testing imports...")
    
    try:
        # Test main engine import
        from engine import Game
        print("✓ Game class imported")
        
        # Test core modules
        from engine.actor import Actor, Component, Transform
        print("✓ Actor system imported")
        
        from engine.components import (
            SpriteComponent, PhysicsComponent, InputComponent,
            AudioComponent, AnimationComponent, HealthComponent
        )
        print("✓ Components imported")
        
        from engine.scene import Scene
        print("✓ Scene system imported")
        
        from engine.asset_manager import AssetManager
        print("✓ Asset manager imported")
        
        from engine.particles import ParticleSystem, ParticleEmitter
        print("✓ Particle system imported")
        
        from engine.ui import UIManager, Widget, Panel, Label, Button, Slider
        print("✓ UI system imported")
        
        from engine.input_manager import InputManager
        print("✓ Input manager imported")
        
        from engine.networking import NetworkManager
        print("✓ Network manager imported")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic engine functionality without creating a window."""
    print("\\nTesting basic functionality...")
    
    try:
        # Prevent pygame from initializing video (for headless testing)
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        
        from engine import Game, Actor, SpriteComponent, Transform
        import pygame
        
        # Initialize pygame without video
        pygame.mixer.pre_init()
        pygame.mixer.init()
        pygame.font.init()
        
        print("✓ Pygame initialized")
        
        # Test Actor creation
        actor = Actor("TestActor")
        assert actor.name == "TestActor"
        assert actor.active == True
        print("✓ Actor creation")
        
        # Test Transform
        transform = Transform()
        assert isinstance(transform.local_position, pygame.Vector2)
        print("✓ Transform system")
        
        # Test Component system
        sprite = SpriteComponent()
        actor.add_component(sprite)
        assert actor.has_component(SpriteComponent)
        assert actor.get_component(SpriteComponent) == sprite
        print("✓ Component system")
        
        # Test hierarchy
        child = Actor("Child")
        actor.add_child(child)
        assert child.parent == actor
        assert child in actor.children
        print("✓ Actor hierarchy")
        
        # Test Asset Manager
        from engine.asset_manager import AssetManager
        asset_manager = AssetManager()
        assert asset_manager.base_path.name == "assets"
        print("✓ Asset manager")
        
        # Test Input Manager
        from engine.input_manager import InputManager
        input_manager = InputManager()
        input_manager.bind_key("test", pygame.K_SPACE)
        assert "test" in input_manager.key_bindings
        print("✓ Input manager")
        
        # Test Particle System
        from engine.particles import ParticleSystem, ParticleEmitter
        particle_system = ParticleSystem()
        emitter = ParticleEmitter(pygame.Vector2(100, 100))
        particle_system.add_emitter(emitter)
        assert len(particle_system.emitters) == 1
        print("✓ Particle system")
        
        # Test UI System
        from engine.ui import UIManager, Button
        ui_manager = UIManager((800, 600))
        button = Button(pygame.Rect(10, 10, 100, 30), "Test")
        ui_manager.add_widget(button)
        assert len(ui_manager.root_widgets) == 1
        print("✓ UI system")
        
        # Test Network Manager (without actual networking)
        from engine.networking import NetworkManager
        network_manager = NetworkManager()
        assert network_manager.mode is None
        print("✓ Network manager")
        
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        traceback.print_exc()
        return False

def test_examples_syntax():
    """Test that example files have valid syntax."""
    print("\\nTesting example syntax...")
    
    examples_dir = Path(__file__).parent / "examples"
    if not examples_dir.exists():
        print("✗ Examples directory not found")
        return False
        
    examples = [
        "basic_game.py",
        "multiplayer_game.py", 
        "particle_demo.py",
        "ui_demo.py"
    ]
    
    for example in examples:
        example_path = examples_dir / example
        if not example_path.exists():
            print(f"✗ Example not found: {example}")
            continue
            
        try:
            with open(example_path, 'r', encoding='utf-8') as f:
                code = f.read()
            compile(code, str(example_path), 'exec')
            print(f"✓ {example} syntax valid")
        except Exception as e:
            print(f"✗ {example} syntax error: {e}")
            return False
            
    return True

def test_asset_structure():
    """Test that asset directories exist."""
    print("\\nTesting asset structure...")
    
    base_path = Path(__file__).parent / "assets"
    required_dirs = ["images", "sounds", "fonts", "data"]
    
    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        if dir_path.exists():
            print(f"✓ {dir_name} directory exists")
        else:
            print(f"✗ {dir_name} directory missing")
            return False
            
    # Test data file
    config_file = base_path / "data" / "game_config.json"
    if config_file.exists():
        try:
            import json
            with open(config_file, 'r') as f:
                config = json.load(f)
            print("✓ Game config file valid")
        except Exception as e:
            print(f"✗ Game config file invalid: {e}")
            return False
    else:
        print("✗ Game config file missing")
        return False
        
    return True

def main():
    """Run all tests."""
    print("Wicked Wizard Washdown Engine Test Suite")
    print("=" * 45)
    
    tests = [
        test_imports,
        test_basic_functionality,
        test_examples_syntax,
        test_asset_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
        
    print("=" * 45)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The engine is ready to use.")
        print("\\nTo run examples:")
        print("  python launch.py basic       # Basic game demo")
        print("  python launch.py particles   # Particle effects demo")
        print("  python launch.py ui          # UI system demo")
        print("  python launch.py multiplayer --server  # Multiplayer server")
        print("  python launch.py multiplayer --client  # Multiplayer client")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
