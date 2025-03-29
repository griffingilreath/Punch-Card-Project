#!/usr/bin/env python3
"""
Minimalist Punch Card GUI Display

A clean, modern GUI for displaying punch card messages using PyQt6,
matching exact IBM punch card specifications.
"""

import sys
import time
import random
import math
import os
import socket
import threading
from functools import partial
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import json

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QStackedLayout, QRadioButton,
                            QSizePolicy, QFrame, QDialog, QTextEdit, QSpinBox,
                            QCheckBox, QFormLayout, QGroupBox, QTabWidget, 
                            QLineEdit, QComboBox, QSlider, QDoubleSpinBox,
                            QDialogButtonBox, QMessageBox, QMenu, QSpacerItem)
from PyQt6.QtCore import Qt, QTimer, QSize, QRect, QRectF, pyqtSignal, QDir, QObject, QEvent, QPoint, QDateTime
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPalette, QBrush, QPainterPath, QKeyEvent

from src.display.settings_dialog import SettingsDialog

# Color scheme
COLORS = {
    'background': QColor(0, 0, 0),        # Black background
    'card_bg': QColor(0, 0, 0),           # Black card background
    'card_outline': QColor(255, 255, 255), # White card outline
    'hole_outline': QColor(255, 255, 255), # White hole outline
    'hole_fill': QColor(0, 0, 0),         # Black for unpunched holes
    'hole_punched': QColor(255, 255, 255), # White for punched holes
    'text': QColor(255, 255, 255),        # White text
    'button_bg': QColor(30, 30, 30),      # Dark button background
    'button_hover': QColor(50, 50, 50),   # Slightly lighter on hover
    'button_text': QColor(255, 255, 255), # White button text
    'console_bg': QColor(20, 20, 20),     # Darker background for console
    'console_text': QColor(200, 200, 200), # Light gray for console text
    'title_bar': QColor(40, 40, 40),      # Dark gray for title bar
    'title_text': QColor(200, 200, 200),  # Light gray for title text
    'title_line': QColor(100, 100, 100),  # Medium gray for title lines
    'error': QColor(150, 50, 50),         # Dark red for errors
    'success': QColor(50, 150, 50),       # Dark green for success
    'warning': QColor(150, 150, 50),      # Dark yellow for warnings
}

# Font configuration
# Use system fonts that are guaranteed to be available on macOS
FONT_FAMILY = "Courier New"
FONT_SIZE = 12  # Use consistent font size throughout the application

def get_font(bold=False, italic=False, size=FONT_SIZE) -> QFont:
    """Get a font with the specified style."""
    font = QFont()
    font.setFamily("Courier New")
    font.setPointSize(size)
    font.setBold(bold)
    font.setItalic(italic)
    font.setStyleHint(QFont.StyleHint.Monospace)  # Fallback to any monospace font
    return font

def get_font_css(bold=False, italic=False, size=FONT_SIZE) -> str:
    """Get CSS font styling with the specified style."""
    weight = "bold" if bold else "normal"
    style = "italic" if italic else "normal"
    return f"font-family: {FONT_FAMILY}; font-size: {size}px; font-weight: {weight}; font-style: {style};"

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

