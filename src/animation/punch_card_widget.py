#!/usr/bin/env python3
"""
Simple Punch Card Widget for testing animations
"""

from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, pyqtSignal, QSize


class PunchCardWidget(QWidget):
    """Simple widget for displaying a punch card with LEDs"""
    
    # Signal emitted when card changes
    changed = pyqtSignal()
    
    def __init__(self, parent=None, num_rows=12, num_cols=80):
        """Initialize punch card widget"""
        super().__init__(parent)
        
        # Set dimensions
        self.num_rows = num_rows
        self.num_cols = num_cols
        
        # Initialize grid
        self.grid = [[False for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        # Calculate dimensions
        self.hole_width = 6
        self.hole_height = 12
        self.hole_spacing_h = 8
        self.hole_spacing_v = 16
        self.calculate_dimensions()
        
        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(30, 30, 30))
        self.setPalette(palette)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Set minimum size
        self.setMinimumSize(400, 250)
    
    def calculate_dimensions(self):
        """Calculate card dimensions based on number of rows and columns"""
        self.card_width = self.num_cols * self.hole_spacing_h
        self.card_height = self.num_rows * self.hole_spacing_v
    
    def sizeHint(self):
        """Return the preferred size of the widget"""
        return QSize(self.card_width + 40, self.card_height + 40)
    
    def paintEvent(self, event):
        """Paint the punch card grid"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate offsets to center the card
        x_offset = (self.width() - self.card_width) // 2
        y_offset = (self.height() - self.card_height) // 2
        
        # Draw card background
        painter.setPen(QPen(QColor(50, 50, 50), 1))
        painter.setBrush(QColor(20, 20, 20))
        painter.drawRect(x_offset, y_offset, self.card_width, self.card_height)
        
        # Draw grid lines
        painter.setPen(QPen(QColor(40, 40, 40), 1))
        
        # Draw vertical lines
        for col in range(self.num_cols + 1):
            x = x_offset + col * self.hole_spacing_h
            painter.drawLine(x, y_offset, x, y_offset + self.card_height)
        
        # Draw horizontal lines
        for row in range(self.num_rows + 1):
            y = y_offset + row * self.hole_spacing_v
            painter.drawLine(x_offset, y, x_offset + self.card_width, y)
        
        # Draw the holes (LEDs)
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                x = x_offset + col * self.hole_spacing_h + 1
                y = y_offset + row * self.hole_spacing_v + 2
                
                # Set the color based on LED state
                if self.grid[row][col]:
                    # ON - bright amber
                    painter.setBrush(QColor(255, 180, 0))
                    painter.setPen(QPen(QColor(255, 200, 50), 1))
                else:
                    # OFF - dark amber
                    painter.setBrush(QColor(50, 35, 0))
                    painter.setPen(QPen(QColor(100, 70, 0), 1))
                
                # Draw the hole
                painter.drawRect(x, y, self.hole_width, self.hole_height)
    
    def set_led(self, row, col, state):
        """Set the state of an LED (hole) in the grid"""
        if 0 <= row < self.num_rows and 0 <= col < self.num_cols:
            if self.grid[row][col] != state:
                self.grid[row][col] = state
                self.changed.emit()
                self.update()
                return True
        return False
    
    def get_led(self, row, col):
        """Get the state of an LED in the grid"""
        if 0 <= row < self.num_rows and 0 <= col < self.num_cols:
            return self.grid[row][col]
        return False
    
    def clear_grid(self):
        """Clear the entire grid (turn all LEDs off)"""
        changed = False
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.grid[row][col]:
                    self.grid[row][col] = False
                    changed = True
        
        if changed:
            self.changed.emit()
            self.update()
        
        return changed
    
    def fill_grid(self):
        """Fill the entire grid (turn all LEDs on)"""
        changed = False
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if not self.grid[row][col]:
                    self.grid[row][col] = True
                    changed = True
        
        if changed:
            self.changed.emit()
            self.update()
        
        return changed
    
    def get_all_leds(self):
        """Get a copy of the entire grid"""
        return [row[:] for row in self.grid]  # Deep copy 