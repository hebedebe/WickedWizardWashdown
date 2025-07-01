"""
Main window for the Scene Editor.
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional, Dict, List

from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSplitter,
    QMenuBar, QMenu, QStatusBar, QTabWidget, QMessageBox, QFileDialog,
    QInputDialog, QProgressBar, QLabel, QApplication, QToolBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QKeySequence, QIcon, QPixmap, QCloseEvent, QAction

# Add engine to path and patch it
sys.path.insert(0, str(Path(__file__).parent.parent))
import editor_dummy  # This patches the engine

from editor_project import EditorProject
from editor_scene import EditorScene
from editor_utils import show_error, show_warning, show_info, ask_yes_no, UndoRedoManager
from editor_hierarchy import HierarchyWidget
from editor_inspector import InspectorWidget
from editor_scene_view import SceneViewWidget
from editor_console import ConsoleWidget
from editor_tools import ToolsWidget

logger = logging.getLogger(__name__)

class EditorMainWindow(QMainWindow):
    """Main window for the scene editor."""
    
    # Signals
    scene_changed = pyqtSignal(str)  # scene_id
    project_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Initialize core systems
        self.project: Optional[EditorProject] = None
        self.undo_manager = UndoRedoManager()
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._auto_save)
        
        # Initialize UI
        self._init_ui()
        self._init_menus()
        self._init_toolbars()
        self._init_status_bar()
        self._setup_shortcuts()
        self._connect_signals()
        
        # Create new project by default
        self._new_project()
        
        logger.info("Scene Editor initialized")
        
    def _init_ui(self):
        """Initialize the main UI layout."""
        self.setWindowTitle("Wicked Wizard Washdown - Scene Editor")
        self.setMinimumSize(1200, 800)
        self.resize(1600, 1000)
        
        # Central widget with splitters
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        central_widget_layout = QVBoxLayout(central_widget)
        central_widget_layout.addWidget(main_splitter)
        central_widget_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left panel (Hierarchy + Tools)
        left_splitter = QSplitter(Qt.Orientation.Vertical)
        left_splitter.setMaximumWidth(400)
        left_splitter.setMinimumWidth(250)
        
        self.hierarchy_widget = HierarchyWidget()
        self.tools_widget = ToolsWidget()
        
        left_splitter.addWidget(self.hierarchy_widget)
        left_splitter.addWidget(self.tools_widget)
        left_splitter.setSizes([300, 200])
        
        # Center panel (Scene tabs + Console)
        center_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Scene tabs
        self.scene_tabs = QTabWidget()
        self.scene_tabs.setTabsClosable(True)
        self.scene_tabs.tabCloseRequested.connect(self._close_scene_tab)
        self.scene_tabs.currentChanged.connect(self._scene_tab_changed)
        
        self.console_widget = ConsoleWidget()
        
        center_splitter.addWidget(self.scene_tabs)
        center_splitter.addWidget(self.console_widget)
        center_splitter.setSizes([600, 200])
        
        # Right panel (Inspector)
        self.inspector_widget = InspectorWidget()
        self.inspector_widget.setMaximumWidth(400)
        self.inspector_widget.setMinimumWidth(250)
        
        # Add panels to main splitter
        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(center_splitter)
        main_splitter.addWidget(self.inspector_widget)
        main_splitter.setSizes([300, 800, 300])
        
    def _init_menus(self):
        """Initialize the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # New project
        new_project_action = QAction("&New Project", self)
        new_project_action.setShortcut(QKeySequence.StandardKey.New)
        new_project_action.triggered.connect(self._new_project)
        file_menu.addAction(new_project_action)
        
        # Open project
        open_project_action = QAction("&Open Project...", self)
        open_project_action.setShortcut(QKeySequence.StandardKey.Open)
        open_project_action.triggered.connect(self._open_project)
        file_menu.addAction(open_project_action)
        
        file_menu.addSeparator()
        
        # Save project
        self.save_project_action = QAction("&Save Project", self)
        self.save_project_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_project_action.triggered.connect(self._save_project)
        file_menu.addAction(self.save_project_action)
        
        # Save project as
        save_project_as_action = QAction("Save Project &As...", self)
        save_project_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_project_as_action.triggered.connect(self._save_project_as)
        file_menu.addAction(save_project_as_action)
        
        file_menu.addSeparator()
        
        # New scene
        new_scene_action = QAction("New &Scene", self)
        new_scene_action.setShortcut(QKeySequence("Ctrl+Shift+N"))
        new_scene_action.triggered.connect(self._new_scene)
        file_menu.addAction(new_scene_action)
        
        # Import scene
        import_scene_action = QAction("&Import Scene...", self)
        import_scene_action.triggered.connect(self._import_scene)
        file_menu.addAction(import_scene_action)
        
        file_menu.addSeparator()
        
        # Import custom components/widgets
        import_components_action = QAction("Import Custom &Components...", self)
        import_components_action.triggered.connect(self._import_custom_components)
        file_menu.addAction(import_components_action)
        
        import_widgets_action = QAction("Import Custom &Widgets...", self)
        import_widgets_action.triggered.connect(self._import_custom_widgets)
        file_menu.addAction(import_widgets_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        # Undo/Redo
        self.undo_action = QAction("&Undo", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.triggered.connect(self.undo_manager.undo)
        edit_menu.addAction(self.undo_action)
        
        self.redo_action = QAction("&Redo", self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.triggered.connect(self.undo_manager.redo)
        edit_menu.addAction(self.redo_action)
        
        edit_menu.addSeparator()
        
        # Copy/Paste
        self.copy_action = QAction("&Copy", self)
        self.copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        self.copy_action.triggered.connect(self._copy)
        edit_menu.addAction(self.copy_action)
        
        self.paste_action = QAction("&Paste", self)
        self.paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        self.paste_action.triggered.connect(self._paste)
        edit_menu.addAction(self.paste_action)
        
        # Delete
        delete_action = QAction("&Delete", self)
        delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        delete_action.triggered.connect(self._delete)
        edit_menu.addAction(delete_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        # Reset layout
        reset_layout_action = QAction("&Reset Layout", self)
        reset_layout_action.triggered.connect(self._reset_layout)
        view_menu.addAction(reset_layout_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        # Scene validation
        validate_scene_action = QAction("&Validate Current Scene", self)
        validate_scene_action.triggered.connect(self._validate_scene)
        tools_menu.addAction(validate_scene_action)
        
        # Performance profiler
        profiler_action = QAction("&Performance Profiler", self)
        profiler_action.triggered.connect(self._show_profiler)
        tools_menu.addAction(profiler_action)
        
        # Python debugger
        debugger_action = QAction("Python &Debugger", self)
        debugger_action.triggered.connect(self._show_debugger)
        tools_menu.addAction(debugger_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        # About
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
    def _init_toolbars(self):
        """Initialize toolbars."""
        # Main toolbar
        main_toolbar = self.addToolBar("Main")
        main_toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        # New project
        new_project_action = QAction("New Project", self)
        new_project_action.triggered.connect(self._new_project)
        main_toolbar.addAction(new_project_action)
        
        # Open project
        open_project_action = QAction("Open Project", self)
        open_project_action.triggered.connect(self._open_project)
        main_toolbar.addAction(open_project_action)
        
        # Save project
        save_project_action = QAction("Save Project", self)
        save_project_action.triggered.connect(self._save_project)
        main_toolbar.addAction(save_project_action)
        
        main_toolbar.addSeparator()
        
        # New scene
        new_scene_action = QAction("New Scene", self)
        new_scene_action.triggered.connect(self._new_scene)
        main_toolbar.addAction(new_scene_action)
        
    def _init_status_bar(self):
        """Initialize the status bar."""
        self.status_bar = self.statusBar()
        
        # Project status
        self.project_status_label = QLabel("No project loaded")
        self.status_bar.addWidget(self.project_status_label)
        
        # Scene status
        self.scene_status_label = QLabel("")
        self.status_bar.addPermanentWidget(self.scene_status_label)
        
        # Progress bar for operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
    def _setup_shortcuts(self):
        """Set up additional keyboard shortcuts."""
        pass
        
    def _connect_signals(self):
        """Connect internal signals."""
        self.undo_manager.changed.connect(self._update_undo_redo_actions)
        self.hierarchy_widget.selection_changed.connect(self.inspector_widget.set_object)
        self.inspector_widget.property_changed.connect(self._on_property_changed)
        
    def _update_undo_redo_actions(self):
        """Update undo/redo action states."""
        self.undo_action.setEnabled(self.undo_manager.can_undo())
        self.redo_action.setEnabled(self.undo_manager.can_redo())
        
    def _new_project(self):
        """Create a new project."""
        if self._check_unsaved_changes():
            self.project = EditorProject("New Project")
            self._update_project_status()
            self._clear_scene_tabs()
            self.undo_manager.clear()
            logger.info("Created new project")
            
    def _open_project(self):
        """Open an existing project."""
        if not self._check_unsaved_changes():
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "Project files (*.wwproject);;All files (*)"
        )
        
        if file_path:
            try:
                project = EditorProject()
                project.load_from_file(Path(file_path))
                self.project = project
                self._update_project_status()
                self._load_project_scenes()
                self.undo_manager.clear()
                logger.info(f"Opened project: {file_path}")
                
            except Exception as e:
                show_error("Error", f"Failed to open project:\n{str(e)}", self)
                
    def _save_project(self):
        """Save the current project."""
        if not self.project:
            return
            
        if not self.project.project_dir:
            self._save_project_as()
            return
            
        try:
            project_file = self.project.project_dir / f"{self.project.name}.wwproject"
            self.project.save_to_file(project_file)
            self._update_project_status()
            logger.info("Project saved")
            
        except Exception as e:
            show_error("Error", f"Failed to save project:\n{str(e)}", self)
            
    def _save_project_as(self):
        """Save the project with a new name/location."""
        if not self.project:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Project As", f"{self.project.name}.wwproject", 
            "Project files (*.wwproject);;All files (*)"
        )
        
        if file_path:
            try:
                self.project.save_to_file(Path(file_path))
                self._update_project_status()
                logger.info(f"Project saved as: {file_path}")
                
            except Exception as e:
                show_error("Error", f"Failed to save project:\n{str(e)}", self)
                
    def _new_scene(self):
        """Create a new scene."""
        if not self.project:
            return
            
        name, ok = QInputDialog.getText(self, "New Scene", "Scene name:")
        if ok and name:
            scene_id = self.project.create_new_scene(name)
            self._add_scene_tab(scene_id)
            self._update_project_status()
            
    def _import_scene(self):
        """Import a scene from file."""
        if not self.project:
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Scene", "", "Scene files (*.scene);;All files (*)"
        )
        
        if file_path:
            try:
                scene = EditorScene()
                scene.load_from_file(Path(file_path))
                scene_id = self.project.add_scene(scene)
                self._add_scene_tab(scene_id)
                logger.info(f"Imported scene: {file_path}")
                
            except Exception as e:
                show_error("Error", f"Failed to import scene:\n{str(e)}", self)
                
    def _import_custom_components(self):
        """Import custom components from a Python file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Custom Components", "", "Python files (*.py);;All files (*)"
        )
        
        if file_path and self.project:
            self.project.add_custom_component_path(file_path)
            show_info("Success", f"Added custom component path: {file_path}", self)
            
    def _import_custom_widgets(self):
        """Import custom widgets from a Python file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Custom Widgets", "", "Python files (*.py);;All files (*)"
        )
        
        if file_path and self.project:
            self.project.add_custom_widget_path(file_path)
            show_info("Success", f"Added custom widget path: {file_path}", self)
            
    def _copy(self):
        """Copy selected objects."""
        # TODO: Implement copy functionality
        pass
        
    def _paste(self):
        """Paste copied objects."""
        # TODO: Implement paste functionality
        pass
        
    def _delete(self):
        """Delete selected objects."""
        # TODO: Implement delete functionality
        pass
        
    def _reset_layout(self):
        """Reset the UI layout to default."""
        # TODO: Implement layout reset
        pass
        
    def _validate_scene(self):
        """Validate the current scene."""
        # TODO: Implement scene validation
        show_info("Scene Validation", "Scene validation not yet implemented", self)
        
    def _show_profiler(self):
        """Show the performance profiler."""
        # TODO: Implement profiler
        show_info("Profiler", "Performance profiler not yet implemented", self)
        
    def _show_debugger(self):
        """Show the Python debugger."""
        # TODO: Implement debugger
        show_info("Debugger", "Python debugger not yet implemented", self)
        
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About Scene Editor", 
                         "Wicked Wizard Washdown Scene Editor\nVersion 1.0\n\nA comprehensive scene editing tool.")
                         
    def _update_project_status(self):
        """Update the project status display."""
        if self.project:
            status = f"Project: {self.project.name}"
            if self.project.is_dirty:
                status += " *"
            self.project_status_label.setText(status)
            
            # Update window title
            title = f"Scene Editor - {self.project.name}"
            if self.project.has_unsaved_changes():
                title += " *"
            self.setWindowTitle(title)
        else:
            self.project_status_label.setText("No project loaded")
            self.setWindowTitle("Scene Editor")
            
    def _clear_scene_tabs(self):
        """Clear all scene tabs."""
        self.scene_tabs.clear()
        
    def _load_project_scenes(self):
        """Load scenes from the current project."""
        if not self.project:
            return
            
        self._clear_scene_tabs()
        
        for scene_id in self.project.scenes:
            self._add_scene_tab(scene_id)
            
        # Set active scene
        if self.project.active_scene:
            self._set_active_scene_tab(self.project.active_scene)
            
    def _add_scene_tab(self, scene_id: str):
        """Add a scene tab."""
        scene = self.project.get_scene(scene_id)
        if not scene:
            return
            
        scene_view = SceneViewWidget(scene)
        index = self.scene_tabs.addTab(scene_view, scene.name)
        self.scene_tabs.setCurrentIndex(index)
        
        # Connect scene view signals
        scene_view.selection_changed.connect(self.hierarchy_widget.set_selection)
        
    def _set_active_scene_tab(self, scene_id: str):
        """Set the active scene tab."""
        for i in range(self.scene_tabs.count()):
            widget = self.scene_tabs.widget(i)
            if hasattr(widget, 'scene') and widget.scene and scene_id in self.project.scenes:
                if widget.scene == self.project.scenes[scene_id]:
                    self.scene_tabs.setCurrentIndex(i)
                    break
                    
    def _close_scene_tab(self, index: int):
        """Close a scene tab."""
        widget = self.scene_tabs.widget(index)
        if hasattr(widget, 'scene') and widget.scene:
            # Check for unsaved changes
            if widget.scene.is_dirty:
                reply = ask_yes_no("Unsaved Changes", 
                                 f"Scene '{widget.scene.name}' has unsaved changes. Close anyway?", self)
                if not reply:
                    return
                    
        self.scene_tabs.removeTab(index)
        
    def _scene_tab_changed(self, index: int):
        """Handle scene tab change."""
        if index >= 0:
            widget = self.scene_tabs.widget(index)
            if hasattr(widget, 'scene') and widget.scene:
                # Find scene ID
                for scene_id, scene in self.project.scenes.items():
                    if scene == widget.scene:
                        self.project.set_active_scene(scene_id)
                        self.hierarchy_widget.set_scene(scene)
                        self.scene_changed.emit(scene_id)
                        break
                        
    def _on_property_changed(self, obj, property_name: str, new_value):
        """Handle property changes from the inspector."""
        # TODO: Create undo command for property changes
        setattr(obj, property_name, new_value)
        if hasattr(obj, 'scene'):
            obj.scene.mark_dirty()
        elif self.project and self.project.get_active_scene():
            self.project.get_active_scene().mark_dirty()
        self._update_project_status()
        
    def _check_unsaved_changes(self) -> bool:
        """Check for unsaved changes and ask user what to do."""
        if not self.project or not self.project.has_unsaved_changes():
            return True
            
        reply = QMessageBox.question(
            self, "Unsaved Changes", 
            "There are unsaved changes. Do you want to save them?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Save:
            self._save_project()
            return not self.project.has_unsaved_changes()  # Only proceed if save was successful
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:  # Cancel
            return False
            
    def _auto_save(self):
        """Auto-save the project."""
        if (self.project and 
            self.project.settings.get("editor_settings", {}).get("auto_save", False) and
            self.project.has_unsaved_changes()):
            try:
                self._save_project()
                logger.info("Auto-saved project")
            except Exception as e:
                logger.error(f"Auto-save failed: {e}")
                
    def closeEvent(self, event: QCloseEvent):
        """Handle window close event."""
        if self._check_unsaved_changes():
            event.accept()
        else:
            event.ignore()
