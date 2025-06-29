# Enhanced Animation Component Documentation

The `FileAnimationComponent` provides a powerful, file-based animation system that prioritizes human readability and ease of use while maintaining good performance.

**Note**: As of the latest version, `FileAnimationComponent` has replaced the original `AnimationComponent` throughout the engine. For backward compatibility, `AnimationComponent` now aliases to `FileAnimationComponent`.

## Features

- **📁 File-Based Animations**: Load animations from YAML or JSON files
- **🎨 Human-Readable Format**: Easy to read and write animation definitions
- **🔄 Advanced Playback**: Loop, ping-pong, frame events, and chained animations
- **📊 Spritesheet Support**: Load frames from spritesheets with rect definitions
- **🎯 Event System**: Trigger callbacks on animation events and specific frames
- **💾 Caching**: Automatic surface caching for performance
- **🔄 Transform Support**: Per-frame offsets, flipping, and transformations

## File Format

### YAML Format (Recommended)

```yaml
name: "Character Name"
base_path: "assets/images/"
default_animation: "idle"

animations:
  idle:
    loop: true
    frames:
      - source: "character_idle_01.png"
        duration: 0.15
      - source: "character_idle_02.png"
        duration: 0.15

  attack:
    loop: false
    next_animation: "idle"
    on_end: "attack_finished"
    frame_events:
      2: "deal_damage"
    frames:
      - source: "character_attack_01.png"
        duration: 0.1
      - source: "character_attack_02.png"
        duration: 0.1
      - source: "character_attack_03.png"
        duration: 0.2
```

### JSON Format

```json
{
  "name": "Character Name",
  "base_path": "assets/images/",
  "default_animation": "idle",
  "animations": {
    "idle": {
      "loop": true,
      "frames": [
        {"source": "character_idle_01.png", "duration": 0.15},
        {"source": "character_idle_02.png", "duration": 0.15}
      ]
    }
  }
}
```

## Animation Properties

### Animation Sequence Properties

- **`loop`** (bool): Whether the animation should loop
- **`ping_pong`** (bool): Play forward then backward
- **`next_animation`** (string): Animation to play after this one finishes
- **`on_start`** (string): Event triggered when animation starts
- **`on_end`** (string): Event triggered when animation ends  
- **`on_loop`** (string): Event triggered when animation loops
- **`frame_events`** (dict): Events triggered on specific frames

### Frame Properties

- **`source`** (string): Image file path (required)
- **`duration`** (float): Frame duration in seconds (default: 0.1)
- **`offset_x`**, **`offset_y`** (int): Position offset for this frame
- **`flip_x`**, **`flip_y`** (bool): Flip the frame
- **`rect_x`**, **`rect_y`**, **`rect_w`**, **`rect_h`** (int): Spritesheet rectangle

## Basic Usage

### 1. Create Animation File

```yaml
name: "My Character"
base_path: "assets/images/"
default_animation: "idle"

animations:
  idle:
    loop: true
    frames:
      - "character_idle_01.png"
      - "character_idle_02.png"
      - "character_idle_03.png"
```

### 2. Add to Actor

```python
from engine import Actor, SpriteComponent, FileAnimationComponent

# Create actor
character = Actor("MyCharacter")
character.add_component(SpriteComponent())

# Add animation component
animation = FileAnimationComponent("assets/data/character_animations.yaml")
character.add_component(animation)
```

### 3. Control Animations

```python
# Play an animation
animation.play("walk")

# Check if playing
if animation.is_playing("attack"):
    print("Currently attacking!")

# Pause/resume
animation.pause()
animation.resume()

# Stop
animation.stop()

# Get available animations
animations = animation.get_animation_names()
```

## Advanced Features

### Event Callbacks

```python
# Set up event callbacks
animation.add_event_callback("attack_finished", on_attack_done)
animation.add_event_callback("deal_damage", on_deal_damage)
animation.add_event_callback("footstep", on_footstep_sound)

def on_attack_done():
    print("Attack animation finished!")
    
def on_deal_damage():
    print("Deal damage to enemies!")
```

### Animation File with Events

```yaml
animations:
  attack:
    loop: false
    next_animation: "idle"
    on_start: "attack_started"
    on_end: "attack_finished"
    frame_events:
      2: "deal_damage"      # Frame 2 triggers damage
      3: "screen_shake"     # Frame 3 triggers screen shake
    frames:
      - source: "attack_01.png"
        duration: 0.1
      - source: "attack_02.png"
        duration: 0.1
      - source: "attack_03.png"
        duration: 0.15
      - source: "attack_04.png"
        duration: 0.1
```

### Spritesheet Support

```yaml
animations:
  explosion:
    loop: false
    frames:
      - source: "effects_sheet.png"
        rect_x: 0
        rect_y: 0
        rect_w: 32
        rect_h: 32
        duration: 0.1
      - source: "effects_sheet.png"
        rect_x: 32
        rect_y: 0
        rect_w: 32
        rect_h: 32
        duration: 0.1
```

