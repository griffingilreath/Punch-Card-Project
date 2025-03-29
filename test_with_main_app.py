#!/usr/bin/env python3
"""
Test script to run the main application with animations enabled
"""

import os
import sys
import subprocess

# Run the application with animation testing enabled
if __name__ == "__main__":
    print("=" * 60)
    print("Running main application with animation testing enabled")
    print("=" * 60)
    
    # Run the main application with both animation flags
    try:
        # Get the Python executable path
        python_exe = sys.executable
        
        # Run the app with animation flags
        subprocess.run([python_exe, "run_app.py", "--enable-animations", "--test-animations"])
    except Exception as e:
        print(f"Error running application: {e}")
        sys.exit(1) 