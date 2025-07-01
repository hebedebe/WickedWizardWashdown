"""
Inspector widget for editing properties of selected objects.
"""

import sys
from pathlib import Path
from typing import Any, Optional, Dict, List
import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel, 
    QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton,
    QColorDialog, QGroupBox, QFormLayout, QComboBox, QTextEdit,
    QSlider, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPalette

# Add engine to path and patch it
sys.path.insert(0, str(Path(__file__).parent.parent))
import editor_dummy

from editor_utils import get_property_info, serialize_value, deserialize_value
from engine.actor.actor import Actor
from engine.ui.widget import Widget
from engine.component.component import Component

logger = logging.getLogger(__name__)

class PropertyWidget(QWidget):
    """Base class for property editing widgets."""
    
    value_changed = pyqtSignal(object)  # new_value
    
    def __init__(self, property_name: str, property_info: Dict[str, Any]):
        super().__init__()
        self.property_name = property_name
        self.property_info = property_info
        self.updating = False
        
    def set_value(self, value: Any):
        """Set the widget value."""
        raise NotImplementedError
        
    def get_value(self) -> Any:
        """Get the widget value."""
        raise NotImplementedError

class StringPropertyWidget(PropertyWidget):
    """Widget for editing string properties."""
    
    def __init__(self, property_name: str, property_info: Dict[str, Any]):
        super().__init__(property_name, property_info)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.line_edit = QLineEdit()
        self.line_edit.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.line_edit)
        
    def set_value(self, value: Any):
        if not self.updating:
            self.updating = True
            self.line_edit.setText(str(value) if value is not None else "")
            self.updating = False
            
    def get_value(self) -> str:
        return self.line_edit.text()
        
    def _on_text_changed(self):
        if not self.updating:
            self.value_changed.emit(self.get_value())

class IntPropertyWidget(PropertyWidget):
    """Widget for editing integer properties."""
    
    def __init__(self, property_name: str, property_info: Dict[str, Any]):
        super().__init__(property_name, property_info)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.spin_box = QSpinBox()
        self.spin_box.setRange(
            property_info.get("min", -999999), 
            property_info.get("max", 999999)
        )
        self.spin_box.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.spin_box)
        
    def set_value(self, value: Any):
        if not self.updating:
            self.updating = True
            self.spin_box.setValue(int(value) if value is not None else 0)
            self.updating = False
            
    def get_value(self) -> int:
        return self.spin_box.value()
        
    def _on_value_changed(self):
        if not self.updating:
            self.value_changed.emit(self.get_value())

class FloatPropertyWidget(PropertyWidget):
    """Widget for editing float properties."""
    
    def __init__(self, property_name: str, property_info: Dict[str, Any]):
        super().__init__(property_name, property_info)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.spin_box = QDoubleSpinBox()
        self.spin_box.setRange(
            property_info.get("min", -999999.0), 
            property_info.get("max", 999999.0)
        )
        self.spin_box.setDecimals(3)
        self.spin_box.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.spin_box)
        
    def set_value(self, value: Any):
        if not self.updating:
            self.updating = True
            self.spin_box.setValue(float(value) if value is not None else 0.0)
            self.updating = False
            
    def get_value(self) -> float:
        return self.spin_box.value()
        
    def _on_value_changed(self):
        if not self.updating:
            self.value_changed.emit(self.get_value())

class BoolPropertyWidget(PropertyWidget):
    """Widget for editing boolean properties."""
    
    def __init__(self, property_name: str, property_info: Dict[str, Any]):
        super().__init__(property_name, property_info)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.check_box = QCheckBox()
        self.check_box.toggled.connect(self._on_toggled)
        layout.addWidget(self.check_box)
        
    def set_value(self, value: Any):
        if not self.updating:
            self.updating = True
            self.check_box.setChecked(bool(value) if value is not None else False)
            self.updating = False
            
    def get_value(self) -> bool:
        return self.check_box.isChecked()
        
    def _on_toggled(self):
        if not self.updating:
            self.value_changed.emit(self.get_value())