### Frame Transformations

```yaml
animations:
  hurt:
    loop: false
    next_animation: "idle"
    frames:
      - source: "character_hurt.png"
        duration: 0.1
        offset_x: -2    # Shake left
      - source: "character_hurt.png"
        duration: 0.1
        offset_x: 2     # Shake right
      - source: "character_hurt.png"
        duration: 0.1
        offset_x: -1    # Smaller shake
      - source: "character_hurt.png"
        duration: 0.1
        offset_x: 1
```

### Ping-Pong Animation

```yaml
animations:
  charge_spell:
    loop: true
    ping_pong: true    # Plays forward then backward
    frames:
      - source: "charge_01.png"
        duration: 0.1
      - source: "charge_02.png"
        duration: 0.1
      - source: "charge_03.png"
        duration: 0.1
      - source: "charge_04.png"
        duration: 0.2
```

## File Size Optimization

### Simplified Format

For simple animations, use the shortened format:

```yaml
animations:
  walk:
    loop: true
    frames:
      - "walk_01.png"  # Just filename, uses default duration
      - "walk_02.png"
      - "walk_03.png"
      - "walk_04.png"
```

### Shared Properties

Use YAML anchors for repeated properties:

```yaml
# Define common frame settings
frame_defaults: &default_frame
  duration: 0.1
  offset_x: 0
  offset_y: 0

animations:
  walk:
    loop: true
    frames:
      - <<: *default_frame
        source: "walk_01.png"
      - <<: *default_frame
        source: "walk_02.png"
```

## Creating Animation Files

### Programmatic Creation

```python
from engine import create_animation_template

# Create a template file
create_animation_template("my_character.yaml", "My Character")
```

### Manual Creation

1. Create a `.yaml` or `.json` file
2. Define the animation set properties
3. Add animations with frames
4. Test with the demo

## Performance Tips

1. **Use Spritesheets**: Reduces file count and loading time
2. **Cache Surfaces**: The component automatically caches loaded images
3. **Reasonable Frame Rates**: Don't use too many frames for simple animations
4. **Optimize Image Sizes**: Use appropriate image dimensions
5. **Use Default Duration**: Omit duration for frames that use the default

## Example: Complete Character

```yaml
name: "Player Character"
base_path: "assets/images/player/"
default_animation: "idle"

animations:
  idle:
    loop: true
    frames:
      - source: "idle_01.png"
        duration: 0.2
      - source: "idle_02.png"
        duration: 0.2
      - source: "idle_03.png"
        duration: 0.2
      - source: "idle_04.png"
        duration: 0.2

  walk:
    loop: true
    frames: ["walk_01.png", "walk_02.png", "walk_03.png", "walk_04.png"]

  run:
    loop: true
    frames:
      - {source: "run_01.png", duration: 0.08}
      - {source: "run_02.png", duration: 0.08}
      - {source: "run_03.png", duration: 0.08}
      - {source: "run_04.png", duration: 0.08}

  jump:
    loop: false
    next_animation: "fall"
    frames:
      - {source: "jump_01.png", duration: 0.1}
      - {source: "jump_02.png", duration: 0.1}
      - {source: "jump_03.png", duration: 0.2}

  fall:
    loop: true
    frames:
      - {source: "fall_01.png", duration: 0.1}
      - {source: "fall_02.png", duration: 0.1}

  attack:
    loop: false
    next_animation: "idle"
    on_start: "attack_started"
    on_end: "attack_finished"
    frame_events:
      2: "deal_damage"
    frames:
      - {source: "attack_01.png", duration: 0.1}
      - {source: "attack_02.png", duration: 0.1}
      - {source: "attack_03.png", duration: 0.15}
      - {source: "attack_04.png", duration: 0.1}

  hurt:
    loop: false
    next_animation: "idle"
    frames:
      - {source: "hurt.png", duration: 0.1, offset_x: -2}
      - {source: "hurt.png", duration: 0.1, offset_x: 2}
      - {source: "hurt.png", duration: 0.1, offset_x: -1}
      - {source: "hurt.png", duration: 0.1, offset_x: 1}

  death:
    loop: false
    frames:
      - {source: "death_01.png", duration: 0.1}
      - {source: "death_02.png", duration: 0.1}
      - {source: "death_03.png", duration: 0.1}
      - {source: "death_04.png", duration: 1.0}
```

## Integration with Existing Code

The `FileAnimationComponent` has completely replaced the original `AnimationComponent`:

- Use `FileAnimationComponent` (or its alias `AnimationComponent`) for all animation needs
- Both can be used in the same project for different purposes

The file-based approach is ideal for:
- Character animations
- Complex sequences
- Artist-created animations
- Rapid iteration and tweaking
- Non-programmer content creation
