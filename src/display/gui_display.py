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

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QStackedLayout,
                            QSizePolicy, QFrame, QDialog, QTextEdit, QSpinBox,
                            QCheckBox, QFormLayout, QGroupBox)
from PyQt6.QtCore import Qt, QTimer, QSize, QRect, QRectF, pyqtSignal, QDir
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPalette, QBrush, QPainterPath, QKeyEvent

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
# Use a fallback approach for fonts - try Space Mono first, then fall back to system fonts
FONT_FAMILY = "Space Mono, Courier New, monospace"
FONT_SIZE = 12  # Use consistent font size throughout the application

def get_font(bold=False, italic=False, size=FONT_SIZE) -> QFont:
    """Get a font with the specified style."""
    font = QFont()
    font.setFamily("Space Mono")
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
                
                # Add a small margin for the update region to include the hole outline
                margin = 2
                update_rect = QRect(int(x - margin), int(y - margin), 
                                   int(self.hole_width + 2*margin), int(self.hole_height + 2*margin))
                
                # Update only the region of this LED for better performance
                self.update(update_rect)
    
    def clear_grid(self):
        """Clear the entire grid."""
        # Check if grid already empty to avoid unnecessary updates
        if any(any(row) for row in self.grid):
            self.grid = [[False for _ in range(self.num_cols)] for _ in range(self.num_rows)]
            self.update()
    
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
    """Settings dialog for configuring the punch card display."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)
        
        # Set dark theme
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background'].name()};
                color: {COLORS['text'].name()};
            }}
            QLabel, QSpinBox, QCheckBox {{
                color: {COLORS['text'].name()};
            }}
        """)
        
        layout = QFormLayout(self)
        
        # Display settings
        display_group = QGroupBox("Display Settings")
        display_layout = QFormLayout()
        
        self.led_delay = QSpinBox()
        self.led_delay.setRange(50, 500)
        self.led_delay.setValue(100)
        self.led_delay.setSuffix(" ms")
        display_layout.addRow("LED Update Delay:", self.led_delay)
        
        self.message_delay = QSpinBox()
        self.message_delay.setRange(1000, 10000)
        self.message_delay.setValue(3000)
        self.message_delay.setSuffix(" ms")
        display_layout.addRow("Message Delay:", self.message_delay)
        
        self.random_delay = QCheckBox()
        self.random_delay.setChecked(True)
        display_layout.addRow("Random Delay:", self.random_delay)
        
        self.show_splash = QCheckBox()
        self.show_splash.setChecked(True)
        display_layout.addRow("Show Splash Screen:", self.show_splash)
        
        self.auto_console = QCheckBox()
        self.auto_console.setChecked(True)
        display_layout.addRow("Auto-Open Console:", self.auto_console)
        
        display_group.setLayout(display_layout)
        layout.addRow(display_group)
        
        # Card dimensions settings
        card_group = QGroupBox("Card Dimensions")
        card_layout = QFormLayout()
        
        self.scale_factor = QSpinBox()
        self.scale_factor.setRange(1, 10)
        self.scale_factor.setValue(3)
        self.scale_factor.setSuffix("x")
        self.scale_factor.valueChanged.connect(self.update_card_dimensions)
        card_layout.addRow("Scale Factor:", self.scale_factor)
        
        self.top_margin = QSpinBox()
        self.top_margin.setRange(1, 20)
        self.top_margin.setValue(4)
        self.top_margin.setSuffix(" mm")
        self.top_margin.valueChanged.connect(self.update_card_dimensions)
        card_layout.addRow("Top/Bottom Margin:", self.top_margin)
        
        self.side_margin = QSpinBox()
        self.side_margin.setRange(1, 20)
        self.side_margin.setValue(5)
        self.side_margin.setSuffix(" mm")
        self.side_margin.valueChanged.connect(self.update_card_dimensions)
        card_layout.addRow("Side Margin:", self.side_margin)
        
        self.row_spacing = QSpinBox()
        self.row_spacing.setRange(1, 10)
        self.row_spacing.setValue(2)
        self.row_spacing.setSuffix(" mm")
        self.row_spacing.valueChanged.connect(self.update_card_dimensions)
        card_layout.addRow("Row Spacing:", self.row_spacing)
        
        self.column_spacing = QSpinBox()
        self.column_spacing.setRange(1, 10)
        self.column_spacing.setValue(1)
        self.column_spacing.setSuffix(" mm")
        self.column_spacing.valueChanged.connect(self.update_card_dimensions)
        card_layout.addRow("Column Spacing:", self.column_spacing)
        
        self.hole_width = QSpinBox()
        self.hole_width.setRange(1, 5)
        self.hole_width.setValue(1)
        self.hole_width.setSuffix(" mm")
        self.hole_width.valueChanged.connect(self.update_card_dimensions)
        card_layout.addRow("Hole Width:", self.hole_width)
        
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

