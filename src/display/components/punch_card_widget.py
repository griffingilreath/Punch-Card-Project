#!/usr/bin/env python3
"""
Punch Card Widget Module

A PyQt6 widget for displaying punch card messages using PyQt6,
matching exact IBM punch card specifications.
"""

import sys
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtCore import Qt, QRect, QRectF
from PyQt6.QtGui import QPainter, QPalette, QPainterPath, QBrush, QPen

from src.utils.colors import COLORS

# Real IBM punch card dimensions (scaled up for display)
SCALE_FACTOR = 3  # Scaled for comfortable monitor viewing
CARD_WIDTH = int(187.325 * SCALE_FACTOR)  # 7⅜ inches = 187.325mm
CARD_HEIGHT = int(82.55 * SCALE_FACTOR)   # 3¼ inches = 82.55mm

# Margins and spacing (scaled)
TOP_BOTTOM_MARGIN = int(4.2625 * SCALE_FACTOR)  # Reduced from original 4.7625mm
SIDE_MARGIN = int(4.68 * SCALE_FACTOR)          # Reduced from original 6.35mm
ROW_SPACING = int(2.24 * SCALE_FACTOR)          # Reduced from original 3.175mm
COLUMN_SPACING = int(0.8 * SCALE_FACTOR)        # Reduced from 1mm

# Hole dimensions (scaled)
HOLE_WIDTH = int(1 * SCALE_FACTOR)    # 1mm
HOLE_HEIGHT = int(3 * SCALE_FACTOR)   # 3mm

# Notch dimensions (scaled)
NOTCH_WIDTH = int(3.175 * SCALE_FACTOR)   # 2/16 inch = 3.175mm
NOTCH_HEIGHT = int(6.35 * SCALE_FACTOR)   # 4/16 inch = 6.35mm

# Number of rows and columns
NUM_ROWS = 12
NUM_COLS = 80

