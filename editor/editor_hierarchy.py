"""
Hierarchy widget for displaying and managing actors and UI elements in the scene.
"""

import sys
from pathlib import Path
from typing import Optional, List, Any
import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem, 
    QPushButton, QMenu, QInputDialog, QComboBox, QLabel, QSplitter,
    QTabWidget, QMessageBox, QDialog, QFormLayout, QLineEdit, QSpinBox,
    QDoubleSpinBox, QCheckBox, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QPoint
from PyQt6.QtGui import QDrag, QDropEvent, QDragEnterEvent, QDragMoveEvent

# Add engine to path and patch it
sys.path.insert(0, str(Path(__file__).parent.parent))
import editor_dummy

from editor_scene import EditorScene
from editor_utils import get_engine_components, get_engine_widgets
from engine.actor.actor import Actor
from engine.ui.widget import Widget

logger = logging.getLogger(__name__)

class DraggableTreeWidget(QTreeWidget):
    """Tree widget with drag and drop support for parenting."""
    
    items_dropped = pyqtSignal(QTreeWidgetItem, QTreeWidgetItem)  # dropped_item, target_item
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        
    def dropEvent(self, event: QDropEvent):
        """Handle drop events for parenting."""
        dropped_item = self.currentItem()
        target_item = self.itemAt(event.position().toPoint())
        
        if dropped_item and target_item and dropped_item != target_item:
            # Check if target is not a descendant of dropped item
            parent = target_item
            while parent:
                if parent == dropped_item:
                    event.ignore()
                    return
                parent = parent.parent()
                
            self.items_dropped.emit(dropped_item, target_item)
            
        super().dropEvent(event)

