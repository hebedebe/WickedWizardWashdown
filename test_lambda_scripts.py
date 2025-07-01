#!/usr/bin/env python3
"""
Test script to verify lambda scripting functionality
"""

import sys
import os

# Add the parent directory to the path to import engine modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_lambda_scripts():
    """Test lambda script functionality"""
    print("Testing lambda script functionality...")
    
    try:
        import pygame
        pygame.init()
        pygame.font.init()
        
        from PyQt6.QtWidgets import QApplication
        
        # Need QApplication for GUI components
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from editor.editor import EditorScene
        from engine.ui.builtin.button import Button
        from engine.actor.actor import Actor
        
        # Test Scene lambda scripts
        print("\n=== Testing Scene Lambda Scripts ===")
        scene = EditorScene()
        
        # Add some test scripts
        scene.add_lambda_script('onEnter', 'print("Scene entered!")')
        scene.add_lambda_script('update', 'print(f"Update called with dt={dt}")')
        scene.add_lambda_script('update', 'actors[0].name = "Updated Actor"')
        
        # Add a test actor
        test_actor = Actor("TestActor")
        scene.addActor(test_actor)
        
        print(f"Scene lambda scripts: {scene.lambda_scripts}")
        
        # Test script execution
        print("Testing onEnter scripts...")
        scene.execute_lambda_scripts('onEnter')
        
        print("Testing update scripts...")
        scene.execute_lambda_scripts('update', dt=0.016)
        
        print(f"Actor name after script: {test_actor.name}")
        
        # Test UI Widget lambda scripts
        print("\n=== Testing UI Widget Lambda Scripts ===")
        button = Button(pygame.Rect(0, 0, 100, 30), "Test Button", name="TestButton")
        
        # Add lambda scripts to button
        button.add_lambda_script('click', 'print("Button clicked!")')
        button.add_lambda_script('custom', 'widget.visible = not widget.visible')
        
        print(f"Button lambda scripts: {button.lambda_scripts}")
        
        # Test script execution
        print("Testing click script...")
        button.execute_lambda_script('click', None)
        
        print("Testing custom script...")
        initial_visibility = button.visible
        button.execute_lambda_script('custom', None)
        print(f"Button visibility changed: {initial_visibility} -> {button.visible}")
        
        # Test serialization
        print("\n=== Testing Serialization ===")
        scene_data = scene.serialize()
        print("Scene lambda scripts in serialization:", scene_data.get('lambda_scripts', {}))
        
        # Test widget serialization
        widget_data = scene._serializeUIElement(button)
        print("Widget lambda scripts in serialization:", widget_data.get('lambda_scripts', {}))
        
        print("\n✅ All lambda script tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing lambda scripts: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_lambda_scripts()
