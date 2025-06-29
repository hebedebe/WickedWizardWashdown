# Animation System

The animation system provides flexible animation support through file-based definitions and runtime property animations.

## Overview

The engine includes two animation systems:
1. **FileAnimationComponent** - File-based sprite animations (YAML/JSON)
2. **PropertyAnimation** - Runtime property tweening and interpolation

## FileAnimationComponent

The main animation component loads animations from external files for easy management and artist-friendly workflows.

### Basic Setup

```python
from engine import FileAnimationComponent

# Load animations from file
animation = FileAnimationComponent("assets/data/player_animations.yaml")
actor.add_component(animation)

# Play animations
animation.play_animation("walk")
animation.play_animation("jump", loop=False)
```

### Animation File Format (YAML)

```yaml
# player_animations.yaml
name: "Player Character"
base_path: "assets/images/"
default_animation: "idle"

animations:
  idle:
    loop: true
    frames:
      - source: "player_idle_01.png"
        duration: 0.15
      - source: "player_idle_02.png"
        duration: 0.15
      - source: "player_idle_03.png"
        duration: 0.15

  walk:
    loop: true
    frames:
      - source: "player_walk_01.png"
        duration: 0.1
      - source: "player_walk_02.png"
        duration: 0.1
      - source: "player_walk_03.png"
        duration: 0.1
      - source: "player_walk_04.png"
        duration: 0.1

  jump:
    loop: false
    next_animation: "idle"
    frames:
      - source: "player_jump_01.png"
        duration: 0.1
      - source: "player_jump_02.png"
        duration: 0.2
      - source: "player_jump_03.png"
        duration: 0.1

  attack:
    loop: false
    next_animation: "idle"
    on_end: "attack_finished"
    frame_events:
      2: "deal_damage"  # Event on frame 2
    frames:
      - source: "player_attack_01.png"
        duration: 0.05
      - source: "player_attack_02.png"
        duration: 0.1
      - source: "player_attack_03.png"
        duration: 0.15
```

### Animation Control

```python
# Play animations
animation.play_animation("walk")
animation.play_animation("attack", loop=False)

# Control playback
animation.pause()
animation.resume()
animation.stop()

# Check status
if animation.is_playing():
    current_anim = animation.current_animation
    frame_index = animation.current_frame
    
# Animation events
def on_attack_finished():
    print("Attack animation completed")
    
def on_deal_damage():
    print("Deal damage to enemies")
    
animation.on_animation_complete = on_attack_finished
animation.on_frame_event = on_deal_damage
```

### Advanced Features

#### Spritesheet Support

```yaml
animations:
  run:
    spritesheet: "character_run_sheet.png"
    frame_size: [32, 32]
    loop: true
    frames:
      - rect: [0, 0, 32, 32]    # x, y, width, height
        duration: 0.1
      - rect: [32, 0, 32, 32]
        duration: 0.1
      - rect: [64, 0, 32, 32]
        duration: 0.1
```

#### Frame Transformations

```yaml
animations:
  flip_walk:
    loop: true
    frames:
      - source: "walk_01.png"
        duration: 0.1
        flip_x: true
        offset: [2, -1]     # Pixel offset
        scale: [1.2, 1.0]   # Scale factors
```

#### Animation Chains

```yaml
animations:
  combo_attack:
    loop: false
    next_animation: "combo_finish"
    frames:
      - source: "combo_01.png"
        duration: 0.1
        
  combo_finish:
    loop: false
    next_animation: "idle"
    frames:
      - source: "combo_02.png"
        duration: 0.2
```

## Property Animation System

Runtime animation of object properties with easing and interpolation.

### Basic Property Animation

```python
from engine import PropertyAnimation, EasingType
import pygame

# Animate actor position
position_anim = PropertyAnimation(
    target=actor.transform,
    property_name="local_position",
    start_value=pygame.Vector2(0, 0),
    end_value=pygame.Vector2(200, 100),
    duration=2.0,
    easing=EasingType.EASE_IN_OUT
)

# Start animation
position_anim.start()

# Update in game loop (usually handled automatically)
position_anim.update(dt)
```

