@echo off
REM This script sets up the environment and runs the editor for Wicked Wizard Washdown.
echo Setting up the environment for Wicked Wizard Washdown editor...
pip install --upgrade pip
pip install -r requirements.txt
echo launching the editor...
python editor/run_editor.py