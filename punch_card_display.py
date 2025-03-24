#!/usr/bin/env python3
"""
Punch Card Display - A simple script to display text on a punch card display.

This script can be imported or run directly to display text on a simulated
IBM 026 keypunch punch card.
"""

import sys
import logging
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QWidget

# Import from simple_display.py
from simple_display import PunchCardWidget, format_punch_card, NUM_ROWS, NUM_COLS

def display_text_on_punch_card(text):
    """Display text on the punch card GUI directly without animation.
    
    This function initializes the GUI and displays the provided text
    on the punch card display, allowing visual verification of the 
    IBM 026 character encoding.
    """
    logging.info(f"Starting application with text: {text}")
    print(f"Displaying text on punch card: {text}")
    
    try:
        # Initialize the application
        app = QApplication(sys.argv)
        
        # Create main window
        window = QMainWindow()
        window.setWindowTitle("IBM 026 Keypunch Display")
        window.setMinimumSize(800, 600)
        
        # Create central widget with layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Add header label
        header = QLabel(f"IBM 026 Keypunch - '{text}'")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 16pt; font-weight: bold; margin: 10px;")
        layout.addWidget(header)
        
        # Create the punch card widget
        punch_card = PunchCardWidget()
        layout.addWidget(punch_card)
        
        # Add reference label
        reference = QLabel("Row order (top to bottom): 12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9")
        reference.setAlignment(Qt.AlignmentFlag.AlignCenter)
        reference.setStyleSheet("font-size: 12pt; margin: 10px;")
        layout.addWidget(reference)
        
        window.setCentralWidget(central_widget)
        
        # Format the punch card text
        punch_card_str = format_punch_card(text)
        print(f"Formatted punch card pattern:\n{punch_card_str}")
        
        # First, clear any existing LEDs
        punch_card.clear_grid()
        
        # Parse the punch card string into a matrix and set LEDs directly
        if punch_card_str:
            rows = punch_card_str.strip().split('\n')
            for i, row in enumerate(rows):
                if i >= NUM_ROWS:
                    break  # Avoid going out of bounds
                    
                for j, char in enumerate(row):
                    if j >= NUM_COLS:
                        break  # Avoid going out of bounds
                        
                    # Set the LED state based on character ('O' = punched hole)
                    if char == 'O':
                        print(f"Setting LED at row {i}, col {j} to ON")
                        punch_card.set_led(i, j, True)
        
        # Show the window
        window.show()
        
        # Start the application event loop
        return app.exec()
    except Exception as e:
        logging.error(f"Error running application: {e}")
        raise

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Get text from command line or use default
    text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if len(sys.argv) > 1:
        text = sys.argv[1]
        
    # Display the text
    sys.exit(display_text_on_punch_card(text)) 