#!/usr/bin/env python3
"""
Minimal test to check if PyQt6 works.
"""

import sys

try:
    from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
    from PyQt6.QtCore import Qt
    
    print("✅ PyQt6 import successful!")
    
    # Test creating application
    app = QApplication(sys.argv)
    print("✅ QApplication created successfully!")
    
    # Test creating a simple window
    window = QMainWindow()
    window.setWindowTitle("Test Window")
    window.resize(300, 200)
    
    label = QLabel("Editor Test", window)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    window.setCentralWidget(label)
    
    print("✅ Test window created successfully!")
    print("✅ PyQt6 is working correctly!")
    
    # Don't show the window, just verify it can be created
    app.quit()
    
except Exception as e:
    print(f"❌ PyQt6 test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("✅ All PyQt6 tests passed!")
