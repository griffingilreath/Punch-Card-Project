#!/usr/bin/env python3
"""
Fix Script - A standalone script to display IBM 026 punch card patterns.

This script provides the essential functionality to display IBM 026 punch card
patterns without relying on the broken simple_display.py file.
"""

import sys
import logging
from PyQt6.QtCore import Qt, QTimer, QRectF, QPoint
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QWidget,
    QPushButton, QHBoxLayout
)
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPalette
import argparse

# Constants
NUM_ROWS = 12
NUM_COLS = 80

# Colors for the punch card display
COLORS = {
    'background': QColor(0, 0, 0),      # Pure black background
    'card_bg': QColor(0, 0, 0),         # Black card background
    'grid': QColor(40, 40, 40),         # Grid lines
    'hole': QColor(255, 255, 255),      # White hole
    'hole_outline': QColor(255, 255, 255), # White hole outline
    'hole_fill': QColor(0, 0, 0),       # Black for unpunched holes
    'hole_punched': QColor(255, 255, 255), # White for punched holes
    'text': QColor(200, 200, 200),      # Light gray text
    'border': QColor(100, 100, 120),    # Border color
    'card_outline': QColor(255, 255, 255) # White card outline
}

# Card dimensions
SCALE_FACTOR = 3  # Scaled for comfortable monitor viewing
CARD_WIDTH = int(187.325 * SCALE_FACTOR)  # 7⅜ inches = 187.325mm
CARD_HEIGHT = int(82.55 * SCALE_FACTOR)   # 3¼ inches = 82.55mm
TOP_BOTTOM_MARGIN = int(4.2625 * SCALE_FACTOR)
SIDE_MARGIN = int(4.68 * SCALE_FACTOR)
ROW_SPACING = int(2.24 * SCALE_FACTOR)
COLUMN_SPACING = int(0.8 * SCALE_FACTOR)
HOLE_WIDTH = int(1 * SCALE_FACTOR)
HOLE_HEIGHT = int(3 * SCALE_FACTOR)
NOTCH_WIDTH = int(3.175 * SCALE_FACTOR)
NOTCH_HEIGHT = int(6.35 * SCALE_FACTOR)

def format_punch_card(message, max_width=80):
    """Format message for the punch card display.
    
    Args:
        message: The message to format
        max_width: Maximum number of columns to use
        
    Returns:
        A string representation of the punch card, with 'O' for punched holes (LED ON)
        and ' ' for no hole (LED OFF). Rows are in IBM order from top to bottom.
        
    Note:
        In IBM 026/029 punch card, the row order is: 
        12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 (from top to bottom)
    """
    if not message:
        return None
        
    # Define patterns based on IBM 026 standard - using IBM row numbers directly
    IBM_CHAR_MAPPING = {
        # Letters A–I: zone punch 12 + digit punches 1-9
        'A': [12, 1],    # 12 + 1
        'B': [12, 2],    # 12 + 2
        'C': [12, 3],    # 12 + 3
        'D': [12, 4],    # 12 + 4
        'E': [12, 5],    # 12 + 5
        'F': [12, 6],    # 12 + 6
        'G': [12, 7],    # 12 + 7
        'H': [12, 8],    # 12 + 8
        'I': [12, 9],    # 12 + 9

        # Letters J–R: zone punch 11 + digit punches 1-9
        'J': [11, 1],    # 11 + 1
        'K': [11, 2],    # 11 + 2
        'L': [11, 3],    # 11 + 3
        'M': [11, 4],    # 11 + 4
        'N': [11, 5],    # 11 + 5
        'O': [11, 6],    # 11 + 6
        'P': [11, 7],    # 11 + 7
        'Q': [11, 8],    # 11 + 8
        'R': [11, 9],    # 11 + 9

        # Letters S–Z: zone punch 0 + digit punches 2-9
        'S': [0, 2],     # 0 + 2
        'T': [0, 3],     # 0 + 3
        'U': [0, 4],     # 0 + 4
        'V': [0, 5],     # 0 + 5
        'W': [0, 6],     # 0 + 6
        'X': [0, 7],     # 0 + 7
        'Y': [0, 8],     # 0 + 8
        'Z': [0, 9],     # 0 + 9

        # Numbers (single punch in rows 0-9)
        '0': [0],        # 0 only
        '1': [1],        # 1 only
        '2': [2],        # 2 only
        '3': [3],        # 3 only
        '4': [4],        # 4 only
        '5': [5],        # 5 only
        '6': [6],        # 6 only
        '7': [7],        # 7 only
        '8': [8],        # 8 only
        '9': [9],        # 9 only
        
        # Common special characters
        ' ': [],                 # No punches
        '.': [12, 3, 8],         # 12 + 3 + 8
        ',': [0, 3, 8],          # 0 + 3 + 8
        '-': [11],               # 11 only (dash/hyphen)
        '/': [0, 1],             # 0 + 1
        '&': [12],               # 12 only (ampersand)
    }
    
    logging.info(f"Encoding message: {message}")
    
    # Truncate message if needed
    if len(message) > max_width:
        message = message[:max_width]
        
    # Convert message to all uppercase since punch cards typically used uppercase
    message = message.upper()
    
    # Create a 12×n matrix where:
    # - Each row corresponds to one IBM punch card row (12, 11, 0-9)
    # - Each column corresponds to one character position
    # - 'O' indicates a punched hole, ' ' indicates no hole
    
    # Initialize matrix with empty holes (12 rows)
    matrix = [[' ' for _ in range(len(message))] for _ in range(12)]
    
    # Map from IBM 026 row numbers to display positions (0-11)
    def ibm_row_to_display_position(ibm_row):
        if ibm_row == 12:
            return 0
        elif ibm_row == 11:
            return 1
        else:
            return ibm_row + 2
    
    # Fill in the matrix based on character mappings
    for col, char in enumerate(message):
        char_upper = char.upper()
        if char_upper in IBM_CHAR_MAPPING:
            for ibm_row in IBM_CHAR_MAPPING[char_upper]:
                row_idx = ibm_row_to_display_position(ibm_row)
                if 0 <= row_idx < 12:
                    matrix[row_idx][col] = 'O'  # Mark as punched
    
    # Convert matrix to a single string, with rows separated by newlines
    result = '\n'.join(''.join(row) for row in matrix)
    
    logging.info(f"Encoded {len(message)} characters in IBM 026 format")
    return result

