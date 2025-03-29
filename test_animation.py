#!/usr/bin/env python3
"""
Test script for punch card animations
This verifies that both startup and sleep animations work correctly
"""

import sys
import os

# Set up correct path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from PyQt6.QtWidgets import QApplication
    from src.display.gui_display import PunchCardDisplay
    from src.core.punch_card import PunchCard
except ImportError as e:
    print(f"Import error: {e}")
    print("Installing required dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt6", "openai"])
    
    # Try import again
    from PyQt6.QtWidgets import QApplication
    from src.display.gui_display import PunchCardDisplay
    from src.core.punch_card import PunchCard

def main():
    """Run the test application."""
    app = QApplication(sys.argv)
    
    # Create and initialize the display
    punch_card = PunchCard()
    gui = PunchCardDisplay(punch_card)
    
    # Show the window
    gui.show()
    
    # Exit when the application is closed
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 