class ClassicTitleBar(QWidget):
    """Classic Macintosh-style title bar."""
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.setFixedHeight(20)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['title_bar'].name()};
                color: {COLORS['title_text'].name()};
                {get_font_css(bold=True, size=12)}
            }}
        """)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Set font for title
        painter.setFont(get_font(bold=True, size=12))
        
        # Draw title
        painter.setPen(COLORS['title_text'])
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.title)
        
        # Draw decorative lines
        line_y = self.height() // 2
        line_width = 20
        spacing = 40
        
        # Left lines
        for i in range(3):
            x = 10 + (i * spacing)
            painter.setPen(QPen(COLORS['title_line'], 1))
            painter.drawLine(x, line_y - 1, x + line_width, line_y - 1)
            painter.drawLine(x, line_y + 1, x + line_width, line_y + 1)
        
        # Right lines
        for i in range(3):
            x = self.width() - 10 - line_width - (i * spacing)
            painter.setPen(QPen(COLORS['title_line'], 1))
            painter.drawLine(x, line_y - 1, x + line_width, line_y - 1)
            painter.drawLine(x, line_y + 1, x + line_width, line_y + 1)

class RetroButton(QPushButton):
    """Minimalist styled button."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['button_bg'].name()};
                color: {COLORS['button_text'].name()};
                border: 1px solid {COLORS['hole_outline'].name()};
                padding: 6px 12px;
                {get_font_css(size=12)}
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['button_hover'].name()};
            }}
        """)
        # Set proper font
        self.setFont(get_font(size=12))


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

class ConsoleWindow(QDialog):
    """Console window for displaying system information and debug data."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Console")
        self.setMinimumSize(600, 400)
        
        # Set dark theme
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['console_bg'].name()};
                color: {COLORS['console_text'].name()};
            }}
            QTextEdit {{
                background-color: {COLORS['console_bg'].name()};
                color: {COLORS['console_text'].name()};
                {get_font_css(size=12)}
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        # Create console text area
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        layout.addWidget(self.console)
        
        # Add buttons layout
        button_layout = QHBoxLayout()
        
        # Add save button
        save_button = RetroButton("Save Log")
        save_button.clicked.connect(self.save_log)
        button_layout.addWidget(save_button)
        
        # Add clear button
        clear_button = RetroButton("Clear")
        clear_button.clicked.connect(self.clear_log)
        button_layout.addWidget(clear_button)
        
        # Add close button
        close_button = RetroButton("Close")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def log(self, message: str, level: str = "INFO"):
        """Add a message to the console with timestamp and level."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        level_color = {
            "INFO": "white",
            "LED": "cyan",
            "WARNING": "yellow",
            "ERROR": "red",
            "SUCCESS": "green"
        }.get(level, "white")
        
        self.console.append(f'<span style="color: gray">[{timestamp}]</span> '
                          f'<span style="color: {level_color}">[{level}]</span> '
                          f'<span style="color: white">{message}</span>')
        self.console.verticalScrollBar().setValue(
            self.console.verticalScrollBar().maximum()
        )

    def save_log(self):
        """Save the console log to a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"console_log_{timestamp}.txt"
        try:
            with open(filename, 'w') as f:
                f.write(self.console.toPlainText())
            self.log(f"Log saved to {filename}", "SUCCESS")
        except Exception as e:
            self.log(f"Error saving log: {str(e)}", "ERROR")
    
    def clear_log(self):
        """Clear the console log."""
        self.console.clear()
        self.log("Console cleared", "INFO")

class SettingsDialog(QDialog):
    """Dialog for configuring punch card settings."""

    def __init__(self, parent=None):
        """Initialize the settings dialog."""
        super().__init__(parent)
        self.setWindowTitle("Punch Card Settings")
        self.resize(550, 650)  # Make dialog larger to accommodate tabs
        
        # Set dark theme
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background'].name()};
                color: {COLORS['text'].name()};
            }}
            QLabel, QSpinBox, QCheckBox, QLineEdit, QComboBox, QTextEdit, QSlider {{
                color: {COLORS['text'].name()};
            }}
            QTabWidget::pane {{
                border: 1px solid {COLORS['hole_outline'].name()};
                background-color: {COLORS['background'].name()};
            }}
            QTabBar::tab {{
                background-color: {COLORS['button_bg'].name()};
                color: {COLORS['text'].name()};
                padding: 6px 12px;
                border: 1px solid {COLORS['hole_outline'].name()};
                border-bottom: none;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['button_hover'].name()};
            }}
        """)
        
        # Create the main layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.display_tab = QWidget()
        self.card_tab = QWidget()
        self.openai_tab = QWidget()
        self.stats_tab = QWidget()  # New stats tab
        
        # Set up tabs
        self._setup_display_tab()
        self._setup_card_tab()
        self._setup_openai_tab()
        self._setup_stats_tab()  # Set up stats tab
        
        # Add tabs to widget
        self.tab_widget.addTab(self.display_tab, "Display")
        self.tab_widget.addTab(self.card_tab, "Card Dimensions")
        self.tab_widget.addTab(self.openai_tab, "🤖 OpenAI API")
        self.tab_widget.addTab(self.stats_tab, "📊 Statistics")
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.layout.addWidget(button_box)
        
        # Load existing settings
        self._load_settings()
        
        # Initialize message stats if not exists
        global message_stats
        if 'message_stats' not in globals():
            self._initialize_message_stats()

    def _initialize_message_stats(self):
        """Initialize global message stats variable if it doesn't exist."""
        global message_stats
        message_stats = {
            "total": 0,
            "local": 0,
            "openai": 0,
            "database": 0,
            "system": 0,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_message": "",
            "last_source": ""
        }
        
        # Initialize service status tracking
        global service_status
        service_status = {
            "openai": {
                "status": "unknown",
                "message": "Not checked yet",
                "last_checked": "Never"
            },
            "flyio": {
                "status": "unknown",
                "message": "Not checked yet",
                "last_checked": "Never"
            }
        }

    def _setup_display_tab(self):
        """Set up the display settings tab."""
        layout = QFormLayout()
        self.display_tab.setLayout(layout)
        
        # LED Update Delay
        self.led_delay = QSpinBox()
        self.led_delay.setRange(50, 500)
        self.led_delay.setValue(100)
        self.led_delay.setSuffix(" ms")
        layout.addRow("LED Update Delay:", self.led_delay)
        
        # Message interval
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 3600)
        self.interval_spin.setSuffix(" seconds")
        layout.addRow("Message interval:", self.interval_spin)
        
        # Message display time
        self.display_time_spin = QSpinBox()
        self.display_time_spin.setRange(1, 3600)
        self.display_time_spin.setSuffix(" seconds")
        layout.addRow("Message display time:", self.display_time_spin)
        
        # Delay factor
        self.delay_factor_spin = QDoubleSpinBox()
        self.delay_factor_spin.setRange(0.1, 10.0)
        self.delay_factor_spin.setSingleStep(0.1)
        layout.addRow("Typing delay factor:", self.delay_factor_spin)
        
        # Random Delay
        self.random_delay = QCheckBox()
        self.random_delay.setChecked(True)
        layout.addRow("Random Delay:", self.random_delay)
        
        # Show Splash Screen
        self.show_splash = QCheckBox()
        self.show_splash.setChecked(True)
        layout.addRow("Show Splash Screen:", self.show_splash)
        
        # Auto-Open Console
        self.auto_console = QCheckBox()
        self.auto_console.setChecked(True)
        layout.addRow("Auto-Open Console:", self.auto_console)
        
        # Card dimensions settings
        card_group = QGroupBox("Card Dimensions")
        card_layout = QFormLayout()
        
        # Scale Factor
        self.scale_factor = QSpinBox()
        self.scale_factor.setRange(1, 10)
        self.scale_factor.setValue(3)
        self.scale_factor.setSuffix("x")
        self.scale_factor.valueChanged.connect(self.update_card_dimensions)
        card_layout.addRow("Scale Factor:", self.scale_factor)
        
        # Width and Height
        self.width_spin = QSpinBox()
        self.width_spin.setRange(10, 1000)
        self.width_spin.setSuffix(" pixels")
        card_layout.addRow("Card width:", self.width_spin)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(10, 1000)
        self.height_spin.setSuffix(" pixels")
        card_layout.addRow("Card height:", self.height_spin)
        
        # Top/Bottom Margin
        self.top_margin = QSpinBox()
        self.top_margin.setRange(1, 20)
        self.top_margin.setValue(4)
        self.top_margin.setSuffix(" mm")
        self.top_margin.valueChanged.connect(self.update_card_dimensions)
        card_layout.addRow("Top/Bottom Margin:", self.top_margin)
        
        # Side Margin
        self.side_margin = QSpinBox()
        self.side_margin.setRange(1, 20)
        self.side_margin.setValue(5)
        self.side_margin.setSuffix(" mm")
        self.side_margin.valueChanged.connect(self.update_card_dimensions)
        card_layout.addRow("Side Margin:", self.side_margin)
        
        # Row Spacing
        self.row_spacing = QSpinBox()
        self.row_spacing.setRange(1, 10)
        self.row_spacing.setValue(2)
        self.row_spacing.setSuffix(" mm")
        self.row_spacing.valueChanged.connect(self.update_card_dimensions)
        card_layout.addRow("Row Spacing:", self.row_spacing)
        
        # Column Spacing
        self.column_spacing = QSpinBox()
        self.column_spacing.setRange(1, 10)
        self.column_spacing.setValue(1)
        self.column_spacing.setSuffix(" mm")
        self.column_spacing.valueChanged.connect(self.update_card_dimensions)
        card_layout.addRow("Column Spacing:", self.column_spacing)
        
        # Hole Width
        self.hole_width = QSpinBox()
        self.hole_width.setRange(1, 5)
        self.hole_width.setValue(1)
        self.hole_width.setSuffix(" mm")
        self.hole_width.valueChanged.connect(self.update_card_dimensions)
        card_layout.addRow("Hole Width:", self.hole_width)
        
        # Hole Height
        self.hole_height = QSpinBox()
        self.hole_height.setRange(1, 10)
        self.hole_height.setValue(3)
        self.hole_height.setSuffix(" mm")
        self.hole_height.valueChanged.connect(self.update_card_dimensions)
        card_layout.addRow("Hole Height:", self.hole_height)
        
        card_group.setLayout(card_layout)
        layout.addRow(card_group)
        
        # Add buttons
        button_layout = QHBoxLayout()
        save_button = RetroButton("Save")
        cancel_button = RetroButton("Cancel")
        
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addRow(button_layout)
    
    def update_card_dimensions(self):
        """Update the card dimensions based on current settings."""
        if hasattr(self, 'parent') and self.parent():
            self.parent().update_card_dimensions(self.get_card_settings())
    
    def get_settings(self) -> Dict[str, Any]:
        """Get the current settings values."""
        return {
            'led_delay': self.led_delay.value(),
            'message_delay': self.message_delay.value(),
            'message_display_time': self.message_display_time.value(),
            'random_delay': self.random_delay.isChecked(),
            'show_splash': self.show_splash.isChecked(),
            'auto_console': self.auto_console.isChecked(),
            **self.get_card_settings()
        }
    
    def get_card_settings(self) -> Dict[str, Any]:
        """Get the current card dimension settings."""
        return {
            'scale_factor': self.scale_factor.value(),
            'top_margin': self.top_margin.value(),
            'side_margin': self.side_margin.value(),
            'row_spacing': self.row_spacing.value(),
            'column_spacing': self.column_spacing.value(),
            'hole_width': self.hole_width.value(),
            'hole_height': self.hole_height.value()
        }

    def _setup_openai_tab(self):
        """Set up the OpenAI API tab."""
        layout = QVBoxLayout()
        self.openai_tab.setLayout(layout)
        
        # API Key Section
        api_key_group = QGroupBox("API Key")
        api_key_layout = QVBoxLayout()
        api_key_group.setLayout(api_key_layout)
        
        # API Key input with layout
        key_input_layout = QHBoxLayout()
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_edit.setPlaceholderText("Enter your OpenAI API key")
        key_input_layout.addWidget(self.api_key_edit)
        
        # Toggle visibility button
        toggle_btn = RetroButton("👁")
        toggle_btn.setMaximumWidth(30)
        toggle_btn.clicked.connect(self.toggle_key_visibility)
        key_input_layout.addWidget(toggle_btn)
        
        api_key_layout.addLayout(key_input_layout)
        
        # API key status label
        self.api_key_status = QLabel("Status: Not verified")
        api_key_layout.addWidget(self.api_key_status)
        
        # API Key action buttons
        key_buttons_layout = QHBoxLayout()
        
        verify_btn = RetroButton("Verify Key")
        verify_btn.clicked.connect(self.verify_api_key)
        key_buttons_layout.addWidget(verify_btn)
        
        save_btn = RetroButton("Save Key")
        save_btn.clicked.connect(self.save_api_key)
        key_buttons_layout.addWidget(save_btn)
        
        api_key_layout.addLayout(key_buttons_layout)
        
        # Add the API key group to the main layout
        layout.addWidget(api_key_group)
        
        # Add separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator1)
        
        # Model Selection Section
        model_group = QGroupBox("Model Selection")
        model_layout = QVBoxLayout()
        model_group.setLayout(model_layout)
        
        # Model dropdown with refresh button
        model_select_layout = QHBoxLayout()
        
        model_layout.addWidget(QLabel("Select OpenAI Model:"))
        self.model_combo = QComboBox()
        
        # Add models
        self.model_combo.addItems([
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ])
        self.model_combo.currentIndexChanged.connect(self.update_model_description)
        model_select_layout.addWidget(self.model_combo)
        
        # Refresh models button
        refresh_button = RetroButton("Refresh")
        refresh_button.setFixedWidth(80)
        refresh_button.clicked.connect(self.refresh_models)
        model_select_layout.addWidget(refresh_button)
        
        model_layout.addLayout(model_select_layout)
        
        # Model description
        self.model_description = QLabel("GPT 4o: OpenAI's most capable multimodal model")
        self.model_description.setWordWrap(True)
        model_layout.addWidget(self.model_description)
        
        # Temperature setting
        model_layout.addWidget(QLabel("Temperature (randomness):"))
        
        temp_layout = QHBoxLayout()
        self.temperature_slider = QSlider(Qt.Orientation.Horizontal)
        self.temperature_slider.setRange(0, 100)
        self.temperature_slider.setValue(70)
        self.temperature_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.temperature_slider.setTickInterval(10)
        temp_layout.addWidget(self.temperature_slider)
        
        self.temperature_label = QLabel("0.7")
        self.temperature_slider.valueChanged.connect(lambda v: self.temperature_label.setText(f"{v/100:.1f}"))
        temp_layout.addWidget(self.temperature_label)
        
        model_layout.addLayout(temp_layout)
        
        model_layout.addWidget(QLabel("Higher values = more random outputs"))
        
        # Add model group to main layout
        layout.addWidget(model_group)
        
        # Add separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator2)
        
        # Usage and Cost Tracking Section
        usage_group = QGroupBox("Usage and Cost Tracking")
        usage_layout = QVBoxLayout()
        usage_group.setLayout(usage_layout)
        
        # Add usage display
        self.usage_text = QTextEdit()
        self.usage_text.setReadOnly(True)
        self.usage_text.setMaximumHeight(150)
        self.usage_text.setStyleSheet(f"""
            background-color: {COLORS['console_bg'].name()};
            color: {COLORS['console_text'].name()};
            border: 1px solid {COLORS['hole_outline'].name()};
            {get_font_css(size=11)}
        """)
        usage_layout.addWidget(self.usage_text)
        
        # Buttons for usage stats
        usage_buttons = QHBoxLayout()
        
        update_usage_btn = RetroButton("Update Stats")
        update_usage_btn.clicked.connect(self.update_usage_stats)
        usage_buttons.addWidget(update_usage_btn)
        
        reset_usage_btn = RetroButton("Reset Stats")
        reset_usage_btn.clicked.connect(self.reset_usage_stats)
        usage_buttons.addWidget(reset_usage_btn)
        
        usage_layout.addLayout(usage_buttons)
        
        # Add usage group to main layout
        layout.addWidget(usage_group)
        
        # Add separator
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.Shape.HLine)
        separator3.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator3)
        
        # Service status section
        service_group = QGroupBox("OpenAI Service Status")
        service_layout = QHBoxLayout()
        service_group.setLayout(service_layout)
        
        self.service_status_label = QLabel("Status: Not checked")
        service_layout.addWidget(self.service_status_label)
        
        check_status_btn = RetroButton("Check Status")
        check_status_btn.clicked.connect(self.check_openai_service)
        service_layout.addWidget(check_status_btn)
        
        layout.addWidget(service_group)

    def toggle_key_visibility(self):
        """Toggle visibility of the API key."""
        if self.api_key_edit.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)

    def update_model_description(self, index):
        """Update the model description when selection changes."""
        model = self.model_combo.currentText()
        
        descriptions = {
            "gpt-3.5-turbo": "Fast and cost-effective for most tasks",
            "gpt-4": "More capable than GPT-3.5 but slower and more expensive",
            "gpt-4-turbo": "Improved version of GPT-4 with better performance",
            "gpt-4o": "Most advanced model with visual capabilities",
            "gpt-3.5-turbo-16k": "GPT-3.5 Turbo with extended context window"
        }
        
        description = descriptions.get(model, "No description available")
        self.model_description.setText(f"{model}: {description}")
    
    def refresh_models(self):
        """Refresh the available models list."""
        try:
            # Try to get the models from the API if we have a key
            api_key = self.api_key_edit.text().strip()
            if api_key and len(api_key) > 20 and api_key != "●●●●●●●●●●●●●●●●●●●●●●●●●●●●":
                # Import OpenAI
                try:
                    from openai import OpenAI
                    
                    # Create a temporary client
                    temp_client = OpenAI(api_key=api_key)
                    
                    # Try to get models
                    models = temp_client.models.list()
                    
                    # Extract model names that are appropriate for chat
                    model_names = [
                        model.id for model in models.data
                        if model.id.startswith(("gpt-3", "gpt-4")) and not model.id.endswith("-vision")
                    ]
                    
                    if model_names:
                        # Remember the current selection
                        current_model = self.model_combo.currentText()
                        
                        # Update the combo box
                        self.model_combo.clear()
                        self.model_combo.addItems(model_names)
                        
                        # Try to restore previous selection
                        index = self.model_combo.findText(current_model)
                        if index >= 0:
                            self.model_combo.setCurrentIndex(index)
                        
                        self.model_description.setText("Models refreshed from API")
                        return
                    
                except ImportError:
                    self.model_description.setText("Error: OpenAI module not installed")
                except Exception as e:
                    self.model_description.setText(f"Error refreshing models: {str(e)[:60]}")
            
            # Fallback to default models if we can't get them from the API
            self.model_combo.clear()
            self.model_combo.addItems([
                "gpt-4o",
                "gpt-4-turbo",
                "gpt-4",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k"
            ])
            self.model_description.setText("Using default model list (API key not set or error)")
            
        except Exception as e:
            self.model_description.setText(f"Error: {str(e)[:60]}")

    def verify_api_key(self):
        """Check if the API key is valid."""
        # Get API key from input
        api_key = self.api_key_edit.text()
        
        # Check if we have text entered
        if not api_key or len(api_key.strip()) < 10:
            self.api_key_status.setText("Status: Invalid key (too short)")
            self.api_key_status.setStyleSheet("color: #FF5555;")
            return
        
        # Update UI
        self.api_key_status.setText("Status: Verifying...")
        self.api_key_status.setStyleSheet("color: #AAAAAA;")
        
        # Try to initialize a client to test the key
        try:
            # Import OpenAI
            from openai import OpenAI, APIError
            
            # Create a temporary client
            temp_client = OpenAI(api_key=api_key)
            
            # Try a lightweight API call to verify the key
            try:
                models = temp_client.models.list(limit=1)
                
                # Key is valid
                self.api_key_status.setText(f"Status: Valid ✅")
                self.api_key_status.setStyleSheet("color: #55AA55;")
                
            except APIError as e:
                # API-specific errors (usually authentication or permissions)
                self.api_key_status.setText(f"Status: Invalid key - {str(e)[:60]}")
                self.api_key_status.setStyleSheet("color: #FF5555;")
                
        except ImportError:
            self.api_key_status.setText("Status: OpenAI module not installed")
            self.api_key_status.setStyleSheet("color: #FF5555;")
        except Exception as e:
            self.api_key_status.setText(f"Status: Error - {str(e)[:60]}")
            self.api_key_status.setStyleSheet("color: #FF5555;")

    def save_api_key(self):
        """Update the API key in the configuration."""
        api_key = self.api_key_edit.text()
        
        # Skip if key is just placeholder asterisks
        if api_key == "●●●●●●●●●●●●●●●●●●●●●●●●●●●●":
            QMessageBox.warning(
                self, 
                "API Key Update", 
                "Please enter your actual API key, not the placeholder."
            )
            return
        
        if not api_key:
            QMessageBox.warning(
                self, 
                "API Key Update", 
                "API key cannot be empty."
            )
            return
        
        # Save the API key to settings
        try:
            import json
            import os
            
            # Load existing settings
            settings_path = "punch_card_settings.json"
            settings = {}
            
            if os.path.exists(settings_path):
                with open(settings_path, "r") as f:
                    settings = json.load(f)
            
            # Update with new API key
            settings["openai_api_key"] = api_key
            
            # Add model and temperature if they don't exist
            settings["openai_model"] = self.model_combo.currentText()
            settings["temperature"] = float(self.temperature_slider.value()) / 100.0
            
            # Save updated settings
            with open(settings_path, "w") as f:
                json.dump(settings, f, indent=4)
            
            QMessageBox.information(
                self, 
                "API Key Update", 
                "✅ API key successfully saved to settings file."
            )
            
            # Update API key status
            self.verify_api_key()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "API Key Update Error",
                f"An error occurred while updating your API key: {str(e)}"
            )

    def check_openai_service(self):
        """Check the OpenAI service status."""
        self.service_status_label.setText("Status: Checking...")
        
        try:
            import requests
            
            url = "https://status.openai.com/api/v2/status.json"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                status_indicator = data.get("status", {}).get("indicator", "unknown")
                status_description = data.get("status", {}).get("description", "Unknown status")
                
                if status_indicator == "none":
                    self.service_status_label.setText("Status: All systems operational")
                    self.service_status_label.setStyleSheet("color: #55AA55;")
                else:
                    self.service_status_label.setText(f"Status: {status_description}")
                    
                    # Set color based on status
                    if status_indicator == "minor":
                        self.service_status_label.setStyleSheet("color: #FFAA55;")
                    elif status_indicator == "major" or status_indicator == "critical":
                        self.service_status_label.setStyleSheet("color: #FF5555;")
                    else:
                        self.service_status_label.setStyleSheet("color: #AAAAAA;")
            else:
                self.service_status_label.setText(f"Status: Error (HTTP {response.status_code})")
                self.service_status_label.setStyleSheet("color: #FF5555;")
                
        except Exception as e:
            self.service_status_label.setText(f"Status: Error - {str(e)[:60]}")
            self.service_status_label.setStyleSheet("color: #FF5555;")

    def update_usage_stats(self):
        """Update the OpenAI usage statistics display."""
        import json
        import os
        
        # Default display if no stats available
        usage_text = "No OpenAI usage data available."
        
        try:
            # Load settings file to get usage data
            settings_path = "punch_card_settings.json"
            
            if os.path.exists(settings_path):
                with open(settings_path, "r") as f:
                    settings = json.load(f)
                
                # Check if we have OpenAI usage data
                if "openai_usage" in settings:
                    usage = settings["openai_usage"]
                    
                    # Format the usage statistics
                    usage_text = "=== OpenAI API Usage ===\n"
                    usage_text += f"Total API calls: {usage.get('total_calls', 0)}\n"
                    usage_text += f"Total tokens: {usage.get('total_tokens', 0)}\n"
                    usage_text += f"Prompt tokens: {usage.get('prompt_tokens', 0)}\n"
                    usage_text += f"Completion tokens: {usage.get('completion_tokens', 0)}\n"
                    usage_text += f"Estimated cost: ${usage.get('estimated_cost', 0):.4f}\n"
                    
                    # Add last updated timestamp if available
                    if "last_updated" in usage:
                        usage_text += f"\nLast updated: {usage.get('last_updated', 'Never')}"
            
            # Update the usage text display
            self.usage_text.setText(usage_text)
            
        except Exception as e:
            self.usage_text.setText(f"Error loading usage stats: {str(e)}")

    def reset_usage_stats(self):
        """Reset the OpenAI usage statistics."""
        import json
        import os
        from datetime import datetime
        
        # Confirm with user
        confirm = QMessageBox.question(
            self,
            "Reset Usage Statistics",
            "Are you sure you want to reset all OpenAI usage statistics?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                # Load settings file
                settings_path = "punch_card_settings.json"
                settings = {}
                
                if os.path.exists(settings_path):
                    with open(settings_path, "r") as f:
                        settings = json.load(f)
                
                # Reset OpenAI usage stats
                settings["openai_usage"] = {
                    "total_calls": 0,
                    "total_tokens": 0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "estimated_cost": 0.0,
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "history": []
                }
                
                # Save updated settings
                with open(settings_path, "w") as f:
                    json.dump(settings, f, indent=4)
                
                # Update the display
                self.update_usage_stats()
                
                QMessageBox.information(
                    self,
                    "Usage Statistics Reset",
                    "OpenAI usage statistics have been reset."
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Reset Error",
                    f"An error occurred while resetting usage statistics: {str(e)}"
                )

    def _setup_stats_tab(self):
        """Set up the statistics tab."""
        layout = QVBoxLayout()
        self.stats_tab.setLayout(layout)
        
        # Message Statistics Section
        stats_group = QGroupBox("Message Statistics")
        stats_layout = QVBoxLayout()
        stats_group.setLayout(stats_layout)
        
        # Add stats display
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMinimumHeight(150)
        self.stats_text.setStyleSheet(f"""
            background-color: {COLORS['console_bg'].name()};
            color: {COLORS['console_text'].name()};
            border: 1px solid {COLORS['hole_outline'].name()};
            {get_font_css(size=11)}
        """)
        stats_layout.addWidget(self.stats_text)
        
        # Reset stats button
        reset_stats_btn = RetroButton("Reset Statistics")
        reset_stats_btn.clicked.connect(self.reset_message_stats)
        stats_layout.addWidget(reset_stats_btn)
        
        # Add stats group to main layout
        layout.addWidget(stats_group)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Service Status Section
        service_group = QGroupBox("Service Status")
        service_layout = QVBoxLayout()
        service_group.setLayout(service_layout)
        
        # Add service status display
        self.service_status_text = QTextEdit()
        self.service_status_text.setReadOnly(True)
        self.service_status_text.setMinimumHeight(150)
        self.service_status_text.setStyleSheet(f"""
            background-color: {COLORS['console_bg'].name()};
            color: {COLORS['console_text'].name()};
            border: 1px solid {COLORS['hole_outline'].name()};
            {get_font_css(size=11)}
        """)
        service_layout.addWidget(self.service_status_text)
        
        # Refresh status button
        refresh_status_btn = RetroButton("Refresh Service Status")
        refresh_status_btn.clicked.connect(self.refresh_service_status)
        service_layout.addWidget(refresh_status_btn)
        
        # Add service group to main layout
        layout.addWidget(service_group)
        
        # Update the statistics display
        self.update_stats_display()

    def update_stats_display(self):
        """Update the statistics display with current stats."""
        # Update message statistics
        self.stats_text.setText(self.get_stats_text())
        
        # Update service status
        self.service_status_text.setText(self.get_service_status_text())
        
        # Update OpenAI usage stats
        self.update_usage_stats()

    def get_stats_text(self):
        """Format and return statistics as text."""
        global message_stats
        if 'message_stats' not in globals():
            self._initialize_message_stats()
            
        ms = message_stats
        text = "=== Message Counts ===\n"
        text += f"Total messages: {ms.get('total', 0)}\n"
        text += f"Local messages: {ms.get('local', 0)}\n"
        text += f"OpenAI messages: {ms.get('openai', 0)}\n"
        text += f"Database messages: {ms.get('database', 0)}\n"
        text += f"System messages: {ms.get('system', 0)}\n\n"
        
        text += f"Last updated: {ms.get('last_updated', 'Never')}\n"
        
        if ms.get('last_message') and ms.get('last_source'):
            text += f"Last message: '{ms.get('last_message', '')}'\n"
            text += f"Source: {ms.get('last_source', '')}\n"
        
        return text

    def get_service_status_text(self):
        """Get formatted text of service statuses."""
        global service_status
        if 'service_status' not in globals():
            self._initialize_message_stats()
            
        openai_status = service_status.get("openai", {})
        flyio_status = service_status.get("flyio", {})
        
        text = "=== Service Status ===\n"
        text += f"OpenAI: {openai_status.get('status', 'Unknown')} - {openai_status.get('message', 'No message')}\n"
        text += f"Last checked: {openai_status.get('last_checked', 'Never')}\n\n"
        
        text += f"Fly.io: {flyio_status.get('status', 'Unknown')} - {flyio_status.get('message', 'No message')}\n"
        text += f"Last checked: {flyio_status.get('last_checked', 'Never')}\n"
        
        return text

    def reset_message_stats(self):
        """Reset the message statistics."""
        global message_stats
        
        # Confirm with user
        confirm = QMessageBox.question(
            self,
            "Reset Statistics",
            "Are you sure you want to reset all message statistics?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            # Reset stats
            message_stats = {
                "total": 0,
                "local": 0,
                "openai": 0,
                "database": 0,
                "system": 0,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_message": "",
                "last_source": ""
            }
            
            # Update display
            self.update_stats_display()
            
            QMessageBox.information(
                self,
                "Statistics Reset",
                "Message statistics have been reset."
            )

    def refresh_service_status(self):
        """Refresh the service status display."""
        global service_status
        
        # Update the status
        self.check_openai_status()
        self.check_flyio_status()
        
        # Update the display
        self.service_status_text.setText(self.get_service_status_text())
        
        QMessageBox.information(
            self,
            "Service Status",
            "Service status has been refreshed."
        )

    def check_openai_status(self):
        """Check OpenAI API status and update global status tracking."""
        global service_status
        
        import requests
        from datetime import datetime
        
        url = "https://status.openai.com/api/v2/status.json"
        service_status["openai"]["last_checked"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # Try to make a simple API request
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            status_indicator = data.get("status", {}).get("indicator", "unknown")
            status_description = data.get("status", {}).get("description", "Unknown status")
            
            if status_indicator == "none":
                service_status["openai"]["status"] = "operational"
                service_status["openai"]["message"] = "All systems operational"
            else:
                service_status["openai"]["status"] = status_indicator
                service_status["openai"]["message"] = status_description
                
            return True
        except Exception as e:
            service_status["openai"]["status"] = "error"
            service_status["openai"]["message"] = f"Error checking status: {str(e)[:50]}"
            return False

    def check_flyio_status(self):
        """Check fly.io status and update global status tracking."""
        global service_status
        
        import requests
        from datetime import datetime
        
        url = "https://status.fly.io/api/v2/status.json"
        service_status["flyio"]["last_checked"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # Try to make a simple API request
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            status_indicator = data.get("status", {}).get("indicator", "unknown")
            status_description = data.get("status", {}).get("description", "Unknown status")
            
            service_status["flyio"]["status"] = status_indicator
            service_status["flyio"]["message"] = status_description
                
            return True
        except Exception as e:
            service_status["flyio"]["status"] = "error"
            service_status["flyio"]["message"] = f"Error checking status: {str(e)[:50]}"
            return False

    def _load_settings(self):
        """Load existing settings into the dialog."""
        import json
        import os
        
        settings_path = "punch_card_settings.json"
        
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r") as f:
                    settings = json.load(f)
                
                # Load display settings
                self.led_delay.setValue(settings.get("led_delay", 100))
                self.interval_spin.setValue(settings.get("interval", 5))
                self.display_time_spin.setValue(settings.get("message_display_time", 3))
                self.delay_factor_spin.setValue(settings.get("delay_factor", 1.0))
                self.random_delay.setChecked(settings.get("random_delay", True))
                self.show_splash.setChecked(settings.get("show_splash", True))
                self.auto_console.setChecked(settings.get("auto_console", True))
                
                # Load dimension settings
                self.width_spin.setValue(settings.get("card_width", 300))
                self.height_spin.setValue(settings.get("card_height", 200))
                
                # Load card settings if available
                if "scale_factor" in settings:
                    self.scale_factor.setValue(settings.get("scale_factor", 3))
                if "top_margin" in settings:
                    self.top_margin.setValue(settings.get("top_margin", 4))
                if "side_margin" in settings:
                    self.side_margin.setValue(settings.get("side_margin", 5))
                if "row_spacing" in settings:
                    self.row_spacing.setValue(settings.get("row_spacing", 2))
                if "column_spacing" in settings:
                    self.column_spacing.setValue(settings.get("column_spacing", 1))
                if "hole_width" in settings:
                    self.hole_width.setValue(settings.get("hole_width", 1))
                if "hole_height" in settings:
                    self.hole_height.setValue(settings.get("hole_height", 3))
                
                # Load OpenAI settings
                if "openai_api_key" in settings:
                    self.api_key_edit.setText("●●●●●●●●●●●●●●●●●●●●●●●●●●●●")
                
                # Set model if it exists
                if "openai_model" in settings:
                    index = self.model_combo.findText(settings["openai_model"])
                    if index >= 0:
                        self.model_combo.setCurrentIndex(index)
                
                # Set temperature if it exists
                if "temperature" in settings:
                    temp_value = int(settings["temperature"] * 100)
                    self.temperature_slider.setValue(temp_value)
                
            except Exception as e:
                print(f"Error loading settings: {e}")

    def accept(self):
        """Save settings and close the dialog."""
        self.save_settings()
        super().accept()

    def save_settings(self):
        """Save settings to a file."""
        import json
        import os
        from datetime import datetime
        
        # Get settings from form
        settings = {
            # Display settings
            "led_delay": self.led_delay.value(),
            "interval": self.interval_spin.value(),
            "message_display_time": self.display_time_spin.value(),
            "delay_factor": self.delay_factor_spin.value(),
            "random_delay": self.random_delay.isChecked(),
            "show_splash": self.show_splash.isChecked(),
            "auto_console": self.auto_console.isChecked(),
            
            # Card dimensions
            "card_width": self.width_spin.value(),
            "card_height": self.height_spin.value(),
            
            # Card detailed settings
            "scale_factor": self.scale_factor.value(),
            "top_margin": self.top_margin.value(),
            "side_margin": self.side_margin.value(),
            "row_spacing": self.row_spacing.value(),
            "column_spacing": self.column_spacing.value(),
            "hole_width": self.hole_width.value(),
            "hole_height": self.hole_height.value(),
            
            # OpenAI settings (don't overwrite API key if placeholder)
            "openai_model": self.model_combo.currentText(),
            "temperature": float(self.temperature_slider.value()) / 100.0
        }
        
        # API key - only save if it's not the placeholder
        api_key = self.api_key_edit.text()
        if api_key and api_key != "●●●●●●●●●●●●●●●●●●●●●●●●●●●●":
            settings["openai_api_key"] = api_key
        
        # Load existing settings to preserve other values
        settings_path = "punch_card_settings.json"
        existing_settings = {}
        
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r") as f:
                    existing_settings = json.load(f)
            except json.JSONDecodeError:
                print("Warning: Could not parse settings file. Creating new file.")
        
        # Merge with existing settings
        existing_settings.update(settings)
        
        # Initialize OpenAI usage section if it doesn't exist
        if "openai_usage" not in existing_settings:
            existing_settings["openai_usage"] = {
                "total_calls": 0,
                "total_tokens": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "estimated_cost": 0.0,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "history": []
            }
        
        # Save settings
        with open(settings_path, "w") as f:
            json.dump(existing_settings, f, indent=4)

    def _setup_card_tab(self):
        """Set up the card dimensions tab."""
        self.card_tab = QWidget()
        card_layout = QVBoxLayout(self.card_tab)
        
        # Create form for card dimensions
        card_form = QFormLayout()
        card_form.setSpacing(10)
        
        # Card width input
        self.card_width_input = QSpinBox()
        self.card_width_input.setRange(10, 200)
        self.card_width_input.setValue(80)
        self.card_width_input.setFixedWidth(100)
        card_form.addRow("Card Width:", self.card_width_input)
        
        # Card height input
        self.card_height_input = QSpinBox()
        self.card_height_input.setRange(5, 50)
        self.card_height_input.setValue(12)
        self.card_height_input.setFixedWidth(100)
        card_form.addRow("Card Height:", self.card_height_input)
        
        # Add explanation
        card_explanation = QLabel(
            "Card dimensions determine how many columns and rows are displayed in the punch card."
            "\nChanges will take effect after restarting the application."
        )
        card_explanation.setStyleSheet("color: gray; font-style: italic;")
        card_explanation.setWordWrap(True)
        
        # Add form and explanation to layout
        card_layout.addLayout(card_form)
        card_layout.addWidget(card_explanation)
        card_layout.addStretch(1)
        
        # Update values from settings
        self.update_card_dimensions()

class MessageGenerator:
    """Generates random messages for display."""
    def __init__(self):
        self.messages = [
            "HELLO WORLD",
            "WELCOME TO THE PUNCH CARD DISPLAY",
            "IBM PUNCH CARD SYSTEM",
            "DO NOT FOLD SPINDLE OR MUTILATE",
            "COMPUTING THE FUTURE",
            "BINARY DREAMS",
            "PAPER TAPES AND PUNCH CARDS",
            "FROM MECHANICAL TO DIGITAL",
            "HISTORY IN HOLES",
            "DATA PUNCHED IN TIME"
        ]
    
    def generate_message(self) -> str:
        """Generate a random message."""
        return random.choice(self.messages)

class HardwareDetector:
    """Detects and monitors hardware components like Raspberry Pi and LED controller."""
    
    def __init__(self, console_logger=None):
        self.console_logger = console_logger
        self.raspberry_pi_status = "Detecting..."
        self.led_controller_status = "Detecting..."
        self.is_hardware_ready = False
        self.using_virtual_mode = False
        self.raspberry_pi_ip = "192.168.1.10"  # Default IP - can be configured
        self.raspberry_pi_port = 5555          # Default port - can be configured
        self.detection_complete = False
        
    def log(self, message, level="INFO"):
        """Log a message if console logger is available."""
        if self.console_logger:
            self.console_logger.log(message, level)
        else:
            print(f"[{level}] {message}")
    
    def detect_hardware(self):
        """Start hardware detection in a background thread."""
        self.log("Starting hardware detection process", "INFO")
        threading.Thread(target=self._run_detection, daemon=True).start()
    
    def _run_detection(self):
        """Run the detection process for Raspberry Pi and LED controller."""
        # Check for Raspberry Pi connection
        self.raspberry_pi_status = "Detecting..."
        self.log(f"Attempting to connect to Raspberry Pi at {self.raspberry_pi_ip}:{self.raspberry_pi_port}", "INFO")
        
        try:
            # Try to establish a socket connection to the Pi
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)  # 3 second timeout
            s.connect((self.raspberry_pi_ip, self.raspberry_pi_port))
            
            # If connection successful, check LED controller
            self.raspberry_pi_status = "Connected"
            self.log("Successfully connected to Raspberry Pi", "SUCCESS")
            
            # Send a command to query LED controller status
            s.sendall(b"CHECK_LED_CONTROLLER")
            response = s.recv(1024).decode('utf-8')
            
            if "READY" in response:
                self.led_controller_status = "Ready"
                self.log("LED controller is ready", "SUCCESS")
                self.is_hardware_ready = True
            else:
                self.led_controller_status = "Error: " + response
                self.log(f"LED controller error: {response}", "ERROR")
            
            s.close()
            
        except (socket.timeout, socket.error) as e:
            self.raspberry_pi_status = "Not Found"
            self.led_controller_status = "Not Available"
            self.log(f"Failed to connect to Raspberry Pi: {str(e)}", "ERROR")
            self.log("Will use virtual mode for testing", "WARNING")
            self.using_virtual_mode = True
        
        # Mark detection as complete
        self.detection_complete = True
        self.log("Hardware detection complete", "INFO")
    
    def enable_virtual_mode(self):
        """Explicitly enable virtual mode for testing."""
        self.log("Virtual mode enabled for testing", "WARNING")
        self.raspberry_pi_status = "Virtual Mode"
        self.led_controller_status = "Virtual Mode"
        self.using_virtual_mode = True
        self.is_hardware_ready = True
        self.detection_complete = True

class APIConsoleWindow(QDialog):
    """Console window specifically for API activity, requests, and error logging."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API Console")
        self.setMinimumSize(600, 400)
        
        # Set dark theme with accent color for API
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['console_bg'].name()};
                color: {COLORS['console_text'].name()};
            }}
            QTextEdit {{
                background-color: {COLORS['console_bg'].name()};
                color: {COLORS['console_text'].name()};
                {get_font_css(size=12)}
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        # Add header with status
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("API Status: Unknown")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text'].name()};
                {get_font_css(bold=True, size=12)}
            }}
        """)
        status_layout.addWidget(self.status_label)
        
        self.endpoint_label = QLabel("")
        self.endpoint_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text'].name()};
                {get_font_css(size=11)}
            }}
        """)
        status_layout.addWidget(self.endpoint_label, 1)
        
        layout.addLayout(status_layout)
        
        # Create console text area
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        layout.addWidget(self.console)
        
        # Add filter options
        filter_layout = QHBoxLayout()
        
        self.show_requests = QCheckBox("Requests")
        self.show_requests.setChecked(True)
        self.show_requests.setStyleSheet(f"color: {COLORS['text'].name()}")
        
        self.show_responses = QCheckBox("Responses")
        self.show_responses.setChecked(True)
        self.show_responses.setStyleSheet(f"color: {COLORS['text'].name()}")
        
        self.show_errors = QCheckBox("Errors")
        self.show_errors.setChecked(True)
        self.show_errors.setStyleSheet(f"color: {COLORS['text'].name()}")
        
        self.show_status = QCheckBox("Status Changes")
        self.show_status.setChecked(True)
        self.show_status.setStyleSheet(f"color: {COLORS['text'].name()}")
        
        filter_layout.addWidget(QLabel("Show:"))
        filter_layout.addWidget(self.show_requests)
        filter_layout.addWidget(self.show_responses) 
        filter_layout.addWidget(self.show_errors)
        filter_layout.addWidget(self.show_status)
        filter_layout.addStretch(1)
        
        layout.addLayout(filter_layout)
        
        # Add buttons layout
        button_layout = QHBoxLayout()
        
        # Add save button
        save_button = RetroButton("Save Log")
        save_button.clicked.connect(self.save_log)
        button_layout.addWidget(save_button)
        
        # Add clear button
        clear_button = RetroButton("Clear")
        clear_button.clicked.connect(self.clear_log)
        button_layout.addWidget(clear_button)
        
        # Add test API button
        test_button = RetroButton("Test API")
        test_button.clicked.connect(self.test_api_connection)
        button_layout.addWidget(test_button)
        
        # Add close button
        close_button = RetroButton("Close")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Initialize with endpoint info
        self.set_endpoint("https://punch-card-api-v3.fly.dev")
    
    def set_endpoint(self, endpoint):
        """Set the API endpoint information."""
        self.endpoint_label.setText(f"Endpoint: {endpoint}")
        self.api_endpoint = endpoint
    
    def update_status(self, status):
        """Update the API status display."""
        self.status_label.setText(f"API Status: {status}")
        
        # Set color based on status
        color = COLORS['text'].name()
        if status == "Connected":
            color = COLORS['success'].name()
        elif status == "Fallback Mode":
            color = COLORS['warning'].name()
        elif status in ["Error", "Unavailable", "No API Key", "Timeout"]:
            color = COLORS['error'].name()
            
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                {get_font_css(bold=True, size=12)}
            }}
        """)
        
        # Log status change if filter enabled
        if self.show_status.isChecked():
            self.log(f"API Status changed to: {status}", "STATUS")
    
    def log(self, message, level="INFO"):
        """Add a message to the console with timestamp and level."""
        # Apply filtering based on level and checkbox settings
        if (level == "REQUEST" and not self.show_requests.isChecked() or
            level == "RESPONSE" and not self.show_responses.isChecked() or
            level == "ERROR" and not self.show_errors.isChecked() or
            level == "STATUS" and not self.show_status.isChecked()):
            return
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        level_color = {
            "INFO": "white",
            "REQUEST": "cyan",
            "RESPONSE": "lightgreen",
            "ERROR": "red",
            "STATUS": "yellow"
        }.get(level, "white")
        
        self.console.append(f'<span style="color: gray">[{timestamp}]</span> '
                          f'<span style="color: {level_color}">[{level}]</span> '
                          f'<span style="color: white">{message}</span>')
        self.console.verticalScrollBar().setValue(
            self.console.verticalScrollBar().maximum()
        )

    def log_request(self, endpoint, params=None):
        """Log an API request."""
        request_details = f"Request to {endpoint}"
        if params:
            request_details += f" with params: {params}"
        self.log(request_details, "REQUEST")
    
    def log_response(self, response_data, status_code=200):
        """Log an API response."""
        import json
        try:
            # Format JSON for better readability
            formatted_data = json.dumps(response_data, indent=2)
            self.log(f"Response (Status {status_code}):\n{formatted_data}", "RESPONSE")
        except:
            # Fallback for non-JSON responses
            self.log(f"Response (Status {status_code}): {response_data}", "RESPONSE")
    
    def log_error(self, error_message, exception=None):
        """Log an API error."""
        error_text = f"Error: {error_message}"
        if exception:
            error_text += f"\nException: {str(exception)}"
        self.log(error_text, "ERROR")

    def save_log(self):
        """Save the console log to a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_log_{timestamp}.txt"
        try:
            with open(filename, 'w') as f:
                f.write(self.console.toPlainText())
            self.log(f"Log saved to {filename}", "INFO")
        except Exception as e:
            self.log(f"Error saving log: {str(e)}", "ERROR")
    
    def clear_log(self):
        """Clear the console log."""
        self.console.clear()
        self.log("Console cleared", "INFO")
    
    def test_api_connection(self):
        """Test the API connection and log results."""
        self.log("Testing API connection...", "INFO")
        
        try:
            import requests
            self.log_request(f"{self.api_endpoint}/health")
            
            response = requests.get(f"{self.api_endpoint}/health", timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                self.log_response(data, response.status_code)
                
                if data.get('api', {}).get('api_key_exists', False):
                    self.update_status("Connected")
                else:
                    self.update_status("No API Key")
            else:
                self.log_response(f"Non-200 status code: {response.status_code}", response.status_code)
                self.update_status("Error")
                
        except requests.exceptions.Timeout:
            self.log_error("Request timed out after 3 seconds")
            self.update_status("Timeout")
        except Exception as e:
            self.log_error("Failed to connect to API", e)
            self.update_status("Unavailable")

class WiFiStatusWidget(QWidget):
    """Custom widget for displaying WiFi status with rectangular bars."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(30)
        self.setFixedHeight(22)
        self.setProperty("status", "connected")
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # Show pointer cursor on hover
        
        # Create popup menu for WiFi settings
        self.wifi_menu = QMenu(self)
        self.wifi_menu.setStyleSheet("""
            QMenu {
                background-color: black;
                color: white;
                border: 1px solid white;
                font-family: Courier New, monospace;
                font-size: 12px;
            }
            QMenu::item {
                padding: 4px 25px;
            }
            QMenu::item:selected {
                background-color: white;
                color: black;
            }
            QMenu::separator {
                height: 1px;
                background-color: #444444;
                margin: 4px 2px;
            }
        """)
        
        # Add menu items
        self.connected_action = self.wifi_menu.addAction("Connected")
        self.connected_action.setCheckable(True)
        self.connected_action.setChecked(True)
        self.connected_action.triggered.connect(lambda: self.set_wifi_status("connected"))
        
        self.weak_action = self.wifi_menu.addAction("Weak Signal")
        self.weak_action.setCheckable(True)
        self.weak_action.triggered.connect(lambda: self.set_wifi_status("weak"))
        
        self.disconnected_action = self.wifi_menu.addAction("Disconnected")
        self.disconnected_action.setCheckable(True)
        self.disconnected_action.triggered.connect(lambda: self.set_wifi_status("disconnected"))
        
        self.wifi_menu.addSeparator()
        self.wifi_menu.addAction("WiFi Settings...").triggered.connect(self.show_wifi_settings)
    
    def set_wifi_status(self, status):
        """Set the WiFi status and update checked actions."""
        self.setProperty("status", status)
        
        # Update checked states
        self.connected_action.setChecked(status == "connected")
        self.weak_action.setChecked(status == "weak")
        self.disconnected_action.setChecked(status == "disconnected")
        
        # Repaint the widget
        self.update()
    
    def show_wifi_settings(self):
        """Show more detailed WiFi settings dialog."""
        QMessageBox.information(self, "WiFi Settings", 
                               "This would show a detailed WiFi configuration dialog.\n"
                               "Currently in simulation mode only.")
    
    def mousePressEvent(self, event):
        """Handle mouse press to show the popup menu."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Get the window and calculate its right edge
            window = self.window()
            window_right_edge = window.mapToGlobal(QPoint(window.width(), 0)).x()
            
            # Get the menu width
            menu_width = self.wifi_menu.sizeHint().width()
            
            # Get position - x from current widget, y from menu bar bottom
            x_pos = self.mapToGlobal(QPoint(0, 0)).x()
            
            # Get parent menu bar to determine its bottom edge
            parent_menubar = self.parent()
            y_pos = parent_menubar.mapToGlobal(QPoint(0, parent_menubar.height() - 1)).y()  # Moved down 1 pixel
            
            # Make sure menu doesn't go off screen
            x_position = min(x_pos, window_right_edge - menu_width)
            
            # Show popup at the adjusted position
            self.wifi_menu.popup(QPoint(x_position, y_pos))
    
    def paintEvent(self, event):
        """Paint the WiFi status icon with rectangular bars."""
        super().paintEvent(event)
        
        # Get WiFi connection status
        status = self.property("status") or "disconnected"
        
        # Create painter for this widget
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Use white color for WiFi bars in all states
        color = QColor(255, 255, 255)
        
        # Determine number of bars based on connection status
        if status == "connected":
            bars = 3
        elif status == "weak":
            bars = 2
        else:  # Disconnected
            bars = 1
        
        # Configure painter
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))
        
        # Calculate position centered in widget
        center_x = self.width() // 2
        y_base = self.height() - 7  # Add more space at the bottom (was 6)
        
        # Calculate total width of all bars
        bar_width = 3
        spacing = 2
        total_width = (3 * bar_width) + (2 * spacing)  # Always show 3 bars (some empty)
        start_x = center_x - (total_width // 2)
        
        # Draw all three bars (filled or empty based on status)
        for i in range(3):
            x = start_x + (i * (bar_width + spacing))
            bar_height = 4 + (i * 2)  # Slightly shorter bars (was i*3)
            y = y_base - bar_height
            
            # If this bar should be filled based on status
            if i < bars:
                painter.setBrush(QBrush(color))
            else:
                # Draw outline for inactive bars
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(QPen(color, 0.8))
            
            painter.drawRect(x, y, bar_width, bar_height)
            painter.setPen(Qt.PenStyle.NoPen)  # Reset pen for next iteration


class InAppMenuBar(QWidget):
    """Custom in-app menu bar that simulates classic Mac menu bar appearance."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(22)
        
        # Set NO background styling in CSS - we'll handle all drawing manually
        self.setStyleSheet("""
            background-color: transparent;
            color: white;
            border: none;
        """)
        
        # Create main layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Zero margins to ensure full width
        self.layout.setSpacing(1)  # Reduced spacing between menu items
        
        # Left side - Menu items
        # Create left container to hold all menu buttons
        self.left_container = QWidget()
        self.left_layout = QHBoxLayout(self.left_container)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(1)  # Reduced spacing
        
        # Apple menu button
        self.apple_menu = QPushButton("▭")  # Rectangle symbol for a punch card
        self.apple_menu.setFlat(True)
        self.apple_menu.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: white;
                border: none;
                padding: 0px 8px;
                text-align: center;
                font-size: 22px;
                font-weight: normal;
                min-width: 24px;
                min-height: 22px;
                margin: 0px;
                margin-top: -4px;  /* Move up by adding negative top margin */
                line-height: 15px;  /* Reduced further to move symbol up */
                vertical-align: top;
                padding-top: 0px;  /* Remove top padding */
            }}
            QPushButton:hover {{
                background-color: white;
                color: black;
            }}
            QPushButton:pressed {{
                background-color: #444444;
                color: white;
            }}
        """)
        self.left_layout.addWidget(self.apple_menu)
        
        # Other menu buttons
        self.card_menu = self.create_menu_button("Punch Card")
        self.settings_menu = self.create_menu_button("Settings")
        self.console_menu = self.create_menu_button("Console")
        
        # Right side - Status indicators
        # Create right container to hold all status indicators
        self.right_container = QWidget()
        self.right_layout = QHBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(5)  # Spacing between WiFi and clock
        
        # Add a small spacer to push WiFi icon to the right
        right_spacer = QSpacerItem(10, 1, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.right_layout.addItem(right_spacer)
        
        # Create WiFi indicator using our custom widget
        self.wifi_status = WiFiStatusWidget(self)
        
        # Create clock button instead of label
        self.clock_button = QPushButton()
        self.clock_button.setFlat(True)
        self.clock_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: white;
                border: none;
                padding: 2px 8px;
                text-align: center;
                {get_font_css(size=11, bold=False)}
            }}
            QPushButton:hover {{
                background-color: white;
                color: black;
            }}
            QPushButton:pressed {{
                background-color: #444444;
                color: white;
            }}
        """)
        self.clock_button.setMinimumWidth(140)  # Ensure enough space for the date format
        
        # Add status indicators to right container
        self.right_layout.addWidget(self.wifi_status)
        self.right_layout.addWidget(self.clock_button)
        
        # Add left and right containers to main layout
        self.layout.addWidget(self.left_container)
        self.layout.addStretch(1)  # Push items to the sides
        self.layout.addWidget(self.right_container)
        
        # Create empty menus to be set up later
        self.apple_menu_popup = QMenu(self)
        self.card_menu_popup = QMenu(self)
        self.settings_menu_popup = QMenu(self)
        self.console_menu_popup = QMenu(self)
        self.notifications_popup = QMenu(self)
        
        # Connect menu buttons to popup functions
        self.apple_menu.clicked.connect(self.show_apple_menu)
        self.card_menu.clicked.connect(self.show_card_menu)
        self.settings_menu.clicked.connect(self.show_settings_menu)
        self.console_menu.clicked.connect(self.show_console_menu)
        self.clock_button.clicked.connect(self.show_notifications)
        
        # Setup clock timer
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)  # Update every second
        self.update_clock()
        
        # Update WiFi status periodically
        self.wifi_timer = QTimer(self)
        self.wifi_timer.timeout.connect(self.update_wifi_status)
        self.wifi_timer.start(5000)  # Check every 5 seconds
        self.update_wifi_status()

    def create_menu_button(self, text):
        """Create a button that looks like a menu item."""
        button = QPushButton(text)
        button.setFlat(True)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: white;
                border: none;
                padding: 2px 8px;
                text-align: center;
                {get_font_css(size=12)}
            }}
            QPushButton:hover {{
                background-color: white;
                color: black;
            }}
            QPushButton:pressed {{
                background-color: #444444;
                color: white;
            }}
        """)
        self.left_layout.addWidget(button)
        return button
    
    def setup_menu_actions(self, main_window):
        """Set up menu actions after the main window is fully initialized."""
        # Define common menu style
        menu_style = f"""
            QMenu {{
                background-color: black;
                color: white;
                border: 1px solid white;
                {get_font_css(size=12)}
            }}
            QMenu::item {{
                padding: 4px 25px;
            }}
            QMenu::item:selected {{
                background-color: white;
                color: black;
            }}
            QMenu::separator {{
                height: 1px;
                background-color: #444444;
                margin: 4px 2px;
            }}
        """
        
        # Apply styles to all menus
        self.apple_menu_popup.setStyleSheet(menu_style)
        self.card_menu_popup.setStyleSheet(menu_style)
        self.settings_menu_popup.setStyleSheet(menu_style)
        self.console_menu_popup.setStyleSheet(menu_style)
        self.notifications_popup.setStyleSheet(menu_style)
        
        # ---- Apple menu items ----
        about_action = self.apple_menu_popup.addAction("About This Punch Card")
        self.apple_menu_popup.addSeparator()
        sleep_action = self.apple_menu_popup.addAction("Sleep")
        restart_action = self.apple_menu_popup.addAction("Restart")
        shutdown_action = self.apple_menu_popup.addAction("Shut Down")
        
        # Connect Apple menu signals
        about_action.triggered.connect(main_window.show_about_dialog)
        sleep_action.triggered.connect(main_window.start_sleep_mode)
        restart_action.triggered.connect(main_window.restart_app)
        shutdown_action.triggered.connect(main_window.safe_shutdown)  # Use safe shutdown
        
        # ---- Punch Card menu ----
        display_message_action = self.card_menu_popup.addAction("Display Message")
        clear_card_action = self.card_menu_popup.addAction("Clear Card")
        self.card_menu_popup.addSeparator()
        card_settings_action = self.card_menu_popup.addAction("Card Dimensions...")
        
        # Connect Punch Card menu signals
        display_message_action.triggered.connect(main_window.start_display)
        if hasattr(main_window, 'punch_card'):
            clear_card_action.triggered.connect(main_window.punch_card.clear_grid)
        card_settings_action.triggered.connect(main_window.show_card_settings)
        
        # ---- Settings menu ----
        display_settings_action = self.settings_menu_popup.addAction("Display Settings...")
        api_settings_action = self.settings_menu_popup.addAction("API Settings...")
        self.settings_menu_popup.addSeparator()
        inline_settings_action = self.settings_menu_popup.addAction("Quick Settings Panel")
        
        # Connect Settings menu signals
        display_settings_action.triggered.connect(main_window.show_card_settings)  # Use card settings instead
        api_settings_action.triggered.connect(main_window.show_api_settings)
        inline_settings_action.triggered.connect(main_window.toggle_quick_settings)
        
        # ---- Console menu ----
        system_console_action = self.console_menu_popup.addAction("System Console")
        api_console_action = self.console_menu_popup.addAction("API Console")
        
        # Connect Console menu signals
        system_console_action.triggered.connect(lambda: main_window.console.show())
        api_console_action.triggered.connect(lambda: main_window.api_console.show())
        
        # ---- Notifications menu (for future use) ----
        self.notifications_popup.addAction("No New Notifications")
        self.notifications_popup.addSeparator()
        notification_settings = self.notifications_popup.addAction("Notification Settings...")
        clear_all = self.notifications_popup.addAction("Clear All")
        
        # These actions don't need to do anything yet - placeholder for future functionality
    
    def show_apple_menu(self):
        """Show the Apple menu popup."""
        # Get the absolute position of the menu bar's bottom edge
        pos = self.mapToGlobal(QPoint(0, self.height() - 1))  # Moved down 1 pixel (was -2)
        # No vertical adjustment needed - this lines up with the bottom border
        self.apple_menu_popup.popup(pos)
    
    def show_card_menu(self):
        """Show the Punch Card menu popup."""
        # Get horizontal position from the button but vertical from menu bar bottom
        x_pos = self.card_menu.mapToGlobal(QPoint(0, 0)).x()
        y_pos = self.mapToGlobal(QPoint(0, self.height() - 1)).y()  # Moved down 1 pixel (was -2)
        self.card_menu_popup.popup(QPoint(x_pos, y_pos))
    
    def show_settings_menu(self):
        """Show the Settings menu popup."""
        # Get horizontal position from the button but vertical from menu bar bottom
        x_pos = self.settings_menu.mapToGlobal(QPoint(0, 0)).x()
        y_pos = self.mapToGlobal(QPoint(0, self.height() - 1)).y()  # Moved down 1 pixel (was -2)
        self.settings_menu_popup.popup(QPoint(x_pos, y_pos))
    
    def show_console_menu(self):
        """Show the Console menu popup."""
        # Get horizontal position from the button but vertical from menu bar bottom
        x_pos = self.console_menu.mapToGlobal(QPoint(0, 0)).x()
        y_pos = self.mapToGlobal(QPoint(0, self.height() - 1)).y()  # Moved down 1 pixel (was -2)
        self.console_menu_popup.popup(QPoint(x_pos, y_pos))
    
    def show_notifications(self):
        """Show the notifications popup menu."""
        # Get the menu width to calculate proper positioning
        menu_width = self.notifications_popup.sizeHint().width()
        
        # Get the global position of the right edge of the window
        window = self.window()
        window_right_edge = window.mapToGlobal(QPoint(window.width(), 0)).x()
        
        # Get y position from menu bar bottom (moved down 1 pixel)
        y_pos = self.mapToGlobal(QPoint(0, self.height() - 1)).y()
        
        # Position the menu so its right edge aligns with the window right edge
        x_position = window_right_edge - menu_width
        
        # Create final position
        adjusted_pos = QPoint(x_position, y_pos)
        
        # Show the popup at the calculated position
        self.notifications_popup.popup(adjusted_pos)
    
    def update_clock(self):
        """Update the clock display with date and time in macOS style."""
        current_time = QDateTime.currentDateTime()
        # Use macOS style format: "Thu Apr 4 2:15 PM" or abbreviated "Thu 2:15 PM"
        day_name = current_time.toString("ddd")
        date_str = current_time.toString("MMM d")
        time_str = current_time.toString("h:mm AP")
        self.clock_button.setText(f"{day_name} {date_str} {time_str}")
    
    def update_wifi_status(self):
        """Update the WiFi status indicator."""
        # Simulate WiFi status check - in a real app, this would check actual connectivity
        import random
        status = random.choice(["connected", "weak", "disconnected"])
        
        # Update the custom WiFi widget with the new status
        self.wifi_status.set_wifi_status(status)
    
    def paintEvent(self, event):
        """Custom paint event to draw the menu bar with classic Mac styling."""
        # Create painter for drawing
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)  # Turn off antialiasing for crisp lines
        
        # Step 1: Draw the black background over everything
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        
        # Step 2: Let the base class handle child widgets
        painter.end()
        super().paintEvent(event)
        
        # Step 3: Create a new painter to draw on top of everything
        painter = QPainter(self)
        
        # Set up a pen for the white bottom border
        pen = QPen(QColor(255, 255, 255))
        pen.setWidth(1)
        pen.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        
        # Draw the line precisely at the bottom of the widget
        bottom_y = self.height() - 1
        painter.drawLine(0, bottom_y, self.width(), bottom_y)


class PunchCardDisplay(QMainWindow):
    """Main window for the minimalist punch card display application."""
    
    def __init__(self, punch_card=None):
        super().__init__()
        self.setWindowTitle("Punch Card Display")
        self.setMinimumSize(900, 600)
        
        # Store the punch card instance
        self.punch_card_instance = punch_card
        
        # Set window style and background color
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {COLORS['background'].name()};
                color: {COLORS['text'].name()};
                {get_font_css(bold=False, size=FONT_SIZE)}
            }}
        """)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # No margins to allow full-width menu bar
        self.main_layout.setSpacing(0)  # Reduce spacing to minimize shifts
        
        # ================== MENU BAR SECTION ==================
        # Add custom in-app menu bar
        self.menu_bar = InAppMenuBar(self)
        self.main_layout.addWidget(self.menu_bar)
        
        # Add spacer to separate menu bar from content
        menu_spacer = QWidget()
        menu_spacer.setFixedHeight(5)
        self.main_layout.addWidget(menu_spacer)
        
        # ================== CONTENT CONTAINER ==================
        # Create container for all content below menu bar (with proper margins)
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(0)
        self.main_layout.addWidget(content_container)
        
        # ================== TOP SECTION ==================
        # Create a container for the top section (message label) with fixed height
        top_section = QWidget()
        top_section.setFixedHeight(60)  # Fixed height to prevent layout shifts
        top_layout = QVBoxLayout(top_section)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)
        
        # Create message display label container with proper alignment
        self.message_container = QWidget()
        message_layout = QHBoxLayout(self.message_container)
        message_layout.setContentsMargins(0, 0, 0, 0)
        message_layout.setSpacing(0)
        
        # Create message display label - left aligned
        self.message_label = QLabel("")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.message_label.setStyleSheet(f"""
            {get_font_css(bold=False, size=FONT_SIZE+2)}
            color: {COLORS['text'].name()};
            padding: 10px 0px;
        """)
        self.message_label.setFont(get_font(bold=False, size=FONT_SIZE+2))
        
        # Add message label to container with proper alignment
        message_layout.addWidget(self.message_label, 1)  # 1 = stretch factor
        top_layout.addWidget(self.message_container)
        
        # Add the top section to the content layout
        content_layout.addWidget(top_section)
        
        # ================== MIDDLE SECTION (PUNCH CARD) ==================
        # Create a fixed container for the punch card to ensure it stays in place
        punch_card_container = QWidget()
        punch_card_layout = QVBoxLayout(punch_card_container)
        punch_card_layout.setContentsMargins(0, 0, 0, 0)
        punch_card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create punch card widget
        self.punch_card = PunchCardWidget()
        punch_card_layout.addWidget(self.punch_card)
        
        # Add the punch card container to the content layout with stretch factor
        content_layout.addWidget(punch_card_container, 1)  # 1 = stretch factor
        
        # ================== BOTTOM SECTION ==================
        # Create a container for the bottom section with fixed height
        # This ensures that the punch card position remains stable
        bottom_section = QWidget()
        bottom_section.setFixedHeight(80)  # Reduced from 190px since we removed buttons
        bottom_layout = QVBoxLayout(bottom_section)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(5)
        
        # Create status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.status_label.setStyleSheet(f"""
            {get_font_css(bold=False, size=FONT_SIZE)}
            color: {COLORS['text'].name()};
            padding: 5px 0px;
        """)
        self.status_label.setFont(get_font(bold=False, size=FONT_SIZE))
        self.status_label.setFixedHeight(40)
        bottom_layout.addWidget(self.status_label)
        
        # Create hardware status label for initialization phase
        self.hardware_status_label = QLabel("")
        self.hardware_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hardware_status_label.setStyleSheet(f"""
            {get_font_css(bold=False, size=FONT_SIZE-2)}
            color: {COLORS['text'].name()};
            padding: 5px;
        """)
        self.hardware_status_label.setFont(get_font(bold=False, size=FONT_SIZE-2))
        self.hardware_status_label.setFixedHeight(30)
        bottom_layout.addWidget(self.hardware_status_label)
        
        # Create keyboard shortcut hint label
        self.keyboard_hint_label = QLabel("Press [SPACE] to skip hardware detection and use virtual mode")
        self.keyboard_hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.keyboard_hint_label.setStyleSheet(f"""
            {get_font_css(italic=True, size=FONT_SIZE-2)}
            color: {QColor(150, 150, 150).name()};
            padding: 5px;
        """)
        self.keyboard_hint_label.setFixedHeight(30)
        bottom_layout.addWidget(self.keyboard_hint_label)
        
        # Create API status label
        self.api_status_label = QLabel("API: Unknown")
        self.api_status_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text'].name()};
                background-color: {COLORS['card_bg'].name()};
                padding: 3px 8px;
                border: 1px solid {COLORS['hole_outline'].name()};
                border-radius: 2px;
                {get_font_css(bold=True, size=10)}
            }}
        """)
        self.api_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.api_status_label.setVisible(False)  # Hide the API status label completely
        bottom_layout.addWidget(self.api_status_label)
        
        # Create a spacer widget to maintain spacing even when elements are hidden
        spacer = QWidget()
        spacer.setFixedHeight(10)
        bottom_layout.addWidget(spacer)
        
        # Create control buttons in a container with fixed height - all buttons now hidden
        self.button_container = QWidget()
        self.button_container.setVisible(False)  # Hide all buttons
        button_layout = QHBoxLayout(self.button_container)
        button_layout.setSpacing(10)
        
        self.start_button = RetroButton("DISPLAY MESSAGE")
        self.clear_button = RetroButton("CLEAR")
        self.api_button = RetroButton("API CONSOLE")
        self.exit_button = RetroButton("EXIT")
        
        self.start_button.clicked.connect(self.start_display)
        self.clear_button.clicked.connect(self.punch_card.clear_grid)
        self.api_button.clicked.connect(self.show_api_console)
        self.exit_button.clicked.connect(self.close)
        
        button_layout.addStretch(1)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.api_button)
        button_layout.addWidget(self.exit_button)
        button_layout.addStretch(1)
        
        self.button_container.setFixedHeight(60)
        bottom_layout.addWidget(self.button_container)
        
        # Add the bottom section to the content layout
        content_layout.addWidget(bottom_section)
        
        # Initialize variables
        self.showing_splash = True  # Start with splash screen
        self.led_delay = 100
        self.message_delay = 3000
        self.message_display_time = 5  # Default 5 seconds for message display
        self.current_message = ""
        self.current_char_index = 0
        self.running = False
        self.card_errors = {}
        self.hardware_detected = False
        self.splash_step = 0
        self.splash_delay = 50
        
        # Setup timers
        self.timer = QTimer()
        self.timer.timeout.connect(self.display_next_char)
        
        # Add a timer for message display time
        self.message_display_timer = QTimer()
        self.message_display_timer.setSingleShot(True)
        self.message_display_timer.timeout.connect(self.clear_message)
        
        # Create console and settings dialogs
        self.console = ConsoleWindow(self)
        self.settings = SettingsDialog(self)
        
        # Create API console window
        self.api_console = APIConsoleWindow(self)
        
        # Setup menu bar actions
        self.menu_bar.setup_menu_actions(self)
        
        # Initialize clock timer to update clock in menu bar
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)  # Update every second
        
        # Show console automatically
        self.console.show()
        
        # Initialize message generator
        self.message_generator = MessageGenerator()
        
        # Set up keyboard shortcuts
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Initialize auto-timer but don't start it yet
        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(self.generate_next_message)
        
        # Initialize hardware detector
        self.hardware_detector = HardwareDetector(self.console)
        
        # Add splash screen timer
        self.splash_timer = QTimer()
        self.splash_timer.timeout.connect(self.update_splash)
        self.splash_step = 0
        self.showing_splash = True
        self.hardware_check_complete = False
        self.countdown_seconds = 10
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        
        # Hardware status update timer
        self.hardware_status_timer = QTimer()
        self.hardware_status_timer.timeout.connect(self.update_hardware_status)
        self.hardware_status_timer.start(500)  # Check every 500ms
        
        # Add more variables for animation control
        self.hardware_detection_finished = False
        self.animation_started = False
        
        # Always start with splash screen
        self.start_splash_screen()
        
        # Load settings from file
        self.load_settings()
    
    def validate_led_state(self, row: int, col: int, expected_state: bool, phase: str):
        """Validate that an LED is in the expected state and fix if necessary."""
        actual_state = self.punch_card.grid[row][col]
        if actual_state != expected_state:
            self.console.log(f"LED STATE ERROR: LED at ({row},{col}) is {actual_state} but should be {expected_state} during {phase}", "ERROR")
            self.punch_card.set_led(row, col, expected_state)
            return False
        else:
            self.console.log(f"LED STATE VALID: LED at ({row},{col}) is correctly {expected_state} during {phase}", "INFO")
            return True
            
    def verify_top_left_corner(self, expected_state: bool, phase: str):
        """Verify that the top-left corner LED is in the expected state."""
        return self.validate_led_state(0, 0, expected_state, phase)
    
    def generate_next_message(self):
        """Generate and display the next random message."""
        if not self.running and not self.showing_splash:
            message = self.message_generator.generate_message()
            self.display_message(message)
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard shortcuts."""
        if event.key() == Qt.Key.Key_C:
            self.console.show()
        elif event.key() == Qt.Key.Key_A:
            self.api_console.show()
        elif event.key() == Qt.Key.Key_S:
            if self.settings.exec() == QDialog.DialogCode.Accepted:
                settings = self.settings.get_settings()
                self.led_delay = settings['led_delay']
                self.message_display_time = settings['message_display_time']
                self.timer.setInterval(self.led_delay)
                self.console.log(f"Settings updated: {settings}")
                self.console.log(f"Message display time set to {self.message_display_time} seconds", "INFO")
        elif event.key() == Qt.Key.Key_Space and self.showing_splash and not self.hardware_check_complete:
            # Skip hardware detection and use virtual mode
            self.auto_skip_hardware_detection()
    
    def update_status(self, status: str):
        """Update the status label with a new status message."""
        self.status_label.setText(status)
        
        # Make sure the status always has consistent styling
        QTimer.singleShot(10, self.align_message_with_card)
            
        self.console.log(f"Status: {status}")
    
    def display_message(self, message: str, source: str = "", delay: int = 100):
        """Display a message with optional source information."""
        # Update source information if provided (including API status)
        if source:
            # Check if source includes API status
            if "API:" in source:
                api_status = source.split("|")[0].strip().replace("API: ", "")
                self.update_api_status(api_status)
                
                # Update status label with just the serial number part
                if "|" in source:
                    serial_info = source.split("|")[1].strip()
                    self.status_label.setText(serial_info)
                else:
                    self.status_label.setText("")
            else:
                # Traditional source display (backward compatibility)
                self.status_label.setText(source)
        else:
            self.status_label.setText("")
            
        # Don't display messages during splash screen
        if self.showing_splash:
            self.console.log("Ignoring message display request during splash animation", "WARNING")
            return
            
        self.current_message = message.upper()
        self.current_char_index = 0
        self.punch_card.clear_grid()
        self.led_delay = delay
        self.timer.setInterval(delay)
        self.message_label.setText(message)
        
        # Ensure the message is always aligned with the punch card
        QTimer.singleShot(10, self.align_message_with_card)
        
        self.update_status(f"PROCESSING: {message}")
        self.start_display()
    
    def start_display(self):
        """Start displaying the message."""
        if not self.current_message:
            return  # Don't start if there's no message
            
        self.running = True
        self.start_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self.update_status("TYPING")
        self.timer.start(self.led_delay)
    
    def display_next_char(self):
        """Display the next character in the message."""
        if self.current_char_index < len(self.current_message) and self.current_char_index < self.punch_card.num_cols:
            # Clear the current column first
            for row in range(self.punch_card.num_rows):
                self.punch_card.set_led(row, self.current_char_index, False)
            
            char = self.current_message[self.current_char_index]
            self._display_character(char, self.current_char_index)
            self.update_status(f"DISPLAYING: {self.current_message[:self.current_char_index+1]}")
            self.current_char_index += 1
        else:
            # Display complete - Keep the message displayed for the configured time
            self.timer.stop()
            self.running = False
            self.update_status("DISPLAY COMPLETE")
            
            # Start the message display timer
            display_time_ms = self.message_display_time * 1000  # Convert seconds to milliseconds
            self.console.log(f"Message will be displayed for {self.message_display_time} seconds", "INFO")
            self.message_display_timer.start(display_time_ms)
            
            # Keep buttons disabled until the message display time is complete
            self.start_button.setEnabled(False)
            self.clear_button.setEnabled(False)
    
    def _display_character(self, char: str, col: int):
        """Display a character on the punch card grid."""
        # Convert to uppercase
        char = char.upper()
        
        # Clear the column first
        for row in range(self.punch_card.num_rows):
            self.punch_card.set_led(row, col, False)
            self.console.log(f"LED: Cleared row {row}, col {col}", "LED")
        
        # Log the character being displayed
        self.console.log(f"Displaying character '{char}' in column {col}", "INFO")
        
        # Handle different character types
        if char.isalpha():
            # Letters
            if char in "ABCDEFGHI":
                # A-I: row 12 + digit 1-9
                self.punch_card.set_led(0, col, True)  # Row 12
                digit = ord(char) - ord('A') + 1
                self.punch_card.set_led(digit + 2, col, True)  # Convert to punch card row
                self.console.log(f"LED: Row 12 + Row {digit + 2} for '{char}'", "LED")
            elif char in "JKLMNOPQR":
                # J-R: row 11 + digit 1-9
                self.punch_card.set_led(1, col, True)  # Row 11
                digit = ord(char) - ord('J') + 1
                self.punch_card.set_led(digit + 2, col, True)  # Convert to punch card row
                self.console.log(f"LED: Row 11 + Row {digit + 2} for '{char}'", "LED")
            else:
                # S-Z: row 0 + digit 2-9
                self.punch_card.set_led(2, col, True)  # Row 0
                digit = ord(char) - ord('S') + 2
                if digit <= 9:
                    self.punch_card.set_led(digit + 2, col, True)  # Convert to punch card row
                    self.console.log(f"LED: Row 0 + Row {digit + 2} for '{char}'", "LED")
        
        elif char.isdigit():
            # Digits 0-9
            digit = int(char)
            if digit == 0:
                self.punch_card.set_led(2, col, True)  # Row 0
                self.console.log(f"LED: Row 0 for '0'", "LED")
            else:
                self.punch_card.set_led(digit + 2, col, True)  # Convert to punch card row
                self.console.log(f"LED: Row {digit + 2} for '{digit}'", "LED")
        
        elif char == ' ':
            # Space - no punches
            self.console.log("LED: Space character - no punches", "LED")
            pass
        
        else:
            # Special characters - simplified version
            self.punch_card.set_led(1, col, True)  # Row 11
            self.punch_card.set_led(2, col, True)  # Row 0
            self.console.log(f"LED: Special character '{char}' - Row 11 + Row 0", "LED")

    def update_card_dimensions(self, settings: Dict[str, Any]):
        """Update the punch card dimensions with new settings."""
        self.punch_card.update_dimensions(settings)
        self.console.log(f"Card dimensions updated: {settings}")

    def start_splash_screen(self):
        """Start the splash screen animation with simplified flow."""
        # Set initial state
        self.showing_splash = True
        self.message_label.setText("")
        self.status_label.setText("INITIALIZING SYSTEM...")
        
        # Disable buttons during splash
        for button in [self.start_button, self.clear_button, self.exit_button]:
            button.setEnabled(False)
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['button_bg'].name()};
                    color: {COLORS['button_text'].name()};
                    border: 1px solid {COLORS['hole_outline'].name()};
                    padding: 6px 12px;
                    {get_font_css(size=12)}
                    border-radius: 3px;
                    opacity: 0.5;
                }}
            """)
        
        # Skip hardware detection completely - always use virtual mode
        self.hardware_detector.enable_virtual_mode()
        self.hardware_check_complete = True
        self.hardware_detection_finished = True
        
        # Reset animation flags
        self.animation_started = False
        self.splash_step = 0
        self.splash_progress = 0
        
        # Fill the entire card with holes to prepare for the animation
        # This ensures our animation of clearing holes is visible
        for row in range(NUM_ROWS):
            for col in range(NUM_COLS):
                self.punch_card.set_led(row, col, True)
        
        # Load the punch card sounds if not already loaded
        self.load_punch_card_sounds()
        
        # Start the splash screen animation timer
        self.splash_timer = QTimer()
        self.splash_timer.timeout.connect(self.update_splash)
        self.splash_timer.start(100)  # Update every 100ms
        
        # Console log for debugging only
        self.console.log("Splash screen started - filling card with holes first", "INFO")
    
    def update_countdown(self):
        """Update the countdown timer during hardware detection."""
        self.countdown_seconds -= 1
        
        # Update the keyboard hint with the remaining seconds
        self.keyboard_hint_label.setText(f"Press [SPACE] to skip hardware detection ({self.countdown_seconds}s)")
        
        # If countdown has reached zero or hardware detection is already complete
        if self.countdown_seconds <= 0 or self.hardware_detector.detection_complete:
            # Auto-skip when countdown reaches zero
            self.auto_skip_hardware_detection()
    
    def auto_skip_hardware_detection(self):
        """Skip hardware detection and enable virtual mode."""
        # Stop the countdown timer 
        self.countdown_timer.stop()
        
        # Only proceed if hardware detection is not already complete
        if not self.hardware_check_complete:
            self.console.log("Auto-skipping hardware detection - enabling virtual mode", "WARNING")
            
            # Force the hardware detector into virtual mode
            self.hardware_detector.enable_virtual_mode()
            
            # Set ALL the necessary flags to ensure we can proceed
            self.hardware_check_complete = True
            self.hardware_detection_finished = True
            
            # Update hardware status message
            self.hardware_status_label.setText("Hardware detection skipped - using virtual mode")
            self.hardware_status_label.setStyleSheet(f"""
                {get_font_css(bold=False, size=FONT_SIZE-2)}
                color: {COLORS['warning'].name()};
                padding: 5px;
            """)
            
            # Update the keyboard hint message
            self.keyboard_hint_label.setText("Hardware virtualization will be used instead")
            self.keyboard_hint_label.setStyleSheet(f"""
                {get_font_css(italic=True, size=FONT_SIZE-2)}
                color: {COLORS['warning'].name()};
                padding: 5px;
            """)
            
            # Start the animation immediately
            self.start_animation()
    
    def start_animation(self):
        """Start the splash animation after hardware detection is complete."""
        # If the animation is already started, don't restart it
        if self.animation_started:
            return
            
        # Set animation as started regardless of hardware detection status
        self.animation_started = True
        self.status_label.setText("STARTING ANIMATION...")
        self.console.log("Starting splash animation", "INFO")
        
        # Make sure hardware detection is considered finished
        self.hardware_detection_finished = True
        self.hardware_check_complete = True
        
        # Ensure the hardware detector is in a valid state
        if not self.hardware_detector.detection_complete:
            self.hardware_detector.enable_virtual_mode()
        
        # Start the splash animation timer
        self.splash_timer.start(100)
    
    def update_hardware_status(self):
        """Update the hardware status label."""
        # If hardware detection is complete and animation hasn't started yet
        if self.hardware_detector.detection_complete and not self.animation_started:
            # Show hardware detection results
            pi_status = self.hardware_detector.raspberry_pi_status
            led_status = self.hardware_detector.led_controller_status
            
            # Format status for display
            pi_color = "green" if pi_status == "Connected" else "yellow" if pi_status == "Virtual Mode" else "red"
            led_color = "green" if led_status == "Ready" else "yellow" if led_status == "Virtual Mode" else "red"
            
            # Update the hardware status label with colored status indicators
            self.hardware_status_label.setText(
                f'Raspberry Pi: <span style="color:{pi_color};">{pi_status}</span>, ' +
                f'LED Controller: <span style="color:{led_color};">{led_status}</span>'
            )
            
            # Set flags and start animation if not already started
            if not self.hardware_check_complete:
                self.hardware_check_complete = True
                self.hardware_detection_finished = True
                mode_type = "hardware" if not self.hardware_detector.using_virtual_mode else "virtual"
                self.console.log(f"Hardware detection complete - using {mode_type} mode", "INFO")
                
                # Update keyboard hint to show the active mode
                self.keyboard_hint_label.setText(f"System ready - using {mode_type.upper()} mode")
                color = QColor(100, 200, 100) if mode_type == "hardware" else QColor(200, 200, 100)
                self.keyboard_hint_label.setStyleSheet(f"""
                    {get_font_css(italic=True, size=FONT_SIZE-2)}
                    color: {color.name()};
                    padding: 5px;
                """)
                
                # Start the animation
                self.start_animation()
                
        # If hardware detection is still in progress and animation hasn't started
        elif not self.hardware_detector.detection_complete and not self.animation_started:
            # Hardware detection still in progress - update status
            self.hardware_status_label.setText(
                f'Raspberry Pi: <span style="color:yellow;">Detecting...</span>, ' +
                f'LED Controller: <span style="color:yellow;">Waiting...</span>'
            )
    
    def update_splash(self):
        """Startup animation that punches all holes first, then clears them diagonally."""
        if not self.showing_splash:
            return
        
        # Calculate progress percentage (0-100)
        self.splash_progress += 5
        progress_percent = self.splash_progress / 100
        
        # Update status text in phases
        if self.splash_progress < 25:
            self.status_label.setText("INITIALIZING...")
        elif self.splash_progress < 50:
            self.status_label.setText("STARTING UP...")
        elif self.splash_progress < 75:
            self.status_label.setText("ALMOST READY...")
        elif self.splash_progress < 95:
            self.status_label.setText("SYSTEM READY")
        else:
            # Completed animation
            self.splash_timer.stop()
            
            # Play final sound
            if hasattr(self, 'card_eject_sound'):
                self.card_eject_sound.play()
                
            self.complete_splash_screen()
            return
        
        # Phase 1 (0-30%): Punch all holes in the card
        if self.splash_progress <= 30:
            # Calculate how many holes to punch based on progress
            total_cells = NUM_ROWS * NUM_COLS
            cells_to_punch = int(total_cells * (self.splash_progress / 30))
            
            # Play card insert sound at the beginning
            if self.splash_progress == 5 and hasattr(self, 'card_insert_sound'):
                self.card_insert_sound.play()
            
            # Play punch sound every few frames
            if hasattr(self, 'punch_sound') and self.splash_progress % 10 == 0:
                self.play_punch_sound()
                
            # Punch holes in order (row by row)
            cells_punched = 0
            for row in range(NUM_ROWS):
                for col in range(NUM_COLS):
                    if cells_punched < cells_to_punch and not self.punch_card.grid[row][col]:
                        self.punch_card.set_led(row, col, True)
                        cells_punched += 1
                        if cells_punched >= cells_to_punch:
                            break
                if cells_punched >= cells_to_punch:
                    break
        
        # Phase 2 (31-100%): Clear holes diagonally with 12-hole width
        else:
            # Calculate total steps needed for diagonal pattern
            total_steps = NUM_ROWS + NUM_COLS - 1
            
            # Map 31-100% progress to 0-total_steps
            clear_progress = ((self.splash_progress - 30) / 70) * total_steps
            current_step = int(clear_progress)
            
            # Play eject sound periodically
            if self.splash_progress % 15 == 0 and hasattr(self, 'card_eject_sound'):
                self.card_eject_sound.play()
            
            # We'll clear diagonals from top-left to bottom-right
            # Each diagonal passes through cells where row+col = constant
            for row in range(NUM_ROWS):
                for col in range(NUM_COLS):
                    if row + col <= current_step:
                        # Clear this diagonal and all previous ones
                        self.punch_card.set_led(row, col, False)
        
        # Force a repaint
        self.punch_card.update()
    
    def complete_splash_screen(self):
        """Complete the splash screen transition and prepare for normal operation."""
        self.showing_splash = False
        
        # Make sure countdown timer is stopped
        try:
            if hasattr(self, 'countdown_timer') and self.countdown_timer.isActive():
                self.countdown_timer.stop()
        except Exception as e:
            self.console.log(f"Non-critical error stopping countdown timer: {str(e)}", "WARNING")
        
        # First update the status text while other elements are hidden
        self.status_label.setText("READY")
        self.console.log("Splash screen completed, ready for operation", "INFO")
        
        # Remove the mode type variable and display only "SYSTEM READY"
        self.message_label.setText("SYSTEM READY")
        self.message_label.setStyleSheet(f"""
            {get_font_css(bold=False, size=FONT_SIZE+2)}
            color: {COLORS['text'].name()};
            padding: 10px 0px;
        """)
        
        # Ensure message label aligns with the left edge of the punch card
        QTimer.singleShot(10, self.align_message_with_card)
        
        # Hide hardware-specific status indicators by making them transparent
        # but keep their space in the layout
        try:
            if hasattr(self, 'hardware_status_label'):
                self.hardware_status_label.setStyleSheet(f"""
                    {get_font_css(bold=False, size=FONT_SIZE-2)}
                    color: {COLORS['background'].name()};
                    padding: 5px;
                """)
        except Exception as e:
            self.console.log(f"Non-critical error hiding hardware status: {str(e)}", "WARNING")
        
        try: 
            if hasattr(self, 'keyboard_hint_label'):
                self.keyboard_hint_label.setStyleSheet(f"""
                    {get_font_css(italic=True, size=FONT_SIZE-2)}
                    color: {COLORS['background'].name()};
                    padding: 5px;
                """)
        except Exception as e:
            self.console.log(f"Non-critical error hiding keyboard hint: {str(e)}", "WARNING")
        
        # Restore button styles
        for button in [self.start_button, self.clear_button, self.exit_button]:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['button_bg'].name()};
                    color: {COLORS['button_text'].name()};
                    border: 1px solid {COLORS['hole_outline'].name()};
                    padding: 6px 12px;
                    {get_font_css(size=12)}
                    border-radius: 3px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['button_hover'].name()};
                }}
            """)
            button.setEnabled(True)
        
        # Wait a significant time before starting auto messages
        # This gives the user time to see the initial state
        QTimer.singleShot(5000, lambda: self.auto_timer.start(5000))
    
    def resizeEvent(self, event):
        """Handle resize events to ensure message label aligns with punch card."""
        super().resizeEvent(event)
        
        # Update message label alignment when window is resized
        # We need a small delay to ensure the punch card widget has been properly laid out
        QTimer.singleShot(20, self.align_message_with_card)
    
    def align_message_with_card(self):
        """Align the message label with the left edge of the punch card."""
        # Calculate the exact left edge position of the punch card
        card_margin = (self.width() - self.punch_card.card_width) // 2
        
        # We need to account for the main layout's margins as well
        main_left_margin = self.main_layout.contentsMargins().left()
        
        # Calculate the exact margin needed for alignment
        left_margin = card_margin - main_left_margin
        
        # Update the message container margins
        self.message_container.layout().setContentsMargins(left_margin, 0, 0, 0)
        
        # Update the status label alignment and margins
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.status_label.setStyleSheet(f"""
            {get_font_css(bold=False, size=FONT_SIZE)}
            color: {COLORS['text'].name()};
            padding: 5px 0px;
            margin-left: {left_margin}px;
        """)
        
        # Debug logging to help diagnose alignment issues
        self.console.log(f"Alignment: window={self.width()}, card={self.punch_card.card_width}, " +
                         f"card_margin={card_margin}, main_margin={main_left_margin}, " +
                         f"applied_margin={left_margin}", "INFO")

    def update_api_status(self, status: str):
        """Update the API status display."""
        # API status label was removed from UI, so just log the status
        self.console.log(f"API Status: {status}", "INFO")
        
        # Update API console window if it exists
        if hasattr(self, 'api_console'):
            self.api_console.update_status(status)

    def show_api_console(self):
        """Show the API console window."""
        self.api_console.show()
        self.api_console.raise_()
        self.api_console.activateWindow()

    def clear_message(self):
        """Clear the message after the display time has elapsed."""
        # Clear the entire grid
        self.punch_card.clear_grid()
        
        # Enable buttons
        self.start_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        
        self.console.log("Message display time elapsed, cleared display", "INFO")
        self.update_status("READY")

    def load_settings(self):
        """Load settings from the settings file."""
        try:
            # Try different possible locations for the settings file
            settings_file_paths = [
                "punch_card_settings.json",
                "../punch_card_settings.json",
                "../../punch_card_settings.json",
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../punch_card_settings.json")
            ]
            
            settings_data = None
            settings_path = None
            
            for path in settings_file_paths:
                try:
                    if os.path.exists(path):
                        with open(path, 'r') as f:
                            settings_data = json.load(f)
                            settings_path = path
                            break
                except Exception as e:
                    self.console.log(f"Error loading settings from {path}: {str(e)}", "ERROR")
            
            if settings_data:
                self.console.log(f"Loaded settings from {settings_path}", "INFO")
                
                # Load message display time
                if 'message_display_time' in settings_data:
                    self.message_display_time = settings_data['message_display_time']
                    self.console.log(f"Message display time loaded: {self.message_display_time} seconds", "INFO")
                
                # Load other settings
                if 'display_delay' in settings_data:
                    self.led_delay = settings_data['display_delay']
                    self.timer.setInterval(self.led_delay)
                    self.console.log(f"LED delay loaded: {self.led_delay} ms", "INFO")
                
                # Update settings dialog values
                if hasattr(self, 'settings'):
                    self.settings.led_delay.setValue(self.led_delay)
                    self.settings.message_display_time.setValue(self.message_display_time)
            else:
                self.console.log("No settings file found, using defaults", "WARNING")
        
        except Exception as e:
            self.console.log(f"Error loading settings: {str(e)}", "ERROR")

    def update_clock(self):
        """Update the clock in the menu bar."""
        if hasattr(self, 'menu_bar'):
            self.menu_bar.update_clock()
            
    def restart_app(self):
        """Restart the application."""
        QMessageBox.information(self, "Restart", "The application will now restart.")
        self.close()
        
    def safe_shutdown(self):
        """Safely shut down the application."""
        self.close()
        
    def show_card_settings(self):
        """Show the card dimensions settings tab."""
        self.update_status("Opening Card Settings...")
        self.settings.setCurrentIndex(2)  # Assuming card settings is on tab index 2
        self.settings.exec()
        
    def show_api_settings(self):
        """Show the API settings tab."""
        self.update_status("Opening API Settings...")
        # Create and show the settings dialog with API tab selected
        from src.display.settings_dialog import SettingsDialog
        settings_dialog = SettingsDialog(self)
        settings_dialog.tab_widget.setCurrentIndex(2)  # OpenAI API tab index
        settings_dialog.exec()
        
    def show_about_dialog(self):
        """Show about dialog with application information."""
        self.update_status("Showing About Information...")
        QMessageBox.about(self, "About This Punch Card",
                         "<h3>Punch Card Simulator v1.0.2</h3>"
                         "<p>A minimalist punch card display system with "
                         "authentic IBM punch card specifications.</p>"
                         "<p>GitHub: <a href='https://github.com/griffingilreath/Punch-Card-Project'>"
                         "github.com/griffingilreath/Punch-Card-Project</a></p>"
                         "<p>© 2023-2025 Griffin Gilreath</p>"
                         "<p><small>Built with PyQt6 and a passion for digital history</small></p>")
                         
    def toggle_quick_settings(self):
        """Toggle the quick settings panel."""
        self.update_status("Quick Settings Panel (Not Yet Implemented)")
        QMessageBox.information(self, "Quick Settings", 
                               "This would show a quick settings panel.\n"
                               "Feature not yet implemented.")
                               
    def show_settings_dialog(self):
        """Show the settings dialog."""
        self.update_status("Opening Settings...")
        # Create and show the settings dialog
        settings_dialog = SettingsDialog(self)
        if settings_dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_ui_from_settings()

    def start_sleep_mode(self):
        """Start sleep mode for the punch card.
        
        This will play the startup animation in reverse and mirrored horizontally,
        moving from top right to bottom left, then pause all visible processes.
        """
        # Don't start sleep if we're already sleeping
        if hasattr(self, 'is_sleeping') and self.is_sleeping:
            return
            
        # Set sleep state
        self.is_sleeping = True
        self.update_status("GOING TO SLEEP...")
        self.console.log("Entering sleep mode", "INFO")
        
        # Stop ALL ongoing processes and timers
        for timer_attr in ['timer', 'display_timer', 'message_display_timer', 'auto_timer']:
            if hasattr(self, timer_attr) and getattr(self, timer_attr).isActive():
                getattr(self, timer_attr).stop()
                self.console.log(f"Stopped {timer_attr} for sleep mode", "INFO")
        
        # Reset any running animation flags
        self.running = False
        
        # Clear the card first
        self.punch_card.clear_grid()
        
        # Load the punch card sounds if not already loaded
        self.load_punch_card_sounds()
        
        # Start the sleep animation
        self.sleep_step = 0
        self.sleep_timer = QTimer(self)
        self.sleep_timer.timeout.connect(self.update_sleep_animation)
        self.sleep_timer.start(100)  # Same interval as startup animation
    
    def load_punch_card_sounds(self):
        """Load punch card sounds for animations."""
        try:
            from PyQt6.QtMultimedia import QSoundEffect
            from PyQt6.QtCore import QUrl
            import os
            
            self.console.log("Loading punch card sounds...", "INFO")
            
            # Define sound paths relative to the project
            sound_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets/sounds")
            
            # Create sound effects if they don't exist
            if not hasattr(self, 'punch_sound'):
                self.punch_sound = QSoundEffect()
                punch_path = os.path.join(sound_dir, "punch.wav")
                if os.path.exists(punch_path):
                    self.punch_sound.setSource(QUrl.fromLocalFile(punch_path))
                    self.punch_sound.setVolume(0.5)
                    self.console.log(f"Loaded punch sound from {punch_path}", "INFO")
                else:
                    self.console.log(f"Sound file not found: {punch_path}", "WARNING")
            
            if not hasattr(self, 'card_insert_sound'):
                self.card_insert_sound = QSoundEffect()
                insert_path = os.path.join(sound_dir, "card_insert.wav")
                if os.path.exists(insert_path):
                    self.card_insert_sound.setSource(QUrl.fromLocalFile(insert_path))
                    self.card_insert_sound.setVolume(0.5)
                    self.console.log(f"Loaded card insert sound from {insert_path}", "INFO")
                else:
                    self.console.log(f"Sound file not found: {insert_path}", "WARNING")
            
            if not hasattr(self, 'card_eject_sound'):
                self.card_eject_sound = QSoundEffect()
                eject_path = os.path.join(sound_dir, "card_eject.wav")
                if os.path.exists(eject_path):
                    self.card_eject_sound.setSource(QUrl.fromLocalFile(eject_path))
                    self.card_eject_sound.setVolume(0.5)
                    self.console.log(f"Loaded card eject sound from {eject_path}", "INFO")
                else:
                    self.console.log(f"Sound file not found: {eject_path}", "WARNING")
                    
        except ImportError:
            self.console.log("QSoundEffect not available, running without sound", "WARNING")
        except Exception as e:
            self.console.log(f"Error loading sounds: {str(e)}", "ERROR")
    
    def play_punch_sound(self):
        """Play the punch card sound if available."""
        if hasattr(self, 'punch_sound') and hasattr(self.punch_sound, 'play'):
            self.punch_sound.play()
    
    def update_sleep_animation(self):
        """Update the sleep animation (reverse of startup animation)."""
        if not hasattr(self, 'is_sleeping') or not self.is_sleeping:
            return
            
        # Calculate total steps needed to cover the entire card
        total_steps = NUM_COLS + NUM_ROWS - 1
        
        # Log animation progress
        self.console.log(f"Sleep animation step: {self.sleep_step} of {total_steps*2 + 12}", "INFO")
        
        # Phase 1: Starting punch pattern (reverse of startup clear phase)
        if self.sleep_step < total_steps:
            # Make sure the bottom-right corner is explicitly set as the first step
            if self.sleep_step == 0:
                # Play card insert sound at the beginning of animation
                if hasattr(self, 'card_insert_sound'):
                    self.card_insert_sound.play()
                    
                # Start animation from bottom-right (reverse of top-left in startup)
                self.console.log(f"LED: Starting from bottom-right corner", "LED")
                self.punch_card.set_led(NUM_ROWS-1, NUM_COLS-1, True)
            
            # Set the LEDs in the current diagonal (working backward)
            led_changed = False
            for row in range(NUM_ROWS):
                # Calculate column from bottom-right (NUM_COLS-1) working back
                # Instead of working from 0 forward in startup animation
                col = (NUM_COLS - 1) - (self.sleep_step - ((NUM_ROWS-1) - row))
                if 0 <= col < NUM_COLS and 0 <= row < NUM_ROWS:
                    # Skip bottom-right corner as we already set it
                    if not (row == NUM_ROWS-1 and col == NUM_COLS-1):
                        self.console.log(f"LED: Setting row {row}, col {col} ON (Sleep Phase 1)", "LED")
                        self.punch_card.set_led(row, col, True)
                        led_changed = True
            
            # Play punch sound if any LEDs changed
            if led_changed and self.sleep_step % 3 == 0:  # Play every 3rd step
                self.play_punch_sound()
        
        # Phase 2: Rolling diagonal with 12-column width (reverse of startup phase 2)
        elif self.sleep_step < total_steps * 2:
            current_step = self.sleep_step - total_steps
            
            # Set new LEDs ON in the current diagonal (moving from bottom-right to top-left)
            on_changed = False
            for row in range(NUM_ROWS):
                # Reverse column calculation from startup animation
                col = (NUM_COLS - 1) - (current_step - ((NUM_ROWS-1) - row))
                if 0 <= col < NUM_COLS and 0 <= row < NUM_ROWS:
                    self.console.log(f"LED: Setting row {row}, col {col} ON (Sleep Phase 2)", "LED")
                    self.punch_card.set_led(row, col, True)
                    on_changed = True
            
            # Clear trailing LEDs that are 12 columns behind (opposite of startup)
            off_changed = False
            trailing_step = max(0, current_step - 12)
            for row in range(NUM_ROWS):
                # Reverse column calculation for trailing clear
                col = (NUM_COLS - 1) - (trailing_step - ((NUM_ROWS-1) - row))
                if 0 <= col < NUM_COLS and 0 <= row < NUM_ROWS:
                    self.console.log(f"LED: Setting row {row}, col {col} OFF (Sleep Phase 2 trailing)", "LED")
                    self.punch_card.set_led(row, col, False)
                    off_changed = True
            
            # Play sounds
            if on_changed and self.sleep_step % 3 == 0:  # Every 3rd step for new holes
                self.play_punch_sound()
            elif off_changed and self.sleep_step % 5 == 0:  # Every 5th step for clearing holes
                if hasattr(self, 'card_eject_sound'):
                    self.card_eject_sound.play()
        
        # Phase 3: Clear the final pattern (reverse of startup phase 3)
        elif self.sleep_step < total_steps * 2 + 12:
            current_clear_step = self.sleep_step - (total_steps * 2)
            
            # Calculate which LEDs to clear next (moving toward top-left)
            led_changed = False
            for row in range(NUM_ROWS):
                # Reverse column calculation
                col = (NUM_COLS - 1) - (current_clear_step - ((NUM_ROWS-1) - row)) - (total_steps - 12)
                if 0 <= col < NUM_COLS and 0 <= row < NUM_ROWS:
                    self.console.log(f"LED: Setting row {row}, col {col} OFF (Sleep Phase 3)", "LED")
                    self.punch_card.set_led(row, col, False)
                    led_changed = True
            
            # Play eject sound if any LEDs changed
            if led_changed and self.sleep_step % 4 == 0:  # Play every 4th step
                if hasattr(self, 'card_eject_sound'):
                    self.card_eject_sound.play()
        
        # Animation completed
        else:
            # Play final card eject sound
            if hasattr(self, 'card_eject_sound'):
                self.card_eject_sound.play()
                
            # Stop the timer
            self.sleep_timer.stop()
            self.console.log("Sleep animation completed, system is now sleeping", "INFO")
            
            # Clear all LEDs
            self.punch_card.clear_grid()
            
            # Update status
            self.update_status("SLEEPING")
            
            # Create wake button if it doesn't exist
            if not hasattr(self, 'wake_button'):
                self.wake_button = RetroButton("WAKE", self)
                self.wake_button.setStyleSheet("""
                    background-color: rgba(50, 50, 50, 0.7);
                    color: white;
                    border: 1px solid white;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-size: 16px;
                """)
                self.wake_button.clicked.connect(self.wake_from_sleep)
                
                # Calculate center position
                button_width = 120
                button_height = 40
                center_x = (self.width() - button_width) // 2
                center_y = (self.height() - button_height) // 2
                
                self.wake_button.setGeometry(center_x, center_y, button_width, button_height)
                self.wake_button.show()
                
            return
        
        # Force a repaint
        self.punch_card.update()
        self.sleep_step += 1
    
    def wake_from_sleep(self):
        """Wake up from sleep mode."""
        if not hasattr(self, 'is_sleeping') or not self.is_sleeping:
            return
        
        # Remove the wake button
        if hasattr(self, 'wake_button'):
            self.wake_button.deleteLater()
            delattr(self, 'wake_button')
        
        # Update state
        self.is_sleeping = False
        self.update_status("WAKING UP...")
        self.console.log("Waking from sleep mode", "INFO")
        
        # Play card insert sound
        if hasattr(self, 'card_insert_sound'):
            self.card_insert_sound.play()
        
        # Reset animation-related flags to ensure animation plays
        self.showing_splash = True
        self.splash_step = 0
        self.splash_progress = 0
        self.animation_started = False  # Reset this flag to ensure animation plays
        
        # Fill the entire card with holes to prepare for the animation
        for row in range(NUM_ROWS):
            for col in range(NUM_COLS):
                self.punch_card.set_led(row, col, True)
        
        # Run the startup animation - this will automatically be followed by messages
        self.start_animation()
        
        # After animation delay, handle message display
        QTimer.singleShot(5000, self.post_wake_setup)
    
    def post_wake_setup(self):
        """Actions to perform after wake sequence completes."""
        self.update_status("READY")
        
        # Update the message label to only display "SYSTEM READY"
        self.message_label.setText("SYSTEM READY")
        self.message_label.setStyleSheet(f"""
            {get_font_css(bold=False, size=FONT_SIZE+2)}
            color: {COLORS['text'].name()};
            padding: 10px 0px;
        """)
        
        # Ensure message label aligns with the left edge of the punch card
        QTimer.singleShot(10, self.align_message_with_card)
        
        # Restart auto message timer
        QTimer.singleShot(2000, lambda: self.auto_timer.start(5000))


def run_gui_app():
    """
    Main entry point for the GUI application.
    """
    import sys
    from PyQt6.QtWidgets import QApplication
    from src.core.punch_card import PunchCard
    
    try:
        # Initialize application
        app = QApplication.instance() if QApplication.instance() else QApplication(sys.argv)
        punch_card = PunchCard()
        gui = PunchCardDisplay(punch_card)
        gui.show()
        
        # Run application
        sys.exit(app.exec())
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception(f"Error in GUI application: {e}")
        print(f"\nAn error occurred: {e}")

# If run directly, start the GUI application
if __name__ == "__main__":
    run_gui_app() 