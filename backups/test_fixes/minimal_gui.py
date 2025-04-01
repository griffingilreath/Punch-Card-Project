#!/usr/bin/env python3
"""
Minimal GUI for the Punch Card Project.
Uses the message bus monitoring approach that worked in testing.
"""

import os
import sys
import time
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MinimalGUI")

# Ensure src is in the path
sys.path.append('.')

# Import the fixed punch card widget
from src.display.widgets.punch_card_widget import PunchCardWidget

def run_minimal_gui():
    """Run a minimal GUI application."""
    
    logger.info("Starting minimal GUI...")
    
    try:
        # Initialize QApplication
        app = QApplication(sys.argv)
        
        # Create main window
        main_window = QMainWindow()
        main_window.setWindowTitle("Minimal Punch Card Display")
        main_window.resize(800, 600)
        
        # Create central widget
        central = QWidget()
        main_window.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Add title
        title = QLabel("Punch Card Display")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Create the punch card widget
        logger.info("Creating punch card widget...")
        punch_card = PunchCardWidget()
        layout.addWidget(punch_card, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Show the window
        main_window.show()
        
        # Draw a test pattern
        logger.info("Drawing test pattern...")
        for i in range(5):
            for j in range(5):
                punch_card.set_led(i, j, True)
        
        # Run the application
        logger.info("Starting event loop...")
        return app.exec()
        
    except Exception as e:
        logger.exception(f"Error running minimal GUI: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_minimal_gui()) 