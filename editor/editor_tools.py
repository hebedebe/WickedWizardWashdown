"""
Tools widget for various editor utilities and profilers.
"""

import sys
import os
import time
import threading
import psutil
from pathlib import Path
from typing import Dict, List, Optional
import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
    QPushButton, QTextEdit, QTreeWidget, QTreeWidgetItem,
    QProgressBar, QSpinBox, QCheckBox, QGroupBox, QFormLayout,
    QSlider, QComboBox, QListWidget, QSplitter, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject
from PyQt6.QtGui import QFont

# Add engine to path and patch it
sys.path.insert(0, str(Path(__file__).parent.parent))
import editor_dummy

logger = logging.getLogger(__name__)

class PerformanceMonitor(QObject):
    """Performance monitoring system."""
    
    stats_updated = pyqtSignal(dict)  # Performance stats
    
    def __init__(self):
        super().__init__()
        self.monitoring = False
        self.process = psutil.Process()
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_stats)
        
    def start_monitoring(self):
        """Start performance monitoring."""
        self.monitoring = True
        self.timer.start(1000)  # Update every second
        
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring = False
        self.timer.stop()
        
    def _update_stats(self):
        """Update performance statistics."""
        try:
            stats = {
                'cpu_percent': self.process.cpu_percent(),
                'memory_mb': self.process.memory_info().rss / 1024 / 1024,
                'memory_percent': self.process.memory_percent(),
                'threads': self.process.num_threads(),
                'open_files': len(self.process.open_files()),
                'uptime': time.time() - self.process.create_time()
            }
            self.stats_updated.emit(stats)
        except Exception as e:
            logger.error(f"Failed to update performance stats: {e}")

class SceneValidator:
    """Scene validation system."""
    
    @staticmethod
    def validate_scene(scene) -> List[Dict[str, str]]:
        """Validate a scene and return list of issues."""
        issues = []
        
        if not scene:
            return [{"type": "error", "message": "No scene provided"}]
            
        try:
            # Check for actors without names
            for i, actor in enumerate(scene.scene.actors):
                if not actor.name or actor.name.strip() == "":
                    issues.append({
                        "type": "warning",
                        "message": f"Actor at index {i} has no name"
                    })
                    
                # Check for duplicate actor names
                duplicate_names = [a for a in scene.scene.actors if a.name == actor.name]
                if len(duplicate_names) > 1:
                    issues.append({
                        "type": "warning",
                        "message": f"Multiple actors with name '{actor.name}'"
                    })
                    
                # Check for components without required properties
                for j, component in enumerate(actor.components):
                    if not hasattr(component, 'enabled'):
                        issues.append({
                            "type": "error",
                            "message": f"Component {j} on actor '{actor.name}' missing 'enabled' property"
                        })
                        
            # Check UI widgets
            if hasattr(scene.scene, 'uiManager') and scene.scene.uiManager:
                for widget in scene.scene.uiManager.widgets:
                    if not hasattr(widget, 'rect'):
                        issues.append({
                            "type": "error",
                            "message": f"UI widget '{widget.name}' missing rect property"
                        })
                        
                    if widget.rect.width <= 0 or widget.rect.height <= 0:
                        issues.append({
                            "type": "warning",
                            "message": f"UI widget '{widget.name}' has invalid size"
                        })
                        
            # Check lambda scripts for syntax errors
            if hasattr(scene.scene, 'lambda_scripts'):
                for event_type, scripts in scene.scene.lambda_scripts.items():
                    for script in scripts:
                        try:
                            compile(script, '<string>', 'eval')
                        except SyntaxError as e:
                            issues.append({
                                "type": "error",
                                "message": f"Syntax error in {event_type} lambda script: {e}"
                            })
                            
        except Exception as e:
            issues.append({
                "type": "error", 
                "message": f"Validation failed: {str(e)}"
            })
            
        return issues