class PunchCardWidget(QWidget):
    """Widget for displaying the punch card."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.num_rows = NUM_ROWS
        self.num_cols = NUM_COLS
        self.grid = [[False for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        # Set black background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, COLORS['background'])
        self.setPalette(palette)
        
        # Set minimum size
        window_margin = 40
        self.setMinimumSize(CARD_WIDTH + 2*window_margin, CARD_HEIGHT + 2*window_margin)
    
    def set_led(self, row: int, col: int, state: bool):
        """Set a single LED in the grid."""
        if 0 <= row < self.num_rows and 0 <= col < self.num_cols:
            # Only update if the state is actually changing
            if self.grid[row][col] != state:
                self.grid[row][col] = state
                logging.info(f"LED: R{row}C{col} turned {'ON' if state else 'OFF'}")
                self.update()
    
    def clear_grid(self):
        """Clear the punch card display."""
        self.grid = [[False for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        self.update()
    
    def paintEvent(self, event):
        """Paint the punch card with exact IBM specifications."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate the centered position of the card
        card_x = (self.width() - CARD_WIDTH) // 2
        card_y = (self.height() - CARD_HEIGHT) // 2
        
        # Draw card background (black)
        painter.fillRect(card_x, card_y, CARD_WIDTH, CARD_HEIGHT, COLORS['card_bg'])
        
        # Draw card outline (white) with thinner stroke
        painter.setPen(QPen(COLORS['card_outline'], 0.3))
        painter.drawRect(card_x, card_y, CARD_WIDTH, CARD_HEIGHT)
        
        # Calculate usable area for holes
        usable_width = CARD_WIDTH - (2 * SIDE_MARGIN)
        usable_height = CARD_HEIGHT - (2 * TOP_BOTTOM_MARGIN)
        
        # Calculate spacing between holes
        col_spacing = (usable_width - (NUM_COLS * HOLE_WIDTH)) / (NUM_COLS - 1)
        row_spacing = (usable_height - (NUM_ROWS * HOLE_HEIGHT)) / (NUM_ROWS - 1)
        
        # Draw all holes
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                # Calculate hole position
                x = card_x + SIDE_MARGIN + col * (HOLE_WIDTH + col_spacing)
                y = card_y + TOP_BOTTOM_MARGIN + row * (HOLE_HEIGHT + row_spacing)
                
                # Create the hole rectangle
                hole_rect = QRectF(x, y, HOLE_WIDTH, HOLE_HEIGHT)
                
                # Set fill color based on hole state
                if self.grid[row][col]:
                    painter.fillRect(hole_rect, COLORS['hole_punched'])
                else:
                    painter.fillRect(hole_rect, COLORS['hole_fill'])
                
                # Draw hole outline (white) with thinner stroke
                painter.setPen(QPen(COLORS['hole_outline'], 0.15))
                painter.drawRect(hole_rect)

