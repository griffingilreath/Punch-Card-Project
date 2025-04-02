"""
Simple GUI Display for the Punch Card Project.
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette

from src.display.widgets.punch_card_widget import PunchCardWidget

class SimpleGUI(QMainWindow):
    """Simple GUI for the Punch Card display."""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.setWindowTitle("Punch Card Display")
        self.resize(800, 600)
        
        # Set dark background
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        self.setPalette(palette)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create punch card widget
        self.punch_card = PunchCardWidget()
        layout.addWidget(self.punch_card, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Display a simple pattern (for testing)
        self.display_test_pattern()
    
    def display_test_pattern(self):
        """Display a test pattern on the punch card."""
        # Clear the card first
        self.punch_card.clear_grid()
        
        # Display "HELLO" diagonally
        message = "HELLO"
        for i, char in enumerate(message):
            row = i
            col = i * 2
            
            # Convert char to row/col position
            if char.isalpha():
                if char in "ABCDEFGHI":
                    self.punch_card.set_led(0, col, True)  # Row 12
                    self.punch_card.set_led(ord(char) - ord('A') + 3, col, True)
                elif char in "JKLMNOPQR":
                    self.punch_card.set_led(1, col, True)  # Row 11
                    self.punch_card.set_led(ord(char) - ord('J') + 3, col, True)
                else:  # S-Z
                    self.punch_card.set_led(2, col, True)  # Row 0
                    digit = ord(char) - ord('S') + 2
                    if digit <= 9:
                        self.punch_card.set_led(digit + 2, col, True)

def run_gui_app():
    """Run the GUI application."""
    try:
        app = QApplication(sys.argv)
        window = SimpleGUI()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"Error running GUI application: {str(e)}")
        print(f"\nAn error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_gui_app() 