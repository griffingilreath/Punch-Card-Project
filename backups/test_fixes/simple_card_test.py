#!/usr/bin/env python3
"""
Simple test for the Punch Card Widget with fixed drawing.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import Qt, QPoint

# Define card dimensions
CARD_WIDTH = 600
CARD_HEIGHT = 300
NUM_ROWS = 12
NUM_COLS = 80

class SimpleCardWidget(QWidget):
    """A simple punch card widget with fixed drawing."""
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(CARD_WIDTH, CARD_HEIGHT)
        
        # Initialize grid
        self.grid = [[False for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
        
        # Define colors
        self.colors = {
            'card_bg': QColor(0, 0, 0),
            'grid': QColor(40, 40, 40),
            'hole': QColor(255, 255, 255),
            'hole_outline': QColor(255, 255, 255),
            'card_edge': QColor(150, 150, 170)
        }
    
    def paintEvent(self, event):
        """Paint the punch card with fixed drawing calls."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw card background
        painter.fillRect(self.rect(), self.colors['card_bg'])
        
        # Draw grid lines - FIXED: Using integers for drawLine
        painter.setPen(QPen(self.colors['grid'], 1))
        for row in range(NUM_ROWS + 1):
            y = int((row * CARD_HEIGHT) / NUM_ROWS)
            painter.drawLine(0, y, CARD_WIDTH, y)
        
        for col in range(NUM_COLS + 1):
            x = int((col * CARD_WIDTH) / NUM_COLS)
            painter.drawLine(x, 0, x, CARD_HEIGHT)
        
        # Draw holes
        for row in range(NUM_ROWS):
            for col in range(NUM_COLS):
                if self.grid[row][col]:
                    self._draw_hole(painter, row, col)
        
        # Draw card edges
        painter.setPen(QPen(self.colors['card_edge'], 2))
        painter.drawRect(0, 0, CARD_WIDTH - 1, CARD_HEIGHT - 1)
    
    def _draw_hole(self, painter, row, col):
        """Draw a single hole at the specified position."""
        x = int((col * CARD_WIDTH) / NUM_COLS + (CARD_WIDTH / NUM_COLS) / 2)
        y = int((row * CARD_HEIGHT) / NUM_ROWS + (CARD_HEIGHT / NUM_ROWS) / 2)
        radius = int(min(CARD_WIDTH, CARD_HEIGHT) / (max(NUM_ROWS, NUM_COLS) * 2))
        
        # Draw hole outline
        painter.setPen(QPen(self.colors['hole_outline'], 1))
        painter.setBrush(QBrush(self.colors['hole']))
        painter.drawEllipse(QPoint(x, y), radius, radius)
    
    def set_led(self, row, col, state):
        """Set the state of an LED in the grid."""
        if 0 <= row < NUM_ROWS and 0 <= col < NUM_COLS:
            self.grid[row][col] = state
            self.update()
    
    def clear_grid(self):
        """Clear all LEDs in the grid."""
        self.grid = [[False for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
        self.update()

class SimpleTestWindow(QMainWindow):
    """A simple test window for the punch card widget."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Punch Card Test")
        self.resize(800, 500)
        
        # Set up central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Create punch card widget
        self.card = SimpleCardWidget()
        main_layout.addWidget(self.card)
        
        # Add some buttons
        button_layout = QHBoxLayout()
        
        test_button = QPushButton("Test Pattern")
        test_button.clicked.connect(self.show_test_pattern)
        button_layout.addWidget(test_button)
        
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.card.clear_grid)
        button_layout.addWidget(clear_button)
        
        main_layout.addLayout(button_layout)
    
    def show_test_pattern(self):
        """Display a test pattern on the card."""
        self.card.clear_grid()
        
        # Draw a diagonal line
        for i in range(min(NUM_ROWS, NUM_COLS)):
            self.card.set_led(i, i, True)
        
        # Draw "HELLO" using dots
        pattern = [
            [0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0],  # H
            [0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],  # E
            [0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],  # L
            [0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],  # L
            [0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0]   # O
        ]
        
        for row_idx, row in enumerate(pattern):
            for col_idx, val in enumerate(row):
                if val:
                    self.card.set_led(row_idx + 3, col_idx + 20, True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleTestWindow()
    window.show()
    sys.exit(app.exec()) 