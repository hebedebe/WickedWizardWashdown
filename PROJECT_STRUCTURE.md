# Project Structure Overview

## Main Files
- `main.py` - Game entry point and setup
- `requirements.txt` - Python dependencies
- `dev.py` - Development utilities script
- `README.md` - Project documentation
- `.gitignore` - Git ignore rules

## Engine Directory (`engine/`)
Core game engine with modular components:

- `__init__.py` - Main Game class and engine exports
- `scene.py` - Scene management system  
- `actor.py` - Base Actor and Component classes
- `components.py` - Core components (Sprite, Physics, Input, etc.)
- `physics.py` - Physics system using pymunk
- `networking.py` - Client-server networking
- `network_component.py` - Network synchronization component
- `ui.py` - User interface widgets and management
- `input_manager.py` - Input handling system
- `asset_manager.py` - Asset loading and caching
- `particles.py` - Particle system
- `enhanced_animation.py` - Animation system
- `text_component.py` - Text rendering component

## Game Directory (`game/`)
Game-specific implementations:

### Scenes (`game/scenes/`)
- `__init__.py` - Scene exports
- `main_menu.py` - Main menu with navigation
- `settings.py` - Settings/options screen
- `game_select.py` - Game mode selection
- `lobby_select.py` - Multiplayer lobby selection
- `lobby.py` - Multiplayer lobby waiting room
- `game.py` - Main gameplay scene

### Actors (`game/actors/`)
- `player.py` - Player character implementation

### Components (`game/components/`)
- `physics_player_controller.py` - Player movement controller
- `player_data_component.py` - Player data management
- `tilemap.py` - Tilemap rendering component

### Data (`game/`)
- `player_data.py` - Player data models

## Assets Directory (`assets/`)
Game assets organized by type:
- `images/` - Sprites, textures, UI elements
- `sounds/` - Audio files
- `fonts/` - Font files
- `data/` - Configuration and data files

## Examples Directory (`examples/`)
Demonstration and test implementations:
- `basic_game.py` - Simple game setup example
- `physics_demo.py` - Physics system demonstration
- `network_component_demo.py` - Networking example
- `multiplayer_game.py` - Complete multiplayer example
- `ui_demo.py` - UI widgets demonstration
- `particle_demo.py` - Particle effects showcase
- `enhanced_animation_demo.py` - Animation system demo
- `fps_demo.py` - FPS monitoring example
- `singleton_demo.py` - Singleton pattern demonstration
- `property_animation_demo.py` - Property animation example

## Documentation Directory (`Documentation/`)
API and technical documentation:
- `API_REFERENCE.md` - Complete API documentation
- `PHYSICS_SYSTEM_DOCS.md` - Physics system details
- `NETWORK_COMPONENT_DOCS.md` - Networking documentation
- `ENHANCED_ANIMATION_DOCS.md` - Animation system documentation

## Architecture Overview

The engine follows an Entity-Component-System (ECS) pattern:

1. **Entities (Actors)** - Game objects that can contain components
2. **Components** - Modular behaviors attached to actors
3. **Systems** - Manage and update components each frame
4. **Scenes** - Containers that manage collections of actors

### Key Design Patterns Used:
- **Singleton** - Game class for global access
- **Component Pattern** - Modular actor behaviors
- **Observer Pattern** - Event handling in UI and networking
- **Factory Pattern** - Asset creation and management
- **Strategy Pattern** - Different physics body types

### Data Flow:
1. Game loop updates current scene
2. Scene updates all active actors
3. Actors update their components
4. Systems (physics, rendering) process components
5. Scene renders all actors to screen
