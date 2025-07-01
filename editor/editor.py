#!/usr/bin/env python3
"""
Wicked Wizard Washdown Scene Editor

A comprehensive scene editor for creating and editing game scenes.
Features:
- Actor hierarchy management with drag & drop
- Component inspection and editing
- UI element support
- Custom component/UI import system
- File operations with undo/redo
- Keyboard shortcuts
- Unsaved changes warning

Author: Scene Editor Generator
"""

import sys
import os
import json
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Any, Type, Union
from dataclasses import dataclass, field

# Add the parent directory to the path to import engine modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QTreeWidget, QTreeWidgetItem, QSplitter, QMenuBar, QMenu, QToolBar,
    QFileDialog, QMessageBox, QInputDialog, QTabWidget, QScrollArea,
    QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QCheckBox, QTextEdit, QGroupBox, QFormLayout, QListWidget, QListWidgetItem,
    QDialog, QDialogButtonBox, QProgressBar, QStatusBar, QFrame
)
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal, QMimeData, QPoint, QSettings, QSize,
    QDir, QFileInfo, QStandardPaths
)
from PyQt6.QtGui import (
    QAction, QKeySequence, QFont, QIcon, QPixmap, QPainter, QColor,
    QDrag, QPalette, QUndoStack, QUndoCommand
)

# Import engine components
from engine.actor.actor import Actor, Transform
from engine.component.component import Component
from engine.ui.widget import Widget


class EditorScene:
    """A simplified scene class for the editor that doesn't require Game instance."""
    
    def __init__(self):
        """Initialize the editor scene."""
        # Actor management
        self.actors: List[Actor] = []
        self.actor_lookup: Dict[str, Actor] = {}  # By name
        self.actors_by_tag: Dict[str, List[Actor]] = {}
        
        # UI element management
        self.ui_elements: List[Widget] = []
        self.ui_lookup: Dict[str, Widget] = {}  # By name
        
        # Scene state
        self.active = True
        self.paused = False
        
        # Lambda scripts for scene lifecycle events
        self.lambda_scripts: Dict[str, List[str]] = {
            'onEnter': [],
            'onExit': [],
            'onPause': [],
            'onResume': [],
            'update': [],
            'lateUpdate': [],
            'preRender': [],
            'postRender': []
        }

    def addActor(self, actor: Actor):
        """Add an actor to the scene."""
        if actor.name in self.actor_lookup:
            # Handle duplicate names by appending a number
            base_name = actor.name
            counter = 1
            while f"{base_name}_{counter}" in self.actor_lookup:
                counter += 1
            actor.name = f"{base_name}_{counter}"

        actor.scene = self  # Set the scene reference in the actor
        
        self.actors.append(actor)
        self.actor_lookup[actor.name] = actor
        
        # Add actor to tags
        for tag in actor.tags:
            if tag not in self.actors_by_tag:
                self.actors_by_tag[tag] = []
            self.actors_by_tag[tag].append(actor)

    def removeActor(self, actor: Actor):
        """Remove an actor from the scene."""
        if actor.name not in self.actor_lookup:
            raise ValueError(f"Actor with name '{actor.name}' does not exist in the scene.")
        
        actor.scene = None  # Clear the scene reference in the actor
        
        self.actors.remove(actor)
        del self.actor_lookup[actor.name]
        
        # Remove actor from tags
        for tag in actor.tags:
            if tag in self.actors_by_tag:
                self.actors_by_tag[tag].remove(actor)
                if not self.actors_by_tag[tag]:
                    del self.actors_by_tag[tag]

    def addUIElement(self, ui_element: Widget):
        """Add a UI element to the scene."""
        if ui_element.name in self.ui_lookup:
            # Handle duplicate names by appending a number
            base_name = ui_element.name
            counter = 1
            while f"{base_name}_{counter}" in self.ui_lookup:
                counter += 1
            ui_element.name = f"{base_name}_{counter}"
        
        self.ui_elements.append(ui_element)
        self.ui_lookup[ui_element.name] = ui_element

    def removeUIElement(self, ui_element: Widget):
        """Remove a UI element from the scene."""
        if ui_element.name not in self.ui_lookup:
            raise ValueError(f"UI element with name '{ui_element.name}' does not exist in the scene.")
        
        self.ui_elements.remove(ui_element)
        del self.ui_lookup[ui_element.name]
        
    def add_lambda_script(self, event_type: str, script: str) -> None:
        """Add a lambda script for a scene lifecycle event."""
        if event_type in self.lambda_scripts:
            self.lambda_scripts[event_type].append(script)
        else:
            print(f"Warning: Unknown scene event type '{event_type}'. Available: {list(self.lambda_scripts.keys())}")
            
    def remove_lambda_script(self, event_type: str, script: str) -> None:
        """Remove a specific lambda script from a scene lifecycle event."""
        if event_type in self.lambda_scripts and script in self.lambda_scripts[event_type]:
            self.lambda_scripts[event_type].remove(script)
            
    def clear_lambda_scripts(self, event_type: str) -> None:
        """Clear all lambda scripts for a scene lifecycle event."""
        if event_type in self.lambda_scripts:
            self.lambda_scripts[event_type].clear()
            
    def execute_lambda_scripts(self, event_type: str, **kwargs) -> None:
        """Execute all lambda scripts for a specific event type."""
        if event_type in self.lambda_scripts:
            for script in self.lambda_scripts[event_type]:
                try:
                    # Create a safe execution environment
                    safe_globals = {
                        '__builtins__': {
                            'print': print,
                            'len': len,
                            'str': str,
                            'int': int,
                            'float': float,
                            'bool': bool,
                            'min': min,
                            'max': max,
                            'abs': abs,
                            'round': round,
                        },
                        'scene': self,
                        'actors': self.actors,
                        'actor_lookup': self.actor_lookup,
                        'actors_by_tag': self.actors_by_tag,
                        'ui_elements': self.ui_elements,
                        'ui_lookup': self.ui_lookup,
                        **kwargs  # Additional context like dt, surface, etc.
                    }
                    
                    # Execute the lambda script
                    exec(script, safe_globals)
                    
                except Exception as e:
                    print(f"Error executing lambda script for {event_type}: {e}")
                    print(f"Script: {script}")

    def serialize(self) -> dict:
        """Serialize the scene to a dictionary."""
        return {
            "actors": [actor.serialize() for actor in self.actors],
            "ui_elements": [self._serializeUIElement(ui) for ui in self.ui_elements],
            "active": self.active,
            "paused": self.paused,
            "lambda_scripts": self.lambda_scripts
        }
    
    def _serializeUIElement(self, ui_element: Widget) -> dict:
        """Serialize a UI element."""
        data = {
            "name": ui_element.name,
            "type": ui_element.__class__.__name__,
            "module": ui_element.__class__.__module__,
            "rect": [ui_element.rect.x, ui_element.rect.y, ui_element.rect.width, ui_element.rect.height],
            "visible": ui_element.visible,
            "enabled": ui_element.enabled,
            "lambda_scripts": ui_element.lambda_scripts
        }
        return data
    
    def deserialize(self, data: dict) -> None:
        """Deserialize the scene from a dictionary."""
        # Clear current actors and UI elements
        self.actors.clear()
        self.actor_lookup.clear() 
        self.actors_by_tag.clear()
        self.ui_elements.clear()
        self.ui_lookup.clear()
        
        # Deserialize actors
        new_actors = []
        for actor_data in data.get("actors", []):
            actor = Actor.createFromSerializedData(actor_data)
            new_actors.append(actor)
        
        # Re-establish parent-child relationships
        Actor.establishRelationshipsFromSerialization(new_actors)
        
        # Add actors to scene
        for actor in new_actors:
            self.addActor(actor)
        
        # Deserialize UI elements
        for ui_data in data.get("ui_elements", []):
            ui_element = self._deserializeUIElement(ui_data)
            if ui_element:
                self.addUIElement(ui_element)
        
        # Restore scene state
        self.active = data.get("active", True)
        self.paused = data.get("paused", False)
    
    def _deserializeUIElement(self, data: dict) -> Optional[Widget]:
        """Deserialize a UI element."""
        try:
            import pygame
            rect_data = data.get("rect", [0, 0, 100, 30])
            rect = pygame.Rect(rect_data[0], rect_data[1], rect_data[2], rect_data[3])
            
            # Create basic widget for now - this could be expanded to support specific types
            ui_element = Widget(rect, data.get("name", "UIElement"))
            ui_element.visible = data.get("visible", True)
            ui_element.enabled = data.get("enabled", True)
            
            return ui_element
        except Exception as e:
            print(f"Failed to deserialize UI element: {e}")
            return None


@dataclass
class ComponentInfo:
    """Information about a component class."""
    name: str
    class_type: Type[Component]
    module_path: str
    description: str = ""
    category: str = "Custom"


