"""
Fixed Punch Card Widget Module

A PyQt6 widget for displaying punch card messages.
"""

from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPalette

# Card dimensions
CARD_WIDTH = 600  # pixels
CARD_HEIGHT = 300  # pixels

class FixedPunchCardWidget(QWidget):
    """A widget that displays a punch card."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(CARD_WIDTH, CARD_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        # Initialize grid
        self.num_rows = 12
        self.num_cols = 80
        self.grid = [[False for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        # Set up colors
        self.colors = {
            'background': QColor(25, 25, 35),
            'card_bg': QColor(0, 0, 0),
            'grid': QColor(40, 40, 40),
            'hole': QColor(255, 255, 255),
            'hole_outline': QColor(255, 255, 255),
            'text': QColor(200, 200, 200),
            'border': QColor(100, 100, 120),
            'card_edge': QColor(150, 150, 170)
        }
        
        # Set dark background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
        self.setPalette(palette)
    
    def paintEvent(self, event):
        """Paint the punch card widget."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw card background
        painter.fillRect(self.rect(), self.colors['card_bg'])
        
        # Draw grid lines
        painter.setPen(QPen(self.colors['grid'], 1))
        # Horizontal lines
        for row in range(self.num_rows + 1):
            y = int((row * CARD_HEIGHT) / self.num_rows)
            painter.drawLine(0, y, CARD_WIDTH, y)
        
        # Vertical lines
        for col in range(self.num_cols + 1):
            x = int((col * CARD_WIDTH) / self.num_cols)
            painter.drawLine(x, 0, x, CARD_HEIGHT)
        
        # Draw holes
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.grid[row][col]:
                    self._draw_hole(painter, row, col)
        
        # Draw card edges
        painter.setPen(QPen(self.colors['card_edge'], 2))
        painter.drawRect(0, 0, CARD_WIDTH - 1, CARD_HEIGHT - 1)
    
    def _draw_hole(self, painter, row, col):
        """Draw a single hole at the specified position."""
        x = int((col * CARD_WIDTH) / self.num_cols + (CARD_WIDTH / self.num_cols) / 2)
        y = int((row * CARD_HEIGHT) / self.num_rows + (CARD_HEIGHT / self.num_rows) / 2)
        radius = min(CARD_WIDTH, CARD_HEIGHT) / (max(self.num_rows, self.num_cols) * 2)
        
        # Draw hole outline
        painter.setPen(QPen(self.colors['hole_outline'], 1))
        painter.setBrush(QBrush(self.colors['hole']))
        painter.drawEllipse(QPoint(x, y), int(radius), int(radius))
    
    def set_led(self, row, col, state):
        """Set the state of an LED in the grid."""
        if 0 <= row < self.num_rows and 0 <= col < self.num_cols:
            self.grid[row][col] = state
            self.update()
    
    def clear_grid(self):
        """Clear all LEDs in the grid."""
        self.grid = [[False for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        self.update() 