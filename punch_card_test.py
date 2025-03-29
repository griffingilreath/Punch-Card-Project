#!/usr/bin/env python3
"""
Simple test to verify the punch card widget display
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

# Import the punch card widget
from src.display.gui_display import PunchCardWidget, RetroButton

class SimpleTestWindow(QMainWindow):
    """Simple test window to display the punch card"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Punch Card Test")
        self.resize(800, 600)
        
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Create punch card widget
        self.punch_card = PunchCardWidget()
        layout.addWidget(self.punch_card)
        
        # Create a test button to set some LEDs
        self.test_button = RetroButton("Test LEDs")
        self.test_button.clicked.connect(self.set_test_pattern)
        layout.addWidget(self.test_button)
        
        # Create a clear button
        self.clear_button = RetroButton("Clear")
        self.clear_button.clicked.connect(self.punch_card.clear_grid)
        layout.addWidget(self.clear_button)
    
    def set_test_pattern(self):
        """Set a test pattern on the punch card"""
        # Create a simple pattern
        for row in range(0, 12, 2):
            for col in range(0, 80, 2):
                self.punch_card.set_led(row, col, True)
        
        # Create a letter H
        for row in range(2, 10):
            self.punch_card.set_led(row, 20, True)  # Left vertical
            self.punch_card.set_led(row, 26, True)  # Right vertical
        
        for col in range(20, 27):
            self.punch_card.set_led(6, col, True)  # Horizontal middle


def main():
    """Run the simple punch card test"""
    app = QApplication(sys.argv)
    window = SimpleTestWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 