@dataclass
class UIElementInfo:
    """Information about a UI element class."""
    name: str
    class_type: Type[Widget]
    module_path: str
    description: str = ""
    category: str = "Custom"


class EditorSettings:
    """Manages editor settings and preferences."""
    
    def __init__(self):
        self.settings = QSettings("WickedWizard", "SceneEditor")
        
    def getValue(self, key: str, default: Any = None) -> Any:
        return self.settings.value(key, default)
        
    def setValue(self, key: str, value: Any):
        self.settings.setValue(key, value)
        
    def getRecentFiles(self) -> List[str]:
        files = self.getValue("recentFiles", [])
        return files if isinstance(files, list) else []
        
    def addRecentFile(self, filepath: str):
        recent = self.getRecentFiles()
        if filepath in recent:
            recent.remove(filepath)
        recent.insert(0, filepath)
        recent = recent[:10]  # Keep only 10 recent files
        self.setValue("recentFiles", recent)


class UndoCommand(QUndoCommand):
    """Base class for undo commands."""
    
    def __init__(self, description: str, editor: 'SceneEditor'):
        super().__init__(description)
        self.editor = editor


class AddActorCommand(UndoCommand):
    """Command for adding an actor."""
    
    def __init__(self, actor: Actor, parent: Optional[Actor], editor: 'SceneEditor'):
        super().__init__(f"Add Actor '{actor.name}'", editor)
        self.actor = actor
        self.parent = parent
        
    def redo(self):
        self.editor.scene.addActor(self.actor)
        if self.parent:
            self.actor.setParent(self.parent)
        self.editor.refreshActorTree()
        
    def undo(self):
        self.editor.scene.removeActor(self.actor)
        self.editor.refreshActorTree()


class DeleteActorCommand(UndoCommand):
    """Command for deleting an actor."""
    
    def __init__(self, actor: Actor, editor: 'SceneEditor'):
        super().__init__(f"Delete Actor '{actor.name}'", editor)
        self.actor = actor
        self.parent = actor.parent
        self.scene_data = actor.serialize()
        
    def redo(self):
        self.editor.scene.removeActor(self.actor)
        self.editor.refreshActorTree()
        
    def undo(self):
        # Recreate actor from serialized data
        new_actor = Actor.createFromSerializedData(self.scene_data)
        self.editor.scene.addActor(new_actor)
        if self.parent and self.parent in self.editor.scene.actors:
            new_actor.setParent(self.parent)
        self.actor = new_actor
        self.editor.refreshActorTree()


class PropertyChangedCommand(UndoCommand):
    """Command for property changes."""
    
    def __init__(self, target: Any, property_name: str, old_value: Any, new_value: Any, editor: 'SceneEditor'):
        super().__init__(f"Change {property_name}", editor)
        self.target = target
        self.property_name = property_name
        self.old_value = old_value
        self.new_value = new_value
        
    def redo(self):
        setattr(self.target, self.property_name, self.new_value)
        self.editor.refreshInspector()
        
    def undo(self):
        setattr(self.target, self.property_name, self.old_value)
        self.editor.refreshInspector()


class ComponentRegistry:
    """Registry for available components."""
    
    def __init__(self):
        self.components: Dict[str, ComponentInfo] = {}
        self.ui_elements: Dict[str, UIElementInfo] = {}
        self._loadBuiltinComponents()
        self._loadBuiltinUIElements()
        
    def _loadBuiltinComponents(self):
        """Load built-in engine components."""
        builtin_path = Path(__file__).parent.parent / "engine" / "component" / "builtin"
        for py_file in builtin_path.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
                
            try:
                module_name = f"engine.component.builtin.{py_file.stem}"
                module = importlib.import_module(module_name)
                
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, Component) and 
                        obj != Component):
                        
                        # Skip complex constraint components that require runtime setup
                        skip_components = {
                            'ConstraintComponent', 'DampedSpringComponent', 
                            'PinJointComponent', 'PivotJointComponent', 
                            'PhysicsComponent'  # Requires pymunk setup
                        }
                        
                        if name in skip_components:
                            print(f"Skipping complex component: {name} (requires runtime setup)")
                            continue
                        
                        info = ComponentInfo(
                            name=name,
                            class_type=obj,
                            module_path=module_name,
                            description=obj.__doc__ or "",
                            category="Built-in"
                        )
                        self.components[name] = info
                        
            except Exception as e:
                print(f"Failed to load component from {py_file}: {e}")
                
    def _loadBuiltinUIElements(self):
        """Load built-in UI elements."""
        builtin_path = Path(__file__).parent.parent / "engine" / "ui" / "builtin"
        
        # Don't add the abstract Widget class - it can't be instantiated
        # self.ui_elements["Widget"] = UIElementInfo(...)
        
        # Try to load from builtin directory
        if builtin_path.exists():
            for py_file in builtin_path.glob("*.py"):
                if py_file.name.startswith("__"):
                    continue
                    
                try:
                    module_name = f"engine.ui.builtin.{py_file.stem}"
                    module = importlib.import_module(module_name)
                    
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, Widget) and 
                            obj != Widget):
                            
                            info = UIElementInfo(
                                name=name,
                                class_type=obj,
                                module_path=module_name,
                                description=obj.__doc__ or "",
                                category="Built-in"
                            )
                            self.ui_elements[name] = info
                            
                except Exception as e:
                    print(f"Failed to load UI element from {py_file}: {e}")
    
    def loadCustomModule(self, filepath: str):
        """Load custom components/UI elements from a Python file."""
        try:
            spec = importlib.util.spec_from_file_location("custom_module", filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for components
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj):
                    if issubclass(obj, Component) and obj != Component:
                        info = ComponentInfo(
                            name=name,
                            class_type=obj,
                            module_path=filepath,
                            description=obj.__doc__ or "",
                            category="Custom"
                        )
                        self.components[name] = info
                        
                    elif issubclass(obj, Widget) and obj != Widget:
                        info = UIElementInfo(
                            name=name,
                            class_type=obj,
                            module_path=filepath,
                            description=obj.__doc__ or "",
                            category="Custom"
                        )
                        self.ui_elements[name] = info
                        
            return True
            
        except Exception as e:
            print(f"Failed to load custom module {filepath}: {e}")
            return False
    
    def getComponentNames(self) -> List[str]:
        return list(self.components.keys())
        
    def getUIElementNames(self) -> List[str]:
        return list(self.ui_elements.keys())
        
    def createComponent(self, name: str) -> Optional[Component]:
        if name in self.components:
            component_class = self.components[name].class_type
            
            try:
                # Handle different component constructor patterns
                if name == "CircleRendererComponent":
                    import pygame
                    return component_class(radius=50, color=pygame.Color(255, 255, 255))
                elif name == "SpriteComponent":
                    return component_class(sprite_name="default", tint_color=None)
                elif name == "TextComponent":
                    return component_class(text="Text", font_name=None, font_size=24)
                elif name == "AudioComponent":
                    return component_class(sound_name=None, volume=1.0, loop=False)
                elif name == "InputComponent":
                    return component_class()
                elif name == "PhysicsComponent":
                    # PhysicsComponent requires pymunk objects, which are complex to create
                    print(f"PhysicsComponent requires complex setup (pymunk body and shapes), skipping for now")
                    return None
                elif name == "ConstraintComponent":
                    # ConstraintComponent requires actors and constraints, complex to create
                    print(f"ConstraintComponent requires complex setup (actors and constraints), skipping for now")
                    return None
                else:
                    # Default constructor (no arguments)
                    return component_class()
                    
            except Exception as e:
                print(f"Failed to create component {name}: {e}")
                print(f"Component class: {component_class}")
                # Try default constructor as fallback
                try:
                    return component_class()
                except Exception as e2:
                    print(f"Fallback constructor also failed: {e2}")
                    return None
        return None
        
    def createUIElement(self, name: str) -> Optional[Widget]:
        if name in self.ui_elements:
            import pygame
            
            # Initialize pygame.font if not already done
            if not pygame.font.get_init():
                pygame.font.init()
            
            default_rect = pygame.Rect(0, 0, 100, 30)
            element_class = self.ui_elements[name].class_type
            
            try:
                # Try different constructor patterns for different UI elements
                if name == "Button":
                    return element_class(default_rect, text="Button", name=f"New{name}")
                elif name == "Label":
                    return element_class(default_rect, text="Label", name=f"New{name}")
                elif name == "Panel":
                    return element_class(default_rect, name=f"New{name}")
                elif name == "TextInput":
                    return element_class(default_rect, name=f"New{name}")
                elif name == "Slider":
                    return element_class(default_rect, name=f"New{name}")
                elif name == "Widget":
                    # Widget is abstract, use Panel instead
                    print("Widget is abstract, creating Panel instead")
                    panel_class = self.ui_elements.get("Panel")
                    if panel_class:
                        return panel_class.class_type(default_rect, name=f"NewPanel")
                    return None
                else:
                    # Default pattern for unknown types
                    return element_class(default_rect, name=f"New{name}")
                    
            except Exception as e:
                print(f"Failed to create UI element {name}: {e}")
                print(f"Element class: {element_class}")
                return None
        return None


