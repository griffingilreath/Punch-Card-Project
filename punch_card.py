#!/usr/bin/env python3
"""
IBM 026 Punch Card Project - Main Entry Point

This is the main entry point for the IBM 026 Punch Card Project.
It imports and runs the main application from the core module.
"""

import sys
import os

# Ensure that the src directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from src.core.run_punch_card import main
    
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please make sure you are running this script from the project root directory.")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