class PunchCardDisplay(QMainWindow):
    """Main window for the minimalist punch card display application."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Punch Card Display")
        self.setMinimumSize(900, 600)
        
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
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(0)  # Reduce spacing to minimize shifts
        
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
        
        # Add the top section to the main layout
        self.main_layout.addWidget(top_section)
        
        # ================== MIDDLE SECTION (PUNCH CARD) ==================
        # Create a fixed container for the punch card to ensure it stays in place
        punch_card_container = QWidget()
        punch_card_layout = QVBoxLayout(punch_card_container)
        punch_card_layout.setContentsMargins(0, 0, 0, 0)
        punch_card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create punch card widget
        self.punch_card = PunchCardWidget()
        punch_card_layout.addWidget(self.punch_card)
        
        # Add the punch card container to the main layout with stretch factor
        self.main_layout.addWidget(punch_card_container, 1)  # 1 = stretch factor
        
        # ================== BOTTOM SECTION ==================
        # Create a container for the bottom section with fixed height
        # This ensures that the punch card position remains stable
        bottom_section = QWidget()
        bottom_section.setFixedHeight(190)  # Increased from 170 to prevent button cutoff
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
        bottom_layout.addWidget(self.api_status_label)
        
        # Create a spacer widget to maintain spacing even when elements are hidden
        spacer = QWidget()
        spacer.setFixedHeight(10)
        bottom_layout.addWidget(spacer)
        
        # Create control buttons in a container with fixed height
        self.button_container = QWidget()
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
        
        # Add the bottom section to the main layout
        self.main_layout.addWidget(bottom_section)
        
        # Initialize display variables
        self.current_message = ""
        self.current_char_index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.display_next_char)
        self.led_delay = 100  # milliseconds
        self.running = False
        
        # Create console and settings dialogs
        self.console = ConsoleWindow(self)
        self.settings = SettingsDialog(self)
        
        # Create API console window
        self.api_console = APIConsoleWindow(self)
        
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
                self.timer.setInterval(self.led_delay)
                self.console.log(f"Settings updated: {settings}")
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
            # Clear the entire grid when done
            self.punch_card.clear_grid()
            self.timer.stop()
            self.running = False
            self.start_button.setEnabled(True)
            self.clear_button.setEnabled(True)
            self.update_status("DISPLAY COMPLETE")
    
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
        """Start the splash screen animation."""
        self.showing_splash = True
        self.splash_step = 0
        self.hardware_check_complete = False
        self.countdown_seconds = 10  # Reset countdown to 10 seconds
        self.hardware_detection_finished = False
        self.animation_started = False
        
        # Instead of hiding UI elements, just make them invisible or empty
        # This preserves their space in the layout
        self.message_label.setText("")
        self.message_label.setStyleSheet(f"""
            {get_font_css(bold=False, size=FONT_SIZE+2)}
            color: {COLORS['background'].name()};  # Make text invisible
            padding: 10px 0px;
        """)
        
        # Calculate the left edge position of the punch card - ensure it works for splash screen too
        self.align_message_with_card()
        
        self.status_label.setText("DETECTING HARDWARE...")
        
        self.hardware_status_label.setText("Starting hardware detection...")
        self.hardware_status_label.setStyleSheet(f"""
            {get_font_css(bold=False, size=FONT_SIZE-2)}
            color: {COLORS['text'].name()};
            padding: 5px;
        """)
        
        # Update keyboard hint text with countdown
        self.keyboard_hint_label.setText(f"Press [SPACE] to skip hardware detection ({self.countdown_seconds}s)")
        self.keyboard_hint_label.setStyleSheet(f"""
            {get_font_css(italic=True, size=FONT_SIZE-2)}
            color: {QColor(150, 150, 150).name()};
            padding: 5px;
        """)
        
        # Start the countdown timer
        self.countdown_timer.start(1000)  # 1000ms = 1 second
        
        # Make buttons invisible but keep their space in the layout
        for button in [self.start_button, self.clear_button, self.exit_button]:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['background'].name()};
                    color: {COLORS['background'].name()};
                    border: 0px solid {COLORS['background'].name()};
                    padding: 6px 12px;
                    {get_font_css(size=12)}
                    border-radius: 3px;
                }}
            """)
            button.setEnabled(False)
        
        self.console.log("Starting hardware detection - clearing all LEDs", "INFO")
        
        # Clear any potential artifacts
        self.punch_card.clear_grid()
        
        # Start the hardware detection process
        self.console.log("Starting hardware detection", "INFO")
        self.hardware_detector.detect_hardware()
    
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
        """Update the splash screen animation."""
        if not self.showing_splash:
            return
            
        # Calculate total steps needed to cover the entire card
        total_steps = NUM_COLS + NUM_ROWS - 1  # This ensures we cover the entire diagonal
        
        # Log the current splash step to console only
        self.console.log(f"Splash step: {self.splash_step} of {total_steps*2 + 12}", "INFO")
        
        # Ensure we have hardware detection complete - critical fix
        if not self.hardware_check_complete:
            # Double-check that we're in a valid state before proceeding
            if self.hardware_detector.detection_complete or self.hardware_detector.using_virtual_mode:
                # Hardware detection completed naturally since last check
                self.hardware_check_complete = True
                self.hardware_detection_finished = True
            else:
                # Still waiting - skip again to avoid getting stuck
                self.auto_skip_hardware_detection()
                return
            
        # Phase transitions - verify top-left corner state
        if self.splash_step == 0:
            # At the very beginning, make sure top-left corner is OFF
            self.verify_top_left_corner(False, "Initial state")
        elif self.splash_step == total_steps:
            # At start of Phase 2, verify top-left corner is OFF before we turn it ON
            self.verify_top_left_corner(False, "Start of Phase 2")
        elif self.splash_step == total_steps * 2:
            # At start of Phase 3, verify that top-left corner is either ON or OFF depending on current animation
            # Logic below will ensure it gets properly set
            pass
            
        # Phase 1: Initial clearing (empty card)
        if self.splash_step < total_steps:
            # Make sure the top-left corner (0,0) is explicitly cleared first
            if self.splash_step == 0:
                self.console.log(f"LED: Explicitly clearing top-left corner (0,0)", "LED")
                self.punch_card.set_led(0, 0, False)
                # Verify it got cleared
                self.verify_top_left_corner(False, "Phase 1 start")
            
            # Clear the current diagonal
            for row in range(NUM_ROWS):
                col = self.splash_step - row
                if 0 <= col < NUM_COLS:
                    # Skip the top-left corner as we've already handled it
                    if not (row == 0 and col == 0):
                        self.console.log(f"LED: Clearing row {row}, col {col} (Phase 1)", "LED")
                        self.punch_card.set_led(row, col, False)
            
            # Only show phase information in console, not in main GUI
            self.console.log(f"SPLASH ANIMATION - CLEARING {self.splash_step}/{total_steps}", "INFO")
        
        # Phase 2: Punching holes with a 12-hole width
        elif self.splash_step < total_steps * 2:
            current_step = self.splash_step - total_steps
            
            # At the beginning of Phase 2, explicitly turn on the top-left corner
            if current_step == 0:
                self.console.log(f"LED: Explicitly turning ON top-left corner (0,0)", "LED")
                self.punch_card.set_led(0, 0, True)
                # Verify it got turned on
                self.verify_top_left_corner(True, "Phase 2 start")
            elif current_step <= 12:
                # During the first 12 steps of Phase 2, keep checking that the top-left corner is ON
                if not self.verify_top_left_corner(True, f"Phase 2 step {current_step}"):
                    # If verification failed, explicitly turn it back ON
                    self.console.log(f"LED: Re-enabling top-left corner (0,0) that was incorrectly OFF", "LED")
                    self.punch_card.set_led(0, 0, True)
            
            # Punch new holes at the current diagonal
            for row in range(NUM_ROWS):
                col = current_step - row
                if 0 <= col < NUM_COLS:
                    # Skip the top-left corner as we've already handled it
                    if not (row == 0 and col == 0):
                        self.console.log(f"LED: Setting row {row}, col {col} ON (Phase 2)", "LED")
                        self.punch_card.set_led(row, col, True)
            
            # Clear old holes (trailing diagonal pattern - 12 columns wide)
            trailing_step = max(0, current_step - 12)
            for row in range(NUM_ROWS):
                col = trailing_step - row
                if 0 <= col < NUM_COLS:
                    # Only clear top-left corner when it's definitely time to clear it
                    # This prevents it from being cleared too early
                    if row == 0 and col == 0 and current_step >= 12:
                        self.console.log(f"LED: Explicitly turning OFF top-left corner (0,0)", "LED")
                        self.punch_card.set_led(0, 0, False)
                        # Verify it got turned off
                        self.verify_top_left_corner(False, f"Phase 2 trailing step {current_step}")
                    elif not (row == 0 and col == 0):
                        self.console.log(f"LED: Setting row {row}, col {col} OFF (Phase 2 trailing)", "LED")
                        self.punch_card.set_led(row, col, False)
            
            # Only show phase information in console, not in main GUI
            self.console.log(f"SPLASH ANIMATION - ILLUMINATING {current_step}/{total_steps}", "INFO")
        
        # Phase 3: Clear the remaining 12 columns in a diagonal pattern
        elif self.splash_step < total_steps * 2 + 12:
            current_clear_step = self.splash_step - (total_steps * 2) + (total_steps - 12)
            
            # Make sure top-left corner is OFF by this phase
            if self.splash_step == total_steps * 2:
                self.console.log(f"LED: Final check - ensuring top-left corner (0,0) is OFF", "LED")
                self.punch_card.set_led(0, 0, False)
                # Verify it got turned off
                self.verify_top_left_corner(False, "Phase 3 start")
            
            for row in range(NUM_ROWS):
                col = current_clear_step - row
                if 0 <= col < NUM_COLS:
                    # Skip the top-left corner as we've already handled it
                    if not (row == 0 and col == 0):
                        self.console.log(f"LED: Setting row {row}, col {col} OFF (Phase 3)", "LED")
                        self.punch_card.set_led(row, col, False)
            
            # Only show phase information in console, not in main GUI
            remaining_steps = (total_steps * 2 + 12) - self.splash_step
            self.console.log(f"SPLASH ANIMATION - FINISHING (REMAINING: {remaining_steps})", "INFO")
        
        else:
            # Wait for hardware detection to complete before ending splash screen
            # This check is now redundant since we only start animation after hardware detection
            # but keeping it for safety
            if not self.hardware_check_complete:
                # Keep the animation paused at this step
                self.status_label.setText("WAITING FOR HARDWARE...")
                return
                
            # Stop all timers
            if self.countdown_timer.isActive():
                self.countdown_timer.stop()
            self.splash_timer.stop()
            self.hardware_status_timer.stop()
            
            # Hide all initialization messages immediately
            self.status_label.setText("")
            self.hardware_status_label.setText("")
            self.keyboard_hint_label.setText("")
            
            # Verify all LEDs are OFF before final clearing
            if self.punch_card.grid[0][0]:
                self.console.log(f"LED STATE ERROR: Top-left corner (0,0) is still ON at end of animation!", "ERROR")
            
            # Clear all LEDs and log each one
            for row in range(NUM_ROWS):
                for col in range(NUM_COLS):
                    if self.punch_card.grid[row][col]:
                        self.console.log(f"LED: Final clearing row {row}, col {col}", "LED")
                        
            # Clear the grid with a single operation after logging
            self.punch_card.clear_grid()
            self.punch_card.update()
            self.console.log("Splash animation completed, transitioning to ready state", "INFO")
            
            # Schedule actual UI reveal and message generation after a delay
            QTimer.singleShot(500, self.complete_splash_screen)
            return
        
        # Force a repaint to ensure LED changes are displayed
        self.punch_card.update()
        self.splash_step += 1
    
    def complete_splash_screen(self):
        """Complete the splash screen transition and prepare for normal operation."""
        self.showing_splash = False
        
        # Make sure countdown timer is stopped
        if self.countdown_timer.isActive():
            self.countdown_timer.stop()
        
        # First update the status text while other elements are hidden
        self.status_label.setText("READY")
        self.console.log("Splash screen completed, ready for operation", "INFO")
        
        # Determine the operation mode based on hardware detection
        mode_type = "HARDWARE" if not self.hardware_detector.using_virtual_mode else "VIRTUAL"
        
        # Pre-set the message label content before showing it
        self.message_label.setText(f"SYSTEM READY - {mode_type} MODE")
        self.message_label.setStyleSheet(f"""
            {get_font_css(bold=False, size=FONT_SIZE+2)}
            color: {COLORS['text'].name()};
            padding: 10px 0px;
        """)
        
        # Ensure message label aligns with the left edge of the punch card
        QTimer.singleShot(10, self.align_message_with_card)
        
        # Hide hardware-specific status indicators by making them transparent
        # but keep their space in the layout
        self.hardware_status_label.setStyleSheet(f"""
            {get_font_css(bold=False, size=FONT_SIZE-2)}
            color: {COLORS['background'].name()};
            padding: 5px;
        """)
        
        self.keyboard_hint_label.setStyleSheet(f"""
            {get_font_css(italic=True, size=FONT_SIZE-2)}
            color: {COLORS['background'].name()};
            padding: 5px;
        """)
        
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
        self.api_status_label.setText(f"API: {status}")
        
        # Set color based on status
        color = COLORS['text'].name()
        if status == "Connected":
            color = COLORS['success'].name()
        elif status == "Fallback Mode":
            color = COLORS['warning'].name()
        elif status in ["Error", "Unavailable", "No API Key"]:
            color = COLORS['error'].name()
            
        self.api_status_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                background-color: {COLORS['card_bg'].name()};
                padding: 3px 8px;
                border: 1px solid {COLORS['hole_outline'].name()};
                border-radius: 2px;
                {get_font_css(bold=True, size=10)}
            }}
        """)
        
        # Update API console window if it exists
        if hasattr(self, 'api_console'):
            self.api_console.update_status(status)

    def show_api_console(self):
        """Show the API console window."""
        self.api_console.show()
        self.api_console.raise_()
        self.api_console.activateWindow()


def main():
    """Run the application."""
    app = QApplication.instance() if QApplication.instance() else QApplication([])
    
    # Create and show the display
    display = PunchCardDisplay()
    display.show()
    
    # If this is run as a script, start the event loop
    if __name__ == "__main__":
        sys.exit(app.exec())
    
    return display, app


if __name__ == "__main__":
    main() 