class PropertyEditor(QWidget):
    """Widget for editing object properties."""
    
    propertyChanged = pyqtSignal(str, object, object)  # property_name, old_value, new_value
    
    def __init__(self):
        super().__init__()
        self.layout = QFormLayout(self)
        self.target = None
        self.property_widgets = {}
        
    def setTarget(self, target: Any):
        """Set the target object to edit."""
        self.target = target
        self.refreshProperties()
        
    def refreshProperties(self):
        """Refresh the property editor with current target properties."""
        # Clear existing widgets
        for widget in self.property_widgets.values():
            if isinstance(widget, tuple):
                # Handle tuple widgets (like position, scale)
                for w in widget:
                    if hasattr(w, 'deleteLater'):
                        w.deleteLater()
            else:
                if hasattr(widget, 'deleteLater'):
                    widget.deleteLater()
        self.property_widgets.clear()
        
        # Clear layout
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        if not self.target:
            return
            
        # Add properties based on target type
        if isinstance(self.target, Actor):
            self._addActorProperties()
        elif isinstance(self.target, Component):
            self._addComponentProperties()
        elif isinstance(self.target, Transform):
            self._addTransformProperties()
        elif isinstance(self.target, Widget):
            self._addUIElementProperties()
            
    def _addActorProperties(self):
        """Add properties for Actor objects."""
        actor = self.target
        
        # Name
        name_edit = QLineEdit(actor.name)
        name_edit.textChanged.connect(lambda text: self._onPropertyChanged("name", actor.name, text))
        self.layout.addRow("Name:", name_edit)
        self.property_widgets["name"] = name_edit
        
        # Tags
        tags_edit = QLineEdit(", ".join(actor.tags))
        tags_edit.textChanged.connect(lambda text: self._onTagsChanged(text))
        self.layout.addRow("Tags:", tags_edit)
        self.property_widgets["tags"] = tags_edit
        
        # Transform
        transform_label = QLabel("Transform")
        transform_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.layout.addRow(transform_label)
        
        # Position
        pos_x = QDoubleSpinBox()
        pos_x.setRange(-9999, 9999)
        pos_x.setValue(actor.transform.position[0])
        pos_x.valueChanged.connect(lambda v: self._onTransformChanged("position", 0, v))
        
        pos_y = QDoubleSpinBox()
        pos_y.setRange(-9999, 9999)
        pos_y.setValue(actor.transform.position[1])
        pos_y.valueChanged.connect(lambda v: self._onTransformChanged("position", 1, v))
        
        pos_widget = QWidget()
        pos_layout = QHBoxLayout(pos_widget)
        pos_layout.addWidget(QLabel("X:"))
        pos_layout.addWidget(pos_x)
        pos_layout.addWidget(QLabel("Y:"))
        pos_layout.addWidget(pos_y)
        pos_layout.setContentsMargins(0, 0, 0, 0)
        
        self.layout.addRow("Position:", pos_widget)
        self.property_widgets["position"] = (pos_x, pos_y)
        
        # Rotation
        rotation_spin = QDoubleSpinBox()
        rotation_spin.setRange(-360, 360)
        rotation_spin.setValue(actor.transform.rotation)
        rotation_spin.valueChanged.connect(lambda v: self._onTransformChanged("rotation", None, v))
        self.layout.addRow("Rotation:", rotation_spin)
        self.property_widgets["rotation"] = rotation_spin
        
        # Scale
        scale_x = QDoubleSpinBox()
        scale_x.setRange(0.01, 100)
        scale_x.setValue(actor.transform.scale[0])
        scale_x.valueChanged.connect(lambda v: self._onTransformChanged("scale", 0, v))
        
        scale_y = QDoubleSpinBox()
        scale_y.setRange(0.01, 100)
        scale_y.setValue(actor.transform.scale[1])
        scale_y.valueChanged.connect(lambda v: self._onTransformChanged("scale", 1, v))
        
        scale_widget = QWidget()
        scale_layout = QHBoxLayout(scale_widget)
        scale_layout.addWidget(QLabel("X:"))
        scale_layout.addWidget(scale_x)
        scale_layout.addWidget(QLabel("Y:"))
        scale_layout.addWidget(scale_y)
        scale_layout.setContentsMargins(0, 0, 0, 0)
        
        self.layout.addRow("Scale:", scale_widget)
        self.property_widgets["scale"] = (scale_x, scale_y)
        
        # Add custom properties section
        custom_label = QLabel("Custom Properties")
        custom_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.layout.addRow(custom_label)
        
        # Add custom properties from actor's __dict__
        for prop_name, value in actor.__dict__.items():
            if self._shouldSkipProperty(prop_name, value):
                continue
                
            # Skip properties we already handled
            if prop_name in ['name', 'tags', 'transform', 'components', 'scene', 'parent', 'children']:
                continue
                
            self._addGenericProperty(prop_name, value)
        
    def _addComponentProperties(self):
        """Add properties for Component objects."""
        component = self.target
        
        # Enabled
        enabled_check = QCheckBox()
        enabled_check.setChecked(component.enabled)
        enabled_check.toggled.connect(lambda checked: self._onPropertyChanged("enabled", component.enabled, checked))
        self.layout.addRow("Enabled:", enabled_check)
        self.property_widgets["enabled"] = enabled_check
        
        # Add custom properties from component's __dict__
        for prop_name, value in component.__dict__.items():
            if self._shouldSkipProperty(prop_name, value):
                continue
                
            self._addGenericProperty(prop_name, value)
            
    def _addUIElementProperties(self):
        """Add properties for UI Widget objects."""
        widget = self.target
        
        # Name
        name_edit = QLineEdit(widget.name)
        name_edit.textChanged.connect(lambda text: self._onPropertyChanged("name", widget.name, text))
        self.layout.addRow("Name:", name_edit)
        self.property_widgets["name"] = name_edit
        
        # Visible
        visible_check = QCheckBox()
        visible_check.setChecked(widget.visible)
        visible_check.toggled.connect(lambda checked: self._onPropertyChanged("visible", widget.visible, checked))
        self.layout.addRow("Visible:", visible_check)
        self.property_widgets["visible"] = visible_check
        
        # Enabled
        enabled_check = QCheckBox()
        enabled_check.setChecked(widget.enabled)
        enabled_check.toggled.connect(lambda checked: self._onPropertyChanged("enabled", widget.enabled, checked))
        self.layout.addRow("Enabled:", enabled_check)
        self.property_widgets["enabled"] = enabled_check
        
        # Rect properties
        rect_label = QLabel("Rectangle")
        rect_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.layout.addRow(rect_label)
        
        # Position
        pos_x = QSpinBox()
        pos_x.setRange(-9999, 9999)
        pos_x.setValue(widget.rect.x)
        pos_x.valueChanged.connect(lambda v: self._onRectChanged("x", v))
        
        pos_y = QSpinBox()
        pos_y.setRange(-9999, 9999)
        pos_y.setValue(widget.rect.y)
        pos_y.valueChanged.connect(lambda v: self._onRectChanged("y", v))
        
        pos_widget = QWidget()
        pos_layout = QHBoxLayout(pos_widget)
        pos_layout.addWidget(QLabel("X:"))
        pos_layout.addWidget(pos_x)
        pos_layout.addWidget(QLabel("Y:"))
        pos_layout.addWidget(pos_y)
        pos_layout.setContentsMargins(0, 0, 0, 0)
        
        self.layout.addRow("Position:", pos_widget)
        self.property_widgets["rect_pos"] = (pos_x, pos_y)
        
        # Size
        width_spin = QSpinBox()
        width_spin.setRange(1, 9999)
        width_spin.setValue(widget.rect.width)
        width_spin.valueChanged.connect(lambda v: self._onRectChanged("width", v))
        
        height_spin = QSpinBox()
        height_spin.setRange(1, 9999)
        height_spin.setValue(widget.rect.height)
        height_spin.valueChanged.connect(lambda v: self._onRectChanged("height", v))
        
        size_widget = QWidget()
        size_layout = QHBoxLayout(size_widget)
        size_layout.addWidget(QLabel("W:"))
        size_layout.addWidget(width_spin)
        size_layout.addWidget(QLabel("H:"))
        size_layout.addWidget(height_spin)
        size_layout.setContentsMargins(0, 0, 0, 0)
        
        self.layout.addRow("Size:", size_widget)
        self.property_widgets["rect_size"] = (width_spin, height_spin)
        
        # Add other widget properties
        for prop_name, value in widget.__dict__.items():
            if self._shouldSkipProperty(prop_name, value):
                continue
                
            # Skip properties we already handled
            if prop_name in ['name', 'visible', 'enabled', 'rect', 'lambda_scripts']:
                continue
                
            self._addGenericProperty(prop_name, value)
            
        # Add lambda scripts section (read-only info, editing done in Scripts tab)
        if hasattr(widget, 'lambda_scripts') and widget.lambda_scripts:
            scripts_label = QLabel("Lambda Scripts (edit in Scripts tab)")
            scripts_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            self.layout.addRow(scripts_label)
            
            for event_type, script in widget.lambda_scripts.items():
                script_preview = script[:30] + "..." if len(script) > 30 else script
                script_label = QLabel(script_preview)
                script_label.setStyleSheet("color: #666; font-style: italic;")
                self.layout.addRow(f"{event_type}:", script_label)
    
    def _shouldSkipProperty(self, prop_name: str, value: Any) -> bool:
        """Check if a property should be skipped in the inspector."""
        # Skip private/internal properties
        if prop_name.startswith('_'):
            return True
            
        # Skip common non-serializable properties
        skip_properties = {
            "actor", "enabled", "parent", "children", "scene", 
            "rect", "name", "visible", "state", "mouse_inside", 
            "mouse_pressed", "event_handlers", "font", "lambda_scripts"
        }
        if prop_name in skip_properties:
            return True
            
        # Skip non-serializable types
        if callable(value):
            return True
            
        # Skip None values
        if value is None:
            return True
            
        # Skip Qt objects and other complex types
        if hasattr(value, '__module__') and value.__module__:
            module = value.__module__
            if any(skip in module for skip in ['PyQt', 'pygame.font', 'pygame.surface']):
                return True
            
        # Skip complex objects that don't have basic serializable types
        if hasattr(value, '__dict__') and not isinstance(value, (str, int, float, bool, list, tuple, dict)):
            # Allow pygame.Color objects though
            if hasattr(value, '__class__') and value.__class__.__name__ not in ['Color', 'Rect', 'Vector2']:
                return True
            
        # Skip very large collections
        if isinstance(value, (list, tuple, dict)) and len(value) > 20:
            return True
            
        return False
        
    def _addGenericProperty(self, name: str, value: Any):
        """Add a generic property editor based on value type."""
        # Handle pygame.Color objects
        if hasattr(value, '__class__') and value.__class__.__name__ == 'Color':
            self._addColorProperty(name, value)
            return
            
        # Handle tuple colors (r, g, b) or (r, g, b, a)
        if isinstance(value, tuple) and len(value) in [3, 4] and all(isinstance(x, int) and 0 <= x <= 255 for x in value):
            self._addTupleColorProperty(name, value)
            return
            
        # Handle lists that might be colors
        if isinstance(value, list) and len(value) in [3, 4] and all(isinstance(x, int) and 0 <= x <= 255 for x in value):
            self._addTupleColorProperty(name, tuple(value))
            return
            
        # Handle dictionaries with color-like structures
        if isinstance(value, dict) and all(key in ['r', 'g', 'b'] or key in ['r', 'g', 'b', 'a'] for key in value.keys()):
            color_tuple = (value.get('r', 0), value.get('g', 0), value.get('b', 0))
            if 'a' in value:
                color_tuple += (value['a'],)
            self._addTupleColorProperty(name, color_tuple)
            return
            
        if isinstance(value, bool):
            widget = QCheckBox()
            widget.setChecked(value)
            widget.toggled.connect(lambda checked: self._onPropertyChanged(name, value, checked))
            
        elif isinstance(value, int):
            widget = QSpinBox()
            widget.setRange(-999999, 999999)
            widget.setValue(value)
            widget.valueChanged.connect(lambda v: self._onPropertyChanged(name, value, v))
            
        elif isinstance(value, float):
            widget = QDoubleSpinBox()
            widget.setRange(-999999.0, 999999.0)
            widget.setValue(value)
            widget.valueChanged.connect(lambda v: self._onPropertyChanged(name, value, v))
            
        elif isinstance(value, str):
            widget = QLineEdit(value)
            widget.textChanged.connect(lambda text: self._onPropertyChanged(name, value, text))
            
        elif isinstance(value, (list, tuple)) and len(value) <= 10:
            # Handle small lists/tuples as comma-separated values
            widget = QLineEdit(str(value))
            widget.textChanged.connect(lambda text: self._onPropertyChanged(name, value, text))
            
        else:
            # For complex types, use text representation
            widget = QLineEdit(str(value))
            widget.textChanged.connect(lambda text: self._onPropertyChanged(name, value, text))
            
        self.layout.addRow(f"{name}:", widget)
        self.property_widgets[name] = widget
        
    def _addColorProperty(self, name: str, color):
        """Add a color property with R, G, B, A components."""
        color_label = QLabel(f"{name} Color")
        color_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
        self.layout.addRow(color_label)
        
        # R component
        r_spin = QSpinBox()
        r_spin.setRange(0, 255)
        r_spin.setValue(color.r)
        r_spin.valueChanged.connect(lambda v: self._onColorChanged(name, "r", v))
        
        # G component
        g_spin = QSpinBox()
        g_spin.setRange(0, 255)
        g_spin.setValue(color.g)
        g_spin.valueChanged.connect(lambda v: self._onColorChanged(name, "g", v))
        
        # B component
        b_spin = QSpinBox()
        b_spin.setRange(0, 255)
        b_spin.setValue(color.b)
        b_spin.valueChanged.connect(lambda v: self._onColorChanged(name, "b", v))
        
        # A component
        a_spin = QSpinBox()
        a_spin.setRange(0, 255)
        a_spin.setValue(color.a)
        a_spin.valueChanged.connect(lambda v: self._onColorChanged(name, "a", v))
        
        color_widget = QWidget()
        color_layout = QHBoxLayout(color_widget)
        color_layout.addWidget(QLabel("R:"))
        color_layout.addWidget(r_spin)
        color_layout.addWidget(QLabel("G:"))
        color_layout.addWidget(g_spin)
        color_layout.addWidget(QLabel("B:"))
        color_layout.addWidget(b_spin)
        color_layout.addWidget(QLabel("A:"))
        color_layout.addWidget(a_spin)
        color_layout.setContentsMargins(0, 0, 0, 0)
        
        self.layout.addRow("RGBA:", color_widget)
        self.property_widgets[f"{name}_color"] = (r_spin, g_spin, b_spin, a_spin)
        
    def _addTupleColorProperty(self, name: str, color_tuple):
        """Add a tuple color property with R, G, B, (A) components."""
        color_label = QLabel(f"{name} Color")
        color_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
        self.layout.addRow(color_label)
        
        # R component
        r_spin = QSpinBox()
        r_spin.setRange(0, 255)
        r_spin.setValue(color_tuple[0])
        r_spin.valueChanged.connect(lambda v: self._onTupleColorChanged(name, 0, v))
        
        # G component
        g_spin = QSpinBox()
        g_spin.setRange(0, 255)
        g_spin.setValue(color_tuple[1])
        g_spin.valueChanged.connect(lambda v: self._onTupleColorChanged(name, 1, v))
        
        # B component
        b_spin = QSpinBox()
        b_spin.setRange(0, 255)
        b_spin.setValue(color_tuple[2])
        b_spin.valueChanged.connect(lambda v: self._onTupleColorChanged(name, 2, v))
        
        color_widget = QWidget()
        color_layout = QHBoxLayout(color_widget)
        color_layout.addWidget(QLabel("R:"))
        color_layout.addWidget(r_spin)
        color_layout.addWidget(QLabel("G:"))
        color_layout.addWidget(g_spin)
        color_layout.addWidget(QLabel("B:"))
        color_layout.addWidget(b_spin)
        
        widgets = [r_spin, g_spin, b_spin]
        
        # A component if it exists
        if len(color_tuple) == 4:
            a_spin = QSpinBox()
            a_spin.setRange(0, 255)
            a_spin.setValue(color_tuple[3])
            a_spin.valueChanged.connect(lambda v: self._onTupleColorChanged(name, 3, v))
            color_layout.addWidget(QLabel("A:"))
            color_layout.addWidget(a_spin)
            widgets.append(a_spin)
        
        color_layout.setContentsMargins(0, 0, 0, 0)
        
        label = "RGBA:" if len(color_tuple) == 4 else "RGB:"
        self.layout.addRow(label, color_widget)
        self.property_widgets[f"{name}_color"] = tuple(widgets)
        
    def _onPropertyChanged(self, prop_name: str, old_value: Any, new_value: Any):
        """Handle property changes."""
        if self.target and hasattr(self.target, prop_name):
            setattr(self.target, prop_name, new_value)
            self.propertyChanged.emit(prop_name, old_value, new_value)
            
    def _onTagsChanged(self, text: str):
        """Handle tags change."""
        if self.target and hasattr(self.target, "tags"):
            old_tags = self.target.tags.copy()
            new_tags = set(tag.strip() for tag in text.split(",") if tag.strip())
            self.target.tags = new_tags
            self.propertyChanged.emit("tags", old_tags, new_tags)
            
    def _onTransformChanged(self, prop_type: str, index: Optional[int], value: float):
        """Handle transform property changes."""
        if not (self.target and hasattr(self.target, "transform")):
            return
            
        transform = self.target.transform
        
        if prop_type == "position":
            old_pos = transform.position
            new_pos = list(old_pos)
            new_pos[index] = value
            transform.position = tuple(new_pos)
            self.propertyChanged.emit("transform.position", old_pos, transform.position)
            
        elif prop_type == "rotation":
            old_rot = transform.rotation
            transform.rotation = value
            self.propertyChanged.emit("transform.rotation", old_rot, value)
            
        elif prop_type == "scale":
            old_scale = transform.scale
            new_scale = list(old_scale)
            new_scale[index] = value
            transform.scale = tuple(new_scale)
            self.propertyChanged.emit("transform.scale", old_scale, transform.scale)
            
    def _onRectChanged(self, prop_type: str, value: int):
        """Handle rect property changes."""
        if not (self.target and hasattr(self.target, "rect")):
            return
            
        old_rect = self.target.rect.copy()
        
        if prop_type == "x":
            self.target.rect.x = value
        elif prop_type == "y":
            self.target.rect.y = value
        elif prop_type == "width":
            self.target.rect.width = value
        elif prop_type == "height":
            self.target.rect.height = value
            
        self.propertyChanged.emit(f"rect.{prop_type}", old_rect, self.target.rect.copy())
        
    def _onColorChanged(self, prop_name: str, component: str, value: int):
        """Handle pygame Color property changes."""
        if not self.target or not hasattr(self.target, prop_name):
            return
            
        color = getattr(self.target, prop_name)
        old_color = color.copy() if hasattr(color, 'copy') else color
        
        if component == "r":
            color.r = value
        elif component == "g":
            color.g = value
        elif component == "b":
            color.b = value
        elif component == "a":
            color.a = value
            
        self.propertyChanged.emit(f"{prop_name}.{component}", old_color, color)
        
    def _onTupleColorChanged(self, prop_name: str, index: int, value: int):
        """Handle tuple color property changes."""
        if not self.target or not hasattr(self.target, prop_name):
            return
            
        color_tuple = getattr(self.target, prop_name)
        old_color = color_tuple
        
        new_color = list(color_tuple)
        new_color[index] = value
        new_color = tuple(new_color)
        
        setattr(self.target, prop_name, new_color)
        self.propertyChanged.emit(f"{prop_name}[{index}]", old_color, new_color)


