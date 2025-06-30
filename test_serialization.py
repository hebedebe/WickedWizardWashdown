"""
Test SpriteComponent serialization
"""

from engine import *
import pygame

def test_sprite_serialization():
    """Test that SpriteComponent can be properly serialized and deserialized."""
    
    print("Testing SpriteComponent serialization...")
    
    # Create a sprite component with various properties
    sprite_comp = SpriteComponent("default_cursor")
    sprite_comp.set_tint(pygame.Color(255, 100, 100, 200))
    sprite_comp.set_alpha(150)
    sprite_comp.set_flip(horizontal=True, vertical=False)
    sprite_comp.scale_modifier = pygame.Vector2(2.5, 1.5)
    sprite_comp.rotation_offset = 45.0
    sprite_comp.offset = pygame.Vector2(10, -5)
    
    # Serialize the component
    serialized_data = sprite_comp.serialize()
    print("Serialized data:")
    print(serialized_data)
    
    # Create a new component and deserialize
    new_sprite_comp = SpriteComponent()
    new_sprite_comp.deserialize(serialized_data)
    
    # Verify the data matches
    print("\nVerification:")
    print(f"Sprite name: {new_sprite_comp.sprite_name} (should be 'default_cursor')")
    print(f"Tint color: {new_sprite_comp.tint_color} (should be (255, 100, 100, 200))")
    print(f"Alpha: {new_sprite_comp.alpha} (should be 150)")
    print(f"Flip horizontal: {new_sprite_comp.flip_horizontal} (should be True)")
    print(f"Flip vertical: {new_sprite_comp.flip_vertical} (should be False)")
    print(f"Scale modifier: {new_sprite_comp.scale_modifier} (should be (2.5, 1.5))")
    print(f"Rotation offset: {new_sprite_comp.rotation_offset} (should be 45.0)")
    print(f"Offset: {new_sprite_comp.offset} (should be (10, -5))")
    
    print("\nSerialization test completed!")

if __name__ == "__main__":
    test_sprite_serialization()
