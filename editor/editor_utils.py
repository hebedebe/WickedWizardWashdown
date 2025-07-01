"""
Editor utilities and helper functions.
"""

import logging
import sys
import os
import json
import copy
import inspect
import importlib.util
import pygame
from pathlib import Path
from typing import Any, Dict, List, Type, Union, Optional

from PyQt6.QtCore import QObject, pyqtSignal, QStandardPaths
from PyQt6.QtWidgets import QMessageBox

def setup_logging():
    """Set up logging to both console and file."""
    # Set up logging to both console and file
    log_dir = os.path.join(os.path.dirname(__file__), '..')
    log_file = os.path.abspath(os.path.join(log_dir, 'editor.log'))

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    # File handler
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Avoid duplicate handlers
    if not logger.hasHandlers():
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    else:
        logger.handlers.clear()
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    logging.info('Scene Editor logging initialized')

def show_error(title: str, message: str, parent=None):
    """Show an error message box."""
    QMessageBox.critical(parent, title, message)

def show_warning(title: str, message: str, parent=None):
    """Show a warning message box."""
    QMessageBox.warning(parent, title, message)

def show_info(title: str, message: str, parent=None):
    """Show an info message box."""
    QMessageBox.information(parent, title, message)

def ask_yes_no(title: str, question: str, parent=None) -> bool:
    """Ask a yes/no question."""
    reply = QMessageBox.question(parent, title, question, 
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    return reply == QMessageBox.StandardButton.Yes

class UndoRedoManager(QObject):
    """Manages undo/redo operations for the editor."""
    
    changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.undo_stack = []
        self.redo_stack = []
        self.max_history = 100
        
    def execute_command(self, command):
        """Execute a command and add it to the undo stack."""
        command.execute()
        self.undo_stack.append(command)
        self.redo_stack.clear()
        
        # Limit history size
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
            
        self.changed.emit()
        
    def undo(self):
        """Undo the last command."""
        if self.undo_stack:
            command = self.undo_stack.pop()
            command.undo()
            self.redo_stack.append(command)
            self.changed.emit()
            
    def redo(self):
        """Redo the last undone command."""
        if self.redo_stack:
            command = self.redo_stack.pop()
            command.execute()
            self.undo_stack.append(command)
            self.changed.emit()
            
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self.undo_stack) > 0
        
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self.redo_stack) > 0
        
    def clear(self):
        """Clear all undo/redo history."""
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.changed.emit()

class EditorCommand:
    """Base class for editor commands."""
    
    def __init__(self, description: str):
        self.description = description
        
    def execute(self):
        """Execute the command."""
        raise NotImplementedError
        
    def undo(self):
        """Undo the command."""
        raise NotImplementedError

def get_engine_components() -> Dict[str, Type]:
    """Get all available engine components."""
    components = {}
    
    try:
        # Import the engine
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from engine.component.component import Component
        
        # Get all builtin components
        builtin_dir = Path(__file__).parent.parent / "engine" / "component" / "builtin"
        for py_file in builtin_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
                
            module_name = py_file.stem
            try:
                # Import using exec to avoid import issues
                module_code = py_file.read_text(encoding='utf-8')
                local_vars = {}
                global_vars = {
                    '__name__': module_name,
                    '__file__': str(py_file),
                    'pygame': __import__('pygame'),
                    'Component': Component,
                }
                
                # Add common imports to globals
                import engine.component.component
                import typing
                global_vars['engine'] = __import__('engine')
                global_vars.update({
                    'Optional': typing.Optional,
                    'List': typing.List,
                    'Dict': typing.Dict,
                    'Any': typing.Any,
                    'Union': typing.Union,
                    'Tuple': typing.Tuple,
                    'Set': typing.Set,
                    'Callable': typing.Callable,
                    'typing': typing
                })
                
                exec(module_code, global_vars, local_vars)
                
                # Find Component classes in the executed module
                for name, obj in local_vars.items():
                    if (inspect.isclass(obj) and 
                        issubclass(obj, Component) and 
                        obj != Component):
                        components[name] = obj
                        
            except Exception as e:
                logging.warning(f"Failed to load component from {py_file}: {e}")
                
    except Exception as e:
        logging.error(f"Failed to load engine components: {e}")
        
    return components

def get_engine_widgets() -> Dict[str, Type]:
    """Get all available engine UI widgets."""
    widgets = {}
    
    try:
        # Import the engine
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from engine.ui.widget import Widget
        from engine.ui import builtin
        
        # Get all builtin widgets
        builtin_dir = Path(__file__).parent.parent / "engine" / "ui" / "builtin"
        for py_file in builtin_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
                
            module_name = py_file.stem
            try:
                # Import using exec to avoid import issues
                module_code = py_file.read_text(encoding='utf-8')
                local_vars = {}
                global_vars = {
                    '__name__': module_name,
                    '__file__': str(py_file),
                    'pygame': __import__('pygame'),
                    'Widget': Widget,
                }
                
                # Add common imports to globals
                import engine.ui.widget
                import typing
                global_vars['engine'] = __import__('engine')
                global_vars.update({
                    'Optional': typing.Optional,
                    'List': typing.List,
                    'Dict': typing.Dict,
                    'Any': typing.Any,
                    'Union': typing.Union,
                    'Tuple': typing.Tuple,
                    'Set': typing.Set,
                    'Callable': typing.Callable,
                    'typing': typing
                })
                
                exec(module_code, global_vars, local_vars)
                
                # Find Widget classes in the executed module
                for name, obj in local_vars.items():
                    if (inspect.isclass(obj) and 
                        issubclass(obj, Widget) and 
                        obj != Widget):
                        widgets[name] = obj
                        
            except Exception as e:
                logging.warning(f"Failed to load widget from {py_file}: {e}")
                
    except Exception as e:
        logging.error(f"Failed to load engine widgets: {e}")
        
    return widgets