class ActorTreeWidget(QTreeWidget):
    """Custom tree widget for actor hierarchy with drag & drop support."""
    
    actorSelected = pyqtSignal(Actor)
    actorParentChanged = pyqtSignal(Actor, Actor)  # child, new_parent
    
    def __init__(self):
        super().__init__()
        self.setHeaderLabel("Scene Actors")
        self.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.itemSelectionChanged.connect(self._onSelectionChanged)
        self.scene = None
        
    def setScene(self, scene: EditorScene):
        """Set the scene to display."""
        self.scene = scene
        self.refreshTree()
        
    def refreshTree(self):
        """Refresh the actor tree."""
        self.clear()
        if not self.scene:
            return
            
        # Create items for root actors (those without parents)
        root_actors = [actor for actor in self.scene.actors if not actor.parent]
        for actor in root_actors:
            self._createActorItem(actor, None)
            
    def _createActorItem(self, actor: Actor, parent_item: Optional[QTreeWidgetItem]) -> QTreeWidgetItem:
        """Create a tree item for an actor."""
        if parent_item:
            item = QTreeWidgetItem(parent_item)
        else:
            item = QTreeWidgetItem(self)
            
        item.setText(0, actor.name)
        item.setData(0, Qt.ItemDataRole.UserRole, actor)
        
        # Add children
        for child in actor.children:
            self._createActorItem(child, item)
            
        item.setExpanded(True)
        return item
        
    def _onSelectionChanged(self):
        """Handle selection changes."""
        items = self.selectedItems()
        if items:
            actor = items[0].data(0, Qt.ItemDataRole.UserRole)
            if actor:
                self.actorSelected.emit(actor)
                
    def dropEvent(self, event):
        """Handle drop events for parenting."""
        item = self.itemAt(event.position().toPoint())
        source_items = self.selectedItems()
        
        if not source_items:
            return
            
        source_item = source_items[0]
        source_actor = source_item.data(0, Qt.ItemDataRole.UserRole)
        
        if item:
            target_actor = item.data(0, Qt.ItemDataRole.UserRole)
            # Prevent parenting to self or descendants
            if target_actor and not self._isDescendant(target_actor, source_actor):
                self.actorParentChanged.emit(source_actor, target_actor)
        else:
            # Dropped on empty space - remove parent
            self.actorParentChanged.emit(source_actor, None)
            
        super().dropEvent(event)
        
    def _isDescendant(self, potential_descendant: Actor, ancestor: Actor) -> bool:
        """Check if an actor is a descendant of another."""
        current = potential_descendant.parent
        while current:
            if current == ancestor:
                return True
            current = current.parent
        return False


