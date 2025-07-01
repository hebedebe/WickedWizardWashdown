"""
Scene view widget for visual editing of scenes.
"""

import sys
from pathlib import Path
from typing import Optional, List, Tuple, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel,
    QPushButton, QComboBox, QSlider, QFrame, QSizePolicy, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRect, QSize, QTimer
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPixmap, QPaintEvent,
    QMouseEvent, QWheelEvent, QKeyEvent, QTransform
)

# Add engine to path and patch it
sys.path.insert(0, str(Path(__file__).parent.parent))
import editor_dummy

from editor_scene import EditorScene
from engine.actor.actor import Actor
from engine.ui.widget import Widget

class SceneCanvas(QWidget):
    """Canvas widget for displaying and editing the scene visually."""
    
    selection_changed = pyqtSignal(object)  # Selected object
    object_moved = pyqtSignal(object, float, float)  # Object, dx, dy
    
    def __init__(self):
        super().__init__()
        
        self.scene: Optional[EditorScene] = None
        self.selected_objects: List[Any] = []
        self.grid_size = 20
        self.show_grid = True
        self.zoom_level = 1.0
        self.pan_offset = QPoint(0, 0)
        
        # Mouse interaction
        self.last_mouse_pos = QPoint()
        self.dragging = False
        self.panning = False
        
        # Visual settings
        self.background_color = QColor(50, 50, 50)
        self.grid_color = QColor(70, 70, 70)
        self.selection_color = QColor(255, 165, 0)  # Orange
        self.actor_color = QColor(100, 150, 255)    # Light blue
        self.ui_color = QColor(150, 255, 100)       # Light green
        
        self.setMinimumSize(400, 300)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        
    def set_scene(self, scene: EditorScene):
        """Set the scene to display."""
        self.scene = scene
        self.update()
        
    def set_selection(self, objects: List[Any]):
        """Set the selected objects."""
        self.selected_objects = objects if isinstance(objects, list) else [objects] if objects else []
        self.update()
        
    def set_zoom(self, zoom: float):
        """Set the zoom level."""
        self.zoom_level = max(0.1, min(5.0, zoom))
        self.update()
        
    def set_grid_size(self, size: int):
        """Set the grid size."""
        self.grid_size = max(5, size)
        self.update()
        
    def toggle_grid(self, show: bool):
        """Toggle grid visibility."""
        self.show_grid = show
        self.update()
        
    def world_to_screen(self, world_pos: Tuple[float, float]) -> QPoint:
        """Convert world coordinates to screen coordinates."""
        x, y = world_pos
        screen_x = int((x * self.zoom_level) + self.pan_offset.x() + self.width() // 2)
        screen_y = int((y * self.zoom_level) + self.pan_offset.y() + self.height() // 2)
        return QPoint(screen_x, screen_y)
        
    def screen_to_world(self, screen_pos: QPoint) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates."""
        world_x = (screen_pos.x() - self.width() // 2 - self.pan_offset.x()) / self.zoom_level
        world_y = (screen_pos.y() - self.height() // 2 - self.pan_offset.y()) / self.zoom_level
        return (world_x, world_y)
        
    def paintEvent(self, event: QPaintEvent):
        """Paint the scene."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), self.background_color)
        
        # Draw grid
        if self.show_grid:
            self._draw_grid(painter)
            
        # Draw scene objects
        if self.scene:
            self._draw_actors(painter)
            self._draw_ui_widgets(painter)
            
        # Draw selection highlights
        self._draw_selection(painter)
        
        # Draw viewport info
        self._draw_viewport_info(painter)
        
    def _draw_grid(self, painter: QPainter):
        """Draw the grid."""
        painter.setPen(QPen(self.grid_color, 1))
        
        # Calculate grid spacing in screen coordinates
        grid_spacing = int(self.grid_size * self.zoom_level)
        if grid_spacing < 5:
            return  # Don't draw grid if too small
            
        # Calculate grid offset
        offset_x = (self.pan_offset.x() + self.width() // 2) % grid_spacing
        offset_y = (self.pan_offset.y() + self.height() // 2) % grid_spacing
        
        # Draw vertical lines
        x = offset_x
        while x < self.width():
            painter.drawLine(x, 0, x, self.height())
            x += grid_spacing
            
        # Draw horizontal lines
        y = offset_y
        while y < self.height():
            painter.drawLine(0, y, self.width(), y)
            y += grid_spacing
            
    def _draw_actors(self, painter: QPainter):
        """Draw actors in the scene."""
        if not self.scene or not self.scene.scene.actors:
            return
            
        painter.setPen(QPen(self.actor_color, 2))
        painter.setBrush(QBrush(self.actor_color.lighter(150)))
        
        for actor in self.scene.scene.actors:
            self._draw_actor(painter, actor)
            
    def _draw_actor(self, painter: QPainter, actor: Actor):
        """Draw a single actor."""
        # Get actor position
        pos = actor.transform.position
        screen_pos = self.world_to_screen(pos)
        
        # Draw actor as a small rectangle
        size = int(20 * self.zoom_level)
        rect = QRect(int(screen_pos.x() - size//2), int(screen_pos.y() - size//2), size, size)
        painter.drawRect(rect)
        
        # Draw actor name
        if self.zoom_level > 0.5:
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.setFont(QFont("Arial", max(8, int(10 * self.zoom_level))))
            text_rect = QRect(int(screen_pos.x() - 50), int(screen_pos.y() + size//2 + 2), 100, 20)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, actor.name)
            
        # Draw children connections
        for child in actor.children:
            child_pos = child.transform.position
            child_screen_pos = self.world_to_screen(child_pos)
            painter.setPen(QPen(self.actor_color.darker(150), 1))
            painter.drawLine(screen_pos, child_screen_pos)
            
    def _draw_ui_widgets(self, painter: QPainter):
        """Draw UI widgets in the scene."""
        if not self.scene or not hasattr(self.scene.scene, 'uiManager'):
            return
            
        painter.setPen(QPen(self.ui_color, 2))
        painter.setBrush(QBrush(self.ui_color.lighter(150)))
        
        for widget in self.scene.scene.uiManager.root_widgets:
            self._draw_widget(painter, widget)
            
    def _draw_widget(self, painter: QPainter, widget: Widget):
        """Draw a single UI widget."""
        # Convert widget rect to screen coordinates
        world_rect = (widget.rect.x, widget.rect.y, widget.rect.width, widget.rect.height)
        top_left = self.world_to_screen((world_rect[0], world_rect[1]))
        bottom_right = self.world_to_screen((world_rect[0] + world_rect[2], world_rect[1] + world_rect[3]))
        
        screen_rect = QRect(top_left, bottom_right)
        painter.drawRect(screen_rect)
        
        # Draw widget name/type
        if self.zoom_level > 0.3:
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.setFont(QFont("Arial", max(8, int(9 * self.zoom_level))))
            name = widget.name or widget.__class__.__name__
            painter.drawText(screen_rect, Qt.AlignmentFlag.AlignCenter, name)
            
        # Draw children
        for child in widget.children:
            self._draw_widget(painter, child)
            
    def _draw_selection(self, painter: QPainter):
        """Draw selection highlights."""
        if not self.selected_objects:
            return
            
        painter.setPen(QPen(self.selection_color, 3))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        
        for obj in self.selected_objects:
            if isinstance(obj, Actor):
                pos = obj.transform.position
                screen_pos = self.world_to_screen(pos)
                size = int(25 * self.zoom_level)
                rect = QRect(int(screen_pos.x() - size//2), int(screen_pos.y() - size//2), size, size)
                painter.drawRect(rect)
            elif isinstance(obj, Widget):
                world_rect = (obj.rect.x, obj.rect.y, obj.rect.width, obj.rect.height)
                top_left = self.world_to_screen((world_rect[0], world_rect[1]))
                bottom_right = self.world_to_screen((world_rect[0] + world_rect[2], world_rect[1] + world_rect[3]))
                screen_rect = QRect(top_left, bottom_right)
                painter.drawRect(screen_rect)
                
    def _draw_viewport_info(self, painter: QPainter):
        """Draw viewport information."""
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.setFont(QFont("Arial", 10))
        
        info_lines = [
            f"Zoom: {self.zoom_level:.1f}x",
            f"Pan: ({self.pan_offset.x()}, {self.pan_offset.y()})",
            f"Objects: {len(self.selected_objects)} selected"
        ]
        
        y = 15
        for line in info_lines:
            painter.drawText(10, y, line)
            y += 15
            
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events."""
        self.last_mouse_pos = event.position().toPoint()
        
        if event.button() == Qt.MouseButton.LeftButton:
            # Check for object selection
            clicked_object = self._get_object_at_pos(event.position().toPoint())
            if clicked_object:
                if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    # Multi-select
                    if clicked_object in self.selected_objects:
                        self.selected_objects.remove(clicked_object)
                    else:
                        self.selected_objects.append(clicked_object)
                else:
                    # Single select
                    self.selected_objects = [clicked_object]
                self.dragging = True
            else:
                # Clear selection
                self.selected_objects = []
                
            self.selection_changed.emit(self.selected_objects[0] if self.selected_objects else None)
            self.update()
            
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.panning = True
            
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events."""
        current_pos = event.position().toPoint()
        delta = current_pos - self.last_mouse_pos
        
        if self.panning:
            # Pan the view
            self.pan_offset += delta
            self.update()
        elif self.dragging and self.selected_objects:
            # Move selected objects
            world_delta = (delta.x() / self.zoom_level, delta.y() / self.zoom_level)
            
            for obj in self.selected_objects:
                if isinstance(obj, Actor):
                    new_x = obj.transform.position[0] + world_delta[0]
                    new_y = obj.transform.position[1] + world_delta[1]
                    obj.transform.setPosition(new_x, new_y)
                    self.object_moved.emit(obj, world_delta[0], world_delta[1])
                elif isinstance(obj, Widget):
                    obj.rect.x += int(world_delta[0])
                    obj.rect.y += int(world_delta[1])
                    self.object_moved.emit(obj, world_delta[0], world_delta[1])
                    
            self.update()
            
        self.last_mouse_pos = current_pos
        
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release events."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.panning = False
            
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel events for zooming."""
        delta = event.angleDelta().y()
        zoom_factor = 1.2 if delta > 0 else 1.0 / 1.2
        
        # Zoom towards mouse position
        mouse_pos = event.position().toPoint()
        world_pos_before = self.screen_to_world(mouse_pos)
        
        self.zoom_level *= zoom_factor
        self.zoom_level = max(0.1, min(5.0, self.zoom_level))
        
        world_pos_after = self.screen_to_world(mouse_pos)
        world_delta = (world_pos_after[0] - world_pos_before[0], world_pos_after[1] - world_pos_before[1])
        
        self.pan_offset.setX(self.pan_offset.x() + int(world_delta[0] * self.zoom_level))
        self.pan_offset.setY(self.pan_offset.y() + int(world_delta[1] * self.zoom_level))
        
        self.update()
        
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Delete and self.selected_objects:
            # Delete selected objects
            for obj in self.selected_objects:
                if isinstance(obj, Actor) and self.scene:
                    self.scene.remove_actor(obj)
                elif isinstance(obj, Widget) and self.scene and hasattr(self.scene.scene, 'uiManager'):
                    self.scene.scene.uiManager.remove_widget(obj)
                    if obj.parent:
                        obj.parent.remove_child(obj)
                        
            self.selected_objects = []
            self.selection_changed.emit(None)
            self.update()
            
    def _get_object_at_pos(self, pos: QPoint) -> Optional[Any]:
        """Get the object at the given screen position."""
        if not self.scene:
            return None
            
        world_pos = self.screen_to_world(pos)
        
        # Check UI widgets first (they're on top)
        if hasattr(self.scene.scene, 'uiManager'):
            for widget in reversed(self.scene.scene.uiManager.widgets):  # Check from top to bottom
                if self._point_in_widget(world_pos, widget):
                    return widget
                    
        # Check actors
        for actor in reversed(self.scene.scene.actors):  # Check from top to bottom
            if self._point_in_actor(world_pos, actor):
                return actor
                
        return None
        
    def _point_in_actor(self, world_pos: Tuple[float, float], actor: Actor) -> bool:
        """Check if a world position is inside an actor."""
        actor_pos = actor.transform.position
        size = 20  # Actor visual size in world units
        
        return (actor_pos[0] - size/2 <= world_pos[0] <= actor_pos[0] + size/2 and
                actor_pos[1] - size/2 <= world_pos[1] <= actor_pos[1] + size/2)
                
    def _point_in_widget(self, world_pos: Tuple[float, float], widget: Widget) -> bool:
        """Check if a world position is inside a widget."""
        return (widget.rect.x <= world_pos[0] <= widget.rect.x + widget.rect.width and
                widget.rect.y <= world_pos[1] <= widget.rect.y + widget.rect.height)

class SceneViewWidget(QWidget):
    """Main scene view widget with controls."""
    
    selection_changed = pyqtSignal(object)
    
    def __init__(self, scene: EditorScene):
        super().__init__()
        
        self.scene = scene
        self._init_ui()
        self._connect_signals()
        
    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        
        # Controls toolbar
        controls_layout = QHBoxLayout()
        
        # Zoom controls
        controls_layout.addWidget(QLabel("Zoom:"))
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(10, 500)  # 0.1x to 5.0x
        self.zoom_slider.setValue(100)  # 1.0x
        self.zoom_slider.setMaximumWidth(150)
        controls_layout.addWidget(self.zoom_slider)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(50)
        controls_layout.addWidget(self.zoom_label)
        
        # Reset view button
        reset_view_btn = QPushButton("Reset View")
        reset_view_btn.clicked.connect(self._reset_view)
        controls_layout.addWidget(reset_view_btn)
        
        controls_layout.addStretch()
        
        # Grid controls
        self.grid_checkbox = QCheckBox("Show Grid")
        self.grid_checkbox.setChecked(True)
        controls_layout.addWidget(self.grid_checkbox)
        
        self.grid_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.grid_size_slider.setRange(5, 100)
        self.grid_size_slider.setValue(20)
        self.grid_size_slider.setMaximumWidth(100)
        controls_layout.addWidget(QLabel("Grid Size:"))
        controls_layout.addWidget(self.grid_size_slider)
        
        layout.addLayout(controls_layout)
        
        # Scene canvas
        self.canvas = SceneCanvas()
        self.canvas.set_scene(self.scene)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.canvas)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
    def _connect_signals(self):
        """Connect internal signals."""
        self.zoom_slider.valueChanged.connect(self._on_zoom_changed)
        self.grid_checkbox.toggled.connect(self.canvas.toggle_grid)
        self.grid_size_slider.valueChanged.connect(self.canvas.set_grid_size)
        
        self.canvas.selection_changed.connect(self.selection_changed.emit)
        self.canvas.object_moved.connect(self._on_object_moved)
        
    def _on_zoom_changed(self, value: int):
        """Handle zoom slider changes."""
        zoom = value / 100.0
        self.canvas.set_zoom(zoom)
        self.zoom_label.setText(f"{value}%")
        
    def _reset_view(self):
        """Reset the view to default."""
        self.zoom_slider.setValue(100)
        self.canvas.pan_offset = QPoint(0, 0)
        self.canvas.update()
        
    def _on_object_moved(self, obj: Any, dx: float, dy: float):
        """Handle object movement."""
        if self.scene:
            self.scene.mark_dirty()