class HierarchyWidget(QWidget):
    """Widget for managing scene hierarchy."""
    
    selection_changed = pyqtSignal(object)  # Selected object (Actor or Widget)
    
    def __init__(self):
        super().__init__()
        
        self.scene: Optional[EditorScene] = None
        self.selected_object: Optional[Any] = None
        
        self._init_ui()
        self._connect_signals()
        
    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        
        # Tab widget for Actors and UI
        self.tab_widget = QTabWidget()
        
        # Actors tab
        actors_widget = QWidget()
        actors_layout = QVBoxLayout(actors_widget)
        
        # Actors tree
        self.actors_tree = DraggableTreeWidget()
        self.actors_tree.setHeaderLabel("Actors")
        self.actors_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.actors_tree.customContextMenuRequested.connect(self._show_actor_context_menu)
        actors_layout.addWidget(self.actors_tree)
        
        # Add actor controls
        actor_controls = QHBoxLayout()
        self.add_actor_btn = QPushButton("Add Actor")
        self.add_component_btn = QPushButton("Add Component")
        actor_controls.addWidget(self.add_actor_btn)
        actor_controls.addWidget(self.add_component_btn)
        actors_layout.addLayout(actor_controls)
        
        self.tab_widget.addTab(actors_widget, "Actors")
        
        # UI tab
        ui_widget = QWidget()
        ui_layout = QVBoxLayout(ui_widget)
        
        # UI tree
        self.ui_tree = DraggableTreeWidget()
        self.ui_tree.setHeaderLabel("UI Elements")
        self.ui_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ui_tree.customContextMenuRequested.connect(self._show_ui_context_menu)
        ui_layout.addWidget(self.ui_tree)
        
        # Add UI controls
        ui_controls = QHBoxLayout()
        self.add_widget_btn = QPushButton("Add Widget")
        ui_controls.addWidget(self.add_widget_btn)
        ui_layout.addLayout(ui_controls)
        
        self.tab_widget.addTab(ui_widget, "UI")
        
        layout.addWidget(self.tab_widget)
        
    def _connect_signals(self):
        """Connect internal signals."""
        self.add_actor_btn.clicked.connect(self._add_actor)
        self.add_component_btn.clicked.connect(self._add_component)
        self.add_widget_btn.clicked.connect(self._add_widget)
        
        self.actors_tree.itemSelectionChanged.connect(self._on_actor_selection_changed)
        self.ui_tree.itemSelectionChanged.connect(self._on_ui_selection_changed)
        
        self.actors_tree.items_dropped.connect(self._on_actors_dropped)
        self.ui_tree.items_dropped.connect(self._on_ui_dropped)
        
    def set_scene(self, scene: EditorScene):
        """Set the scene to display."""
        self.scene = scene
        self._refresh_actors()
        self._refresh_ui()
        
    def _refresh_actors(self):
        """Refresh the actors tree."""
        self.actors_tree.clear()
        
        if not self.scene:
            return
            
        # Add root actors (those without parents)
        for actor in self.scene.scene.actors:
            if not actor.parent:
                self._add_actor_item(actor, None)
                
    def _add_actor_item(self, actor: Actor, parent_item: Optional[QTreeWidgetItem]) -> QTreeWidgetItem:
        """Add an actor item to the tree."""
        if parent_item:
            item = QTreeWidgetItem(parent_item)
        else:
            item = QTreeWidgetItem(self.actors_tree)
            
        item.setText(0, actor.name)
        item.setData(0, Qt.ItemDataRole.UserRole, actor)
        
        # Add children
        for child in actor.children:
            self._add_actor_item(child, item)
            
        item.setExpanded(True)
        return item
        
    def _refresh_ui(self):
        """Refresh the UI tree."""
        self.ui_tree.clear()
        
        if not self.scene or not hasattr(self.scene.scene, 'uiManager'):
            return
            
        # Add root widgets
        for widget in self.scene.scene.uiManager.root_widgets:
            self._add_widget_item(widget, None)
            
    def _add_widget_item(self, widget: Widget, parent_item: Optional[QTreeWidgetItem]) -> QTreeWidgetItem:
        """Add a widget item to the tree."""
        if parent_item:
            item = QTreeWidgetItem(parent_item)
        else:
            item = QTreeWidgetItem(self.ui_tree)
            
        item.setText(0, widget.name or widget.__class__.__name__)
        item.setData(0, Qt.ItemDataRole.UserRole, widget)
        
        # Add children
        for child in widget.children:
            self._add_widget_item(child, item)
            
        item.setExpanded(True)
        return item
        
    def _add_actor(self):
        """Add a new actor."""
        if not self.scene:
            return
            
        name, ok = QInputDialog.getText(self, "New Actor", "Actor name:")
        if ok and name:
            actor = Actor(name)
            
            # Check if we should parent to selected actor
            selected_item = self.actors_tree.currentItem()
            if selected_item:
                parent_actor = selected_item.data(0, Qt.ItemDataRole.UserRole)
                if isinstance(parent_actor, Actor):
                    parent_actor.addChild(actor)
                    
            self.scene.add_actor(actor)
            self._refresh_actors()
            
    def _add_component(self):
        """Add a component to the selected actor."""
        selected_item = self.actors_tree.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "No Selection", "Please select an actor first.")
            return
            
        actor = selected_item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(actor, Actor):
            return
            
        # Get available components
        components = get_engine_components()
        if not components:
            QMessageBox.warning(self, "No Components", "No components available.")
            return
            
        component_name, ok = QInputDialog.getItem(
            self, "Add Component", "Select component type:", 
            list(components.keys()), 0, False
        )
        
        if ok and component_name:
            try:
                component_class = components[component_name]
                
                # Create component with appropriate parameters
                component = self._create_component_with_params(component_class, component_name)
                if component is None:
                    return  # User cancelled or error occurred
                    
                actor.addComponent(component)
                self.scene.mark_dirty()
                
                # Refresh inspector if this actor is selected
                if self.selected_object == actor:
                    self.selection_changed.emit(actor)
                    
            except Exception as e:
                logger.error(e)
                QMessageBox.critical(self, "Error", f"Failed to add component:\n{str(e)}")
                
    def _add_widget(self):
        """Add a new UI widget."""
        if not self.scene:
            return
            
        # Get available widgets
        widgets = get_engine_widgets()
        if not widgets:
            QMessageBox.warning(self, "No Widgets", "No widgets available.")
            return
            
        widget_name, ok = QInputDialog.getItem(
            self, "Add Widget", "Select widget type:", 
            list(widgets.keys()), 0, False
        )
        
        if ok and widget_name:
            try:
                import pygame
                widget_class = widgets[widget_name]
                widget = widget_class(pygame.Rect(0, 0, 100, 50), f"New{widget_name}")
                
                # Check if we should parent to selected widget
                selected_item = self.ui_tree.currentItem()
                if selected_item:
                    parent_widget = selected_item.data(0, Qt.ItemDataRole.UserRole)
                    if isinstance(parent_widget, Widget):
                        parent_widget.add_child(widget)
                        
                if hasattr(self.scene.scene, 'uiManager'):
                    self.scene.scene.uiManager.add_widget(widget)
                    
                self.scene.mark_dirty()
                self._refresh_ui()
                
            except Exception as e:
                logger.error(e)
                QMessageBox.critical(self, "Error", f"Failed to add widget:\n{str(e)}")
                
    def _show_actor_context_menu(self, position: QPoint):
        """Show context menu for actors."""
        item = self.actors_tree.itemAt(position)
        if not item:
            return
            
        actor = item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(actor, Actor):
            return
            
        menu = QMenu(self)
        
        # Rename
        rename_action = menu.addAction("Rename")
        rename_action.triggered.connect(lambda: self._rename_actor(item, actor))
        
        # Duplicate
        duplicate_action = menu.addAction("Duplicate")
        duplicate_action.triggered.connect(lambda: self._duplicate_actor(actor))
        
        # Delete
        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(lambda: self._delete_actor(actor))
        
        menu.exec(self.actors_tree.mapToGlobal(position))
        
    def _show_ui_context_menu(self, position: QPoint):
        """Show context menu for UI widgets."""
        item = self.ui_tree.itemAt(position)
        if not item:
            return
            
        widget = item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(widget, Widget):
            return
            
        menu = QMenu(self)
        
        # Rename
        rename_action = menu.addAction("Rename")
        rename_action.triggered.connect(lambda: self._rename_widget(item, widget))
        
        # Delete
        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(lambda: self._delete_widget(widget))
        
        menu.exec(self.ui_tree.mapToGlobal(position))
        
    def _rename_actor(self, item: QTreeWidgetItem, actor: Actor):
        """Rename an actor."""
        new_name, ok = QInputDialog.getText(self, "Rename Actor", "New name:", text=actor.name)
        if ok and new_name:
            actor.setName(new_name)
            item.setText(0, new_name)
            if self.scene:
                self.scene.mark_dirty()
                
    def _rename_widget(self, item: QTreeWidgetItem, widget: Widget):
        """Rename a widget."""
        new_name, ok = QInputDialog.getText(self, "Rename Widget", "New name:", text=widget.name)
        if ok and new_name:
            widget.name = new_name
            item.setText(0, new_name)
            if self.scene:
                self.scene.mark_dirty()
                
    def _duplicate_actor(self, actor: Actor):
        """Duplicate an actor."""
        # TODO: Implement actor duplication
        QMessageBox.information(self, "Not Implemented", "Actor duplication not yet implemented.")
        
    def _delete_actor(self, actor: Actor):
        """Delete an actor."""
        reply = QMessageBox.question(self, "Delete Actor", 
                                   f"Delete actor '{actor.name}' and all its children?")
        if reply == QMessageBox.StandardButton.Yes:
            if self.scene:
                self.scene.remove_actor(actor)
                self._refresh_actors()
                
    def _delete_widget(self, widget: Widget):
        """Delete a widget."""
        reply = QMessageBox.question(self, "Delete Widget", 
                                   f"Delete widget '{widget.name}' and all its children?")
        if reply == QMessageBox.StandardButton.Yes:
            if self.scene and hasattr(self.scene.scene, 'uiManager'):
                self.scene.scene.uiManager.remove_widget(widget)
                if widget.parent:
                    widget.parent.remove_child(widget)
                self.scene.mark_dirty()
                self._refresh_ui()
                
    def _on_actors_dropped(self, dropped_item: QTreeWidgetItem, target_item: QTreeWidgetItem):
        """Handle actor parenting via drag and drop."""
        dropped_actor = dropped_item.data(0, Qt.ItemDataRole.UserRole)
        target_actor = target_item.data(0, Qt.ItemDataRole.UserRole)
        
        if isinstance(dropped_actor, Actor) and isinstance(target_actor, Actor):
            target_actor.addChild(dropped_actor)
            if self.scene:
                self.scene.mark_dirty()
            self._refresh_actors()
            
    def _on_ui_dropped(self, dropped_item: QTreeWidgetItem, target_item: QTreeWidgetItem):
        """Handle UI widget parenting via drag and drop."""
        dropped_widget = dropped_item.data(0, Qt.ItemDataRole.UserRole)
        target_widget = target_item.data(0, Qt.ItemDataRole.UserRole)
        
        if isinstance(dropped_widget, Widget) and isinstance(target_widget, Widget):
            target_widget.add_child(dropped_widget)
            if self.scene:
                self.scene.mark_dirty()
            self._refresh_ui()
            
    def _on_actor_selection_changed(self):
        """Handle actor selection changes."""
        selected_items = self.actors_tree.selectedItems()
        if selected_items:
            actor = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
            if isinstance(actor, Actor):
                self.selected_object = actor
                self.selection_changed.emit(actor)
                
    def _on_ui_selection_changed(self):
        """Handle UI selection changes."""
        selected_items = self.ui_tree.selectedItems()
        if selected_items:
            widget = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
            if isinstance(widget, Widget):
                self.selected_object = widget
                self.selection_changed.emit(widget)
                
    def set_selection(self, obj: Any):
        """Set the selected object from external source."""
        self.selected_object = obj
        # TODO: Find and select the corresponding tree item
    
    def _create_component_with_params(self, component_class, component_name): ## TODO: FIX THIS!!!
        """Create a component with appropriate parameters based on its type."""
        import inspect
        import pygame
        
        # Get the constructor signature
        params = []
        default_values = []
        needs_explicit_value = False
        try:
            sig = inspect.signature(component_class.__init__)
            for key in list(sig.parameters.keys())[1:]:
                default_param = sig.parameters[key].default
                if default_param != inspect.Parameter.empty:
                    param = sig.parameters[key]
                    params.append(param)
                    default_values.append(default_param)
                else:
                    needs_explicit_value = True
            # params = list(sig.parameters.keys())[1:]  # Skip 'self'
        except Exception as e:
            logger.warning(f"An internal error occurred creating a component: {e}")
            # Fallback for components without parameters
            params = []

        logger.info(f"Component parameters: {params}")
        logger.info(f"Component default values: {default_values}")
        logger.info(f"Component needs explicit values: {needs_explicit_value}")

        if component_name == 'PhysicsComponent':
            return self._create_physics_component()
        
        if not params and not default_values:
            # Component doesn't need parameters
            logger.info("Created component class with no parameters")
            return component_class()
        else:
            if (needs_explicit_value):
                logger.info("Created component class with explicit parameters")
                return self._create_generic_component(component_class, params)
            else:
                logger.info("Created component class with default parameters")
                return component_class(*default_values)
    
    def _create_circle_renderer_component(self):
        """Create CircleRendererComponent with radius and color parameters."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Circle Renderer Component")
        dialog.setModal(True)
        
        layout = QFormLayout(dialog)
        
        # Radius input
        radius_spin = QSpinBox()
        radius_spin.setRange(1, 1000)
        radius_spin.setValue(50)
        layout.addRow("Radius:", radius_spin)
        
        # Color inputs (RGB)
        red_spin = QSpinBox()
        red_spin.setRange(0, 255)
        red_spin.setValue(255)
        layout.addRow("Red:", red_spin)
        
        green_spin = QSpinBox()
        green_spin.setRange(0, 255)
        green_spin.setValue(255)
        layout.addRow("Green:", green_spin)
        
        blue_spin = QSpinBox()
        blue_spin.setRange(0, 255)
        blue_spin.setValue(255)
        layout.addRow("Blue:", blue_spin)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            from engine.component.builtin.circleRendererComponent import CircleRendererComponent
            radius = radius_spin.value()
            color = (red_spin.value(), green_spin.value(), blue_spin.value())
            return CircleRendererComponent(radius, color)
        
        return None
    
    def _create_physics_component(self):
        """Create PhysicsComponent with body and shapes parameters."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Physics Component")
        dialog.setModal(True)
        
        layout = QFormLayout(dialog)
        
        # Body type selection
        body_type_combo = QComboBox()
        body_type_combo.addItems(["Dynamic", "Static", "Kinematic"])
        layout.addRow("Body Type:", body_type_combo)
        
        # Mass input (for dynamic bodies)
        mass_spin = QDoubleSpinBox()
        mass_spin.setRange(0.1, 1000.0)
        mass_spin.setValue(1.0)
        layout.addRow("Mass:", mass_spin)
        
        # Shape type selection
        shape_type_combo = QComboBox()
        shape_type_combo.addItems(["Circle", "Box"])
        layout.addRow("Shape Type:", shape_type_combo)
        
        # Shape size inputs
        size_spin = QDoubleSpinBox()
        size_spin.setRange(1.0, 1000.0)
        size_spin.setValue(25.0)
        layout.addRow("Size/Radius:", size_spin)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            import pymunk
            from engine.component.builtin.physicsComponent import PhysicsComponent
            
            # Create body
            body_type_map = {
                "Dynamic": pymunk.Body.DYNAMIC,
                "Static": pymunk.Body.STATIC,
                "Kinematic": pymunk.Body.KINEMATIC
            }
            body_type = body_type_map[body_type_combo.currentText()]
            
            if body_type == pymunk.Body.DYNAMIC:
                # Calculate moment of inertia
                if shape_type_combo.currentText() == "Circle":
                    moment = pymunk.moment_for_circle(mass_spin.value(), 0, size_spin.value())
                else:  # Box
                    moment = pymunk.moment_for_box(mass_spin.value(), (size_spin.value(), size_spin.value()))
                body = pymunk.Body(mass_spin.value(), moment)
            else:
                body = pymunk.Body(body_type=body_type)
            
            # Create shape
            if shape_type_combo.currentText() == "Circle":
                shape = pymunk.Circle(body, size_spin.value())
            else:  # Box
                shape = pymunk.Poly.create_box(body, (size_spin.value(), size_spin.value()))
            
            return PhysicsComponent(body, [shape])
        
        return None
    
    def _create_generic_component(self, component_class, params):
        """Create a component with a generic parameter dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Create {component_class.__name__}")
        dialog.setModal(True)
        
        layout = QFormLayout(dialog)
        
        inputs = {}
        for param in params:
            # Create a generic string input for each parameter
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"Enter {param}...")
            layout.addRow(f"{param}:", line_edit)
            inputs[param] = line_edit
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                # Try to create the component with string parameters
                args = [inputs[param].text() for param in params]
                return component_class(*args)
            except Exception as e:
                logger.error(e)
                QMessageBox.critical(self, "Error", f"Failed to create component:\n{str(e)}")
                return None
        
        return None
