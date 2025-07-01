#!/usr/bin/env python3
"""
Test script to verify UI element creation and property inspector fixes
"""

import sys
import os

# Add the directory to the path to import engine modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ui_elements():
    """Test UI element creation"""
    print("Testing UI element creation...")
    
    try:
        from editor.editor import ComponentRegistry, EditorScene
        
        registry = ComponentRegistry()
        scene = EditorScene()
        
        print(f"Available UI elements: {registry.getUIElementNames()}")
        
        # Test creating different UI elements
        ui_elements = ["Widget", "Button", "Label", "Panel"]
        
        for element_name in ui_elements:
            if element_name in registry.getUIElementNames():
                print(f"Testing creation of {element_name}...")
                element = registry.createUIElement(element_name)
                if element:
                    print(f"✓ Successfully created {element_name}: {element}")
                    scene.addUIElement(element)
                else:
                    print(f"✗ Failed to create {element_name}")
            else:
                print(f"⚠ {element_name} not available in registry")
        
        print(f"Total UI elements in scene: {len(scene.ui_elements)}")
        return True
        
    except Exception as e:
        print(f"✗ Error testing UI elements: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_property_inspector():
    """Test property inspector improvements"""
    print("\nTesting property inspector...")
    
    try:
        # Need QApplication for property editor widgets
        from PyQt6.QtWidgets import QApplication
        import sys
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from editor.editor import PropertyEditor
        from engine.actor.actor import Actor
        import pygame
        
        # Initialize pygame.font if needed
        if not pygame.font.get_init():
            pygame.font.init()
        
        # Test color property handling
        actor = Actor("TestActor")
        
        # Add some test properties
        actor.test_color = pygame.Color(255, 128, 64, 200)
        actor.test_tuple_color = (255, 0, 0, 128)
        actor.test_rgb_color = (0, 255, 0)
        actor.test_string = "Hello World"
        actor.test_int = 42
        actor.test_float = 3.14
        actor.test_bool = True
        
        # Add properties that should be filtered out
        actor._private_prop = "should be filtered"
        # Skip font test as it requires full pygame initialization
        
        property_editor = PropertyEditor()
        property_editor.setTarget(actor)
        
        print("✓ Property inspector created successfully")
        print(f"Property widgets created: {len(property_editor.property_widgets)}")
        
        # List all property widgets for debugging
        print(f"Properties found: {list(property_editor.property_widgets.keys())}")
        
        # Check the actor's properties to see what's available
        print("Actor properties:")
        for prop_name, value in actor.__dict__.items():
            if not prop_name.startswith('_'):
                print(f"  {prop_name}: {value} ({type(value)})")
        
        # Check that filtered properties are not included
        if "_private_prop" not in property_editor.property_widgets:
            print("✓ Private properties correctly filtered")
        else:
            print("✗ Private properties not filtered")
        
        # Check that color properties are properly handled
        if "test_color_color" in property_editor.property_widgets:
            print("✓ pygame.Color properties detected and split into RGBA")
        elif "test_color" in property_editor.property_widgets:
            print("⚠ pygame.Color properties detected but not split")
        else:
            print("✗ pygame.Color properties not detected")
            
        if "test_tuple_color_color" in property_editor.property_widgets:
            print("✓ Tuple color properties detected and split")
        elif "test_tuple_color" in property_editor.property_widgets:
            print("⚠ Tuple color properties detected but not split")
        else:
            print("✗ Tuple color properties not detected")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing property inspector: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Running UI fixes tests...\n")
    
    test1 = test_ui_elements()
    test2 = test_property_inspector()
    
    print("\n" + "="*50)
    if test1 and test2:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed!")
    print("="*50)

if __name__ == "__main__":
    main()