class ComponentListWidget(QWidget):
    """Widget for listing and managing actor components."""
    
    componentSelected = pyqtSignal(Component)
    componentAdded = pyqtSignal(str)  # component type name
    
    def __init__(self, registry: ComponentRegistry):
        super().__init__()
        self.registry = registry
        self.actor = None
        self.setupUI()
        
    def setupUI(self):
        layout = QVBoxLayout(self)
        
        # Add component section
        add_group = QGroupBox("Add Component")
        add_layout = QVBoxLayout(add_group)
        
        self.component_combo = QComboBox()
        self.component_combo.addItems(self.registry.getComponentNames())
        add_layout.addWidget(self.component_combo)
        
        add_button = QPushButton("Add Component")
        add_button.clicked.connect(self._onAddComponent)
        add_layout.addWidget(add_button)
        
        layout.addWidget(add_group)
        
        # Component list
        list_group = QGroupBox("Components")
        list_layout = QVBoxLayout(list_group)
        
        self.component_list = QListWidget()
        self.component_list.itemSelectionChanged.connect(self._onSelectionChanged)
        list_layout.addWidget(self.component_list)
        
        remove_button = QPushButton("Remove Component")
        remove_button.clicked.connect(self._onRemoveComponent)
        list_layout.addWidget(remove_button)
        
        layout.addWidget(list_group)
        
    def setActor(self, actor: Actor):
        """Set the actor to display components for."""
        self.actor = actor
        self.refreshComponents()
        
    def refreshComponents(self):
        """Refresh the component list."""
        self.component_list.clear()
        if not self.actor:
            return
            
        for component in self.actor.components:
            item = QListWidgetItem(component.__class__.__name__)
            item.setData(Qt.ItemDataRole.UserRole, component)
            self.component_list.addItem(item)
            
    def _onAddComponent(self):
        """Handle adding a new component."""
        component_name = self.component_combo.currentText()
        if component_name and self.actor:
            self.componentAdded.emit(component_name)
            
    def _onRemoveComponent(self):
        """Handle removing a component."""
        current_item = self.component_list.currentItem()
        if current_item and self.actor:
            component = current_item.data(Qt.ItemDataRole.UserRole)
            self.actor.removeComponent(component)
            self.refreshComponents()
            
    def _onSelectionChanged(self):
        """Handle component selection changes."""
        current_item = self.component_list.currentItem()
        if current_item:
            component = current_item.data(Qt.ItemDataRole.UserRole)
            self.componentSelected.emit(component)


