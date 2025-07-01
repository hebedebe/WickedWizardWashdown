# Wicked Wizard Washdown - Scene Editor

A comprehensive PyQt6-based scene editor for the Wicked Wizard Washdown game engine.

## Features

### Core Functionality
- **Actor Hierarchy Management**: Create, delete, and organize actors in a tree structure
- **Drag & Drop Parenting**: Drag actors onto each other to establish parent-child relationships
- **Component System**: Add, remove, and configure components on actors
- **Property Inspector**: Edit actor properties, transforms, and component settings
- **UI Element Support**: Manage UI widgets and elements
- **Custom Module Import**: Import custom components and UI elements from Python files

### File Operations
- **New Scene**: Create a new empty scene
- **Open/Save**: Load and save scenes in JSON format
- **Recent Files**: Quick access to recently opened files
- **Auto-save Warning**: Prompts when closing with unsaved changes

### Editing Features
- **Undo/Redo**: Full undo/redo support for all operations
- **Copy/Paste**: Copy and paste actors with all their components
- **Multi-selection**: Select and operate on multiple actors
- **Property Editing**: Real-time property editing with validation

### Keyboard Shortcuts
- `Ctrl+N`: New Scene
- `Ctrl+O`: Open Scene
- `Ctrl+S`: Save Scene
- `Ctrl+Shift+S`: Save Scene As
- `Ctrl+Z`: Undo
- `Ctrl+Y`: Redo
- `Ctrl+C`: Copy Actor
- `Ctrl+V`: Paste Actor
- `F5`: Refresh
- `Ctrl+Q`: Quit

## Getting Started

### Prerequisites
- Python 3.13+
- PyQt6
- Game engine modules (automatically loaded)

### Installation
1. Ensure PyQt6 is installed:
   ```bash
   pip install PyQt6
   ```

2. Run the editor:
   ```bash
   python editor/main.py
   ```
   
   Or use the convenience script:
   ```bash
   python editor/run_editor.py
   ```

## Usage Guide

### Creating Actors
1. Click "Add Actor" or use the menu `File > Add Actor`
2. Enter a name for the actor
3. The actor will appear in the hierarchy tree

### Managing Actor Hierarchy
- **Parent/Child Relationships**: Drag an actor onto another to make it a child
- **Removing Parent**: Drag an actor to empty space to remove its parent
- **Expanding/Collapsing**: Click the triangle icons to expand/collapse children

### Adding Components
1. Select an actor in the hierarchy
2. In the Components panel, choose a component type from the dropdown
3. Click "Add Component"
4. Configure the component properties in the Inspector

### Property Editing
1. Select an actor or component
2. Use the Inspector panel to edit properties
3. Changes are applied immediately and support undo/redo

### Working with UI Elements
1. Switch to the "UI Elements" tab
2. Select a UI element type from the dropdown
3. Click "Add UI Element"
4. Configure the element properties

### Importing Custom Components
1. Go to `File > Import Custom Module...`
2. Select a Python file containing custom Component or Widget classes
3. The new components/UI elements will appear in the respective dropdowns

### Scene Files
- Scenes are saved as JSON files with `.json` extension
- The format includes all actors, components, and their relationships
- Files can be loaded into the game engine for runtime use

## File Structure

```
editor/
├── main.py              # Main scene editor application
├── run_editor.py        # Convenience runner script
└── README.md           # This file
```

## Architecture

### Core Classes
- **SceneEditor**: Main application window and coordinator
- **EditorScene**: Simplified scene class for editor use
- **ActorTreeWidget**: Hierarchical actor display with drag & drop
- **PropertyEditor**: Generic property editing system
- **ComponentListWidget**: Component management interface
- **ComponentRegistry**: Registry for available components and UI elements

### Undo System
- Full undo/redo support using Qt's QUndoStack
- Commands for: Actor creation/deletion, property changes, hierarchy changes
- Visual feedback in menus and toolbars

### File Format
Scene files use JSON format with the following structure:
```json
{
  "actors": [
    {
      "name": "ActorName",
      "tags": ["tag1", "tag2"],
      "components": [
        {
          "type": "ComponentType",
          "module": "module.path",
          "property1": "value1"
        }
      ],
      "parent_name": "ParentActorName",
      "children_names": ["ChildActor1", "ChildActor2"]
    }
  ],
  "metadata": {
    "created_with": "Wicked Wizard Scene Editor",
    "version": "1.0"
  }
}
```

## Customization

### Adding Custom Components
Create a Python file with Component subclasses:

```python
from engine.component.component import Component

class MyCustomComponent(Component):
    def __init__(self):
        super().__init__()
        self.my_property = "default_value"
        
    def update(self, delta_time):
        # Component logic here
        pass
```

### Adding Custom UI Elements
Create a Python file with Widget subclasses:

```python
from engine.ui.widget import Widget
import pygame

class MyCustomWidget(Widget):
    def __init__(self, rect):
        super().__init__(rect)
        self.my_ui_property = True
        
    def render(self, surface):
        # UI rendering logic here
        pass
```

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure the engine modules are in the Python path
2. **PyQt6 Not Found**: Install PyQt6 using `pip install PyQt6`
3. **Scene Loading Errors**: Check JSON format and component availability

### Debug Mode
Run with debug output:
```bash
python -u editor/main.py
```

## Development

### Contributing
1. Follow the existing code style
2. Add docstrings to new classes and methods
3. Test with various scene configurations
4. Update this README for new features

### Architecture Notes
- The editor uses a simplified scene model that doesn't require the Game instance
- Components are loaded dynamically from their modules
- The property editor uses reflection to create appropriate widgets
- Drag & drop is handled entirely within Qt's framework

## License

Part of the Wicked Wizard Washdown project.
