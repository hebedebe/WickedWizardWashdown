# Wicked Wizard Washdown - 2D Networked Game Engine

A comprehensive 2D game engine built with pygame-ce that supports:

- **Actors with hierarchical children** - Game objects that can contain other actors
- **Component System** - Modular components for behavior, rendering, physics, etc.
- **Asset Loading** - Efficient loading and management of images, sounds, fonts, and other assets
- **Particle System** - Flexible particle effects system
- **UI System** - Complete user interface system with widgets
- **Networking** - Built-in networking for multiplayer games
- **Built-in pygame classes** - Leverages pygame.Vector2, pygame.Rect, pygame.Surface, etc.

## Getting Started

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the example:
```bash
python examples/basic_game.py
```

## Architecture

The engine follows an Entity-Component-System (ECS) architecture where:
- **Actors** are game entities that can have children and components
- **Components** provide specific functionality (rendering, physics, input, etc.)
- **Systems** manage and update components each frame
- **Scenes** contain and manage actors

## Features

### Core Engine
- Game loop with fixed timestep
- Scene management
- Input handling
- Delta time calculations

### Actor System
- Hierarchical actor relationships (parent/child)
- Transform management with inheritance
- Component attachment/detachment

### Component System
- Transform, Sprite, Physics, Input, Audio components
- Easy extension for custom components
- Automatic registration and updates

### Asset Management
- Lazy loading of assets
- Caching and reference counting
- Support for images, sounds, fonts, and data files

### Particle System
- Emitter-based particle system
- Configurable particle properties
- Built-in particle behaviors

### UI System
- Widget-based UI with buttons, labels, panels
- Event handling and theming
- Layout management

### Networking
- Client-server architecture
- Message serialization
- State synchronization