class UIElementManager(QWidget):
    """Widget for managing UI elements in the scene."""
    
    uiElementSelected = pyqtSignal(Widget)
    
    def __init__(self, registry: ComponentRegistry):
        super().__init__()
        self.registry = registry
        self.scene = None
        self.setupUI()
        
    def setupUI(self):
        layout = QVBoxLayout(self)
        
        # Add UI element section
        add_group = QGroupBox("Add UI Element")
        add_layout = QVBoxLayout(add_group)
        
        self.ui_combo = QComboBox()
        self.ui_combo.addItems(self.registry.getUIElementNames())
        add_layout.addWidget(self.ui_combo)
        
        add_button = QPushButton("Add UI Element")
        add_button.clicked.connect(self._onAddUIElement)
        add_layout.addWidget(add_button)
        
        layout.addWidget(add_group)
        
        # UI element list
        list_group = QGroupBox("UI Elements")
        list_layout = QVBoxLayout(list_group)
        
        self.ui_list = QListWidget()
        self.ui_list.itemSelectionChanged.connect(self._onSelectionChanged)
        list_layout.addWidget(self.ui_list)
        
        remove_button = QPushButton("Remove UI Element")
        remove_button.clicked.connect(self._onRemoveUIElement)
        list_layout.addWidget(remove_button)
        
        layout.addWidget(list_group)
        
    def setScene(self, scene: EditorScene):
        """Set the scene to manage UI elements for."""
        self.scene = scene
        self.refreshUIElements()
        
    def refreshUIElements(self):
        """Refresh the UI element list."""
        self.ui_list.clear()
        if not self.scene:
            return
            
        for ui_element in self.scene.ui_elements:
            item = QListWidgetItem(f"{ui_element.name} ({ui_element.__class__.__name__})")
            item.setData(Qt.ItemDataRole.UserRole, ui_element)
            self.ui_list.addItem(item)
            
    def _onAddUIElement(self):
        """Handle adding a new UI element."""
        element_name = self.ui_combo.currentText()
        if element_name and self.scene:
            print(f"Attempting to create UI element: {element_name}")
            element = self.registry.createUIElement(element_name)
            if element:
                print(f"Successfully created {element_name}: {element}")
                self.scene.addUIElement(element)
                self.refreshUIElements()
                print(f"UI element added to scene. Total UI elements: {len(self.scene.ui_elements)}")
            else:
                print(f"Failed to create UI element: {element_name}")
                print(f"Available UI elements: {self.registry.getUIElementNames()}")
                # Try to add basic Widget as fallback
                import pygame
                fallback_widget = Widget(pygame.Rect(0, 0, 100, 30), name=f"Widget_{len(self.scene.ui_elements)}")
                self.scene.addUIElement(fallback_widget)
                self.refreshUIElements()
                print(f"Added fallback Widget instead")
                
    def _onRemoveUIElement(self):
        """Handle removing a UI element."""
        current_item = self.ui_list.currentItem()
        if current_item and self.scene:
            ui_element = current_item.data(Qt.ItemDataRole.UserRole)
            self.scene.removeUIElement(ui_element)
            self.refreshUIElements()
            
    def _onSelectionChanged(self):
        """Handle UI element selection changes."""
        current_item = self.ui_list.currentItem()
        if current_item:
            ui_element = current_item.data(Qt.ItemDataRole.UserRole)
            self.uiElementSelected.emit(ui_element)


class ImportDialog(QDialog):
    """Dialog for importing custom components/UI elements."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Custom Module")
        self.setModal(True)
        self.setupUI()
        
    def setupUI(self):
        layout = QVBoxLayout(self)
        
        # File selection
        file_layout = QHBoxLayout()
        self.file_edit = QLineEdit()
        file_layout.addWidget(QLabel("Python File:"))
        file_layout.addWidget(self.file_edit)
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._onBrowse)
        file_layout.addWidget(browse_button)
        
        layout.addLayout(file_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def _onBrowse(self):
        """Browse for Python file."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select Python Module", "", "Python Files (*.py)"
        )
        if filename:
            self.file_edit.setText(filename)
            
    def getFilePath(self) -> str:
        return self.file_edit.text()


class LambdaScriptManager(QWidget):
    """Widget for managing lambda scripts."""
    
    def __init__(self):
        super().__init__()
        self.scene = None
        self.target_object = None  # Either Scene or Widget
        self.setupUI()
        
    def setupUI(self):
        layout = QVBoxLayout(self)
        
        # Target selection
        target_group = QGroupBox("Script Target")
        target_layout = QVBoxLayout(target_group)
        
        self.target_label = QLabel("No target selected")
        target_layout.addWidget(self.target_label)
        
        layout.addWidget(target_group)
        
        # Event type selection
        event_group = QGroupBox("Event Type")
        event_layout = QVBoxLayout(event_group)
        
        self.event_combo = QComboBox()
        event_layout.addWidget(self.event_combo)
        
        layout.addWidget(event_group)
        
        # Script list
        scripts_group = QGroupBox("Lambda Scripts")
        scripts_layout = QVBoxLayout(scripts_group)
        
        self.scripts_list = QListWidget()
        scripts_layout.addWidget(self.scripts_list)
        
        # Script editor
        self.script_editor = QTextEdit()
        self.script_editor.setPlaceholderText("Enter Python code here...\n\nExamples:\n- print('Hello World!')\n- widget.visible = not widget.visible\n- actors[0].transform.position = (100, 100)")
        self.script_editor.setMaximumHeight(150)
        scripts_layout.addWidget(self.script_editor)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_button = QPushButton("Add Script")
        add_button.clicked.connect(self._onAddScript)
        button_layout.addWidget(add_button)
        
        update_button = QPushButton("Update Script")
        update_button.clicked.connect(self._onUpdateScript)
        button_layout.addWidget(update_button)
        
        remove_button = QPushButton("Remove Script")
        remove_button.clicked.connect(self._onRemoveScript)
        button_layout.addWidget(remove_button)
        
        test_button = QPushButton("Test Script")
        test_button.clicked.connect(self._onTestScript)
        button_layout.addWidget(test_button)
        
        scripts_layout.addLayout(button_layout)
        layout.addWidget(scripts_group)
        
        # Connect selection changes
        self.event_combo.currentTextChanged.connect(self._onEventChanged)
        self.scripts_list.itemSelectionChanged.connect(self._onScriptSelected)
        
    def setScene(self, scene):
        """Set the scene for lambda script management."""
        self.scene = scene
        self.setTarget(scene, "Scene")
        
    def setTarget(self, target_object, target_name: str):
        """Set the target object for lambda script editing."""
        self.target_object = target_object
        self.target_label.setText(f"Target: {target_name}")
        
        # Update event combo based on target type
        self.event_combo.clear()
        if hasattr(target_object, 'lambda_scripts'):
            if isinstance(target_object, Widget):
                # UI Widget events
                self.event_combo.addItems(['click', 'hover', 'focus', 'custom'])
            else:
                # Scene events
                self.event_combo.addItems(list(target_object.lambda_scripts.keys()))
        
        self._refreshScripts()
        
    def _refreshScripts(self):
        """Refresh the scripts list."""
        self.scripts_list.clear()
        
        if not self.target_object or not hasattr(self.target_object, 'lambda_scripts'):
            return
            
        event_type = self.event_combo.currentText()
        if not event_type:
            return
            
        if isinstance(self.target_object, Widget):
            # For widgets, lambda_scripts is a Dict[str, str]
            if event_type in self.target_object.lambda_scripts:
                script = self.target_object.lambda_scripts[event_type]
                item = QListWidgetItem(script[:50] + "..." if len(script) > 50 else script)
                item.setData(Qt.ItemDataRole.UserRole, script)
                self.scripts_list.addItem(item)
        else:
            # For scenes, lambda_scripts is a Dict[str, List[str]]
            if event_type in self.target_object.lambda_scripts:
                for i, script in enumerate(self.target_object.lambda_scripts[event_type]):
                    display_text = f"{i+1}: {script[:40]}..." if len(script) > 40 else f"{i+1}: {script}"
                    item = QListWidgetItem(display_text)
                    item.setData(Qt.ItemDataRole.UserRole, script)
                    self.scripts_list.addItem(item)
                    
    def _onEventChanged(self):
        """Handle event type change."""
        self._refreshScripts()
        self.script_editor.clear()
        
    def _onScriptSelected(self):
        """Handle script selection."""
        current_item = self.scripts_list.currentItem()
        if current_item:
            script = current_item.data(Qt.ItemDataRole.UserRole)
            self.script_editor.setPlainText(script)
            
    def _onAddScript(self):
        """Handle adding a new script."""
        script = self.script_editor.toPlainText().strip()
        if not script:
            return
            
        event_type = self.event_combo.currentText()
        if not event_type:
            return
            
        if isinstance(self.target_object, Widget):
            # For widgets, replace the script
            self.target_object.add_lambda_script(event_type, script)
        else:
            # For scenes, add to the list
            self.target_object.add_lambda_script(event_type, script)
            
        self._refreshScripts()
        self.script_editor.clear()
        
    def _onUpdateScript(self):
        """Handle updating an existing script."""
        current_item = self.scripts_list.currentItem()
        if not current_item:
            return
            
        script = self.script_editor.toPlainText().strip()
        if not script:
            return
            
        event_type = self.event_combo.currentText()
        old_script = current_item.data(Qt.ItemDataRole.UserRole)
        
        if isinstance(self.target_object, Widget):
            # For widgets, just replace
            self.target_object.add_lambda_script(event_type, script)
        else:
            # For scenes, remove old and add new
            self.target_object.remove_lambda_script(event_type, old_script)
            self.target_object.add_lambda_script(event_type, script)
            
        self._refreshScripts()
        
    def _onRemoveScript(self):
        """Handle removing a script."""
        current_item = self.scripts_list.currentItem()
        if not current_item:
            return
            
        event_type = self.event_combo.currentText()
        script = current_item.data(Qt.ItemDataRole.UserRole)
        
        if isinstance(self.target_object, Widget):
            self.target_object.remove_lambda_script(event_type)
        else:
            self.target_object.remove_lambda_script(event_type, script)
            
        self._refreshScripts()
        self.script_editor.clear()
        
    def _onTestScript(self):
        """Handle testing a script."""
        script = self.script_editor.toPlainText().strip()
        if not script:
            return
            
        try:
            if isinstance(self.target_object, Widget):
                self.target_object.execute_lambda_script('custom', None)
            else:
                # Create a test environment for scene scripts
                safe_globals = {
                    '__builtins__': {
                        'print': print,
                        'len': len,
                        'str': str,
                        'int': int,
                        'float': float,
                        'bool': bool,
                        'min': min,
                        'max': max,
                        'abs': abs,
                        'round': round,
                    },
                    'scene': self.target_object,
                    'actors': getattr(self.target_object, 'actors', []),
                    'actor_lookup': getattr(self.target_object, 'actor_lookup', {}),
                    'actors_by_tag': getattr(self.target_object, 'actors_by_tag', {}),
                }
                
                exec(script, safe_globals)
                
            print(f"✓ Script executed successfully")
            
        except Exception as e:
            print(f"✗ Script error: {e}")