class ToolsWidget(QWidget):
    """Widget containing various development tools."""
    
    def __init__(self):
        super().__init__()
        
        self.performance_monitor = PerformanceMonitor()
        self.current_scene = None
        
        self._init_ui()
        self._connect_signals()
        
    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        
        # Tools tabs
        self.tab_widget = QTabWidget()
        
        # Performance tab
        self._init_performance_tab()
        
        # Scene validation tab
        self._init_validation_tab()
        
        # Asset browser tab
        self._init_asset_browser_tab()
        
        # Settings tab
        self._init_settings_tab()
        
        layout.addWidget(self.tab_widget)
        
    def _init_performance_tab(self):
        """Initialize the performance monitoring tab."""
        perf_widget = QWidget()
        perf_layout = QVBoxLayout(perf_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.start_monitoring_btn = QPushButton("Start Monitoring")
        self.start_monitoring_btn.clicked.connect(self._start_monitoring)
        controls_layout.addWidget(self.start_monitoring_btn)
        
        self.stop_monitoring_btn = QPushButton("Stop Monitoring")
        self.stop_monitoring_btn.clicked.connect(self._stop_monitoring)
        self.stop_monitoring_btn.setEnabled(False)
        controls_layout.addWidget(self.stop_monitoring_btn)
        
        controls_layout.addStretch()
        perf_layout.addLayout(controls_layout)
        
        # Performance stats
        stats_group = QGroupBox("Performance Statistics")
        stats_layout = QFormLayout(stats_group)
        
        self.cpu_label = QLabel("0%")
        stats_layout.addRow("CPU Usage:", self.cpu_label)
        
        self.memory_label = QLabel("0 MB")
        stats_layout.addRow("Memory Usage:", self.memory_label)
        
        self.threads_label = QLabel("0")
        stats_layout.addRow("Threads:", self.threads_label)
        
        self.files_label = QLabel("0")
        stats_layout.addRow("Open Files:", self.files_label)
        
        self.uptime_label = QLabel("0s")
        stats_layout.addRow("Uptime:", self.uptime_label)
        
        perf_layout.addWidget(stats_group)
        
        # Memory usage graph (simplified)
        self.memory_history = QTextEdit()
        self.memory_history.setMaximumHeight(100)
        self.memory_history.setReadOnly(True)
        self.memory_history.setFont(QFont("Consolas", 8))
        perf_layout.addWidget(QLabel("Memory History:"))
        perf_layout.addWidget(self.memory_history)
        
        perf_layout.addStretch()
        
        self.tab_widget.addTab(perf_widget, "Performance")
        
    def _init_validation_tab(self):
        """Initialize the scene validation tab."""
        validation_widget = QWidget()
        validation_layout = QVBoxLayout(validation_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.validate_btn = QPushButton("Validate Current Scene")
        self.validate_btn.clicked.connect(self._validate_scene)
        controls_layout.addWidget(self.validate_btn)
        
        self.auto_validate_checkbox = QCheckBox("Auto-validate on changes")
        controls_layout.addWidget(self.auto_validate_checkbox)
        
        controls_layout.addStretch()
        validation_layout.addLayout(controls_layout)
        
        # Validation results
        self.validation_tree = QTreeWidget()
        self.validation_tree.setHeaderLabels(["Type", "Message"])
        self.validation_tree.header().setStretchLastSection(True)
        validation_layout.addWidget(self.validation_tree)
        
        self.tab_widget.addTab(validation_widget, "Validation")
        
    def _init_asset_browser_tab(self):
        """Initialize the asset browser tab."""
        asset_widget = QWidget()
        asset_layout = QVBoxLayout(asset_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        refresh_assets_btn = QPushButton("Refresh")
        refresh_assets_btn.clicked.connect(self._refresh_assets)
        controls_layout.addWidget(refresh_assets_btn)
        
        controls_layout.addStretch()
        asset_layout.addLayout(controls_layout)
        
        # Asset tree
        self.asset_tree = QTreeWidget()
        self.asset_tree.setHeaderLabel("Assets")
        asset_layout.addWidget(self.asset_tree)
        
        # Asset info
        self.asset_info = QTextEdit()
        self.asset_info.setMaximumHeight(100)
        self.asset_info.setReadOnly(True)
        asset_layout.addWidget(QLabel("Asset Info:"))
        asset_layout.addWidget(self.asset_info)
        
        self.tab_widget.addTab(asset_widget, "Assets")
        
    def _init_settings_tab(self):
        """Initialize the settings tab."""
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        
        # Editor settings
        editor_group = QGroupBox("Editor Settings")
        editor_layout = QFormLayout(editor_group)
        
        self.auto_save_checkbox = QCheckBox()
        self.auto_save_checkbox.setChecked(True)
        editor_layout.addRow("Auto-save:", self.auto_save_checkbox)
        
        self.auto_save_interval = QSpinBox()
        self.auto_save_interval.setRange(30, 3600)
        self.auto_save_interval.setValue(300)
        self.auto_save_interval.setSuffix(" seconds")
        editor_layout.addRow("Auto-save interval:", self.auto_save_interval)
        
        self.backup_count = QSpinBox()
        self.backup_count.setRange(1, 20)
        self.backup_count.setValue(5)
        editor_layout.addRow("Backup count:", self.backup_count)
        
        settings_layout.addWidget(editor_group)
        
        # Performance settings
        perf_group = QGroupBox("Performance Settings")
        perf_layout = QFormLayout(perf_group)
        
        self.max_undo_steps = QSpinBox()
        self.max_undo_steps.setRange(10, 1000)
        self.max_undo_steps.setValue(100)
        perf_layout.addRow("Max undo steps:", self.max_undo_steps)
        
        self.refresh_rate = QSpinBox()
        self.refresh_rate.setRange(1, 120)
        self.refresh_rate.setValue(60)
        self.refresh_rate.setSuffix(" FPS")
        perf_layout.addRow("Viewport refresh rate:", self.refresh_rate)
        
        settings_layout.addWidget(perf_group)
        
        settings_layout.addStretch()
        
        self.tab_widget.addTab(settings_widget, "Settings")
        
    def _connect_signals(self):
        """Connect internal signals."""
        self.performance_monitor.stats_updated.connect(self._on_stats_updated)
        
    def _start_monitoring(self):
        """Start performance monitoring."""
        self.performance_monitor.start_monitoring()
        self.start_monitoring_btn.setEnabled(False)
        self.stop_monitoring_btn.setEnabled(True)
        
    def _stop_monitoring(self):
        """Stop performance monitoring."""
        self.performance_monitor.stop_monitoring()
        self.start_monitoring_btn.setEnabled(True)
        self.stop_monitoring_btn.setEnabled(False)
        
    def _on_stats_updated(self, stats: Dict):
        """Handle performance stats update."""
        self.cpu_label.setText(f"{stats['cpu_percent']:.1f}%")
        self.memory_label.setText(f"{stats['memory_mb']:.1f} MB ({stats['memory_percent']:.1f}%)")
        self.threads_label.setText(str(stats['threads']))
        self.files_label.setText(str(stats['open_files']))
        
        # Format uptime
        uptime = int(stats['uptime'])
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60
        self.uptime_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # Add to memory history (simplified graph)
        history_text = self.memory_history.toPlainText()
        new_line = f"{time.strftime('%H:%M:%S')}: {stats['memory_mb']:.1f} MB\n"
        
        # Keep only last 10 lines
        lines = history_text.split('\n')
        if len(lines) >= 10:
            lines = lines[-9:]
        lines.append(new_line.strip())
        
        self.memory_history.setPlainText('\n'.join(lines))
        
        # Auto-scroll to bottom
        cursor = self.memory_history.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.memory_history.setTextCursor(cursor)
        
    def _validate_scene(self):
        """Validate the current scene."""
        if not self.current_scene:
            self.validation_tree.clear()
            item = QTreeWidgetItem(["Error", "No scene to validate"])
            self.validation_tree.addTopLevelItem(item)
            return
            
        issues = SceneValidator.validate_scene(self.current_scene)
        
        self.validation_tree.clear()
        
        if not issues:
            item = QTreeWidgetItem(["Info", "Scene validation passed - no issues found"])
            self.validation_tree.addTopLevelItem(item)
        else:
            for issue in issues:
                item = QTreeWidgetItem([issue["type"].capitalize(), issue["message"]])
                
                # Color code by issue type
                if issue["type"] == "error":
                    item.setForeground(0, Qt.GlobalColor.red)
                    item.setForeground(1, Qt.GlobalColor.red)
                elif issue["type"] == "warning":
                    item.setForeground(0, Qt.GlobalColor.yellow)
                    item.setForeground(1, Qt.GlobalColor.yellow)
                    
                self.validation_tree.addTopLevelItem(item)
                
        self.validation_tree.expandAll()
        
    def _refresh_assets(self):
        """Refresh the asset browser."""
        self.asset_tree.clear()
        
        # Find assets directory
        assets_dir = Path.cwd() / "assets"
        if not assets_dir.exists():
            item = QTreeWidgetItem(["No assets directory found"])
            self.asset_tree.addTopLevelItem(item)
            return
            
        # Recursively add asset files
        self._add_directory_to_tree(assets_dir, None)
        
        self.asset_tree.expandAll()
        
    def _add_directory_to_tree(self, directory: Path, parent_item: Optional[QTreeWidgetItem]):
        """Recursively add directory contents to the asset tree."""
        try:
            for item_path in sorted(directory.iterdir()):
                if item_path.name.startswith('.'):
                    continue  # Skip hidden files
                    
                if parent_item:
                    tree_item = QTreeWidgetItem(parent_item)
                else:
                    tree_item = QTreeWidgetItem(self.asset_tree)
                    
                tree_item.setText(0, item_path.name)
                tree_item.setData(0, Qt.ItemDataRole.UserRole, str(item_path))
                
                if item_path.is_dir():
                    tree_item.setText(0, f"📁 {item_path.name}")
                    self._add_directory_to_tree(item_path, tree_item)
                else:
                    # Add file icon based on extension
                    ext = item_path.suffix.lower()
                    if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                        tree_item.setText(0, f"🖼️ {item_path.name}")
                    elif ext in ['.wav', '.mp3', '.ogg']:
                        tree_item.setText(0, f"🔊 {item_path.name}")
                    elif ext in ['.py']:
                        tree_item.setText(0, f"🐍 {item_path.name}")
                    elif ext in ['.json', '.scene']:
                        tree_item.setText(0, f"📄 {item_path.name}")
                    else:
                        tree_item.setText(0, f"📄 {item_path.name}")
                        
        except Exception as e:
            logger.error(f"Failed to add directory {directory} to tree: {e}")
            
    def set_current_scene(self, scene):
        """Set the current scene for validation."""
        self.current_scene = scene
        
        # Auto-validate if enabled
        if self.auto_validate_checkbox.isChecked():
            self._validate_scene()
            
    def get_settings(self) -> Dict:
        """Get current editor settings."""
        return {
            "auto_save": self.auto_save_checkbox.isChecked(),
            "auto_save_interval": self.auto_save_interval.value(),
            "backup_count": self.backup_count.value(),
            "max_undo_steps": self.max_undo_steps.value(),
            "refresh_rate": self.refresh_rate.value()
        }
        
    def set_settings(self, settings: Dict):
        """Set editor settings."""
        self.auto_save_checkbox.setChecked(settings.get("auto_save", True))
        self.auto_save_interval.setValue(settings.get("auto_save_interval", 300))
        self.backup_count.setValue(settings.get("backup_count", 5))
        self.max_undo_steps.setValue(settings.get("max_undo_steps", 100))
        self.refresh_rate.setValue(settings.get("refresh_rate", 60))