### Easing Types

```python
from engine import EasingType

# Available easing functions
EasingType.LINEAR           # Constant speed
EasingType.EASE_IN          # Slow start, fast end
EasingType.EASE_OUT         # Fast start, slow end  
EasingType.EASE_IN_OUT      # Slow start and end
EasingType.BOUNCE           # Bouncing effect
EasingType.ELASTIC          # Elastic spring effect
EasingType.BACK             # Overshoot and return
```

### Animation Callbacks

```python
def on_move_complete():
    print("Movement finished")
    
def on_move_update(current_value):
    print(f"Current position: {current_value}")

position_anim = PropertyAnimation(
    target=actor.transform,
    property_name="local_position", 
    start_value=pygame.Vector2(0, 0),
    end_value=pygame.Vector2(200, 100),
    duration=1.5,
    on_complete=on_move_complete,
    on_update=on_move_update
)
```

### Animating Different Properties

```python
# Scale animation
scale_anim = PropertyAnimation(
    target=actor.transform,
    property_name="local_scale",
    start_value=pygame.Vector2(1.0, 1.0),
    end_value=pygame.Vector2(2.0, 2.0),
    duration=1.0,
    easing=EasingType.BOUNCE
)

# Rotation animation
rotation_anim = PropertyAnimation(
    target=actor.transform,
    property_name="local_rotation",
    start_value=0,
    end_value=360,
    duration=2.0,
    easing=EasingType.LINEAR
)

# Component property animation
sprite = actor.get_component(SpriteComponent)
alpha_anim = PropertyAnimation(
    target=sprite,
    property_name="alpha",
    start_value=255,
    end_value=0,
    duration=1.0,
    easing=EasingType.EASE_OUT
)
```

## Animation Templates

Create reusable animation templates:

```python
from engine import create_animation_template

# Create template for fade out effect
fade_out_template = create_animation_template({
    "property": "alpha",
    "start_value": 255,
    "end_value": 0,
    "duration": 1.0,
    "easing": EasingType.EASE_OUT
})

# Apply to different sprites
sprite1 = actor1.get_component(SpriteComponent)
fade_anim1 = fade_out_template.create_animation(sprite1)

sprite2 = actor2.get_component(SpriteComponent)
fade_anim2 = fade_out_template.create_animation(sprite2)
```

## Animation Sequences

Chain multiple animations together:

```python
class AnimationSequence:
    def __init__(self):
        self.animations = []
        self.current_index = 0
        
    def add_animation(self, animation):
        animation.on_complete = self.next_animation
        self.animations.append(animation)
        
    def start(self):
        if self.animations:
            self.current_index = 0
            self.animations[0].start()
            
    def next_animation(self):
        self.current_index += 1
        if self.current_index < len(self.animations):
            self.animations[self.current_index].start()
        else:
            self.on_sequence_complete()
            
    def on_sequence_complete(self):
        pass  # Override in subclass

# Usage
sequence = AnimationSequence()
sequence.add_animation(move_anim)
sequence.add_animation(scale_anim)
sequence.add_animation(fade_anim)
sequence.start()
```

## Practical Examples

### Character Animation Controller

```python
class CharacterAnimator(Component):
    def __init__(self, animation_file):
        super().__init__()
        self.animation_comp = FileAnimationComponent(animation_file)
        self.current_state = "idle"
        
    def start(self):
        self.actor.add_component(self.animation_comp)
        
    def set_state(self, new_state):
        if new_state != self.current_state:
            self.current_state = new_state
            self.animation_comp.play_animation(new_state)
            
    def update(self, dt):
        # Get physics component to determine animation state
        physics = self.actor.get_component(RigidBodyComponent)
        if physics:
            velocity = physics.get_velocity()
            
            if abs(velocity[0]) > 10:  # Moving horizontally
                self.set_state("walk")
            elif velocity[1] < -50:   # Jumping
                self.set_state("jump")
            elif velocity[1] > 50:    # Falling
                self.set_state("fall")
            else:                     # Standing still
                self.set_state("idle")
```