class SceneEditor(QMainWindow):
    """Main scene editor window."""
    
    def __init__(self):
        super().__init__()
        self.settings = EditorSettings()
        self.registry = ComponentRegistry()
        self.scene = EditorScene()
        self.current_file = None
        self.is_modified = False
        self.undo_stack = QUndoStack(self)
        
        self.setupUI()
        self.setupMenus()
        self.setupToolbars()
        self.setupStatusBar()
        self.setupConnections()
        self.restoreSettings()
        
        # Set window properties
        self.setWindowTitle("Wicked Wizard Washdown - Scene Editor")
        self.setMinimumSize(1200, 800)
        
    def setupUI(self):
        """Setup the main UI layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Actor hierarchy
        left_panel = QWidget()
        left_panel.setMaximumWidth(300)
        left_layout = QVBoxLayout(left_panel)
        
        # Actor tree
        self.actor_tree = ActorTreeWidget()
        self.actor_tree.setScene(self.scene)
        left_layout.addWidget(self.actor_tree)
        
        # Actor controls
        actor_controls = QWidget()
        actor_controls_layout = QHBoxLayout(actor_controls)
        
        self.add_actor_btn = QPushButton("Add Actor")
        self.add_actor_btn.clicked.connect(self.addActor)
        actor_controls_layout.addWidget(self.add_actor_btn)
        
        self.delete_actor_btn = QPushButton("Delete Actor")
        self.delete_actor_btn.clicked.connect(self.deleteActor)
        actor_controls_layout.addWidget(self.delete_actor_btn)
        
        left_layout.addWidget(actor_controls)
        main_layout.addWidget(left_panel)
        
        # Center panel - Inspector and component management
        center_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Inspector
        inspector_group = QGroupBox("Inspector")
        inspector_layout = QVBoxLayout(inspector_group)
        
        self.inspector_scroll = QScrollArea()
        self.inspector_scroll.setWidgetResizable(True)
        self.property_editor = PropertyEditor()
        self.inspector_scroll.setWidget(self.property_editor)
        inspector_layout.addWidget(self.inspector_scroll)
        
        center_splitter.addWidget(inspector_group)
        
        # Component manager
        self.component_manager = ComponentListWidget(self.registry)
        center_splitter.addWidget(self.component_manager)
        
        main_layout.addWidget(center_splitter)
        
        # Right panel - UI elements and tools
        right_panel = QTabWidget()
        right_panel.setMaximumWidth(300)
        
        # UI Elements tab
        self.ui_manager = UIElementManager(self.registry)
        self.ui_manager.setScene(self.scene)
        right_panel.addTab(self.ui_manager, "UI Elements")
        
        # Lambda Scripts tab
        self.lambda_manager = LambdaScriptManager()
        self.lambda_manager.setScene(self.scene)
        right_panel.addTab(self.lambda_manager, "Scripts")
        
        # Tools tab (placeholder for future tools)
        tools_widget = QWidget()
        right_panel.addTab(tools_widget, "Tools")
        
        main_layout.addWidget(right_panel)
        
    def setupMenus(self):
        """Setup menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # New
        new_action = QAction("&New Scene", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.newScene)
        file_menu.addAction(new_action)
        
        # Open
        open_action = QAction("&Open Scene...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.openScene)
        file_menu.addAction(open_action)
        
        # Recent files
        self.recent_menu = file_menu.addMenu("Recent Files")
        self.updateRecentFilesMenu()
        
        file_menu.addSeparator()
        
        # Save
        save_action = QAction("&Save Scene", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.saveScene)
        file_menu.addAction(save_action)
        
        # Save As
        save_as_action = QAction("Save Scene &As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.saveSceneAs)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # Import
        import_action = QAction("&Import Custom Module...", self)
        import_action.triggered.connect(self.importCustomModule)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        # Undo
        undo_action = self.undo_stack.createUndoAction(self, "&Undo")
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        edit_menu.addAction(undo_action)
        
        # Redo
        redo_action = self.undo_stack.createRedoAction(self, "&Redo")
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        # Copy
        copy_action = QAction("&Copy Actor", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.copyActor)
        edit_menu.addAction(copy_action)
        
        # Paste
        paste_action = QAction("&Paste Actor", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.pasteActor)
        edit_menu.addAction(paste_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        # Refresh
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut(QKeySequence.StandardKey.Refresh)
        refresh_action.triggered.connect(self.refreshAll)
        view_menu.addAction(refresh_action)
        
    def setupToolbars(self):
        """Setup toolbars."""
        toolbar = self.addToolBar("Main")
        
        # Quick actions
        toolbar.addAction("New", self.newScene)
        toolbar.addAction("Open", self.openScene)
        toolbar.addAction("Save", self.saveScene)
        toolbar.addSeparator()
        toolbar.addAction("Add Actor", self.addActor)
        toolbar.addAction("Delete Actor", self.deleteActor)
        
    def setupStatusBar(self):
        """Setup status bar."""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        
    def setupConnections(self):
        """Setup signal connections."""
        # Actor tree connections
        self.actor_tree.actorSelected.connect(self.onActorSelected)
        self.actor_tree.actorParentChanged.connect(self.onActorParentChanged)
        
        # Component manager connections
        self.component_manager.componentSelected.connect(self.onComponentSelected)
        self.component_manager.componentAdded.connect(self.onComponentAdded)
        
        # UI manager connections
        self.ui_manager.uiElementSelected.connect(self.onUIElementSelected)
        
        # Property editor connections
        self.property_editor.propertyChanged.connect(self.onPropertyChanged)
        
        # Undo stack connections
        self.undo_stack.indexChanged.connect(self.onUndoStackChanged)
        
    def restoreSettings(self):
        """Restore editor settings."""
        geometry = self.settings.getValue("geometry")
        if geometry:
            self.restoreGeometry(geometry)
            
        state = self.settings.getValue("windowState")
        if state:
            self.restoreState(state)
            
    def saveSettings(self):
        """Save editor settings."""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        
    def updateRecentFilesMenu(self):
        """Update the recent files menu."""
        self.recent_menu.clear()
        
        recent_files = self.settings.getRecentFiles()
        for filepath in recent_files:
            if os.path.exists(filepath):
                action = QAction(os.path.basename(filepath), self)
                action.setData(filepath)
                action.triggered.connect(lambda checked, path=filepath: self.openSceneFile(path))
                self.recent_menu.addAction(action)
                
    def setModified(self, modified: bool):
        """Set the modified state."""
        self.is_modified = modified
        title = "Wicked Wizard Washdown - Scene Editor"
        if self.current_file:
            title += f" - {os.path.basename(self.current_file)}"
        if modified:
            title += " *"
        self.setWindowTitle(title)
        
    def checkUnsavedChanges(self) -> bool:
        """Check for unsaved changes and prompt user."""
        if not self.is_modified:
            return True
            
        reply = QMessageBox.question(
            self, "Unsaved Changes",
            "You have unsaved changes. Do you want to save before continuing?",
            QMessageBox.StandardButton.Save | 
            QMessageBox.StandardButton.Discard | 
            QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Save:
            return self.saveScene()
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:
            return False
            
    # File operations
    def newScene(self):
        """Create a new scene."""
        if not self.checkUnsavedChanges():
            return
            
        self.scene = EditorScene()
        self.current_file = None
        self.is_modified = False
        self.undo_stack.clear()
        
        # Update all components with new scene
        self.actor_tree.setScene(self.scene)
        self.ui_manager.setScene(self.scene)
        self.lambda_manager.setScene(self.scene)
        
        self.refreshAll()
        self.setModified(False)
        self.status_bar.showMessage("New scene created")
        
    def openScene(self):
        """Open a scene file."""
        if not self.checkUnsavedChanges():
            return
            
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Scene", "", "Scene Files (*.json);;All Files (*)"
        )
        
        if filename:
            self.openSceneFile(filename)
            
    def openSceneFile(self, filename: str):
        """Open a specific scene file."""
        try:
            with open(filename, 'r') as f:
                scene_data = json.load(f)
                
            # Create new scene from data
            self.scene = EditorScene()
            
            # Load actors
            actors_data = scene_data.get("actors", [])
            actors = []
            for actor_data in actors_data:
                actor = Actor.createFromSerializedData(actor_data)
                actors.append(actor)
                self.scene.addActor(actor)
                
            # Establish relationships
            Actor.establishRelationshipsFromSerialization(actors)
            
            self.current_file = filename
            self.is_modified = False
            self.undo_stack.clear()
            
            # Update all components with new scene
            self.actor_tree.setScene(self.scene)
            self.ui_manager.setScene(self.scene)
            self.lambda_manager.setScene(self.scene)
            
            self.settings.addRecentFile(filename)
            self.updateRecentFilesMenu()
            
            self.refreshAll()
            self.setModified(False)
            self.status_bar.showMessage(f"Opened: {os.path.basename(filename)}")
            
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to open scene file:\n{str(e)}"
            )
            
    def saveScene(self) -> bool:
        """Save the current scene."""
        if not self.current_file:
            return self.saveSceneAs()
        else:
            return self.saveSceneFile(self.current_file)
            
    def saveSceneAs(self) -> bool:
        """Save the scene with a new filename."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Scene As", "", "Scene Files (*.json);;All Files (*)"
        )
        
        if filename:
            return self.saveSceneFile(filename)
        return False
        
    def saveSceneFile(self, filename: str) -> bool:
        """Save the scene to a specific file."""
        try:
            scene_data = {
                "actors": [actor.serialize() for actor in self.scene.actors],
                "metadata": {
                    "created_with": "Wicked Wizard Scene Editor",
                    "version": "1.0"
                }
            }
            
            with open(filename, 'w') as f:
                json.dump(scene_data, f, indent=2)
                
            self.current_file = filename
            self.is_modified = False
            
            self.settings.addRecentFile(filename)
            self.updateRecentFilesMenu()
            
            self.setModified(False)
            self.status_bar.showMessage(f"Saved: {os.path.basename(filename)}")
            return True
            
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to save scene file:\n{str(e)}"
            )
            return False
            
    def importCustomModule(self):
        """Import a custom component/UI module."""
        dialog = ImportDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            filepath = dialog.getFilePath()
            if filepath and os.path.exists(filepath):
                if self.registry.loadCustomModule(filepath):
                    # Refresh component lists
                    self.component_manager.component_combo.clear()
                    self.component_manager.component_combo.addItems(self.registry.getComponentNames())
                    
                    self.ui_manager.ui_combo.clear()
                    self.ui_manager.ui_combo.addItems(self.registry.getUIElementNames())
                    
                    self.status_bar.showMessage(f"Imported: {os.path.basename(filepath)}")
                    QMessageBox.information(
                        self, "Success", f"Successfully imported module: {os.path.basename(filepath)}"
                    )
                else:
                    QMessageBox.warning(
                        self, "Warning", f"Failed to import module: {os.path.basename(filepath)}"
                    )
                    
    # Actor operations
    def addActor(self):
        """Add a new actor to the scene."""
        name, ok = QInputDialog.getText(self, "Add Actor", "Actor name:")
        if ok and name:
            actor = Actor(name)
            
            # Get selected parent
            selected_items = self.actor_tree.selectedItems()
            parent = None
            if selected_items:
                parent = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
                
            command = AddActorCommand(actor, parent, self)
            self.undo_stack.push(command)
            self.setModified(True)
            
    def deleteActor(self):
        """Delete the selected actor."""
        selected_items = self.actor_tree.selectedItems()
        if not selected_items:
            return
            
        actor = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        if actor:
            reply = QMessageBox.question(
                self, "Delete Actor",
                f"Are you sure you want to delete '{actor.name}' and all its children?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                command = DeleteActorCommand(actor, self)
                self.undo_stack.push(command)
                self.setModified(True)
                
    def copyActor(self):
        """Copy the selected actor to clipboard."""
        selected_items = self.actor_tree.selectedItems()
        if not selected_items:
            return
            
        actor = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        if actor:
            clipboard = QApplication.clipboard()
            actor_data = json.dumps(actor.serialize())
            clipboard.setText(actor_data)
            self.status_bar.showMessage("Actor copied to clipboard")
            
    def pasteActor(self):
        """Paste actor from clipboard."""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        
        try:
            actor_data = json.loads(text)
            actor = Actor.createFromSerializedData(actor_data)
            
            # Get selected parent
            selected_items = self.actor_tree.selectedItems()
            parent = None
            if selected_items:
                parent = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
                
            command = AddActorCommand(actor, parent, self)
            self.undo_stack.push(command)
            self.setModified(True)
            self.status_bar.showMessage("Actor pasted from clipboard")
            
        except (json.JSONDecodeError, Exception) as e:
            QMessageBox.warning(
                self, "Paste Error", "Invalid actor data in clipboard"
            )
            
    # Event handlers
    def onActorSelected(self, actor: Actor):
        """Handle actor selection."""
        self.property_editor.setTarget(actor)
        self.component_manager.setActor(actor)
        
    def onActorParentChanged(self, child: Actor, new_parent: Optional[Actor]):
        """Handle actor parent change via drag & drop."""
        old_parent = child.parent
        child.setParent(new_parent)
        self.refreshActorTree()
        self.setModified(True)
        
    def onComponentSelected(self, component: Component):
        """Handle component selection."""
        self.property_editor.setTarget(component)
        
    def onUIElementSelected(self, ui_element: Widget):
        """Handle UI element selection."""
        self.property_editor.setTarget(ui_element)
        self.lambda_manager.setTarget(ui_element, f"UI: {ui_element.name}")
        
    def onComponentAdded(self, component_name: str):
        """Handle component addition."""
        if not self.component_manager.actor:
            self.status_bar.showMessage("No actor selected to add component to")
            return
            
        print(f"Attempting to create component: {component_name}")
        component = self.registry.createComponent(component_name)
        
        if component:
            print(f"Successfully created {component_name}: {component}")
            self.component_manager.actor.addComponent(component)
            self.component_manager.refreshComponents()
            self.setModified(True)
            self.status_bar.showMessage(f"Added {component_name} to {self.component_manager.actor.name}")
        else:
            print(f"Failed to create component: {component_name}")
            self.status_bar.showMessage(f"Failed to create component: {component_name}")
            
            # Show available components for debugging
            available = self.registry.getComponentNames()
            print(f"Available components: {available}")
            
    def onPropertyChanged(self, prop_name: str, old_value: Any, new_value: Any):
        """Handle property changes."""
        # Create undo command for property change
        command = PropertyChangedCommand(
            self.property_editor.target, prop_name, old_value, new_value, self
        )
        self.undo_stack.push(command)
        self.setModified(True)
        
    def onUndoStackChanged(self, index: int):
        """Handle undo stack changes."""
        self.refreshAll()
        
    # Refresh methods
    def refreshAll(self):
        """Refresh all UI elements."""
        self.refreshActorTree()
        self.refreshInspector()
        self.refreshComponents()
        self.refreshUIElements()
        
    def refreshActorTree(self):
        """Refresh the actor tree."""
        self.actor_tree.refreshTree()
        
    def refreshInspector(self):
        """Refresh the inspector."""
        self.property_editor.refreshProperties()
        
    def refreshComponents(self):
        """Refresh the component manager."""
        self.component_manager.refreshComponents()
        
    def refreshUIElements(self):
        """Refresh the UI elements manager."""
        self.ui_manager.refreshUIElements()
        
    # Window events
    def closeEvent(self, event):
        """Handle window close event."""
        if self.checkUnsavedChanges():
            self.saveSettings()
            event.accept()
        else:
            event.ignore()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Wicked Wizard Scene Editor")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("WickedWizard")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show editor
    editor = SceneEditor()
    editor.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
