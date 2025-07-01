"""
Scene serialization and deserialization for the editor.
"""

import json
import sys
import pygame
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Add engine to path and patch it
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    import editor_dummy  # This patches the engine
except ImportError:
    # If running from outside editor directory, try absolute import
    sys.path.insert(0, str(Path(__file__).parent))
    import editor_dummy

from engine.scene.scene import Scene
from engine.actor.actor import Actor, Transform
from engine.ui.widget import Widget
from editor_utils import serialize_value, deserialize_value, get_engine_components, get_engine_widgets

logger = logging.getLogger(__name__)

class EditorScene:
    """Extended scene class for editor use."""
    
    def __init__(self, name: str = "New Scene"):
        self.name = name
        self.scene = Scene()
        self.file_path: Optional[Path] = None
        self.is_dirty = False
        self.metadata = {
            "version": "1.0",
            "created_with": "Scene Editor",
            "description": ""
        }
        
    def mark_dirty(self):
        """Mark the scene as having unsaved changes."""
        self.is_dirty = True
        
    def mark_clean(self):
        """Mark the scene as saved."""
        self.is_dirty = False
        
    def add_actor(self, actor: Actor):
        """Add an actor to the scene."""
        self.scene.addActor(actor)
        self.mark_dirty()
        
    def remove_actor(self, actor: Actor):
        """Remove an actor from the scene."""
        self.scene.removeActor(actor)
        self.mark_dirty()
        
    def serialize(self) -> Dict[str, Any]:
        """Serialize the scene to a dictionary."""
        try:
            # Serialize actors
            actors_data = []
            for actor in self.scene.actors:
                actor_data = self._serialize_actor(actor)
                actors_data.append(actor_data)
                
            # Serialize UI widgets
            ui_data = []
            if hasattr(self.scene, 'uiManager') and self.scene.uiManager:
                for widget in self.scene.uiManager.root_widgets:
                    widget_data = self._serialize_widget(widget)
                    ui_data.append(widget_data)
                    
            # Serialize lambda scripts
            lambda_scripts = {}
            if hasattr(self.scene, 'lambda_scripts'):
                lambda_scripts = dict(self.scene.lambda_scripts)
                
            return {
                "metadata": self.metadata,
                "name": self.name,
                "actors": actors_data,
                "ui": ui_data,
                "lambda_scripts": lambda_scripts,
                "physics": {
                    "gravity": list(self.scene.physicsSpace.gravity) if hasattr(self.scene, 'physicsSpace') else [0, 900]
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to serialize scene: {e}")
            raise
            
    def _serialize_actor(self, actor: Actor) -> Dict[str, Any]:
        """Serialize a single actor."""
        # Serialize transform
        transform_data = {
            "position": list(actor.transform.position),
            "rotation": actor.transform.rotation,
            "scale": list(actor.transform.scale)
        }
        
        # Serialize components
        components_data = []
        for component in actor.components:
            comp_data = {
                "type": component.__class__.__name__,
                "module": component.__class__.__module__,
                "enabled": component.enabled,
                "properties": {}
            }
            
            # Serialize component properties
            for attr_name in dir(component):
                if (not attr_name.startswith('_') and 
                    attr_name not in ['actor', 'start', 'update', 'lateUpdate', 'render'] and
                    not callable(getattr(component, attr_name))):
                    try:
                        value = getattr(component, attr_name)
                        comp_data["properties"][attr_name] = serialize_value(value)
                    except Exception as e:
                        logger.warning(f"Failed to serialize component property {attr_name}: {e}")
                        
            components_data.append(comp_data)
            
        # Serialize children
        children_data = []
        for child in actor.children:
            children_data.append(self._serialize_actor(child))
            
        return {
            "name": actor.name,
            "tags": list(actor.tags),
            "transform": transform_data,
            "components": components_data,
            "children": children_data
        }
        
    def _serialize_widget(self, widget: Widget) -> Dict[str, Any]:
        """Serialize a single UI widget."""
        widget_data = {
            "type": widget.__class__.__name__,
            "module": widget.__class__.__module__,
            "name": widget.name,
            "rect": [widget.rect.x, widget.rect.y, widget.rect.width, widget.rect.height],
            "visible": widget.visible,
            "enabled": widget.enabled,
            "properties": {},
            "lambda_scripts": dict(widget.lambda_scripts) if hasattr(widget, 'lambda_scripts') else {},
            "children": []
        }
        
        # Serialize widget properties
        for attr_name in dir(widget):
            if (not attr_name.startswith('_') and 
                attr_name not in ['parent', 'children', 'rect', 'name', 'visible', 'enabled', 'lambda_scripts'] and
                not callable(getattr(widget, attr_name))):
                try:
                    value = getattr(widget, attr_name)
                    widget_data["properties"][attr_name] = serialize_value(value)
                except Exception as e:
                    logger.warning(f"Failed to serialize widget property {attr_name}: {e}")
                    
        # Serialize children
        for child in widget.children:
            widget_data["children"].append(self._serialize_widget(child))
            
        return widget_data
        
    def deserialize(self, data: Dict[str, Any]):
        """Deserialize the scene from a dictionary."""
        try:
            # Clear existing scene
            self.scene.actors.clear()
            self.scene.actor_lookup.clear()
            self.scene.actors_by_tag.clear()
            
            if hasattr(self.scene, 'uiManager') and self.scene.uiManager:
                self.scene.uiManager.widgets.clear()
                self.scene.uiManager.root_widgets.clear()
                
            # Load metadata
            self.metadata = data.get("metadata", {})
            self.name = data.get("name", "Untitled Scene")
            
            # Load actors
            actors_data = data.get("actors", [])
            for actor_data in actors_data:
                actor = self._deserialize_actor(actor_data)
                if actor:
                    self.scene.addActor(actor)
                    
            # Load UI widgets
            ui_data = data.get("ui", [])
            available_widgets = get_engine_widgets()
            for widget_data in ui_data:
                widget = self._deserialize_widget(widget_data, available_widgets)
                if widget and hasattr(self.scene, 'uiManager') and self.scene.uiManager:
                    self.scene.uiManager.add_widget(widget)
                    
            # Load lambda scripts
            lambda_scripts = data.get("lambda_scripts", {})
            if hasattr(self.scene, 'lambda_scripts'):
                self.scene.lambda_scripts = dict(lambda_scripts)
                
            # Load physics settings
            physics_data = data.get("physics", {})
            if hasattr(self.scene, 'physicsSpace') and "gravity" in physics_data:
                self.scene.physicsSpace.gravity = tuple(physics_data["gravity"])
                
            self.mark_clean()
            
        except Exception as e:
            logger.error(f"Failed to deserialize scene: {e}")
            raise
            
    def _deserialize_actor(self, data: Dict[str, Any]) -> Optional[Actor]:
        """Deserialize a single actor."""
        try:
            actor = Actor(data.get("name", "Actor"))
            
            # Set tags
            for tag in data.get("tags", []):
                actor.addTag(tag)
                
            # Set transform
            transform_data = data.get("transform", {})
            actor.transform.position = tuple(transform_data.get("position", [0, 0]))
            actor.transform.rotation = transform_data.get("rotation", 0)
            actor.transform.scale = tuple(transform_data.get("scale", [1, 1]))
            
            # Load components
            available_components = get_engine_components()
            components_data = data.get("components", [])
            for comp_data in components_data:
                comp_type = comp_data.get("type")
                if comp_type in available_components:
                    try:
                        component = available_components[comp_type]()
                        component.enabled = comp_data.get("enabled", True)
                        
                        # Set component properties
                        properties = comp_data.get("properties", {})
                        for prop_name, prop_value in properties.items():
                            if hasattr(component, prop_name):
                                try:
                                    setattr(component, prop_name, deserialize_value(prop_value))
                                except Exception as e:
                                    logger.warning(f"Failed to set component property {prop_name}: {e}")
                                    
                        actor.addComponent(component)
                        
                    except Exception as e:
                        logger.error(f"Failed to create component {comp_type}: {e}")
                else:
                    logger.warning(f"Unknown component type: {comp_type}")
                    
            # Load children (recursive)
            children_data = data.get("children", [])
            for child_data in children_data:
                child = self._deserialize_actor(child_data)
                if child:
                    actor.addChild(child)
                    
            return actor
            
        except Exception as e:
            logger.error(f"Failed to deserialize actor: {e}")
            return None
            
    def _deserialize_widget(self, data: Dict[str, Any], available_widgets: Dict[str, Any]) -> Optional[Widget]:
        """Deserialize a single UI widget."""
        try:
            widget_type = data.get("type")
            if widget_type not in available_widgets:
                logger.warning(f"Unknown widget type: {widget_type}")
                return None
                
            # Create widget with rect
            rect_data = data.get("rect", [0, 0, 100, 100])
            rect = pygame.Rect(*rect_data)
            
            widget = available_widgets[widget_type](rect, data.get("name", ""))
            widget.visible = data.get("visible", True)
            widget.enabled = data.get("enabled", True)
            
            # Set widget properties
            properties = data.get("properties", {})
            for prop_name, prop_value in properties.items():
                if hasattr(widget, prop_name):
                    try:
                        setattr(widget, prop_name, deserialize_value(prop_value))
                    except Exception as e:
                        logger.warning(f"Failed to set widget property {prop_name}: {e}")
                        
            # Set lambda scripts
            lambda_scripts = data.get("lambda_scripts", {})
            if hasattr(widget, 'lambda_scripts'):
                widget.lambda_scripts = dict(lambda_scripts)
                
            # Load children (recursive)
            children_data = data.get("children", [])
            for child_data in children_data:
                child = self._deserialize_widget(child_data, available_widgets)
                if child:
                    widget.add_child(child)
                    
            return widget
            
        except Exception as e:
            logger.error(f"Failed to deserialize widget: {e}")
            return None
            
    def save_to_file(self, file_path: Path):
        """Save the scene to a file."""
        try:
            data = self.serialize()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.file_path = file_path
            self.mark_clean()
            logger.info(f"Scene saved to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save scene to {file_path}: {e}")
            raise
            
    def load_from_file(self, file_path: Path):
        """Load the scene from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.deserialize(data)
            self.file_path = file_path
            self.mark_clean()
            logger.info(f"Scene loaded from {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load scene from {file_path}: {e}")
            raise
