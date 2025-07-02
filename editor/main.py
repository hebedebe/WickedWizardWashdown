#!/usr/bin/env python3
"""
Wicked Wizard Washdown Scene Editor
A comprehensive GUI editor for creating and editing game scenes.
"""

import sys
import os
import traceback
import logging
from pathlib import Path
import pygame

# Add the parent directory to sys.path so we can import the engine
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QDir, qInstallMessageHandler, QtMsgType
from PyQt6.QtGui import QIcon

import qdarktheme

from editor_main_window import EditorMainWindow
from editor_utils import setup_logging, show_error_with_logging

def qt_message_handler(mode, context, message):
    """Custom Qt message handler to redirect Qt logs to our logging system."""
    import logging
    logger = logging.getLogger('Qt')
    
    if mode == QtMsgType.QtDebugMsg:
        logger.debug(message)
    elif mode == QtMsgType.QtWarningMsg:
        logger.warning(message)
    elif mode == QtMsgType.QtCriticalMsg:
        logger.error(message)
    elif mode == QtMsgType.QtFatalMsg:
        logger.critical(message)

def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Global exception handler to log all unhandled exceptions."""
    if issubclass(exc_type, KeyboardInterrupt):
        # Handle Ctrl+C gracefully
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    error_msg = f"Unhandled exception: {exc_type.__name__}: {exc_value}\n"
    error_msg += "".join(traceback.format_tb(exc_traceback))
    
    # Log to file
    logging.getLogger('global_exceptions').critical(error_msg)
    
    # Show popup if possible
    try:
        show_error_with_logging("Unhandled Exception", error_msg)
    except:
        # Fallback to console if GUI is not available
        print(f"CRITICAL ERROR: {error_msg}", file=sys.stderr)

def main():
    """Main entry point for the scene editor."""
    try:
        # Set up logging
        setup_logging()
        
        # Install global exception handler
        sys.excepthook = global_exception_handler
        
        # Create the QApplication
        app = QApplication(sys.argv)

        # qdarktheme.setup_theme()
        # app.setStyle("fusion")
        app.setStyle("windows")

        app.setApplicationName("Wicked Wizard Washdown Scene Editor")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("WickedWizard")
        
        # Install Qt message handler
        qInstallMessageHandler(qt_message_handler)
        
        # Set application icon if available
        icon_path = parent_dir / "assets" / "images" / "editor_icon.png"
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
        
        # Create and show the main window
        main_window = EditorMainWindow()
        main_window.show()
        
        # Start the event loop
        return app.exec()
        
    except Exception as e:
        error_msg = f"Failed to start Scene Editor: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        
        # Log the error and show popup
        show_error_with_logging("Scene Editor Startup Error", error_msg)
        
        return 1

if __name__ == "__main__":
    pygame.init()
    
    # Install the global exception handler
    sys.excepthook = global_exception_handler
    
    sys.exit(main())