### UI Animation Effects

```python
class UIAnimator:
    @staticmethod
    def slide_in(widget, direction="left", duration=0.5):
        """Slide widget in from edge of screen"""
        screen_size = pygame.display.get_surface().get_size()
        
        if direction == "left":
            start_pos = pygame.Vector2(-widget.rect.width, widget.rect.y)
        elif direction == "right":
            start_pos = pygame.Vector2(screen_size[0], widget.rect.y)
        elif direction == "top":
            start_pos = pygame.Vector2(widget.rect.x, -widget.rect.height)
        else:  # bottom
            start_pos = pygame.Vector2(widget.rect.x, screen_size[1])
            
        end_pos = pygame.Vector2(widget.rect.x, widget.rect.y)
        
        # Temporarily move widget to start position
        widget.rect.topleft = start_pos
        
        # Animate to final position
        return PropertyAnimation(
            target=widget.rect,
            property_name="topleft",
            start_value=start_pos,
            end_value=end_pos,
            duration=duration,
            easing=EasingType.EASE_OUT
        )
        
    @staticmethod
    def fade_in(widget, duration=0.3):
        """Fade widget in"""
        return PropertyAnimation(
            target=widget,
            property_name="alpha",
            start_value=0,
            end_value=255,
            duration=duration,
            easing=EasingType.EASE_IN
        )
```

### Particle Animation

```python
class AnimatedParticle(Component):
    def __init__(self):
        super().__init__()
        self.setup_animations()
        
    def setup_animations(self):
        sprite = self.actor.get_component(SpriteComponent)
        
        # Fade out over lifetime
        self.fade_anim = PropertyAnimation(
            target=sprite,
            property_name="alpha",
            start_value=255,
            end_value=0,
            duration=2.0,
            easing=EasingType.LINEAR
        )
        
        # Scale down over time
        self.scale_anim = PropertyAnimation(
            target=self.actor.transform,
            property_name="local_scale",
            start_value=pygame.Vector2(1.0, 1.0),
            end_value=pygame.Vector2(0.1, 0.1),
            duration=2.0,
            easing=EasingType.EASE_IN
        )
        
        # Cleanup when fade completes
        self.fade_anim.on_complete = self.destroy_particle
        
    def start(self):
        self.fade_anim.start()
        self.scale_anim.start()
        
    def destroy_particle(self):
        self.actor.scene.destroy_actor(self.actor)
```

## Performance Considerations

### Optimization Tips

1. **Reuse Animation Objects** - Don't create new animations every frame
2. **Pool Animation Components** - Reuse for frequently animated objects
3. **Limit Active Animations** - Too many simultaneous animations can slow performance
4. **Use Appropriate Frame Rates** - Match animation framerate to content needs

### Memory Management

```python
# Clean up animations when done
animation.on_complete = lambda: animation.cleanup()

# Stop all animations when actor is destroyed
class AnimatedActor(Actor):
    def destroy(self):
        animation = self.get_component(FileAnimationComponent)
        if animation:
            animation.stop()
        super().destroy()
```

## Best Practices

1. **Organize Animation Files** - Keep animations in logical files by character/object
2. **Use Consistent Naming** - Follow naming conventions for easy reference
3. **Test Frame Timing** - Ensure animations feel responsive
4. **Plan Animation States** - Design state machines for complex character behavior
5. **Optimize Assets** - Keep animation frames reasonably sized
6. **Document Events** - Comment frame events and their purposes

The animation system provides both simple sprite animation and complex property tweening, suitable for a wide range of game animation needs.
