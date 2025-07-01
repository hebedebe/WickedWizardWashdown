"""
Console widget for displaying logs and running Python commands.
"""

import sys
import io
import traceback
from pathlib import Path
from typing import Optional, List
import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QComboBox, QSplitter, QTabWidget, QLabel,
    QCheckBox, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject, QTimer
from PyQt6.QtGui import QTextCursor, QFont, QColor, QTextCharFormat

# Add engine to path and patch it
sys.path.insert(0, str(Path(__file__).parent.parent))
import editor_dummy

class LogHandler(logging.Handler):
    """Custom log handler that emits signals for the console."""
    
    def __init__(self):
        super().__init__()
        self.log_signal = None  # Will be set by ConsoleWidget
        
    def emit(self, record):
        if self.log_signal and hasattr(self.log_signal, 'emit'):
            msg = self.format(record)
            self.log_signal.emit(record.levelname, msg)

class PythonInterpreter(QObject):
    """Python interpreter for executing commands."""
    
    output_signal = pyqtSignal(str, str)  # output_type, text
    
    def __init__(self):
        super().__init__()
        self.globals_dict = {}
        self.locals_dict = {}
        self._setup_environment()
        
    def _setup_environment(self):
        """Set up the Python environment with useful imports."""
        setup_code = """
import sys
import os
import math
import json
from pathlib import Path

# Add engine to path
sys.path.insert(0, str(Path.cwd()))

# Import common engine modules
try:
    from engine.actor.actor import Actor, Transform
    from engine.component.component import Component
    from engine.ui.widget import Widget
    from engine.scene.scene import Scene
    print("Engine modules imported successfully")
except Exception as e:
    print(f"Warning: Could not import engine modules: {e}")

# Helper functions
def help_editor():
    print("Scene Editor Python Console")
    print("Available variables:")
    print("  scene - Current scene (if any)")
    print("  project - Current project (if any)")
    print("  editor - Main editor window")
    print("")
    print("Available functions:")
    print("  help_editor() - Show this help")
    print("  clear() - Clear console")
    print("")
    print("Engine classes available:")
    print("  Actor, Transform, Component, Widget, Scene")

def clear():
    # This will be connected to actual clear function
    pass
"""
        
        try:
            exec(setup_code, self.globals_dict, self.locals_dict)
            self.output_signal.emit("info", "Python environment initialized\n")
        except Exception as e:
            self.output_signal.emit("error", f"Failed to initialize Python environment: {e}\n")
            
    def execute(self, code: str):
        """Execute Python code."""
        if not code.strip():
            return
            
        self.output_signal.emit("input", f">>> {code}\n")
        
        # Redirect stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        captured_output = io.StringIO()
        captured_errors = io.StringIO()
        
        sys.stdout = captured_output
        sys.stderr = captured_errors
        
        try:
            # Try to evaluate as expression first
            try:
                result = eval(code, self.globals_dict, self.locals_dict)
                if result is not None:
                    self.output_signal.emit("output", f"{result}\n")
            except SyntaxError:
                # If it's not an expression, execute as statement
                exec(code, self.globals_dict, self.locals_dict)
                
        except Exception as e:
            error_msg = f"Error: {str(e)}\n"
            if hasattr(e, '__traceback__'):
                tb_lines = traceback.format_tb(e.__traceback__)
                # Filter out internal frames
                filtered_tb = [line for line in tb_lines if '<string>' in line or 'editor' in line]
                if filtered_tb:
                    error_msg += ''.join(filtered_tb)
            self.output_signal.emit("error", error_msg)
            
        finally:
            # Restore stdout and stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
            # Get captured output
            stdout_content = captured_output.getvalue()
            stderr_content = captured_errors.getvalue()
            
            if stdout_content:
                self.output_signal.emit("output", stdout_content)
            if stderr_content:
                self.output_signal.emit("error", stderr_content)
                
    def update_context(self, **kwargs):
        """Update the interpreter context with new variables."""
        self.locals_dict.update(kwargs)

