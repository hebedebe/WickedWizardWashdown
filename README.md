# Wicked Wizard Washdown

A 2D game engine built with pygame-ce featuring a complete component-based architecture.

## Features

- **Entity-Component-System Architecture** - Flexible game object composition with reusable components
- **Scene Management** - Complete scene system with transitions and state management
- **Physics System** - Integrated pymunk physics with collision detection
- **UI System** - Widget-based user interface with buttons, labels, and controls
- **Particle System** - Flexible particle effects system
- **Asset Management** - Efficient loading and caching of game assets
- **Animation System** - Frame-based and property animation support

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Game**
   ```bash
   python main.py
   ```

## Project Structure

```
WickedWizardWashdown/
├── main.py                 # Game entry point
├── requirements.txt        # Python dependencies
├── engine/                # Core game engine
│   ├── __init__.py        # Main Game class
│   ├── scene.py           # Scene management
│   ├── actor.py           # Actor and Component base classes
│   ├── components.py      # Core components (Sprite, Physics, etc.)
│   ├── physics.py         # Physics system with pymunk
│   ├── networking.py      # Client-server networking
│   ├── ui.py             # User interface widgets
│   └── ...
├── game/                  # Game-specific code
│   ├── scenes/           # Game scenes
│   ├── actors/           # Game-specific actors
│   └── components/       # Game-specific components
├── assets/               # Game assets
│   ├── images/
│   ├── sounds/
│   └── data/
├── examples/             # Example implementations
└── Documentation/        # API documentation
```

## Game Flow

1. **Main Menu** - Start screen with game options
2. **Game Select** - Choose single player or multiplayer
3. **Lobby System** - Multiplayer lobby creation and joining
4. **Gameplay** - Main game with physics and networking

## Engine Components

### Core Systems
- **Game** - Main game loop and system management
- **Scene** - Container for game objects and logic
- **Actor** - Base game entity with transform and components
- **Component** - Modular behavior system

### Available Components
- **SpriteComponent** - 2D rendering
- **PhysicsComponent** - Physics simulation
- **NetworkComponent** - Network synchronization
- **InputComponent** - Input handling
- **HealthComponent** - Health/damage system
- **AnimationComponent** - Animation playback

## Development

### Adding New Scenes
```python
from engine import Scene

class MyScene(Scene):
    def on_enter(self):
        super().on_enter()
        # Scene initialization
        
    def update(self, dt):
        super().update(dt)
        # Scene logic
```

### Creating Custom Components
```python
from engine import Component

class MyComponent(Component):
    def update(self, dt):
        # Component logic
        pass
```

## Examples

The `examples/` directory contains complete demonstrations of engine features:
- **basic_game.py** - Simple game setup
- **physics_demo.py** - Physics system showcase
- **networking_demo.py** - Multiplayer networking
- **ui_demo.py** - User interface widgets
- **particle_demo.py** - Particle effects

## API Documentation

Comprehensive documentation is available in the `Documentation/` directory:
- **[Documentation Index](Documentation/README.md)** - Complete documentation overview
- **[API Quick Reference](Documentation/API_QUICK_REFERENCE.md)** - Essential API reference
- **[Getting Started](Documentation/GETTING_STARTED.md)** - Installation and setup guide
- **[Best Practices](Documentation/BEST_PRACTICES.md)** - Recommended patterns and approaches

## Requirements

- Python 3.8+
- pygame-ce >= 2.5.5
- pymunk >= 6.7.0
- numpy >= 1.24.0
- PyYAML >= 6.0
- Pillow >= 10.0.0

## License

This project is provided as-is for educational and development purposes.
