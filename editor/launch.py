#!/usr/bin/env python3
"""
Scene Editor Launcher

This script provides an easy way to launch the scene editor with proper configuration.
"""

import sys
import os
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'PyQt6',
        'pygame',
        'numpy',
        'Pillow',
        'PyYAML',
        'pymunk'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.lower().replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies(packages):
    """Install missing dependencies."""
    print(f"Installing missing packages: {', '.join(packages)}")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✓ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")
            return False
    return True

def main():
    """Launch the scene editor."""
    print("Wicked Wizard Washdown - Scene Editor Launcher")
    print("=" * 50)
    
    # Check if we're in the right directory
    current_dir = Path(__file__).parent
    editor_file = current_dir / "editor.py"
    run_editor_file = current_dir / "run_editor.py"
    
    if not editor_file.exists():
        print("Error: editor.py not found in current directory")
        print(f"Please run this script from: {current_dir}")
        return 1
    
    # Check dependencies
    print("Checking dependencies...")
    missing = check_dependencies()
    
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        response = input("Would you like to install them automatically? (y/n): ")
        
        if response.lower() == 'y':
            if not install_dependencies(missing):
                print("Failed to install some dependencies. Please install manually:")
                print(f"pip install {' '.join(missing)}")
                return 1
        else:
            print("Please install missing dependencies and try again:")
            print(f"pip install {' '.join(missing)}")
            return 1
    else:
        print("✓ All dependencies are installed")
    
    # Launch the editor
    print("\nLaunching Scene Editor...")
    print("Features available:")
    print("  • Drag & drop actor hierarchy")
    print("  • Component management")
    print("  • Property inspector")
    print("  • File operations with undo/redo")
    print("  • Custom component import")
    print("  • Keyboard shortcuts")
    print("\nPress Ctrl+C to exit this launcher after starting the editor.")
    
    try:
        if run_editor_file.exists():
            subprocess.run([sys.executable, str(run_editor_file)])
        else:
            # Fallback to direct execution
            subprocess.run([sys.executable, str(editor_file)])
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error launching editor: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
