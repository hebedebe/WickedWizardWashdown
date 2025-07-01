#!/usr/bin/env python3
"""
Simple test to verify the editor can be imported and basic functionality works.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to sys.path so we can import the engine
parent_dir = Path(__file__).parent
sys.path.insert(0, str(parent_dir))

def test_imports():
    """Test that all editor modules can be imported successfully."""
    print("Testing editor imports...")
    
    try:
        # Import editor modules one by one to identify any issues
        print("  Importing editor_utils...")
        from editor import editor_utils
        
        print("  Importing editor_dummy...")
        from editor import editor_dummy
        
        print("  Importing editor_scene...")
        from editor import editor_scene
        
        print("  Importing editor_project...")
        from editor import editor_project
        
        print("  Importing editor_hierarchy...")
        from editor import editor_hierarchy
        
        print("  Importing editor_inspector...")
        from editor import editor_inspector
        
        print("  Importing editor_scene_view...")
        from editor import editor_scene_view
        
        print("  Importing editor_console...")
        from editor import editor_console
        
        print("  Importing editor_tools...")
        from editor import editor_tools
        
        print("  Importing editor_main_window...")
        from editor import editor_main_window
        
        print("All imports successful!")
        return True
        
    except Exception as e:
        print(f"Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic editor functionality without launching GUI."""
    print("\nTesting basic functionality...")
    
    try:
        from editor.editor_utils import discover_components, discover_widgets, setup_logging
        from editor.editor_project import EditorProject
        from editor.editor_scene import EditorScene
        
        # Test setup logging
        print("  Testing logging setup...")
        setup_logging()
        
        # Test component discovery
        print("  Testing component discovery...")
        components = discover_components()
        print(f"    Found {len(components)} components")
        
        # Test widget discovery
        print("  Testing widget discovery...")
        widgets = discover_widgets()
        print(f"    Found {len(widgets)} widgets")
        
        # Test project creation
        print("  Testing project creation...")
        project = EditorProject()
        
        # Test scene creation
        print("  Testing scene creation...")
        scene = EditorScene()
        scene.name = "TestScene"
        
        print("Basic functionality test successful!")
        return True
        
    except Exception as e:
        print(f"Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = True
    
    success &= test_imports()
    success &= test_basic_functionality()
    
    if success:
        print("\n✅ All tests passed! Editor is ready.")
    else:
        print("\n❌ Some tests failed. Check errors above.")
    
    sys.exit(0 if success else 1)
