#!/usr/bin/env python3
"""
IBM 026 Punch Card Alphabet Test Program

This script displays a visual representation of the IBM 026 punch patterns
for the alphabet (A-Z) and numbers (0-9).
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer

class PunchCardRow:
    """Maps IBM punch card rows to display indices"""
    ROW_12 = 0
    ROW_11 = 1
    ROW_0 = 2
    ROW_1 = 3
    ROW_2 = 4
    ROW_3 = 5
    ROW_4 = 6
    ROW_5 = 7
    ROW_6 = 8
    ROW_7 = 9
    ROW_8 = 10
    ROW_9 = 11


class PunchCardDisplay(QWidget):
    """Widget to display punch card patterns"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 300)
        
        # Configure the display grid
        self.num_rows = 12  # IBM rows 12, 11, 0-9
        self.num_cols = 40  # Characters to display
        
        # Grid for punch hole states (True = hole punched)
        self.grid = [[False for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        self.setStyleSheet("""
            background-color: #E0E0E0;
            border: 1px solid #999;
            border-radius: 5px;
        """)
    
    def set_punch(self, row, col, punched=True):
        """Set a punch hole state"""
        if 0 <= row < self.num_rows and 0 <= col < self.num_cols:
            self.grid[row][col] = punched
            self.update()
    
    def clear_grid(self):
        """Clear all punches"""
        self.grid = [[False for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        self.update()
    
    def display_pattern(self, patterns_by_char):
        """Display punch patterns for multiple characters"""
        self.clear_grid()
        
        for col, char in enumerate(patterns_by_char):
            if col >= self.num_cols:
                break
                
            # Get the IBM rows that should be punched for this character
            ibm_rows = IBM_CHAR_MAPPING.get(char, [])
            
            # Convert IBM rows to display rows and set punches
            for ibm_row in ibm_rows:
                display_row = self._ibm_row_to_display_row(ibm_row)
                self.set_punch(display_row, col)
    
    def _ibm_row_to_display_row(self, ibm_row):
        """Convert IBM row number to display row index"""
        if ibm_row == 12:
            return PunchCardRow.ROW_12
        elif ibm_row == 11:
            return PunchCardRow.ROW_11
        else:
            return ibm_row + 2  # Row 0 → index 2, Row 1 → index 3, etc.
    
    def paintEvent(self, event):
        """Draw the punch card display"""
        import math
        from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Define colors
        bg_color = QColor("#F5F5DC")  # Beige for card background
        grid_color = QColor("#AAAAAA")  # Grid lines
        hole_color = QColor("#333333")  # Punched holes
        text_color = QColor("#555555")  # Text
        
        # Get drawing area size
        w, h = self.width(), self.height()
        
        # Draw background
        painter.fillRect(0, 0, w, h, bg_color)
        
        # Calculate cell size
        cell_width = w / (self.num_cols + 1)
        cell_height = h / (self.num_rows + 1)
        
        # Draw grid and holes
        painter.setPen(QPen(grid_color, 1, Qt.SolidLine))
        
        # Draw row labels (IBM row numbers)
        painter.setPen(QPen(text_color, 1, Qt.SolidLine))
        row_labels = ["12", "11", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        for row in range(self.num_rows):
            y = (row + 1) * cell_height
            painter.drawText(5, y + cell_height/2, row_labels[row])
        
        # Draw column labels (characters)
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        for col in range(min(len(alphabet), self.num_cols)):
            x = (col + 1) * cell_width
            painter.drawText(x + cell_width/2 - 4, cell_height/2, alphabet[col])
        
        # Draw punch holes
        for row in range(self.num_rows):
            y = (row + 1) * cell_height
            
            for col in range(self.num_cols):
                x = (col + 1) * cell_width
                
                # Draw the punch hole or empty position
                if col < len(alphabet) and self.grid[row][col]:
                    # Punched hole
                    painter.setBrush(QBrush(hole_color))
                    painter.setPen(QPen(hole_color, 1, Qt.SolidLine))
                    radius = min(cell_width, cell_height) * 0.4
                    painter.drawEllipse(x + cell_width/2 - radius, y + cell_height/2 - radius, 
                                        radius*2, radius*2)
                else:
                    # Empty position (no hole)
                    painter.setBrush(QBrush(bg_color))
                    painter.setPen(QPen(grid_color, 1, Qt.DotLine))
                    radius = min(cell_width, cell_height) * 0.4
                    painter.drawEllipse(x + cell_width/2 - radius, y + cell_height/2 - radius, 
                                        radius*2, radius*2)
        
        painter.end()


# Define IBM 026 keypunch encoding
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
}


def main():
    """Main function to run the application"""
    print("\n===== IBM 026 PUNCH CARD ALPHABET TEST =====")
    print("Displaying punch patterns for A-Z and 0-9...\n")
    
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("IBM 026 Punch Card Alphabet Test")
    window.setGeometry(100, 100, 800, 400)
    
    # Create main widget with layout
    main_widget = QWidget()
    layout = QVBoxLayout(main_widget)
    
    # Add header label
    header = QLabel("IBM 026 Keypunch Character Encoding")
    header.setAlignment(Qt.AlignCenter)
    header.setStyleSheet("font-size: 16pt; font-weight: bold; margin: 10px;")
    layout.addWidget(header)
    
    # Add punch card display
    punch_display = PunchCardDisplay()
    layout.addWidget(punch_display)
    
    # Add reference label
    reference = QLabel("Row order (top to bottom): 12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9")
    reference.setAlignment(Qt.AlignCenter)
    reference.setStyleSheet("font-size: 12pt; margin: 10px;")
    layout.addWidget(reference)
    
    # Set the main widget as central widget
    window.setCentralWidget(main_widget)
    
    # Display the alphabet and numbers
    test_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    
    # Wait a moment before displaying
    window.show()
    QTimer.singleShot(500, lambda: punch_display.display_pattern(test_chars))
    
    # Print quick reference
    print("Quick reference for common characters:")
    print("  'A' = punches in rows 12,1")
    print("  'E' = punches in rows 12,5")
    print("  'I' = punches in rows 12,9")
    print("  'J' = punches in rows 11,1")
    print("  'S' = punches in rows 0,2")
    print("  '0' = punch in row 0")
    print("  '1' = punch in row 1\n")
    
    # Start the application
    print("Running test display. Close the window to exit.")
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main()) 