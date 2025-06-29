#!/usr/bin/env python3
"""
Development setup and utilities for Wicked Wizard Washdown.
"""

import os
import subprocess
import sys
from pathlib import Path


def clean_cache():
    """Remove all Python cache files."""
    print("Cleaning Python cache files...")
    for root, dirs, files in os.walk("."):
        # Remove __pycache__ directories
        if "__pycache__" in dirs:
            cache_path = Path(root) / "__pycache__"
            print(f"Removing {cache_path}")
            subprocess.run(["rm", "-rf", str(cache_path)], check=False)
        
        # Remove .pyc files
        for file in files:
            if file.endswith(('.pyc', '.pyo')):
                pyc_path = Path(root) / file
                print(f"Removing {pyc_path}")
                pyc_path.unlink(missing_ok=True)


def check_dependencies():
    """Check if all required dependencies are installed."""
    print("Checking dependencies...")
    
    required_packages = [
        ('pygame-ce', 'pygame'),
        ('numpy', 'numpy'),
        ('Pillow', 'PIL'),
        ('PyYAML', 'yaml')
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✓ {package_name}")
        except ImportError:
            print(f"✗ {package_name} (missing)")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("All dependencies satisfied!")
    return True


def run_game():
    """Run the main game."""
    print("Starting Wicked Wizard Washdown...")
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
    except subprocess.CalledProcessError as e:
        print(f"Game exited with error code {e.returncode}")


def run_example(example_name):
    """Run a specific example."""
    example_path = Path("examples") / f"{example_name}.py"
    
    if not example_path.exists():
        print(f"Example '{example_name}' not found.")
        print("Available examples:")
        examples_dir = Path("examples")
        if examples_dir.exists():
            for example_file in examples_dir.glob("*.py"):
                print(f"  - {example_file.stem}")
        return
    
    print(f"Running example: {example_name}")
    try:
        subprocess.run([sys.executable, str(example_path)], check=True)
    except KeyboardInterrupt:
        print(f"\nExample '{example_name}' interrupted by user.")
    except subprocess.CalledProcessError as e:
        print(f"Example '{example_name}' exited with error code {e.returncode}")


def main():
    """Main development script."""
    if len(sys.argv) < 2:
        print("Usage: python dev.py <command>")
        print("Commands:")
        print("  clean         - Clean Python cache files")
        print("  check         - Check dependencies")
        print("  run           - Run the main game")
        print("  example <name> - Run a specific example")
        return
    
    command = sys.argv[1]
    
    if command == "clean":
        clean_cache()
    elif command == "check":
        check_dependencies()
    elif command == "run":
        if check_dependencies():
            run_game()
    elif command == "example":
        if len(sys.argv) < 3:
            print("Usage: python dev.py example <example_name>")
            return
        if check_dependencies():
            run_example(sys.argv[2])
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