def load_custom_components(file_path: str) -> Dict[str, Type]:
    """Load custom components from a Python file."""
    components = {}
    
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from engine.component.component import Component
        
        spec = importlib.util.spec_from_file_location("custom_components", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find Component classes in the module
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, Component) and 
                obj != Component):
                components[name] = obj
                
    except Exception as e:
        logging.error(f"Failed to load custom components from {file_path}: {e}")
        
    return components

def load_custom_widgets(file_path: str) -> Dict[str, Type]:
    """Load custom widgets from a Python file."""
    widgets = {}
    
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from engine.ui.widget import Widget
        
        spec = importlib.util.spec_from_file_location("custom_widgets", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find Widget classes in the module
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, Widget) and 
                obj != Widget):
                widgets[name] = obj
                
    except Exception as e:
        logging.error(f"Failed to load custom widgets from {file_path}: {e}")
        
    return widgets

def serialize_object(obj) -> dict:
    """Serialize an object to a dictionary."""
    if hasattr(obj, 'serialize'):
        return obj.serialize()
    elif hasattr(obj, '__dict__'):
        return {k: serialize_value(v) for k, v in obj.__dict__.items() 
                if not k.startswith('_') and not callable(v)}
    else:
        return str(obj)

def serialize_value(value) -> Any:
    """Serialize a value to a JSON-compatible format."""
    import pygame
    
    if value is None:
        return None
    elif isinstance(value, (str, int, float, bool)):
        return value
    elif isinstance(value, (list, tuple)):
        return [serialize_value(v) for v in value]
    elif isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    elif isinstance(value, pygame.Vector2):
        return {"__type__": "Vector2", "x": value.x, "y": value.y}
    elif isinstance(value, pygame.Color):
        return {"__type__": "Color", "r": value.r, "g": value.g, "b": value.b, "a": value.a}
    elif isinstance(value, pygame.Rect):
        return {"__type__": "Rect", "x": value.x, "y": value.y, "width": value.width, "height": value.height}
    elif hasattr(value, 'serialize'):
        return value.serialize()
    else:
        return str(value)

def deserialize_value(value) -> Any:
    """Deserialize a value from a JSON-compatible format."""
    import pygame
    
    if isinstance(value, dict) and "__type__" in value:
        type_name = value["__type__"]
        if type_name == "Vector2":
            return pygame.Vector2(value["x"], value["y"])
        elif type_name == "Color":
            return pygame.Color(value["r"], value["g"], value["b"], value["a"])
        elif type_name == "Rect":
            return pygame.Rect(value["x"], value["y"], value["width"], value["height"])
    elif isinstance(value, list):
        return [deserialize_value(v) for v in value]
    elif isinstance(value, dict):
        return {k: deserialize_value(v) for k, v in value.items()}
    
    return value

def get_property_info(obj, prop_name: str) -> Dict[str, Any]:
    """Get information about an object property for the inspector."""
    if not hasattr(obj, prop_name):
        return {}
        
    value = getattr(obj, prop_name)
    prop_type = type(value).__name__
    
    info = {
        "name": prop_name,
        "type": prop_type,
        "value": value,
        "editable": True
    }
    
    # Add type-specific information
    if isinstance(value, bool):
        info["widget"] = "checkbox"
    elif isinstance(value, (int, float)):
        info["widget"] = "spinbox"
        info["min"] = -999999
        info["max"] = 999999
    elif isinstance(value, str):
        info["widget"] = "lineedit"
    elif hasattr(value, '__class__') and hasattr(value.__class__, '__module__'):
        if 'pygame' in value.__class__.__module__:
            if isinstance(value, pygame.Vector2):
                info["widget"] = "vector2"
            elif isinstance(value, pygame.Color):
                info["widget"] = "color"
            elif isinstance(value, pygame.Rect):
                info["widget"] = "rect"
    
    return info

def show_error_with_logging(title: str, message: str, parent=None):
    """Show an error popup and log the error message."""
    logger = logging.getLogger('editor_errors')
    logger.error(f"{title}: {message}")
    
    try:
        from PyQt6.QtWidgets import QMessageBox, QApplication
        if not QApplication.instance():
            app = QApplication([])
        QMessageBox.critical(parent, title, message)
    except Exception as e:
        logger.error(f"Failed to show error popup: {e}")
        print(f"ERROR - {title}: {message}", file=sys.stderr)

def show_warning_with_logging(title: str, message: str, parent=None):
    """Show a warning popup and log the warning message."""
    logger = logging.getLogger('editor_warnings')
    logger.warning(f"{title}: {message}")
    
    try:
        from PyQt6.QtWidgets import QMessageBox, QApplication
        if not QApplication.instance():
            app = QApplication([])
        QMessageBox.warning(parent, title, message)
    except Exception as e:
        logger.error(f"Failed to show warning popup: {e}")
        print(f"WARNING - {title}: {message}", file=sys.stderr)
