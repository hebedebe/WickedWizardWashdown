# Wicked Wizard Washdown Scene Editor

A comprehensive GUI editor for creating and editing game scenes for the Wicked Wizard Washdown engine.

## Features

### Core Functionality
- **Project Management**: Create, open, save projects with multiple scenes
- **Scene Management**: Create, edit, and manage multiple scenes with tabbed interface
- **Actor Hierarchy**: Add, remove, and organize actors with parent-child relationships
- **Component System**: Add and configure components on actors
- **UI Widget System**: Create and manage UI elements in a separate hierarchy
- **Property Inspector**: Edit properties of selected actors, components, and widgets
- **Scene Validation**: Validate scenes for common issues and errors
- **Auto-save**: Automatic saving with configurable intervals

### User Interface
- **Hierarchy Panel**: Tree view of actors and UI elements with drag-and-drop parenting
- **Scene View**: Visual representation of the scene with zoom, pan, and selection
- **Inspector Panel**: Property editing with specialized widgets for different types
- **Console**: Python console and logging output
- **Tools Panel**: Performance monitoring, asset browser, and settings

### Advanced Features
- **Undo/Redo System**: Full undo/redo support for all operations
- **Copy/Paste**: Copy and paste actors and UI elements
- **Custom Components**: Import and use custom components from Python files
- **Custom Widgets**: Import and use custom UI widgets from Python files
- **Lambda Scripts**: Add inline Python scripts to objects and events
- **Performance Profiler**: Monitor CPU, memory, and other performance metrics
- **Asset Browser**: Browse and manage project assets
- **Scene Tabs**: Work with multiple scenes simultaneously
- **Keyboard Shortcuts**: Standard shortcuts for common operations

## Getting Started

### Prerequisites
- Python 3.8+
- PyQt6
- pygame-ce
- psutil
- All engine dependencies (see main requirements.txt)

### Installation
1. Install dependencies: `pip install -r requirements.txt`
2. Navigate to the editor directory: `cd editor`
3. Run the editor: `python main.py`

### Creating Your First Project
1. The editor starts with a new project automatically
2. Create a new scene: File → New Scene
3. Add actors: Click "Add Actor" in the Hierarchy panel
4. Add components: Select an actor and click "Add Component"
5. Edit properties: Select objects to edit their properties in the Inspector
6. Save your project: File → Save Project

## Interface Overview

### Hierarchy Panel (Left)
- **Actors Tab**: Tree view of all actors in the scene
  - Drag and drop to create parent-child relationships
  - Right-click for context menu (rename, duplicate, delete)
  - Add Actor button to create new actors
  - Add Component button to add components to selected actor

- **UI Tab**: Tree view of all UI widgets in the scene
  - Similar drag-and-drop functionality for UI hierarchy
  - Add Widget button to create new UI widgets

### Scene View (Center Top)
- Visual representation of the scene
- Pan: Middle mouse button or drag
- Zoom: Mouse wheel
- Select: Left click on objects
- Multi-select: Ctrl+click
- Move objects: Drag selected objects
- Delete: Delete key

### Console (Center Bottom)
- **Logs Tab**: All engine and editor log messages with filtering
- **Python Tab**: Interactive Python console with engine access
  - Access to current scene, project, and editor
  - Full Python scripting capabilities

### Inspector (Right)
- **Basic Properties**: Object name, transform, etc.
- **Component Properties**: Properties of attached components grouped by component
- **Lambda Scripts**: Inline Python scripts for events
- Specialized property editors:
  - Vector2: X/Y spinboxes
  - Color: Color picker with RGBA values
  - Rect: X, Y, Width, Height controls
  - Boolean: Checkboxes
  - Numbers: Spinboxes with proper ranges

### Tools Panel (Left Bottom)
- **Performance Tab**: Real-time performance monitoring
- **Validation Tab**: Scene validation with issue reporting
- **Assets Tab**: Project asset browser
- **Settings Tab**: Editor configuration options

## Keyboard Shortcuts

