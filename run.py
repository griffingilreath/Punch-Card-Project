#!/usr/bin/env python3
"""
Launcher script for the Punch Card Project
"""

import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import and run the main application
from src.display.main_window import run_gui_app

if __name__ == "__main__":
    run_gui_app() 