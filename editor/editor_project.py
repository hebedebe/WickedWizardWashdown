"""
Project management for the scene editor.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set
import logging

# Add engine to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from editor_scene import EditorScene

logger = logging.getLogger(__name__)

class EditorProject:
    """Manages multiple scenes and project settings."""
    
    def __init__(self, name: str = "New Project"):
        self.name = name
        self.scenes: Dict[str, EditorScene] = {}
        self.active_scene: Optional[str] = None
        self.project_dir: Optional[Path] = None
        self.settings = {
            "version": "1.0",
            "last_opened_scenes": [],
            "custom_component_paths": [],
            "custom_widget_paths": [],
            "editor_settings": {
                "auto_save": True,
                "auto_save_interval": 300,  # seconds
                "backup_count": 5
            }
        }
        self.is_dirty = False
        
    def mark_dirty(self):
        """Mark the project as having unsaved changes."""
        self.is_dirty = True
        
    def mark_clean(self):
        """Mark the project as saved."""
        self.is_dirty = False
        
    def add_scene(self, scene: EditorScene, scene_id: Optional[str] = None) -> str:
        """Add a scene to the project."""
        if scene_id is None:
            scene_id = scene.name
            
        # Ensure unique scene ID
        counter = 1
        original_id = scene_id
        while scene_id in self.scenes:
            scene_id = f"{original_id}_{counter}"
            counter += 1
            
        self.scenes[scene_id] = scene
        self.mark_dirty()
        
        if self.active_scene is None:
            self.active_scene = scene_id
            
        return scene_id
        
    def remove_scene(self, scene_id: str):
        """Remove a scene from the project."""
        if scene_id in self.scenes:
            del self.scenes[scene_id]
            self.mark_dirty()
            
            if self.active_scene == scene_id:
                self.active_scene = next(iter(self.scenes.keys())) if self.scenes else None
                
    def get_scene(self, scene_id: str) -> Optional[EditorScene]:
        """Get a scene by ID."""
        return self.scenes.get(scene_id)
        
    def get_active_scene(self) -> Optional[EditorScene]:
        """Get the currently active scene."""
        if self.active_scene:
            return self.scenes.get(self.active_scene)
        return None
        
    def set_active_scene(self, scene_id: str):
        """Set the active scene."""
        if scene_id in self.scenes:
            self.active_scene = scene_id
            
    def get_dirty_scenes(self) -> List[str]:
        """Get a list of scene IDs that have unsaved changes."""
        dirty_scenes = []
        for scene_id, scene in self.scenes.items():
            if scene.is_dirty:
                dirty_scenes.append(scene_id)
        return dirty_scenes
        
    def has_unsaved_changes(self) -> bool:
        """Check if there are any unsaved changes in the project or scenes."""
        if self.is_dirty:
            return True
        return len(self.get_dirty_scenes()) > 0
        
    def add_custom_component_path(self, path: str):
        """Add a path to custom components."""
        if path not in self.settings["custom_component_paths"]:
            self.settings["custom_component_paths"].append(path)
            self.mark_dirty()
            
    def add_custom_widget_path(self, path: str):
        """Add a path to custom widgets."""
        if path not in self.settings["custom_widget_paths"]:
            self.settings["custom_widget_paths"].append(path)
            self.mark_dirty()
            
    def serialize(self) -> Dict:
        """Serialize the project to a dictionary."""
        scenes_data = {}
        for scene_id, scene in self.scenes.items():
            scenes_data[scene_id] = {
                "name": scene.name,
                "file_path": str(scene.file_path) if scene.file_path else None,
                "is_dirty": scene.is_dirty
            }
            
        return {
            "name": self.name,
            "active_scene": self.active_scene,
            "scenes": scenes_data,
            "settings": self.settings
        }
        
    def deserialize(self, data: Dict):
        """Deserialize the project from a dictionary."""
        self.name = data.get("name", "Untitled Project")
        self.active_scene = data.get("active_scene")
        self.settings = data.get("settings", {})
        
        # Merge with default settings
        default_settings = {
            "version": "1.0",
            "last_opened_scenes": [],
            "custom_component_paths": [],
            "custom_widget_paths": [],
            "editor_settings": {
                "auto_save": True,
                "auto_save_interval": 300,
                "backup_count": 5
            }
        }
        
        for key, value in default_settings.items():
            if key not in self.settings:
                self.settings[key] = value
            elif isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if sub_key not in self.settings[key]:
                        self.settings[key][sub_key] = sub_value
                        
        # Note: Scene files are loaded separately
        scenes_data = data.get("scenes", {})
        for scene_id, scene_info in scenes_data.items():
            # Create placeholder scenes that will be loaded when opened
            scene = EditorScene(scene_info.get("name", scene_id))
            if scene_info.get("file_path"):
                scene.file_path = Path(scene_info["file_path"])
            scene.is_dirty = scene_info.get("is_dirty", False)
            self.scenes[scene_id] = scene
            
    def save_to_file(self, file_path: Path):
        """Save the project to a file."""
        try:
            # Save all dirty scenes first
            for scene_id, scene in self.scenes.items():
                if scene.is_dirty and scene.file_path:
                    scene.save_to_file(scene.file_path)
                elif scene.is_dirty and not scene.file_path:
                    # Auto-generate scene file path
                    scene_file = file_path.parent / f"{scene_id}.scene"
                    scene.save_to_file(scene_file)
                    
            # Save project file
            data = self.serialize()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            self.project_dir = file_path.parent
            self.mark_clean()
            logger.info(f"Project saved to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save project to {file_path}: {e}")
            raise
            
    def load_from_file(self, file_path: Path):
        """Load the project from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.deserialize(data)
            self.project_dir = file_path.parent
            self.mark_clean()
            logger.info(f"Project loaded from {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load project from {file_path}: {e}")
            raise
            
    def load_scene_content(self, scene_id: str):
        """Load the actual content of a scene from its file."""
        if scene_id not in self.scenes:
            return False
            
        scene = self.scenes[scene_id]
        if not scene.file_path or not scene.file_path.exists():
            return False
            
        try:
            scene.load_from_file(scene.file_path)
            return True
        except Exception as e:
            logger.error(f"Failed to load scene content for {scene_id}: {e}")
            return False
            
    def create_new_scene(self, name: str) -> str:
        """Create a new empty scene."""
        scene = EditorScene(name)
        return self.add_scene(scene)
        
    def duplicate_scene(self, scene_id: str, new_name: str) -> Optional[str]:
        """Duplicate an existing scene."""
        if scene_id not in self.scenes:
            return None
            
        original_scene = self.scenes[scene_id]
        try:
            # Serialize and deserialize to create a copy
            data = original_scene.serialize()
            new_scene = EditorScene(new_name)
            new_scene.deserialize(data)
            new_scene.name = new_name
            new_scene.file_path = None  # Clear file path so it gets a new one
            new_scene.mark_dirty()
            
            return self.add_scene(new_scene)
            
        except Exception as e:
            logger.error(f"Failed to duplicate scene {scene_id}: {e}")
            return None
