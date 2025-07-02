"""
Dummy classes to replace engine dependencies that require pygame initialization.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import pygame

# Add engine to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class DummyScene:
    def addPhysics(self, actor=None):
        return

class DummyGame:
    """Dummy Game class that doesn't require pygame initialization."""
    
    _instance = None
    
    def __init__(self):
        self.width = 1920
        self.height = 1080
        self.running = False
        self.scenes = {}
        # self.current_scene = None
        self.currentScene = DummyScene()
        
    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def addScene(self, name: str, scene):
        self.scenes[name] = scene
        
    def switchScene(self, name: str):
        if name in self.scenes:
            self.current_scene = self.scenes[name]

class DummyUIManager:
    """Dummy UI Manager for editor use."""
    
    def __init__(self, screen_size=(1920, 1080)):
        self.screen_size = screen_size
        self.widgets = []
        self.root_widgets = []
        
    def add_widget(self, widget):
        self.widgets.append(widget)
        if not widget.parent:
            self.root_widgets.append(widget)
            
    def remove_widget(self, widget):
        if widget in self.widgets:
            self.widgets.remove(widget)
        if widget in self.root_widgets:
            self.root_widgets.remove(widget)

def patch_engine_for_editor():
    """Patch the engine to use dummy classes for editor mode."""
    try:
        # Patch the Game class
        import engine
        engine.Game = DummyGame
        
        # Set up a dummy instance
        DummyGame._instance = DummyGame()
        
        # Patch UIManager in scene
        from engine.scene import scene
        scene.UIManager = DummyUIManager
        
    except Exception as e:
        print(f"Warning: Could not patch engine for editor: {e}")

# Initialize patches when this module is imported
patch_engine_for_editor()