class PunchCardWidget(QWidget):
    """Widget for displaying the minimalist punch card."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.num_rows = NUM_ROWS
        self.num_cols = NUM_COLS
        self.grid = [[False for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        # Initialize dimensions
        self.update_dimensions()
        
        # Set black background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, COLORS['background'])
        self.setPalette(palette)
        
        # Ensure widget maintains a consistent size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Set minimum size to prevent collapse during layout changes
        window_margin = 40
        self.setMinimumSize(self.card_width + 2*window_margin, self.card_height + 2*window_margin)
    
    def update_dimensions(self, settings: Optional[Dict[str, Any]] = None):
        """Update the card dimensions based on settings."""
        if settings:
            scale = settings['scale_factor']
            self.card_width = int(187.325 * scale)  # 7⅜ inches = 187.325mm
            self.card_height = int(82.55 * scale)   # 3¼ inches = 82.55mm
            self.top_margin = int(settings['top_margin'] * scale)
            self.side_margin = int(settings['side_margin'] * scale)
            self.row_spacing = int(settings['row_spacing'] * scale)
            self.column_spacing = int(settings['column_spacing'] * scale)
            self.hole_width = int(settings['hole_width'] * scale)
            self.hole_height = int(settings['hole_height'] * scale)
        else:
            # Use default dimensions
            self.card_width = CARD_WIDTH
            self.card_height = CARD_HEIGHT
            self.top_margin = TOP_BOTTOM_MARGIN
            self.side_margin = SIDE_MARGIN
            self.row_spacing = ROW_SPACING
            self.column_spacing = COLUMN_SPACING
            self.hole_width = HOLE_WIDTH
            self.hole_height = HOLE_HEIGHT
        
        # Update minimum size
        window_margin = 40
        self.setMinimumSize(self.card_width + 2*window_margin, self.card_height + 2*window_margin)
        self.update()
    
    def resizeEvent(self, event):
        """Handle resize events to maintain consistent appearance."""
        super().resizeEvent(event)
        # No additional logic needed here as paintEvent will handle proper centering
    
    def set_led(self, row: int, col: int, state: bool):
        """Set a single LED in the grid."""
        if 0 <= row < self.num_rows and 0 <= col < self.num_cols:
            # Only update if the state is actually changing
            if self.grid[row][col] != state:
                self.grid[row][col] = state
                
                # Calculate hole position for targeted update
                card_x = (self.width() - self.card_width) // 2
                card_y = (self.height() - self.card_height) // 2
                
                # Calculate usable area for holes
                usable_width = self.card_width - (2 * self.side_margin)
                usable_height = self.card_height - (2 * self.top_margin)
                
                # Calculate spacing between holes
                col_spacing = (usable_width - (NUM_COLS * self.hole_width)) / (NUM_COLS - 1)
                row_spacing = (usable_height - (NUM_ROWS * self.hole_height)) / (NUM_ROWS - 1)
                
                # Calculate the exact position of this LED
                x = card_x + self.side_margin + col * (self.hole_width + col_spacing)
                y = card_y + self.top_margin + row * (self.hole_height + row_spacing)
                
                # Add a larger margin for the update region to ensure the hole and its outline
                # are completely refreshed, preventing visual artifacts
                margin = 4  # Increased from 2 to 4 for better coverage
                update_rect = QRect(int(x - margin), int(y - margin), 
                                   int(self.hole_width + 2*margin), int(self.hole_height + 2*margin))
                
                # Update the region of this LED with a slight delay to ensure complete rendering
                self.update(update_rect)
    
    def clear_grid(self):
        """Clear the entire grid."""
        # Check if grid already empty to avoid unnecessary updates
        if any(any(row) for row in self.grid):
            # Reset the entire grid to False
            self.grid = [[False for _ in range(self.num_cols)] for _ in range(self.num_rows)]
            
            # Force a complete redraw of the entire widget
            # This ensures all visual artifacts are cleared
            self.repaint()  # Use repaint instead of update for immediate refresh
    
    def paintEvent(self, event):
        """Paint the punch card with exact IBM specifications."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate the centered position of the card
        card_x = (self.width() - self.card_width) // 2
        card_y = (self.height() - self.card_height) // 2
        
        # Create the card path with notched corner
        card_path = QPainterPath()
        
        # Start from the top-left corner (after the notch)
        card_path.moveTo(card_x + NOTCH_WIDTH, card_y)
        
        # Draw the notch
        card_path.lineTo(card_x, card_y + NOTCH_HEIGHT)
        
        # Complete the card outline
        card_path.lineTo(card_x, card_y + self.card_height)  # Left side
        card_path.lineTo(card_x + self.card_width, card_y + self.card_height)  # Bottom
        card_path.lineTo(card_x + self.card_width, card_y)  # Right side
        card_path.lineTo(card_x + NOTCH_WIDTH, card_y)  # Top
        
        # Fill card background (black)
        painter.fillPath(card_path, QBrush(COLORS['card_bg']))
        
        # Draw card outline (white) with thinner stroke
        painter.setPen(QPen(COLORS['card_outline'], 0.3))
        painter.drawPath(card_path)
        
        # Calculate usable area for holes
        usable_width = self.card_width - (2 * self.side_margin)
        usable_height = self.card_height - (2 * self.top_margin)
        
        # Calculate spacing between holes
        col_spacing = (usable_width - (NUM_COLS * self.hole_width)) / (NUM_COLS - 1)
        row_spacing = (usable_height - (NUM_ROWS * self.hole_height)) / (NUM_ROWS - 1)
        
        # Draw all holes
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                # Calculate hole position
                x = card_x + self.side_margin + col * (self.hole_width + col_spacing)
                y = card_y + self.top_margin + row * (self.hole_height + row_spacing)
                
                # Create the hole path
                hole_rect = QRectF(x, y, self.hole_width, self.hole_height)
                
                # Set fill color based on hole state
                if self.grid[row][col]:
                    painter.fillRect(hole_rect, COLORS['hole_punched'])
                else:
                    painter.fillRect(hole_rect, COLORS['hole_fill'])
                
                # Draw hole outline (white) with thinner stroke
                painter.setPen(QPen(COLORS['hole_outline'], 0.15))
                painter.drawRect(hole_rect) 