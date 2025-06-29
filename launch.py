#!/usr/bin/env python3
"""
Launcher script for Wicked Wizard Washdown examples.
"""

import sys
import subprocess
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Wicked Wizard Washdown Game Engine Examples")
    parser.add_argument("example", nargs="?", default="basic", 
                       choices=["basic", "multiplayer", "particles", "ui"],
                       help="Example to run (default: basic)")
    parser.add_argument("--server", action="store_true", 
                       help="Run multiplayer example as server")
    parser.add_argument("--client", action="store_true",
                       help="Run multiplayer example as client")
    parser.add_argument("--host", default="localhost",
                       help="Server host for multiplayer client")
    parser.add_argument("--port", type=int, default=12345,
                       help="Server port for multiplayer")
    
    args = parser.parse_args()
    
    # Get script directory
    script_dir = Path(__file__).parent
    examples_dir = script_dir / "examples"
    
    # Build command
    if args.example == "basic":
        script_path = examples_dir / "basic_game.py"
        cmd = [sys.executable, str(script_path)]
    elif args.example == "multiplayer":
        script_path = examples_dir / "multiplayer_game.py"
        cmd = [sys.executable, str(script_path)]
        
        if args.server:
            cmd.extend(["--server", "--port", str(args.port)])
        elif args.client:
            cmd.extend(["--client", "--host", args.host, "--port", str(args.port)])
        else:
            print("For multiplayer example, specify --server or --client")
            return 1
    elif args.example == "particles":
        script_path = examples_dir / "particle_demo.py"
        cmd = [sys.executable, str(script_path)]
    elif args.example == "ui":
        script_path = examples_dir / "ui_demo.py"
        cmd = [sys.executable, str(script_path)]
    else:
        print(f"Unknown example: {args.example}")
        return 1
    
    if not script_path.exists():
        print(f"Example script not found: {script_path}")
        return 1
    
    print(f"Running: {args.example} example")
    if args.example == "multiplayer":
        mode = "server" if args.server else "client"
        print(f"Mode: {mode}")
        if args.client:
            print(f"Connecting to: {args.host}:{args.port}")
        else:
            print(f"Listening on port: {args.port}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Example failed with exit code: {e.returncode}")
        return e.returncode
    except KeyboardInterrupt:
        print("\\nExample interrupted by user")
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
