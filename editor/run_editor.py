#!/usr/bin/env python3
"""
Test script to run the Scene Editor
"""

import sys
import os

# Add the parent directory to the path to import engine modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from editor import SceneEditor

def main():
    """Run the scene editor."""
    app = QApplication(sys.argv)
    app.setApplicationName("Wicked Wizard Scene Editor")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("WickedWizard")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show editor
    editor = SceneEditor()
    editor.show()
    
    print("Scene Editor started successfully!")
    print("Features:")
    print("- Drag & drop actor hierarchy")
    print("- Component management")
    print("- Property inspector")
    print("- Undo/Redo (Ctrl+Z, Ctrl+Y)")
    print("- File operations (Ctrl+N, Ctrl+O, Ctrl+S)")
    print("- Copy/Paste actors (Ctrl+C, Ctrl+V)")
    print("- Custom component/UI import")
    print("- Auto-save prompts")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