class Vector2PropertyWidget(PropertyWidget):
    """Widget for editing Vector2 properties."""
    
    def __init__(self, property_name: str, property_info: Dict[str, Any]):
        super().__init__(property_name, property_info)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(QLabel("X:"))
        self.x_spin = QDoubleSpinBox()
        self.x_spin.setRange(-999999.0, 999999.0)
        self.x_spin.setDecimals(2)
        self.x_spin.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.x_spin)
        
        layout.addWidget(QLabel("Y:"))
        self.y_spin = QDoubleSpinBox()
        self.y_spin.setRange(-999999.0, 999999.0)
        self.y_spin.setDecimals(2)
        self.y_spin.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.y_spin)
        
    def set_value(self, value: Any):
        if not self.updating:
            self.updating = True
            if value is not None:
                if hasattr(value, 'x') and hasattr(value, 'y'):
                    self.x_spin.setValue(float(value.x))
                    self.y_spin.setValue(float(value.y))
                elif isinstance(value, (list, tuple)) and len(value) >= 2:
                    self.x_spin.setValue(float(value[0]))
                    self.y_spin.setValue(float(value[1]))
            else:
                self.x_spin.setValue(0.0)
                self.y_spin.setValue(0.0)
            self.updating = False
            
    def get_value(self):
        import pygame
        return pygame.Vector2(self.x_spin.value(), self.y_spin.value())
        
    def _on_value_changed(self):
        if not self.updating:
            self.value_changed.emit(self.get_value())

class ColorPropertyWidget(PropertyWidget):
    """Widget for editing Color properties."""
    
    def __init__(self, property_name: str, property_info: Dict[str, Any]):
        super().__init__(property_name, property_info)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.color_button = QPushButton()
        self.color_button.setFixedSize(50, 25)
        self.color_button.clicked.connect(self._choose_color)
        layout.addWidget(self.color_button)
        
        self.color_label = QLabel("(255, 255, 255, 255)")
        layout.addWidget(self.color_label)
        
        self.current_color = QColor(255, 255, 255, 255)
        self._update_button_color()
        
    def set_value(self, value: Any):
        if not self.updating:
            self.updating = True
            if value is not None:
                if hasattr(value, 'r') and hasattr(value, 'g') and hasattr(value, 'b'):
                    r = getattr(value, 'r', 255)
                    g = getattr(value, 'g', 255)
                    b = getattr(value, 'b', 255)
                    a = getattr(value, 'a', 255)
                    self.current_color = QColor(r, g, b, a)
                elif isinstance(value, (list, tuple)) and len(value) >= 3:
                    r, g, b = value[0], value[1], value[2]
                    a = value[3] if len(value) > 3 else 255
                    self.current_color = QColor(r, g, b, a)
            else:
                self.current_color = QColor(255, 255, 255, 255)
            self._update_button_color()
            self.updating = False
            
    def get_value(self):
        import pygame
        return pygame.Color(
            self.current_color.red(),
            self.current_color.green(),
            self.current_color.blue(),
            self.current_color.alpha()
        )
        
    def _choose_color(self):
        color = QColorDialog.getColor(self.current_color, self, "Choose Color", 
                                    QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if color.isValid():
            self.current_color = color
            self._update_button_color()
            if not self.updating:
                self.value_changed.emit(self.get_value())
                
    def _update_button_color(self):
        self.color_button.setStyleSheet(
            f"background-color: rgba({self.current_color.red()}, "
            f"{self.current_color.green()}, {self.current_color.blue()}, "
            f"{self.current_color.alpha()})"
        )
        self.color_label.setText(
            f"({self.current_color.red()}, {self.current_color.green()}, "
            f"{self.current_color.blue()}, {self.current_color.alpha()})"
        )

class RectPropertyWidget(PropertyWidget):
    """Widget for editing Rect properties."""
    
    def __init__(self, property_name: str, property_info: Dict[str, Any]):
        super().__init__(property_name, property_info)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Position row
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("X:"))
        self.x_spin = QDoubleSpinBox()
        self.x_spin.setRange(-999999.0, 999999.0)
        self.x_spin.valueChanged.connect(self._on_value_changed)
        pos_layout.addWidget(self.x_spin)
        
        pos_layout.addWidget(QLabel("Y:"))
        self.y_spin = QDoubleSpinBox()
        self.y_spin.setRange(-999999.0, 999999.0)
        self.y_spin.valueChanged.connect(self._on_value_changed)
        pos_layout.addWidget(self.y_spin)
        
        layout.addLayout(pos_layout)
        
        # Size row
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("W:"))
        self.w_spin = QDoubleSpinBox()
        self.w_spin.setRange(0.0, 999999.0)
        self.w_spin.valueChanged.connect(self._on_value_changed)
        size_layout.addWidget(self.w_spin)
        
        size_layout.addWidget(QLabel("H:"))
        self.h_spin = QDoubleSpinBox()
        self.h_spin.setRange(0.0, 999999.0)
        self.h_spin.valueChanged.connect(self._on_value_changed)
        size_layout.addWidget(self.h_spin)
        
        layout.addLayout(size_layout)
        
    def set_value(self, value: Any):
        if not self.updating:
            self.updating = True
            if value is not None:
                if hasattr(value, 'x') and hasattr(value, 'y') and hasattr(value, 'width') and hasattr(value, 'height'):
                    self.x_spin.setValue(float(value.x))
                    self.y_spin.setValue(float(value.y))
                    self.w_spin.setValue(float(value.width))
                    self.h_spin.setValue(float(value.height))
                elif isinstance(value, (list, tuple)) and len(value) >= 4:
                    self.x_spin.setValue(float(value[0]))
                    self.y_spin.setValue(float(value[1]))
                    self.w_spin.setValue(float(value[2]))
                    self.h_spin.setValue(float(value[3]))
            else:
                self.x_spin.setValue(0.0)
                self.y_spin.setValue(0.0)
                self.w_spin.setValue(100.0)
                self.h_spin.setValue(50.0)
            self.updating = False
            
    def get_value(self):
        import pygame
        return pygame.Rect(
            int(self.x_spin.value()),
            int(self.y_spin.value()),
            int(self.w_spin.value()),
            int(self.h_spin.value())
        )
        
    def _on_value_changed(self):
        if not self.updating:
            self.value_changed.emit(self.get_value())

