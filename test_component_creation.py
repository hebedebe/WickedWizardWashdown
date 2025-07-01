#!/usr/bin/env python3
"""
Test script to verify component creation fixes
"""

import sys
import os

# Add the parent directory to the path to import engine modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_component_creation():
    """Test component creation with various components"""
    print("Testing component creation...")
    
    try:
        import pygame
        pygame.init()
        pygame.font.init()
        
        from editor.editor import ComponentRegistry
        
        registry = ComponentRegistry()
        available_components = registry.getComponentNames()
        print(f"Available components: {available_components}")
        
        success_count = 0
        total_count = len(available_components)
        
        for component_name in available_components:
            print(f"\nTesting creation of {component_name}...")
            component = registry.createComponent(component_name)
            
            if component:
                print(f"✓ Successfully created {component_name}: {component}")
                success_count += 1
            else:
                print(f"✗ Failed to create {component_name}")
        
        print(f"\n==================================================")
        print(f"Component creation results: {success_count}/{total_count} successful")
        
        if success_count == total_count:
            print("✓ All components created successfully!")
        elif success_count > 0:
            print("⚠ Some components created successfully")
        else:
            print("✗ No components could be created")
        print(f"==================================================")
        
        return success_count > 0
        
    except Exception as e:
        print(f"✗ Error testing component creation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_component_creation()