class ConsoleWidget(QWidget):
    """Console widget for logs and Python interaction."""
    
    log_message_signal = pyqtSignal(str, str)  # level, message
    
    def __init__(self):
        super().__init__()
        
        self.log_handler = LogHandler()
        self.log_handler.log_signal = self.log_message_signal
        
        self.python_interpreter = PythonInterpreter()
        self.command_history: List[str] = []
        self.history_index = -1
        
        self._init_ui()
        self._connect_signals()
        self._setup_logging()
        
    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        
        # Tab widget for different console modes
        self.tab_widget = QTabWidget()
        
        # Logs tab
        logs_widget = QWidget()
        logs_layout = QVBoxLayout(logs_widget)
        
        # Log controls
        log_controls = QHBoxLayout()
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_level_combo.setCurrentText("INFO")
        log_controls.addWidget(QLabel("Log Level:"))
        log_controls.addWidget(self.log_level_combo)
        
        self.auto_scroll_checkbox = QCheckBox("Auto Scroll")
        self.auto_scroll_checkbox.setChecked(True)
        log_controls.addWidget(self.auto_scroll_checkbox)
        
        clear_logs_btn = QPushButton("Clear")
        clear_logs_btn.clicked.connect(self._clear_logs)
        log_controls.addWidget(clear_logs_btn)
        
        log_controls.addStretch()
        
        logs_layout.addLayout(log_controls)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 9))
        logs_layout.addWidget(self.log_display)
        
        self.tab_widget.addTab(logs_widget, "Logs")
        
        # Python console tab
        python_widget = QWidget()
        python_layout = QVBoxLayout(python_widget)
        
        # Python output display
        self.python_display = QTextEdit()
        self.python_display.setReadOnly(True)
        self.python_display.setFont(QFont("Consolas", 9))
        self.python_display.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")
        python_layout.addWidget(self.python_display)
        
        # Python input
        input_layout = QHBoxLayout()
        
        self.python_input = QLineEdit()
        self.python_input.setFont(QFont("Consolas", 9))
        self.python_input.setPlaceholderText("Enter Python command...")
        input_layout.addWidget(self.python_input)
        
        execute_btn = QPushButton("Execute")
        execute_btn.clicked.connect(self._execute_python)
        input_layout.addWidget(execute_btn)
        
        clear_python_btn = QPushButton("Clear")
        clear_python_btn.clicked.connect(self._clear_python)
        input_layout.addWidget(clear_python_btn)
        
        python_layout.addLayout(input_layout)
        
        self.tab_widget.addTab(python_widget, "Python")
        
        layout.addWidget(self.tab_widget)
        
    def _connect_signals(self):
        """Connect internal signals."""
        self.python_input.returnPressed.connect(self._execute_python)
        self.python_interpreter.output_signal.connect(self._on_python_output)
        self.log_level_combo.currentTextChanged.connect(self._on_log_level_changed)
        self.log_message_signal.connect(self._on_log_message)
        
    def _setup_logging(self):
        """Set up logging to capture engine logs."""
        # Set up formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.log_handler.setFormatter(formatter)
        
        # Add handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(self.log_handler)
        
        # Set initial log level
        self._on_log_level_changed("INFO")
        
    def _on_log_message(self, level: str, message: str):
        """Handle log messages."""
        # Color code by level
        color = "#ffffff"  # Default white
        if level == "DEBUG":
            color = "#888888"  # Gray
        elif level == "INFO":
            color = "#00ff00"  # Green
        elif level == "WARNING":
            color = "#ffff00"  # Yellow
        elif level == "ERROR":
            color = "#ff4444"  # Red
        elif level == "CRITICAL":
            color = "#ff0000"  # Bright red
            
        # Format message with color
        formatted_message = f'<span style="color: {color}">{message}</span>'
        
        # Add to log display
        self.log_display.append(formatted_message)
        
        # Auto scroll if enabled
        if self.auto_scroll_checkbox.isChecked():
            cursor = self.log_display.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.log_display.setTextCursor(cursor)
            
    def _on_log_level_changed(self, level: str):
        """Handle log level changes."""
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        self.log_handler.setLevel(level_map.get(level, logging.INFO))
        
    def _clear_logs(self):
        """Clear the log display."""
        self.log_display.clear()
        
    def _execute_python(self):
        """Execute Python command."""
        command = self.python_input.text().strip()
        if not command:
            return
            
        # Add to history
        if command not in self.command_history:
            self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        # Clear input
        self.python_input.clear()
        
        # Execute command
        self.python_interpreter.execute(command)
        
    def _on_python_output(self, output_type: str, text: str):
        """Handle Python interpreter output."""
        # Color code by output type
        color = "#ffffff"  # Default white
        if output_type == "input":
            color = "#00ffff"  # Cyan
        elif output_type == "output":
            color = "#ffffff"  # White
        elif output_type == "error":
            color = "#ff4444"  # Red
        elif output_type == "info":
            color = "#00ff00"  # Green
            
        # Format message with color
        formatted_text = f'<span style="color: {color}">{text}</span>'
        
        # Add to Python display
        cursor = self.python_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(formatted_text.replace('\n', '<br>'))
        self.python_display.setTextCursor(cursor)
        
        # Auto scroll
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.python_display.setTextCursor(cursor)
        
    def _clear_python(self):
        """Clear the Python console."""
        self.python_display.clear()
        self.python_interpreter.output_signal.emit("info", "Console cleared\n")
        
    def keyPressEvent(self, event):
        """Handle key press events for command history."""
        if self.python_input.hasFocus():
            if event.key() == Qt.Key.Key_Up:
                # Previous command
                if self.command_history and self.history_index > 0:
                    self.history_index -= 1
                    self.python_input.setText(self.command_history[self.history_index])
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Down:
                # Next command
                if self.command_history and self.history_index < len(self.command_history) - 1:
                    self.history_index += 1
                    self.python_input.setText(self.command_history[self.history_index])
                elif self.history_index >= len(self.command_history) - 1:
                    self.history_index = len(self.command_history)
                    self.python_input.clear()
                event.accept()
                return
                
        super().keyPressEvent(event)
        
    def update_context(self, **kwargs):
        """Update the Python interpreter context."""
        self.python_interpreter.update_context(**kwargs)
        
        # Also update the clear function
        def clear_console():
            self._clear_python()
        self.python_interpreter.locals_dict['clear'] = clear_console
        
    def log_message(self, level: str, message: str):
        """Log a message programmatically."""
        logger = logging.getLogger("Editor")
        level_map = {
            "DEBUG": logger.debug,
            "INFO": logger.info,
            "WARNING": logger.warning,
            "ERROR": logger.error,
            "CRITICAL": logger.critical
        }
        log_func = level_map.get(level.upper(), logger.info)
        log_func(message)