- `Ctrl+N`: New Project
- `Ctrl+O`: Open Project
- `Ctrl+S`: Save Project
- `Ctrl+Shift+S`: Save Project As
- `Ctrl+Shift+N`: New Scene
- `Ctrl+Z`: Undo
- `Ctrl+Y`: Redo
- `Ctrl+C`: Copy
- `Ctrl+V`: Paste
- `Delete`: Delete selected objects
- `F5`: Validate Current Scene

## File Formats

### Project Files (.wwproject)
JSON files containing:
- Project metadata
- Scene references
- Custom component/widget paths
- Editor settings

### Scene Files (.scene)
JSON files containing:
- All actors with components and properties
- UI widget hierarchy
- Lambda scripts
- Physics settings

## Custom Components and Widgets

### Importing Custom Components
1. File → Import Custom Components
2. Select a Python file containing Component subclasses
3. Components become available in the "Add Component" dialog

### Importing Custom Widgets
1. File → Import Custom Widgets
2. Select a Python file containing Widget subclasses
3. Widgets become available in the "Add Widget" dialog

### Example Custom Component
```python
from engine.component.component import Component

class CustomComponent(Component):
    def __init__(self):
        super().__init__()
        self.custom_property = "Hello World"
        self.number_value = 42
        self.enabled_flag = True
    
    def start(self):
        print(f"Custom component started: {self.custom_property}")
```

## Lambda Scripts

Lambda scripts allow you to add inline Python code to objects for events:

### Widget Events
- `onClick`: Executed when widget is clicked
- `onHover`: Executed when mouse hovers over widget
- `onFocus`: Executed when widget gains focus
- `onUpdate`: Executed every frame

### Scene Events
- `onEnter`: When scene becomes active
- `onExit`: When scene becomes inactive
- `update`: Every frame
- `lateUpdate`: After all updates

### Example Lambda Script
```python
# Widget onClick event
print(f"Button {widget.name} was clicked!")
widget.rect.x += 10
```

## Performance Monitoring

The performance monitor tracks:
- CPU usage percentage
- Memory usage in MB and percentage
- Number of threads
- Open file handles
- Application uptime
- Memory usage history

## Scene Validation

The validator checks for:
- Actors without names
- Duplicate actor names
- Missing component properties
- Invalid UI widget dimensions
- Syntax errors in lambda scripts
- Common configuration issues

## Troubleshooting

### Common Issues

**Editor won't start**
- Check that all dependencies are installed
- Verify Python version (3.8+ required)
- Check console output for specific error messages

**Can't import custom components**
- Ensure the Python file is valid
- Check that classes inherit from Component or Widget base classes
- Verify file permissions

**Scene won't load**
- Check that the scene file is valid JSON
- Verify all referenced components are available
- Look at console output for specific errors

**Performance issues**
- Use the performance monitor to identify bottlenecks
- Reduce scene complexity
- Check for memory leaks in custom scripts

### Debug Mode
Run the editor with debug logging:
```bash
python main.py --debug
```

### Log Files
Editor logs are saved to `editor_logs/editor.log` for debugging.

## Architecture

The editor is built with a modular architecture:

- **main.py**: Entry point and application setup
- **editor_main_window.py**: Main window and menu handling
- **editor_project.py**: Project management and serialization
- **editor_scene.py**: Scene editing and serialization
- **editor_hierarchy.py**: Actor/UI hierarchy management
- **editor_inspector.py**: Property editing interface
- **editor_scene_view.py**: Visual scene editing
- **editor_console.py**: Logging and Python console
- **editor_tools.py**: Development tools and utilities
- **editor_utils.py**: Shared utilities and helpers
- **editor_dummy.py**: Engine compatibility layer

## Contributing

To add new features to the editor:

1. Follow the existing code structure and patterns
2. Add appropriate error handling and logging
3. Update the UI to accommodate new features
4. Test thoroughly with various scene configurations
5. Update documentation as needed

## License

This editor is part of the Wicked Wizard Washdown project.