class LambdaScriptWidget(PropertyWidget):
    """Widget for editing lambda script properties."""
    
    def __init__(self, property_name: str, property_info: Dict[str, Any]):
        super().__init__(property_name, property_info)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.text_edit = QTextEdit()
        self.text_edit.setMaximumHeight(100)
        self.text_edit.setPlaceholderText("Enter lambda expression or function body...")
        self.text_edit.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.text_edit)
        
    def set_value(self, value: Any):
        if not self.updating:
            self.updating = True
            self.text_edit.setPlainText(str(value) if value is not None else "")
            self.updating = False
            
    def get_value(self) -> str:
        return self.text_edit.toPlainText()
        
    def _on_text_changed(self):
        if not self.updating:
            self.value_changed.emit(self.get_value())

class InspectorWidget(QWidget):
    """Widget for inspecting and editing object properties."""
    
    property_changed = pyqtSignal(object, str, object)  # obj, property_name, new_value
    
    def __init__(self):
        super().__init__()
        
        self.current_object: Optional[Any] = None
        self.property_widgets: Dict[str, PropertyWidget] = {}
        
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        
        # Title
        self.title_label = QLabel("Inspector")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.title_label)
        
        # Scroll area for properties
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.properties_widget = QWidget()
        self.properties_layout = QVBoxLayout(self.properties_widget)
        self.properties_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area.setWidget(self.properties_widget)
        layout.addWidget(self.scroll_area)
        
    def set_object(self, obj: Any):
        """Set the object to inspect."""
        self.current_object = obj
        self._refresh_properties()
        
    def _refresh_properties(self):
        """Refresh the properties display."""
        # Clear existing widgets
        for widget in self.property_widgets.values():
            widget.deleteLater()
        self.property_widgets.clear()
        
        # Clear layout
        while self.properties_layout.count():
            child = self.properties_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        if not self.current_object:
            self.title_label.setText("Inspector")
            return
            
        # Set title
        if hasattr(self.current_object, 'name'):
            self.title_label.setText(f"Inspector - {self.current_object.name}")
        else:
            self.title_label.setText(f"Inspector - {self.current_object.__class__.__name__}")
            
        # Add basic properties
        if isinstance(self.current_object, Actor):
            self._add_actor_properties()
        else:
            self._add_basic_properties()
        
        # Add component properties for actors
        if isinstance(self.current_object, Actor):
            self._add_component_properties()
            
        # Add lambda scripts
        self._add_lambda_scripts()
        
    def _add_basic_properties(self):
        """Add basic object properties."""
        basic_group = QGroupBox("Basic Properties")
        basic_layout = QFormLayout(basic_group)
        
        # Get object properties
        for attr_name in dir(self.current_object):
            if (not attr_name.startswith('_') and 
                not callable(getattr(self.current_object, attr_name)) and
                attr_name not in ['components', 'children', 'parent', 'scene', 'actor']):
                
                try:
                    value = getattr(self.current_object, attr_name)
                    prop_info = get_property_info(self.current_object, attr_name)
                    
                    if prop_info:
                        widget = self._create_property_widget(attr_name, prop_info, value)
                        if widget:
                            widget.value_changed.connect(
                                lambda new_val, name=attr_name: self._on_property_changed(name, new_val)
                            )
                            self.property_widgets[attr_name] = widget
                            basic_layout.addRow(attr_name, widget)
                            
                except Exception as e:
                    logger.warning(f"Failed to add property {attr_name}: {e}")
                    
        self.properties_layout.addWidget(basic_group)
        
    def _add_component_properties(self):
        """Add component properties for actors."""
        if not isinstance(self.current_object, Actor):
            return
            
        for i, component in enumerate(self.current_object.components):
            comp_group = QGroupBox(f"{component.__class__.__name__}")
            comp_layout = QFormLayout(comp_group)
            
            # Add component properties
            for attr_name in dir(component):
                if (not attr_name.startswith('_') and 
                    not callable(getattr(component, attr_name)) and
                    attr_name not in ['actor', 'enabled']):
                    
                    try:
                        value = getattr(component, attr_name)
                        prop_info = get_property_info(component, attr_name)
                        
                        if prop_info:
                            widget = self._create_property_widget(attr_name, prop_info, value)
                            if widget:
                                widget.value_changed.connect(
                                    lambda new_val, comp=component, name=attr_name: 
                                    self._on_component_property_changed(comp, name, new_val)
                                )
                                prop_key = f"component_{i}_{attr_name}"
                                self.property_widgets[prop_key] = widget
                                comp_layout.addRow(attr_name, widget)
                                
                    except Exception as e:
                        logger.warning(f"Failed to add component property {attr_name}: {e}")
                        
            self.properties_layout.addWidget(comp_group)
            
    def _add_actor_properties(self):
        """Add specialized Actor properties with better handling."""
        if not isinstance(self.current_object, Actor):
            return
            
        # Actor Basic Properties
        actor_group = QGroupBox("Actor Properties")
        actor_layout = QFormLayout(actor_group)
        
        # Name property
        name_widget = StringPropertyWidget("name", {"type": str})
        name_widget.set_value(self.current_object.name)
        name_widget.value_changed.connect(lambda val: self._on_property_changed("name", val))
        self.property_widgets["name"] = name_widget
        actor_layout.addRow("Name", name_widget)
        
        # Tags property (as comma-separated string)
        tags_widget = StringPropertyWidget("tags", {"type": str})
        tags_str = ", ".join(self.current_object.tags) if self.current_object.tags else ""
        tags_widget.set_value(tags_str)
        tags_widget.value_changed.connect(lambda val: self._on_tags_changed(val))
        self.property_widgets["tags"] = tags_widget
        actor_layout.addRow("Tags", tags_widget)
        
        self.properties_layout.addWidget(actor_group)
        
        # Transform Properties
        transform_group = QGroupBox("Transform")
        transform_layout = QFormLayout(transform_group)
        
        # Position
        position_widget = Vector2PropertyWidget("position", {"type": tuple})
        position_widget.set_value(self.current_object.transform.position)
        position_widget.value_changed.connect(lambda val: self._on_transform_changed("position", val))
        self.property_widgets["transform.position"] = position_widget
        transform_layout.addRow("Position", position_widget)
        
        # Rotation
        rotation_widget = FloatPropertyWidget("rotation", {"type": float})
        rotation_widget.set_value(self.current_object.transform.rotation)
        rotation_widget.value_changed.connect(lambda val: self._on_transform_changed("rotation", val))
        self.property_widgets["transform.rotation"] = rotation_widget
        transform_layout.addRow("Rotation", rotation_widget)
        
        # Scale
        scale_widget = Vector2PropertyWidget("scale", {"type": tuple})
        scale_widget.set_value(self.current_object.transform.scale)
        scale_widget.value_changed.connect(lambda val: self._on_transform_changed("scale", val))
        self.property_widgets["transform.scale"] = scale_widget
        transform_layout.addRow("Scale", scale_widget)
        
        self.properties_layout.addWidget(transform_group)
        
    def _add_lambda_scripts(self):
        """Add lambda script editing for widgets."""
        if not hasattr(self.current_object, 'lambda_scripts'):
            return
            
        lambda_group = QGroupBox("Lambda Scripts")
        lambda_layout = QFormLayout(lambda_group)
        
        # Common event types for widgets
        event_types = ['onClick', 'onHover', 'onFocus', 'onBlur', 'onUpdate']
        
        for event_type in event_types:
            script = self.current_object.lambda_scripts.get(event_type, "")
            prop_info = {"type": "lambda", "widget": "lambda"}
            
            widget = LambdaScriptWidget(event_type, prop_info)
            widget.set_value(script)
            widget.value_changed.connect(
                lambda new_val, event=event_type: self._on_lambda_changed(event, new_val)
            )
            
            self.property_widgets[f"lambda_{event_type}"] = widget
            lambda_layout.addRow(event_type, widget)
            
        self.properties_layout.addWidget(lambda_group)
        
    def _create_property_widget(self, property_name: str, property_info: Dict[str, Any], value: Any) -> Optional[PropertyWidget]:
        """Create a property editing widget."""
        prop_type = property_info.get("type", "str")
        widget_type = property_info.get("widget", "")
        
        try:
            if widget_type == "checkbox" or prop_type == "bool":
                return BoolPropertyWidget(property_name, property_info)
            elif widget_type == "spinbox" or prop_type == "int":
                return IntPropertyWidget(property_name, property_info)
            elif prop_type == "float":
                return FloatPropertyWidget(property_name, property_info)
            elif widget_type == "vector2":
                return Vector2PropertyWidget(property_name, property_info)
            elif widget_type == "color":
                return ColorPropertyWidget(property_name, property_info)
            elif widget_type == "rect":
                return RectPropertyWidget(property_name, property_info)
            elif widget_type == "lambda":
                return LambdaScriptWidget(property_name, property_info)
            else:
                return StringPropertyWidget(property_name, property_info)
                
        except Exception as e:
            logger.error(f"Failed to create property widget for {property_name}: {e}")
            return None
            
    def _on_property_changed(self, property_name: str, new_value: Any):
        """Handle property changes."""
        if self.current_object:
            self.property_changed.emit(self.current_object, property_name, new_value)
            
    def _on_component_property_changed(self, component: Component, property_name: str, new_value: Any):
        """Handle component property changes."""
        self.property_changed.emit(component, property_name, new_value)
        
    def _on_lambda_changed(self, event_type: str, new_script: str):
        """Handle lambda script changes."""
        if hasattr(self.current_object, 'lambda_scripts'):
            self.current_object.lambda_scripts[event_type] = new_script
            # Emit property changed signal to mark scene as dirty
            self.property_changed.emit(self.current_object, 'lambda_scripts', self.current_object.lambda_scripts)
                
    def _on_tags_changed(self, tags_str: str):
        """Handle tags property change."""
        if self.current_object:
            # Parse comma-separated tags
            tags = set()
            if tags_str.strip():
                tags = {tag.strip() for tag in tags_str.split(",") if tag.strip()}
            self.current_object.tags = tags
            self.property_changed.emit(self.current_object, "tags", tags)
    
    def _on_transform_changed(self, property_name: str, new_value):
        """Handle transform property changes."""
        if self.current_object and hasattr(self.current_object, 'transform'):
            if property_name == "position":
                self.current_object.transform.position = new_value
            elif property_name == "rotation":
                self.current_object.transform.rotation = new_value
            elif property_name == "scale":
                self.current_object.transform.scale = new_value
            self.property_changed.emit(self.current_object, f"transform.{property_name}", new_value)