def display_text_on_punch_card(text):
    """Display text on the punch card GUI.
    
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
        
        # Add buttons
        button_layout = QHBoxLayout()
        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(window.close)
        exit_button.setStyleSheet("font-size: 12pt; padding: 5px 20px;")
        button_layout.addWidget(exit_button)
        layout.addLayout(button_layout)
        
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

def test_punch_card_encoding():
    """Test function to display all characters and their punch patterns.
    
    This function creates a visual representation of the IBM 026 keypunch encoding
    used in the application, displaying each character alongside its punch pattern.
    """
    print("\n===== IBM 026 KEYPUNCH CHARACTER ENCODING TEST =====")
    print("  Rows: 12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9")
    print("  ('X' indicates a punched hole)\n")
    
    # Character groups to test
    char_groups = [
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "0123456789",
        " .,&/- "
    ]
    
    # IBM row labels for the display
    ibm_rows = "12,11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9"
    
    # Define patterns based on IBM 026 standard
    patterns = {
        # Letters A–I: zone punch 12 + digit punches 1-9
        'A': [12, 1],    # 12 + 1
        'B': [12, 2],    # 12 + 2
        'C': [12, 3],    # 12 + 3
        'D': [12, 4],    # 12 + 4
        'E': [12, 5],    # 12 + 5
        'F': [12, 6],    # 12 + 6
        'G': [12, 7],    # 12 + 7
        'H': [12, 8],    # 12 + 8
        'I': [12, 9],    # 12 + 9

        # Letters J–R: zone punch 11 + digit punches 1-9
        'J': [11, 1],    # 11 + 1
        'K': [11, 2],    # 11 + 2
        'L': [11, 3],    # 11 + 3
        'M': [11, 4],    # 11 + 4
        'N': [11, 5],    # 11 + 5
        'O': [11, 6],    # 11 + 6
        'P': [11, 7],    # 11 + 7
        'Q': [11, 8],    # 11 + 8
        'R': [11, 9],    # 11 + 9

        # Letters S–Z: zone punch 0 + digit punches 2-9
        'S': [0, 2],     # 0 + 2
        'T': [0, 3],     # 0 + 3
        'U': [0, 4],     # 0 + 4
        'V': [0, 5],     # 0 + 5
        'W': [0, 6],     # 0 + 6
        'X': [0, 7],     # 0 + 7
        'Y': [0, 8],     # 0 + 8
        'Z': [0, 9],     # 0 + 9

        # Numbers (single punch in rows 1-9, 0)
        '1': [1],        # 1 only
        '2': [2],        # 2 only
        '3': [3],        # 3 only
        '4': [4],        # 4 only
        '5': [5],        # 5 only
        '6': [6],        # 6 only
        '7': [7],        # 7 only
        '8': [8],        # 8 only
        '9': [9],        # 9 only
        '0': [0],        # 0 only
        
        # Common special characters
        ' ': [],                 # No punches
        '.': [12, 3, 8],         # 12 + 3 + 8
        ',': [0, 3, 8],          # 0 + 3 + 8
        '-': [11],               # 11 only (dash/hyphen)
        '/': [0, 1],             # 0 + 1
        '&': [12],               # 12 only (ampersand)
    }
    
    # Map from IBM 026 row numbers to display positions (0-11)
    def ibm_row_to_display_position(ibm_row):
        if ibm_row == 12:
            return 0
        elif ibm_row == 11:
            return 1
        else:
            return ibm_row + 2
    
    # Display each character and its punch pattern
    for group in char_groups:
        for char in group:
            # Create a punch card row representation
            punch_pattern = [' '] * 12  # 12 rows (12,11,0-9)
            
            # Fill in the punch pattern
            if char in patterns:
                for ibm_row in patterns[char]:
                    pos = ibm_row_to_display_position(ibm_row)
                    if 0 <= pos < 12:
                        punch_pattern[pos] = 'X'
            
            # Display the character and its punch pattern
            pattern_str = '|' + '|'.join(punch_pattern) + '|'
            print(f"  {char}: {pattern_str}  (IBM rows: {ibm_rows})")
        print()  # Add a blank line between groups
    
    # Show mapping for reference
    print("Row mapping in code vs display:")
    print("  IBM Row 12 = Index 0 in array, position 0 in display")
    print("  IBM Row 11 = Index 1 in array, position 1 in display")
    print("  IBM Row 0  = Index 2 in array, position 2 in display")
    print("  IBM Row 1  = Index 3 in array, position 3 in display")
    print("  And so on...\n")
    
    # Display a quick reference to verify specific characters
    print("Quick reference for common characters:")
    print("  'A' = punches in rows 12,1")
    print("  'B' = punches in rows 12,2")
    print("  'E' = punches in rows 12,5")
    print("  'I' = punches in rows 12,9")
    print("  'J' = punches in rows 11,1")
    print("  'S' = punches in rows 0,2")
    print("  '0' = punch in row 0")
    print("  '1' = punch in row 1\n")
    
    print("===== END OF ENCODING TEST =====\n")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="IBM 026 Punch Card Display")
    parser.add_argument("text", nargs="?", default=None, help="Text to display on the punch card")
    parser.add_argument("--test-encoding", action="store_true", help="Test the IBM 026 encoding")
    parser.add_argument("--show-alphabet", action="store_true", help="Display the alphabet on the punch card")
    parser.add_argument("--show-alphanumeric", action="store_true", help="Display the alphabet and numbers on the punch card")
    args = parser.parse_args()
    
    # Run the appropriate function based on arguments
    if args.test_encoding:
        sys.exit(test_punch_card_encoding())
    elif args.show_alphabet:
        text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        sys.exit(display_text_on_punch_card(text))
    elif args.show_alphanumeric:
        text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789"
        sys.exit(display_text_on_punch_card(text))
    elif args.text:
        sys.exit(display_text_on_punch_card(args.text))
    else:
        parser.print_help()
        sys.exit(1) 