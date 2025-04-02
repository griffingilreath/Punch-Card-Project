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
import json
import logging
import shutil
import platform
import datetime
import queue
import subprocess

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QPushButton, QDialog, QMessageBox,
    QPlainTextEdit, QLineEdit, QFileDialog, QMenuBar, QMenu,
    QCheckBox, QComboBox, QProgressBar, QSplitter, QGridLayout,
    QSpinBox, QFrame, QSlider, QTabWidget, QTextEdit, QSpacerItem,
    QSizePolicy, QFormLayout, QDoubleSpinBox, QGroupBox, QDialogButtonBox,
    QWidgetAction
)
from PyQt6.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QSize, QRect, 
    QUrl, QObject, QEvent, QCoreApplication, QDateTime, QRectF, QPoint
)
from PyQt6.QtGui import (
    QIcon, QPalette, QTextCursor, QColor,
    QPixmap, QKeyEvent, QTextCharFormat, QPainter, QPainterPath,
    QBrush, QPen, QAction
)
    
try:
    from PyQt6.QtMultimedia import QSoundEffect
except ImportError:
    print("QSoundEffect not available - running without sound effects")

# Import animation manager
from src.animation.animation_manager import AnimationManager, AnimationType, AnimationState

# Import utility modules
from src.utils.colors import COLORS
from src.utils.fonts import get_font, get_font_css, FONT_SIZE, FONT_FAMILY
from src.utils.ui_components import RetroButton, ClassicTitleBar
from src.utils.sound_manager import SoundManager
from src.core.punch_card import PunchCardStats

from src.display.settings_dialog import SettingsDialog

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

class ConsoleLogger:
    """Simple logger class that acts as a placeholder when no real console is available"""
    def __init__(self):
        self.logs = []
        
    def log(self, message, level="INFO"):
        """Log a message with specified level"""
        self.logs.append((level, message))
        print(f"[{level}] {message}")

    def show(self):
        """Placeholder for show method"""
        pass

    def clear(self):
        """Clear logs"""
        self.logs = []

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
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
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
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
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
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
                    "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
                "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
        url = "https://status.openai.com/api/v2/status.json"
        service_status["openai"]["last_checked"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
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
        url = "https://status.fly.io/api/v2/status.json"
        service_status["flyio"]["last_checked"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
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
        # Get settings from form
        settings = {
            # Display settings
            "led_delay": self.led_delay.value(),
            "interval": self.interval_spin.value(),
            "message_display_time": self.message_display_time.value(),
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
                "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
            
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
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
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
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
    
    def update_status(self):
        """Update the WiFi status (simulated for demo purposes)."""
        # For demo, randomly select a status with bias toward "connected"
        import random
        rand = random.random()
        if rand < 0.7:
            self.set_wifi_status("connected")
        elif rand < 0.9:
            self.set_wifi_status("weak")
        else:
            self.set_wifi_status("disconnected")
    
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
        self.setStyleSheet("background-color: transparent; color: white; border: none;")
        
        # Create main layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(1)
        
        # Left side - Menu items
        self.left_container = QWidget()
        self.left_layout = QHBoxLayout(self.left_container)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(1)
        
        # Create menu buttons
        self.apple_menu = self.create_menu_button("▭", is_apple=True)
        self.card_menu = self.create_menu_button("Punch Card")
        self.settings_menu = self.create_menu_button("Settings")
        self.console_menu = self.create_menu_button("Console")
        
        # Right side - Status indicators
        self.right_container = QWidget()
        self.right_layout = QHBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(5)
        
        # Add WiFi status
        self.wifi_status = WiFiStatusWidget(self)
        self.right_layout.addWidget(self.wifi_status)
        
        # Add clock button
        self.clock_button = QPushButton()
        self.clock_button.setFlat(True)
        self.clock_button.setMinimumWidth(140)
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
        self.right_layout.addWidget(self.clock_button)
        
        # Add containers to main layout
        self.layout.addWidget(self.left_container)
        self.layout.addStretch(1)
        self.layout.addWidget(self.right_container)
        
        # Initialize menus
        self.apple_menu_popup = QMenu(self)
        self.card_menu_popup = QMenu(self)
        self.settings_menu_popup = QMenu(self)
        self.console_menu_popup = QMenu(self)
        self.notifications_popup = QMenu(self)
        
        # Connect menu buttons
        self.apple_menu.clicked.connect(self.show_apple_menu)
        self.card_menu.clicked.connect(self.show_card_menu)
        self.settings_menu.clicked.connect(self.show_settings_menu)
        self.console_menu.clicked.connect(self.show_console_menu)
        self.clock_button.clicked.connect(self.show_notifications)
        
        # Setup timers
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        self.update_clock()
        
        self.wifi_timer = QTimer(self)
        self.wifi_timer.timeout.connect(self.update_wifi_status)
        self.wifi_timer.start(5000)
        self.update_wifi_status()
    
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
        shutdown_action.triggered.connect(main_window.safe_shutdown)
        
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
        
        # Add Sound submenu
        sound_menu = QMenu("Sound", self.settings_menu_popup)
        sound_menu.setStyleSheet(menu_style)
        
        # Add volume control
        volume_action = QWidgetAction(sound_menu)
        volume_widget = QWidget()
        volume_layout = QHBoxLayout(volume_widget)
        volume_layout.setContentsMargins(25, 5, 25, 5)
        
        volume_label = QLabel("Volume:")
        volume_label.setStyleSheet("color: white;")
        volume_layout.addWidget(volume_label)
        
        volume_slider = QSlider(Qt.Orientation.Horizontal)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(100)
        volume_slider.setFixedWidth(100)
        volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #444444;
                height: 4px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: white;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
        """)
        volume_layout.addWidget(volume_slider)
        
        volume_value = QLabel("100%")
        volume_value.setStyleSheet("color: white; min-width: 40px;")
        volume_layout.addWidget(volume_value)
        
        volume_action.setDefaultWidget(volume_widget)
        sound_menu.addAction(volume_action)
        
        # Add mute option
        mute_action = sound_menu.addAction("Mute")
        mute_action.setCheckable(True)
        
        # Add separator
        sound_menu.addSeparator()
        
        # Add sound settings
        sound_settings_action = sound_menu.addAction("Sound Settings...")
        
        # Add sound menu to settings menu
        self.settings_menu_popup.addMenu(sound_menu)
        
        statistics_action = self.settings_menu_popup.addAction("Statistics...")
        api_settings_action = self.settings_menu_popup.addAction("API Settings...")
        self.settings_menu_popup.addSeparator()
        inline_settings_action = self.settings_menu_popup.addAction("Quick Settings Panel")
        
        # Connect settings menu signals
        display_settings_action.triggered.connect(main_window.show_card_settings)
        volume_slider.valueChanged.connect(lambda v: self.on_volume_changed(v, volume_value, main_window))
        mute_action.triggered.connect(lambda checked: self.on_mute_changed(checked, main_window))
        sound_settings_action.triggered.connect(lambda: main_window.sound_settings_dialog.show())
        statistics_action.triggered.connect(main_window.show_statistics_dialog)
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
    
    def on_volume_changed(self, value, label, main_window):
        """Handle volume slider changes."""
        label.setText(f"{value}%")
        if hasattr(main_window, 'sound_manager'):
            main_window.sound_manager.set_volume(value / 100.0)
    
    def on_mute_changed(self, checked, main_window):
        """Handle mute state changes."""
        if hasattr(main_window, 'sound_manager'):
            main_window.sound_manager.set_muted(checked)
    
    def create_menu_button(self, text, is_apple=False):
        """Create a button that looks like a menu item."""
        button = QPushButton(text)
        button.setFlat(True)
        
        if is_apple:
            button.setStyleSheet(f"""
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
                    margin-top: -4px;
                    line-height: 15px;
                    vertical-align: top;
                    padding-top: 0px;
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
        else:
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
    
    def show_apple_menu(self):
        """Show the apple menu."""
        self.apple_menu_popup.exec(self.apple_menu.mapToGlobal(QPoint(0, self.height())))
    
    def show_card_menu(self):
        """Show the punch card menu."""
        self.card_menu_popup.exec(self.card_menu.mapToGlobal(QPoint(0, self.height())))
    
    def show_settings_menu(self):
        """Show the settings menu."""
        self.settings_menu_popup.exec(self.settings_menu.mapToGlobal(QPoint(0, self.height())))
    
    def show_console_menu(self):
        """Show the console menu."""
        self.console_menu_popup.exec(self.console_menu.mapToGlobal(QPoint(0, self.height())))
    
    def show_notifications(self):
        """Show the notifications menu."""
        self.notifications_popup.exec(self.clock_button.mapToGlobal(QPoint(0, self.height())))
    
    def update_clock(self):
        """Update the clock display."""
        now = QDateTime.currentDateTime()
        self.clock_button.setText(now.toString("ddd MMM d h:mm AP"))
    
    def update_wifi_status(self):
        """Update the WiFi status indicator."""
        if hasattr(self, 'wifi_status'):
            self.wifi_status.update_status()
    
    def on_sound_volume_changed(self, value):
        """Handle volume changes from the sound control."""
        if hasattr(self.parent(), 'sound_manager'):
            self.parent().sound_manager.set_volume(value / 100.0)
    
    def on_sound_mute_changed(self, muted):
        """Handle mute state changes from the sound control."""
        if hasattr(self.parent(), 'sound_manager'):
            self.parent().sound_manager.set_muted(muted)

class PunchCardDisplay(QMainWindow):
    """Main window for the minimalist punch card display application."""
    
    def __init__(self, punch_card=None):
        super().__init__()
        
        # Create console window first
        self.console = ConsoleWindow(self)
        
        # Initialize hardware detector
        self.hardware_detector = HardwareDetector(self.console)
        
        # Initialize sound manager
        self.sound_manager = None
        self.initialize_sound_system()
        
        # Set window title
        self.setWindowTitle("Punch Card Display")
        
        # Set window size and style
        self.setMinimumSize(1000, 700)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # No margins to allow full-width menu bar
        self.main_layout.setSpacing(0)  # Reduce spacing to minimize shifts
        
        # Set window style and background color
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {COLORS['background'].name()};
                color: {COLORS['text'].name()};
                {get_font_css(bold=False, size=FONT_SIZE)}
            }}
        """)
        
        # ================== MENU BAR SECTION ==================
        # Add custom in-app menu bar
        self.menu_bar = InAppMenuBar(self)
        self.main_layout.addWidget(self.menu_bar)
        
        # Add spacer to separate menu bar from content
        menu_spacer = QWidget()
        menu_spacer.setFixedHeight(5)
        self.main_layout.addWidget(menu_spacer)
        
        # ================== CONTENT CONTAINER ==================
        # Create container for all content below menu bar
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(20, 20, 20, 20)  # Normal margins
        content_layout.setSpacing(10)  # EXACTLY 10px spacing between all elements
        self.main_layout.addWidget(content_container)
        
        # Create the stats panel but don't add it to the layout yet - it will be positioned when shown
        self.stats_panel = StatsPanel(self)
        self.stats_panel.hide()  # Initially hidden
        
        # Create the sound settings dialog
        self.sound_settings_dialog = SoundSettingsDialog(self)
        
        # Store the punch card instance
        self.punch_card_instance = punch_card
        
        # Use the stats from the punch card instance
        self.stats = self.punch_card_instance.stats if punch_card else PunchCardStats()
        
        # ================== TOP SECTION (MESSAGE LABEL) ==================
        # Create message label in its own container
        message_container = QWidget()
        message_layout = QHBoxLayout(message_container)
        message_layout.setContentsMargins(35, 10, 0, 0)  # Left padding (reduced by 5px) and top padding to move down
        
        self.message_label = QLabel("SYSTEM READY")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.message_label.setStyleSheet(f"""
            {get_font_css(size=14)}
            color: {COLORS['text'].name()};
        """)
        message_layout.addWidget(self.message_label)
        message_layout.addStretch(1)  # Push everything to the left
        
        content_layout.addWidget(message_container)
        
        # ================== CENTER SECTION (CARD) ==================
        # Create punch card in content layout - always create a new PunchCardWidget
        self.punch_card = PunchCardWidget()
        content_layout.addWidget(self.punch_card)
        
        # ================== BOTTOM SECTION (STATUS LABEL) ==================
        # Create status label in its own container
        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(35, 0, 0, 10)  # Left padding (reduced by 5px) and bottom padding
        
        self.status_label = QLabel("READY")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.status_label.setStyleSheet(f"""
            {get_font_css(size=14)}
            color: {COLORS['text'].name()};
        """)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch(1)  # Push everything to the left
        
        content_layout.addWidget(status_container)
        
        # Position the labels initially
        self.position_text_elements()
        
        # Add the hidden UI elements in a container
        hidden_container = QWidget()
        hidden_layout = QVBoxLayout(hidden_container)
        hidden_layout.setContentsMargins(0, 0, 0, 0)
        hidden_layout.setSpacing(0)
        
        self.hardware_status_label = QLabel("")
        self.hardware_status_label.setVisible(False)
        self.hardware_status_label.setMaximumHeight(0)
        hidden_layout.addWidget(self.hardware_status_label)
        
        self.keyboard_hint_label = QLabel("")
        self.keyboard_hint_label.setVisible(False)
        self.keyboard_hint_label.setMaximumHeight(0)
        hidden_layout.addWidget(self.keyboard_hint_label)
        
        self.api_status_label = QLabel("")
        self.api_status_label.setVisible(False)
        self.api_status_label.setMaximumHeight(0)
        hidden_layout.addWidget(self.api_status_label)
        
        # Create hidden button container
        self.button_container = QWidget()
        self.button_container.setVisible(False)
        self.button_container.setMaximumHeight(0)
        button_layout = QHBoxLayout(self.button_container)
        
        # Create required buttons (hidden)
        self.start_button = RetroButton("DISPLAY MESSAGE")
        self.clear_button = RetroButton("CLEAR")
        self.api_button = RetroButton("API CONSOLE")
        self.exit_button = RetroButton("EXIT")
        
        # Connect button signals
        self.start_button.clicked.connect(self.start_display)
        self.clear_button.clicked.connect(self.punch_card.clear_grid)
        self.api_button.clicked.connect(self.show_api_console)
        self.exit_button.clicked.connect(self.close)
        
        # Add buttons to layout
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.api_button)
        button_layout.addWidget(self.exit_button)
        
        hidden_layout.addWidget(self.button_container)
        
        # Add the hidden container to the content layout
        content_layout.addWidget(hidden_container, 0)  # 0 = fixed, non-stretching
        
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
        
        # Create API console window
        self.api_console = APIConsoleWindow(self)
        
        # Setup menu bar actions
        self.menu_bar.setup_menu_actions(self)
        
        # Initialize clock timer to update clock in menu bar
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)  # Update every second
        
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
        
        # Initialize animation manager
        self.animation_manager = AnimationManager(self.punch_card, self)
        self.animation_manager.animation_finished.connect(self.on_animation_finished)
        
        # Always start with splash screen
        self.start_splash_screen()
        
        # Load settings from file
        self.load_settings()
        
    def on_sound_volume_changed(self, value):
        """Handle volume changes from sound settings."""
        if hasattr(self, 'sound_manager'):
            volume = value / 100.0  # Convert percentage to float
            self.sound_manager.set_volume(volume)
            
            # Update menu bar volume slider if it exists
            if hasattr(self.menu_bar, 'sound_control'):
                self.menu_bar.sound_control.volume_slider.setValue(value)
                self.menu_bar.sound_control.volume_value.setText(f"{value}%")
            
            # Save setting to file
            self.save_sound_setting("volume", volume)
    
    def on_sound_mute_changed(self, muted):
        """Handle mute state changes from sound settings."""
        if hasattr(self, 'sound_manager'):
            self.sound_manager.set_muted(muted)
            
            # Update menu bar mute state if it exists
            if hasattr(self.menu_bar, 'sound_control'):
                self.menu_bar.sound_control.mute_action.setChecked(muted)
                self.menu_bar.sound_control.setProperty("muted", muted)
                self.menu_bar.sound_control.update()
            
            # Save setting to file
            self.save_sound_setting("muted", muted)
    
    def on_sound_mappings_changed(self, mappings):
        """Handle sound mapping changes from sound settings."""
        if hasattr(self, 'sound_manager'):
            self.sound_manager.update_sound_mappings(mappings)
            
            # Test the punch sound
            self.sound_manager.play_sound("punch")
            
            # Save setting to file
            self.save_sound_setting("sound_mappings", mappings)
    
    def save_sound_setting(self, setting_name, value):
        """Save a single sound setting to the settings file."""
        try:
            import json
            import os
            
            settings_path = "punch_card_settings.json"
            settings = {}
            
            # Load existing settings if available
            if os.path.exists(settings_path):
                try:
                    with open(settings_path, "r") as f:
                        settings = json.load(f)
                except Exception as e:
                    self.console.log(f"Error loading settings file: {str(e)}", "ERROR")
            
            # Update the setting
            settings[setting_name] = value
            
            # Save settings
            with open(settings_path, "w") as f:
                json.dump(settings, f, indent=4)
            
            self.console.log(f"Saved sound setting: {setting_name}", "INFO")
            
        except Exception as e:
            self.console.log(f"Error saving sound setting: {str(e)}", "ERROR")
    
    def position_overlay_labels(self):
        """This method is no longer needed as labels are now children of the punch card."""
        pass
    
    def resizeEvent(self, event):
        """Handle resize events."""
        super().resizeEvent(event)
        # No need to reposition text elements as they're managed by layouts
    
    def showEvent(self, event):
        """Handle show event."""
        super().showEvent(event)
        # No need to position text elements as they're managed by layouts
    
    def update_status(self, status: str):
        """Update the status overlay with a new status message."""
        if hasattr(self, 'status_overlay'):
            self.status_overlay.setText(status)
            self.status_overlay.adjustSize()
            self.position_overlay_labels()
        
        # Keep the console log
        if hasattr(self, 'console'):
            self.console.log(f"Status: {status}")
    
    def display_message(self, message: str, source: str = "", delay: int = 100):
        """Display a message with optional source information."""
        # Don't display messages during splash screen or when animations are running
        if self.showing_splash:
            self.console.log("Ignoring message display request during splash animation", "WARNING")
            return
            
        self.current_message = message.upper()
        self.current_char_index = 0
        
        # Clear the grid and play clear sound
        self.punch_card.clear_grid()
        self.play_sound("clear")
        
        self.led_delay = delay
        self.timer.setInterval(delay)
        
        # Update message label
        self.message_label.setText(message)
        
        # Update label margins
        self.update_label_margins()
        
        # Update statistics
        if hasattr(self, 'stats'):
            self.stats.update_message_stats(message, message_type=source or "Local")
            # Refresh stats panel if visible
            if hasattr(self, 'stats_panel') and self.stats_panel.isVisible():
                self.stats_panel.refresh_stats()
        
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
            char = self.current_message[self.current_char_index]
            self._display_character(char, self.current_char_index)
            
            # Play punch sound for each character (non-blocking)
            self.play_sound("punch")
            
            self.current_char_index += 1
            
            # Only update status every 10 characters to reduce overhead
            if self.current_char_index % 10 == 0:
                self.update_status(f"DISPLAYING: {self.current_message[:self.current_char_index]}")
        else:
            # Display complete
            self.timer.stop()
            self.running = False
            
            # Play completion sound (non-blocking)
            self.play_sound("complete")
            
            # Update status
            self.update_status("DISPLAY COMPLETE")
            
            # Start the message display timer
            display_time_ms = self.message_display_time * 1000
            self.message_display_timer.start(display_time_ms)
            
            # Keep buttons disabled until the message display time is complete
            self.start_button.setEnabled(False)
            self.clear_button.setEnabled(False)
    
    def _display_character(self, char: str, col: int):
        """Display a character on the punch card grid."""
        # Convert to uppercase
        char = char.upper()
        
        # Clear only the rows we'll use for this character
        rows_to_clear = []
        if char.isalpha():
            if char in "ABCDEFGHI":
                rows_to_clear = [0, ord(char) - ord('A') + 3]
            elif char in "JKLMNOPQR":
                rows_to_clear = [1, ord(char) - ord('J') + 3]
            else:  # S-Z
                rows_to_clear = [2]
                digit = ord(char) - ord('S') + 2
                if digit <= 9:
                    rows_to_clear.append(digit + 2)
        elif char.isdigit():
            digit = int(char)
            rows_to_clear = [2] if digit == 0 else [digit + 2]
        elif char != ' ':
            rows_to_clear = [1, 2]  # Special characters
        
        # Clear only necessary rows
        for row in rows_to_clear:
            if 0 <= row < self.punch_card.num_rows:
                self.punch_card.set_led(row, col, False)
        
        # Set the LEDs for the character
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
        elif char.isdigit():
            digit = int(char)
            if digit == 0:
                self.punch_card.set_led(2, col, True)  # Row 0
            else:
                self.punch_card.set_led(digit + 2, col, True)
        elif char != ' ':
            self.punch_card.set_led(1, col, True)  # Row 11
            self.punch_card.set_led(2, col, True)  # Row 0

    def update_card_dimensions(self, settings: Dict[str, Any]):
        """Update the punch card dimensions with new settings."""
        self.punch_card.update_dimensions(settings)
        self.console.log(f"Card dimensions updated: {settings}")

    def start_splash_screen(self):
        """Start the splash screen animation using the animation manager."""
        # Set initial state
        self.showing_splash = True
        self.message_label.setText("")
        self.status_label.setText("INITIALIZING SYSTEM...")
        
        # Clear the punch card grid for animation
        self.punch_card.clear_grid()
        
        # Disable buttons during splash
        for button in [self.start_button, self.clear_button, self.exit_button]:
            button.setEnabled(False)
            button.setStyleSheet("""
                background-color: #2A2A2A;
                color: #AAAAAA;
                border: 1px solid #444444;
                padding: 6px 12px;
                border-radius: 3px;
                opacity: 0.5;
            """)
        
        # Skip hardware detection
        if hasattr(self, 'hardware_detector'):
            self.hardware_detector.enable_virtual_mode()
            self.hardware_check_complete = True
            self.hardware_detection_finished = True
        
        # Reset animation flags
        self.animation_started = False
        
        # Load the punch card sounds if not already loaded
        if hasattr(self, 'load_punch_card_sounds'):
            self.load_punch_card_sounds()
        
        # Console log for debugging
        if hasattr(self, 'console'):
            self.console.log("Splash screen started using animation manager", "INFO")
            
        # Start the startup animation
        self.animation_manager.play_animation(AnimationType.STARTUP, callback=self.complete_splash_screen)
        
        # Schedule post-wake setup after animation completes (if waking from sleep)
        if hasattr(self, 'sleeping') and not self.sleeping:
            QTimer.singleShot(5000, self.post_wake_setup)

    def on_animation_finished(self, animation_type):
        """Handle animation completion events"""
        if hasattr(self, 'console'):
            self.console.log(f"Animation finished: {animation_type}", "INFO")
            
        # Handle specific animation completion events
        if animation_type == AnimationType.STARTUP:
            # Play final sound
            self.play_sound("eject")
        elif animation_type == AnimationType.SLEEP:
            # Update status
            self.update_status("SLEEPING")
        elif animation_type == AnimationType.WAKE:
            # Update status
            self.update_status("READY")
        
        # Update text positioning
        self.position_text_elements()

    def start_animation(self):
        """Start the animation timer for the splash screen."""
        # If the animation is already started, don't restart it
        if hasattr(self, 'animation_started') and self.animation_started:
            return
            
        # Set animation as started regardless of hardware detection status
        self.animation_started = True
        
        # Update the status text
        if hasattr(self, 'status_label'):
            self.status_label.setText("STARTING ANIMATION...")
        
        # Log the animation start
        if hasattr(self, 'console'):
            self.console.log("Starting splash animation", "INFO")
        elif hasattr(self, 'console_window'):
            self.console_window.log("Starting splash animation", "INFO")
        
        # Make sure hardware detection is considered finished
        if hasattr(self, 'hardware_detection_finished'):
            self.hardware_detection_finished = True
        
        if hasattr(self, 'hardware_check_complete'):
            self.hardware_check_complete = True
        
        # Ensure the hardware detector is in a valid state if it exists
        if hasattr(self, 'hardware_detector') and not self.hardware_detector.detection_complete:
            self.hardware_detector.enable_virtual_mode()
        
        # Start the startup animation
        self.animation_manager.play_animation(AnimationType.STARTUP, callback=self.complete_splash_screen)

    def update_hardware_status(self):
        """Update the hardware status label."""
        # If hardware detection is complete and animation hasn't started yet
        if self.hardware_detector.detection_complete and not self.animation_started:
            # Completely hide the hardware status label - don't show any status text at all
            self.hardware_status_label.setText("")
            
            # Keep this part to set flags and start animation if not already started
            if not self.hardware_check_complete:
                self.hardware_check_complete = True
                self.hardware_detection_finished = True
                
                # Log to console but don't show in the UI
                mode_type = "hardware" if not self.hardware_detector.using_virtual_mode else "virtual"
                self.console.log(f"Hardware detection complete - using {mode_type} mode", "INFO")
                
                # Intentionally set empty text for all labels that might show mode
                self.keyboard_hint_label.setText("")
                self.hardware_status_label.setText("")
                
                # Make the labels invisible to be safe
                self.keyboard_hint_label.setVisible(False)
                self.hardware_status_label.setVisible(False)
                
                # Start the animation
                self.start_animation()
                
        # If hardware detection is still in progress and animation hasn't started
        elif not self.hardware_detector.detection_complete and not self.animation_started:
            # Hardware detection still in progress - but don't show status
            self.hardware_status_label.setText("")
    
    def update_splash(self):
        """Simple splash animation that gradually clears the punch card."""
        # Check if we're in splash mode
        if not hasattr(self, 'showing_splash') or not self.showing_splash:
            return
            
        # Calculate total steps needed for the animation
        NUM_ROWS = self.punch_card.num_rows
        NUM_COLS = self.punch_card.num_cols
        total_steps = NUM_COLS + NUM_ROWS - 1  # Total for diagonal coverage
        
        # Get punch card reference
        punch_card = self.punch_card
        
        # Update progress
        if not hasattr(self, 'splash_progress'):
            self.splash_progress = 0
            
        self.splash_progress += 2
        
        # Log progress periodically
        if self.splash_progress % 5 == 0:
            self.console.log(f"Animation progress: {self.splash_progress} of {total_steps*2 + 12}", "INFO")
        
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
            if hasattr(self, 'splash_timer'):
                self.splash_timer.stop()
                
            # Play final sound
            self.play_sound("eject")
                
            # Complete splash screen setup
            self.complete_splash_screen()
            return
        
        # Play sound effects
        if self.splash_progress % 10 == 0:
            self.play_sound("punch")
            
        if self.splash_progress == 5:
            self.play_sound("insert")
            
        # Phase transitions based on progress
        current_phase = 0
        if self.splash_progress < total_steps:
            current_phase = 1  # Phase 1: Clearing
        elif self.splash_progress < total_steps * 2:
            current_phase = 2  # Phase 2: Diagonal illumination
        else:
            current_phase = 3  # Phase 3: Final clearing
            
        # Phase 1: Initial clearing (empty card)
        if current_phase == 1:
            # Make sure the top-left corner (0,0) is explicitly cleared first
            if self.splash_progress == 0:
                self.console.log("Phase 1: Starting with empty grid and clearing diagonally", "INFO")
                punch_card.set_led(0, 0, False)
            
            # Calculate current diagonal position
            current_step = self.splash_progress
            for row in range(NUM_ROWS):
                col = current_step - row
                if 0 <= col < NUM_COLS:
                    # Skip the top-left corner as we've already handled it
                    if not (row == 0 and col == 0):
                        punch_card.set_led(row, col, False)
        
        # Phase 2: Diagonal illumination with 12-column wide band
        elif current_phase == 2:
            current_step = self.splash_progress - total_steps
            
            # At the beginning of Phase 2, explicitly turn on the top-left corner
            if current_step == 0:
                self.console.log("Phase 2: Creating diagonal pattern of illuminated LEDs", "INFO")
                punch_card.set_led(0, 0, True)
            
            # Illuminate LEDs at the current diagonal
            for row in range(NUM_ROWS):
                col = current_step - row
                if 0 <= col < NUM_COLS:
                    # Skip the top-left corner as we've already handled it
                    if not (row == 0 and col == 0):
                        punch_card.set_led(row, col, True)
            
            # Clear old illuminated LEDs (trailing diagonal - 12 columns wide)
            trailing_step = max(0, current_step - 12)
            for row in range(NUM_ROWS):
                col = trailing_step - row
                if 0 <= col < NUM_COLS:
                    # Only clear top-left corner when it's definitely time
                    if row == 0 and col == 0 and current_step >= 12:
                        punch_card.set_led(0, 0, False)
                    elif not (row == 0 and col == 0):
                        punch_card.set_led(row, col, False)
        
        # Phase 3: Clear the remaining illuminated LEDs
        elif current_phase == 3:
            current_clear_step = self.splash_progress - (total_steps * 2) + (total_steps - 12)
            
            for row in range(NUM_ROWS):
                col = current_clear_step - row
                if 0 <= col < NUM_COLS:
                    # Skip the top-left corner as we've already handled it
                    if not (row == 0 and col == 0):
                        punch_card.set_led(row, col, False)
        
        # Force a repaint to show the updated grid
        punch_card.update()
    
    def complete_splash_screen(self):
        """Complete the splash screen transition and prepare for normal operation."""
        # Set state
        self.showing_splash = False
        
        # Make sure countdown timer is stopped
        if hasattr(self, 'countdown_timer') and hasattr(self.countdown_timer, 'isActive') and self.countdown_timer.isActive():
            self.countdown_timer.stop()
        
        # Update the status text
        self.status_label.setText("READY")
        
        # Log completion
        if hasattr(self, 'console'):
            self.console.log("Splash screen completed, ready for operation", "INFO")
        
        # Display system ready message
        self.message_label.setText("SYSTEM READY")
        
        # AGGRESSIVELY hide ALL hardware status elements 
        if hasattr(self, 'hardware_status_label'):
            self.hardware_status_label.setText("")
            self.hardware_status_label.setVisible(False)
            self.hardware_status_label.setStyleSheet("color: transparent; padding: 0px; margin: 0px; height: 0px;")
        
        if hasattr(self, 'keyboard_hint_label'):
            self.keyboard_hint_label.setText("")
            self.keyboard_hint_label.setVisible(False)
            self.keyboard_hint_label.setStyleSheet("color: transparent; padding: 0px; margin: 0px; height: 0px;")
        
        # Restore button styles with simple styling
        for button in [self.start_button, self.clear_button, self.exit_button]:
            button.setStyleSheet("""
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #444444;
                padding: 6px 12px;
                border-radius: 3px;
            """)
            button.setEnabled(True)
        
        # Start auto messages after delay
        QTimer.singleShot(5000, lambda: self.auto_timer.start(5000))
    
    def on_animation_finished(self, animation_type):
        """Handle animation completion events"""
        if hasattr(self, 'console'):
            self.console.log(f"Animation finished: {animation_type}", "INFO")
            
        # Handle specific animation completion events
        if animation_type == AnimationType.STARTUP:
            # Play final sound
            self.play_sound("eject")
        elif animation_type == AnimationType.SLEEP:
            # Update status
            self.update_status("SLEEPING")
        elif animation_type == AnimationType.WAKE:
            # Update status
            self.update_status("READY")
        
        # Update text positioning
        self.position_text_elements()
    
    def force_text_positioning(self):
        """Force text layout update (no longer needed with layout containers)."""
        # Force a visual update immediately
        self.message_label.update()
        self.status_label.update()
        # Log the action
        self.console.log("Text layout updated", "INFO")
    
    def position_text_elements(self):
        """No longer needed as we're using layout containers."""
        pass  # Labels are now positioned by the layout system
    
    def showEvent(self, event):
        """Handle show event to ensure proper text positioning after window is rendered."""
        super().showEvent(event)
        # Position text elements after the window has been shown
        QTimer.singleShot(100, self.position_text_elements)
    
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
        
        # Play the clear sound
        self.play_sound("clear")
        
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
                
                # Display settings
                if 'message_display_time' in settings_data:
                    self.message_display_time = settings_data['message_display_time']
                    self.console.log(f"Message display time loaded: {self.message_display_time} seconds", "INFO")
                
                if 'led_delay' in settings_data:
                    self.led_delay = settings_data['led_delay']
                    self.timer.setInterval(self.led_delay)
                    self.console.log(f"LED delay loaded: {self.led_delay} ms", "INFO")
                
                # Sound settings
                if hasattr(self, 'sound_manager'):
                    # Volume
                    if 'volume' in settings_data:
                        volume = float(settings_data['volume'])
                        self.sound_manager.set_volume(volume)
                        self.console.log(f"Volume loaded: {int(volume * 100)}%", "INFO")
                    
                    # Mute state
                    if 'muted' in settings_data:
                        muted = bool(settings_data['muted'])
                        self.sound_manager.set_muted(muted)
                        self.console.log(f"Mute state loaded: {muted}", "INFO")
                    
                    # Sound mappings
                    if 'sound_mappings' in settings_data:
                        mappings = settings_data['sound_mappings']
                        self.sound_manager.update_sound_mappings(mappings)
                        self.console.log(f"Sound mappings loaded", "INFO")
                
                # Update settings dialog values if it exists
                if hasattr(self, 'settings'):
                    self.settings.led_delay.setValue(self.led_delay)
                    self.settings.message_display_time.setValue(self.message_display_time)
            else:
                self.console.log("No settings file found, using defaults", "WARNING")
                
                # Save default settings for future use
                self.save_default_settings()
        
        except Exception as e:
            self.console.log(f"Error loading settings: {str(e)}", "ERROR")
    
    def save_default_settings(self):
        """Save default settings to file."""
        try:
            settings = {
                "led_delay": self.led_delay,
                "message_display_time": self.message_display_time,
                "volume": 1.0,
                "muted": False,
                "sound_mappings": {
                    "punch": "Tink",
                    "complete": "Glass", 
                    "clear": "Pop",
                    "startup": "Hero"
                }
            }
            
            settings_path = "punch_card_settings.json"
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=4)
                
            self.console.log("Default settings saved", "INFO")
        except Exception as e:
            self.console.log(f"Error saving default settings: {str(e)}", "ERROR")

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
        """Start the sleep mode animation sequence."""
        # Don't start if already sleeping
        if hasattr(self, 'sleeping') and self.sleeping:
            return
            
        # Log the start of sleep mode
        if hasattr(self, 'console'):
            self.console.log("Starting sleep mode", "INFO")
            
        # Update status
        self.update_status("ENTERING SLEEP MODE...")
            
        # Set sleeping state
        self.sleeping = True
        
        # CRITICAL: Stop any ongoing message display or animations
        for timer_attr in ['timer', 'display_timer', 'message_display_timer', 'auto_timer', 'splash_timer']:
            if hasattr(self, timer_attr) and hasattr(getattr(self, timer_attr), 'isActive') and getattr(self, timer_attr).isActive():
                getattr(self, timer_attr).stop()
                if hasattr(self, 'console'):
                    self.console.log(f"Stopped {timer_attr} for sleep mode", "INFO")
        
        # Clear any running processes
        self.running = False
        
        # Disable buttons
        for button in [self.start_button, self.clear_button, self.exit_button]:
            button.setEnabled(False)
            button.setStyleSheet("""
                background-color: #2A2A2A;
                color: #AAAAAA;
                border: 1px solid #444444;
                padding: 6px 12px;
                border-radius: 4px;
            """)
        
        # Create wake button if it doesn't exist
        if not hasattr(self, 'wake_button'):
            self.wake_button = RetroButton("WAKE", self)
            self.wake_button.clicked.connect(self.wake_from_sleep)
            self.wake_button.setFixedSize(100, 30)
            
            # Center the wake button
            self.wake_button.move(
                (self.width() - self.wake_button.width()) // 2,
                self.height() - 70
            )
        
        # Show the wake button
        self.wake_button.show()
        
        # Play sleep animation
        self.animation_manager.play_animation(AnimationType.SLEEP, callback=self.on_sleep_complete)
        
        # Play card insert sound
        self.play_sound("insert")
    
    def on_sleep_complete(self):
        """Called when sleep animation completes"""
        # Log completion
        if hasattr(self, 'console'):
            self.console.log("Sleep animation completed, system is now sleeping", "SUCCESS")
        
        # Update status
        self.update_status("SLEEPING")
    
    def wake_from_sleep(self):
        """Wake up from sleep mode and restart the animation sequence."""
        # Only proceed if we're sleeping
        if not hasattr(self, 'sleeping') or not self.sleeping:
            return
        
        # Remove the wake button
        if hasattr(self, 'wake_button'):
            self.wake_button.deleteLater()
            delattr(self, 'wake_button')
        
        # Update state
        self.sleeping = False
        self.update_status("WAKING UP...")
        
        # Log the wake event
        if hasattr(self, 'console'):
            self.console.log("Waking from sleep mode", "INFO")
        
        # Play card insert sound
        self.play_sound("insert")
        
        # Reset animation-related flags
        self.showing_splash = True
        self.animation_started = False
        
        # Clear the grid to start fresh
        self.punch_card.clear_grid()
        
        # Start wake animation
        self.animation_manager.play_animation(AnimationType.WAKE, callback=self.on_wake_complete)
    
    def on_wake_complete(self):
        """Called when wake animation completes"""
        # Perform post-wake setup after a delay
        QTimer.singleShot(500, self.post_wake_setup)

    def load_punch_card_sounds(self):
        """Load punch card sounds for animations using the SoundManager."""
        try:
            if not hasattr(self, 'sound_manager'):
                self.initialize_sound_system()
            return True
        except Exception as e:
            self.console.log(f"Error loading punch card sounds: {str(e)}", "ERROR")
            import traceback
            self.console.log(f"Traceback: {traceback.format_exc()}", "ERROR")
            return False
    
    def play_sound(self, sound_type):
        """Play a sound using the SoundManager."""
        if hasattr(self, 'sound_manager'):
            return self.sound_manager.play_sound(sound_type)
        else:
            # Try to initialize sound manager if not done yet
            self.load_punch_card_sounds()
            if hasattr(self, 'sound_manager'):
                return self.sound_manager.play_sound(sound_type)
            return False
            
    def post_wake_setup(self):
        """Actions to perform after wake sequence completes."""
        # Update status
        self.update_status("READY")
        
        # Update the message label
        self.message_label.setText("SYSTEM READY")
        
        # Restart auto message timer
        QTimer.singleShot(2000, lambda: self.auto_timer.start(5000))

    def update_countdown(self):
        """Update the countdown timer display"""
        if hasattr(self, 'countdown_seconds'):
            self.countdown_seconds -= 1
            if self.countdown_seconds <= 0:
                self.countdown_timer.stop()
                self.hardware_detector.enable_virtual_mode()
                self.hardware_check_complete = True
                self.hardware_detection_finished = True
                self.status_label.setText("USING VIRTUAL MODE")
                self.keyboard_hint_label.setText("Hardware detection skipped - using VIRTUAL MODE")
                self.keyboard_hint_label.setStyleSheet(f"""
                    {get_font_css(italic=True, size=FONT_SIZE-2)}
                    color: {QColor(200, 200, 100).name()};
                    padding: 5px;
                """)
                # Start animation after short delay
                QTimer.singleShot(500, self.start_animation)
            else:
                # Update hardware hint label with countdown
                self.keyboard_hint_label.setText(f"Press [SPACE] to skip hardware detection ({self.countdown_seconds}s remaining)")

    def auto_skip_hardware_detection(self):
        """Skip hardware detection and use virtual mode"""
        # Stop the countdown timer if it's running
        if hasattr(self, 'countdown_timer') and self.countdown_timer.isActive():
            self.countdown_timer.stop()
        
        # Set up virtual mode
        self.hardware_detector.enable_virtual_mode()
        self.hardware_check_complete = True
        self.hardware_detection_finished = True
        
        # Update UI
        self.status_label.setText("SKIPPING HARDWARE DETECTION")
        self.keyboard_hint_label.setText("Using VIRTUAL MODE - hardware detection skipped")
        self.keyboard_hint_label.setStyleSheet(f"""
            {get_font_css(italic=True, size=FONT_SIZE-2)}
            color: {QColor(200, 200, 100).name()};
            padding: 5px;
        """)
        
        # Log the action
        if hasattr(self, 'console'):
            self.console.log("Hardware detection skipped by user - using virtual mode", "WARNING")
        
        # Start animation after short delay
        QTimer.singleShot(500, self.start_animation)

    def generate_next_message(self):
        """Generate and display the next random message."""
        # Only generate messages when not running, not showing splash screen, and no animation is playing
        if (not self.running and 
            not self.showing_splash and 
            hasattr(self, 'animation_manager') and 
            self.animation_manager.state != AnimationState.PLAYING):
            
            message = self.message_generator.generate_message()
            self.display_message(message)
        else:
            # Log reason for skipping message generation
            if self.running:
                self.console.log("Skipping message generation: already displaying message", "INFO")
            elif self.showing_splash:
                self.console.log("Skipping message generation: splash screen active", "INFO")
            elif hasattr(self, 'animation_manager') and self.animation_manager.state == AnimationState.PLAYING:
                self.console.log("Skipping message generation: animation is playing", "INFO")
                
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

    def update_label_margins(self):
        """Update the message and status container margins to align with the punch card.
        This is a simplified version that just adjusts the left padding."""
        try:
            # Only proceed if all required widgets exist
            if not hasattr(self, 'punch_card') or not hasattr(self, 'message_label') or not hasattr(self, 'status_label'):
                return
                
            # Ensure the layouts exist
            message_container = self.message_label.parent()
            status_container = self.status_label.parent()
            
            if not message_container or not status_container:
                return
                
            # Get the punch card's container and actual width
            card_width = getattr(self.punch_card, 'card_width', 562)  # Default to CARD_WIDTH
            container_width = self.punch_card.width()
            
            # Calculate the offset needed to align with punch card's left edge
            # This is approximately (content_width - card_width) / 2 + side_margin
            side_margin = getattr(self.punch_card, 'side_margin', 14)  # Default to SIDE_MARGIN
            left_offset = max(35, ((container_width - card_width) // 2) + side_margin - 5)  # 5px less to the right
            
            # Update container margins
            message_layout = message_container.layout()
            status_layout = status_container.layout()
            
            if message_layout:
                message_layout.setContentsMargins(left_offset, 10, 0, 0)  # Add 10px top margin
            
            if status_layout:
                status_layout.setContentsMargins(left_offset, 0, 0, 10)  # Add 10px bottom margin
                
            if hasattr(self, 'console'):
                self.console.log(f"Updated label margins to {left_offset}px", "INFO")
                
        except Exception as e:
            if hasattr(self, 'console'):
                self.console.log(f"Error updating label margins: {str(e)}", "ERROR")
    
    def resizeEvent(self, event):
        """Handle resize events."""
        super().resizeEvent(event)
        # Adjust label margins on resize
        QTimer.singleShot(100, self.update_label_margins)
    
    def showEvent(self, event):
        """Handle show event."""
        super().showEvent(event)
        # Update margins after the window is shown
        QTimer.singleShot(200, self.update_label_margins)
        
    def display_message(self, message: str, source: str = "", delay: int = 100):
        """Display a message with optional source information."""
        # Don't display messages during splash screen or when animations are running
        if self.showing_splash:
            self.console.log("Ignoring message display request during splash animation", "WARNING")
            return
            
        self.current_message = message.upper()
        self.current_char_index = 0
        
        # Clear the grid and play clear sound
        self.punch_card.clear_grid()
        self.play_sound("clear")
        
        self.led_delay = delay
        self.timer.setInterval(delay)
        
        # Update message label
        self.message_label.setText(message)
        
        # Update label margins
        self.update_label_margins()
        
        # Update statistics
        if hasattr(self, 'stats'):
            self.stats.update_message_stats(message, message_type=source or "Local")
            # Refresh stats panel if visible
            if hasattr(self, 'stats_panel') and self.stats_panel.isVisible():
                self.stats_panel.refresh_stats()
        
        self.update_status(f"PROCESSING: {message}")
        self.start_display()

    def initialize_sound_system(self):
        """Initialize the sound system with proper logging."""
        try:
            from src.utils.sound_manager import get_sound_manager
            
            # Only initialize if not already initialized
            if self.sound_manager is None:
                self.console.log("Initializing sound system...", "INFO")
                
                # Get sound manager instance
                self.sound_manager = get_sound_manager(self.console)
                
                # Update sound mappings
                self.sound_manager.update_sound_mappings({
                    'punch': 'Tink',
                    'complete': 'Glass',
                    'clear': 'Pop',
                    'startup': 'Hero',
                    'eject': 'Submarine',
                    'insert': 'Bottle'
                })
                
                # Test sound system after a delay
                QTimer.singleShot(1000, self.test_sound_system)
            
        except Exception as e:
            if hasattr(self, 'console'):
                self.console.log(f"Error initializing sound system: {str(e)}", "ERROR")
                import traceback
                self.console.log(f"Traceback: {traceback.format_exc()}", "ERROR")
    
    def test_sound_system(self):
        """Test the sound system by playing a test sound."""
        try:
            if self.sound_manager is not None:
                self.console.log("Testing sound system...", "INFO")
                success = self.play_sound("punch")
                if success:
                    self.console.log("Sound system test successful", "SUCCESS")
                else:
                    self.console.log("Sound system test failed - no sound played", "WARNING")
            else:
                self.console.log("Sound manager not initialized", "WARNING")
                self.initialize_sound_system()  # Try to initialize again
        except Exception as e:
            self.console.log(f"Error testing sound system: {str(e)}", "ERROR")
    
    def play_sound(self, sound_type: str) -> bool:
        """Play a sound using the SoundManager."""
        try:
            if self.sound_manager is None:
                self.console.log("Sound manager not initialized, initializing now...", "WARNING")
                self.initialize_sound_system()
            
            if self.sound_manager is not None:
                success = self.sound_manager.play_sound(sound_type)
                if not success:
                    self.console.log(f"Failed to play sound: {sound_type}", "WARNING")
                return success
            
            return False

        except Exception as e:
            self.console.log(f"Error playing sound {sound_type}: {str(e)}", "ERROR")
            return False

    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("New Message", self.new_message)
        file_menu.addAction("Open Message", self.open_message)
        file_menu.addAction("Save Message", self.save_message)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)
        
        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        settings_menu.addAction("Sound Settings", self.open_sound_settings)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About", self.show_about)
        help_menu.addAction("Documentation", self.show_documentation)
    
    def open_sound_settings(self):
        """Open macOS System Settings to Sound settings."""
        from src.utils.sound_manager import get_sound_manager
        sound_manager = get_sound_manager(self.console)
        if sound_manager.open_sound_settings():
            self.console.log("Opened Sound settings", "INFO")
        else:
            self.console.log("Failed to open Sound settings", "WARNING")

    def show_statistics_dialog(self):
        """Show/hide the statistics panel as an overlay in the main window."""
        if self.stats_panel.isVisible():
            self.stats_panel.hide()
        else:
            # Position the panel in the top-right corner of the window
            x = self.width() - self.stats_panel.width() - 20
            y = 60  # Below the menu bar
            self.stats_panel.move(x, y)
            
            # Refresh stats before showing
            self.stats_panel.refresh_stats()
            
            self.stats_panel.show()
            self.stats_panel.raise_()  # Ensure it's on top

    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        
        # Update text element positions on resize
        self.position_text_elements()
        
        # Update stats panel position if visible
        if hasattr(self, 'stats_panel') and self.stats_panel.isVisible():
            x = self.width() - self.stats_panel.width() - 20
            y = 60  # Below the menu bar
            self.stats_panel.move(x, y)

class SoundSettingsDialog(QDialog):
    """Dialog for configuring sound settings."""
    
    # Define signals
    volume_changed = pyqtSignal(int)
    mute_changed = pyqtSignal(bool)
    sound_mappings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sound Settings")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Set dark theme matching main application
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background'].name()};
                color: {COLORS['text'].name()};
                border: none;
            }}
            QLabel {{
                color: {COLORS['text'].name()};
                {get_font_css(size=12)}
            }}
            QGroupBox {{
                color: {COLORS['text'].name()};
                border: 1px solid {COLORS['hole_outline'].name()};
                border-radius: 0px;
                margin-top: 1.5ex;
                {get_font_css(size=12)}
            }}
            QCheckBox {{
                color: {COLORS['text'].name()};
                {get_font_css(size=12)}
            }}
            QComboBox {{
                background-color: {COLORS['button_bg'].name()};
                color: {COLORS['text'].name()};
                border: 1px solid {COLORS['hole_outline'].name()};
                border-radius: 3px;
                padding: 5px;
                min-width: 200px;
                {get_font_css(size=12)}
            }}
            QComboBox:hover {{
                background-color: {COLORS['button_hover'].name()};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: none;
            }}
            QPushButton {{
                background-color: {COLORS['button_bg'].name()};
                color: {COLORS['text'].name()};
                border: 1px solid {COLORS['hole_outline'].name()};
                border-radius: 3px;
                padding: 5px 15px;
                {get_font_css(size=12)}
            }}
            QPushButton:hover {{
                background-color: {COLORS['button_hover'].name()};
            }}
            QSlider::groove:horizontal {{
                background: {COLORS['button_bg'].name()};
                height: 4px;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {COLORS['text'].name()};
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }}
            QSlider::sub-page:horizontal {{
                background: {COLORS['text'].name()};
                height: 4px;
                border-radius: 2px;
            }}
        """)
        
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Volume Control Section
        volume_group = QGroupBox("Volume Control")
        volume_layout = QVBoxLayout(volume_group)
        volume_layout.setSpacing(10)
        
        # Volume slider with label and value
        volume_slider_layout = QHBoxLayout()
        volume_label = QLabel("Volume:")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_value = QLabel("100%")
        volume_slider_layout.addWidget(volume_label)
        volume_slider_layout.addWidget(self.volume_slider)
        volume_slider_layout.addWidget(self.volume_value, 0, Qt.AlignmentFlag.AlignRight)
        volume_layout.addLayout(volume_slider_layout)
        
        # Mute checkbox
        self.mute_checkbox = QCheckBox("Mute all sounds")
        volume_layout.addWidget(self.mute_checkbox)
        
        layout.addWidget(volume_group)
        
        # Sound Selection Section
        sound_group = QGroupBox("Sound Selection")
        sound_layout = QVBoxLayout(sound_group)
        sound_layout.setSpacing(15)
        
        # Create sound selection controls
        self.sound_controls = {}
        sound_types = {
            "punch": "Punch/Typing Sound",
            "complete": "Message Complete Sound",
            "clear": "Clear Card Sound",
            "startup": "Startup Sound"
        }
        
        # Get available sounds from sound manager
        available_sounds = ["Tink", "Glass", "Pop", "Hero", "Bottle", "Frog", "Funk",
                          "Morse", "Ping", "Purr", "Sosumi", "Submarine"]
        
        for sound_type, label in sound_types.items():
            control_layout = QHBoxLayout()
            control_layout.setSpacing(10)
            
            # Label with fixed width for alignment
            sound_label = QLabel(f"{label}:")
            sound_label.setFixedWidth(150)
            control_layout.addWidget(sound_label)
            
            # Combo box for sound selection
            combo = QComboBox()
            combo.addItems(available_sounds)
            
            # Set default sound based on type
            default_sound = {
                "punch": "Tink",
                "complete": "Glass",
                "clear": "Pop",
                "startup": "Hero"
            }.get(sound_type, "Tink")
            
            combo.setCurrentText(default_sound)
            self.sound_controls[sound_type] = combo
            control_layout.addWidget(combo)
            
            # Test button
            test_button = QPushButton("Test")
            test_button.setFixedWidth(60)
            test_button.clicked.connect(lambda checked, s=sound_type: self.test_sound(s))
            control_layout.addWidget(test_button)
            
            sound_layout.addLayout(control_layout)
        
        layout.addWidget(sound_group)
        
        # Add spacer
        layout.addStretch()
        
        # Buttons at the bottom
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # System sound settings button (left-aligned)
        system_button = QPushButton("System Sound Settings...")
        system_button.clicked.connect(self.open_system_settings)
        button_layout.addWidget(system_button)
        
        button_layout.addStretch()
        
        # Save and Cancel buttons (right-aligned)
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        self.mute_checkbox.stateChanged.connect(self.on_mute_changed)
        
        # Initialize with current settings if parent has sound manager
        if parent and hasattr(parent, 'sound_manager'):
            volume = int(parent.sound_manager.volume * 100)
            self.volume_slider.setValue(volume)
            self.volume_value.setText(f"{volume}%")
            self.mute_checkbox.setChecked(parent.sound_manager.muted)
            
            # Set sound mappings
            for sound_type, combo in self.sound_controls.items():
                mapped_sound = parent.sound_manager.sound_mappings.get(sound_type)
                if mapped_sound:
                    index = combo.findText(mapped_sound)
                    if index >= 0:
                        combo.setCurrentIndex(index)
    
    def on_volume_changed(self, value):
        """Handle volume slider value changes."""
        self.volume_value.setText(f"{value}%")
        self.volume_changed.emit(value)
        
        # Play test sound if not muted
        if not self.mute_checkbox.isChecked():
            self.test_sound("punch")
    
    def on_mute_changed(self, state):
        """Handle mute checkbox state changes."""
        is_muted = state == Qt.CheckState.Checked.value
        self.mute_changed.emit(is_muted)
        
        # Update UI to reflect muted state
        self.volume_slider.setEnabled(not is_muted)
        for combo in self.sound_controls.values():
            combo.setEnabled(not is_muted)
    
    def test_sound(self, sound_type):
        """Test the selected sound."""
        if self.parent() and hasattr(self.parent(), 'sound_manager'):
            sound_name = self.sound_controls[sound_type].currentText()
            self.parent().sound_manager.play_sound(sound_name)
    
    def open_system_settings(self):
        """Open system sound settings."""
        if self.parent() and hasattr(self.parent(), 'sound_manager'):
            self.parent().sound_manager.open_sound_settings()
    
    def save_settings(self):
        """Save the current sound settings."""
        # Get current sound mappings
        mappings = {
            sound_type: combo.currentText()
            for sound_type, combo in self.sound_controls.items()
        }
        
        # Emit signals with current settings
        self.volume_changed.emit(self.volume_slider.value())
        self.mute_changed.emit(self.mute_checkbox.isChecked())
        self.sound_mappings_changed.emit(mappings)
        
        # Save settings to file
        try:
            import json
            import os
            
            settings_path = "punch_card_settings.json"
            existing_settings = {}
            
            # Load existing settings if available
            if os.path.exists(settings_path):
                try:
                    with open(settings_path, "r") as f:
                        existing_settings = json.load(f)
                except Exception:
                    pass
            
            # Update sound settings
            existing_settings["volume"] = self.volume_slider.value() / 100.0
            existing_settings["muted"] = self.mute_checkbox.isChecked()
            existing_settings["sound_mappings"] = mappings
            
            # Save settings
            with open(settings_path, "w") as f:
                json.dump(existing_settings, f, indent=4)
            
        except Exception as e:
            if hasattr(self.parent(), 'console'):
                self.parent().console.log(f"Error saving sound settings: {str(e)}", "ERROR")
        
        # Close dialog
        self.accept()

class StatsPanel(QFrame):
    """Panel for viewing punch card statistics in an angular and modular design."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(450, 550)
        self.setStyleSheet("""
            QFrame {
                background-color: black;
                color: white;
                border: 1px solid #444444;
            }
            QLabel {
                color: white;
                font-family: 'Courier New';
                font-size: 12px;
                padding: 1px;
                min-width: 120px;
            }
            QGroupBox {
                color: white;
                border: 1px solid #444444;
                border-radius: 0px;
                margin-top: 1.5ex;
                font-family: 'Courier New';
                font-size: 12px;
                font-weight: bold;
                padding: 4px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: white;
                font-family: 'Courier New';
                font-size: 12px;
                font-weight: bold;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Header
        header_label = QLabel("📊 Punch Card Statistics")
        header_label.setStyleSheet(f"{get_font_css(size=14, bold=True)}")
        layout.addWidget(header_label)
        
        # Stats content layout
        content_layout = QVBoxLayout()
        content_layout.setSpacing(8)
        layout.addLayout(content_layout)
        
        # Add General Stats
        self.general_group = QGroupBox("General Statistics")
        general_layout = QGridLayout()
        self.general_group.setLayout(general_layout)
        general_layout.setContentsMargins(8, 15, 8, 8)
        general_layout.setSpacing(4)
        general_layout.setColumnMinimumWidth(1, 120)
        
        # We'll populate these in update_stats
        self.cards_processed_label = QLabel("0")
        self.total_holes_label = QLabel("0")
        self.avg_msg_length_label = QLabel("0.00 characters")
        self.processing_rate_label = QLabel("0.00 cards/hour")
        self.most_used_char_label = QLabel("None")
        self.least_used_char_label = QLabel("None")
        
        # Set alignment for all value labels
        for label in [self.cards_processed_label, self.total_holes_label, 
                     self.avg_msg_length_label, self.processing_rate_label,
                     self.most_used_char_label, self.least_used_char_label]:
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            label.setMinimumWidth(120)
        
        general_layout.addWidget(QLabel("Cards Processed:"), 0, 0)
        general_layout.addWidget(self.cards_processed_label, 0, 1)
        
        general_layout.addWidget(QLabel("Total Holes:"), 1, 0)
        general_layout.addWidget(self.total_holes_label, 1, 1)
        
        general_layout.addWidget(QLabel("Avg Message Length:"), 2, 0)
        general_layout.addWidget(self.avg_msg_length_label, 2, 1)
        
        general_layout.addWidget(QLabel("Processing Rate:"), 3, 0)
        general_layout.addWidget(self.processing_rate_label, 3, 1)
        
        general_layout.addWidget(QLabel("Most Used Char:"), 4, 0)
        general_layout.addWidget(self.most_used_char_label, 4, 1)
        
        general_layout.addWidget(QLabel("Least Used Char:"), 5, 0)
        general_layout.addWidget(self.least_used_char_label, 5, 1)
        
        content_layout.addWidget(self.general_group)
        
        # Message Types
        self.types_group = QGroupBox("Message Types")
        types_layout = QGridLayout()
        self.types_group.setLayout(types_layout)
        types_layout.setContentsMargins(8, 15, 8, 8)
        types_layout.setSpacing(4)
        types_layout.setColumnMinimumWidth(1, 120)
        
        self.local_count_label = QLabel("0")
        self.ai_count_label = QLabel("0")
        self.database_count_label = QLabel("0")
        self.other_count_label = QLabel("0")
        
        # Set alignment for all value labels
        for label in [self.local_count_label, self.ai_count_label,
                     self.database_count_label, self.other_count_label]:
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            label.setMinimumWidth(120)
        
        types_layout.addWidget(QLabel("Local:"), 0, 0)
        types_layout.addWidget(self.local_count_label, 0, 1)
        
        types_layout.addWidget(QLabel("AI:"), 1, 0)
        types_layout.addWidget(self.ai_count_label, 1, 1)
        
        types_layout.addWidget(QLabel("Database:"), 2, 0)
        types_layout.addWidget(self.database_count_label, 2, 1)
        
        types_layout.addWidget(QLabel("Other:"), 3, 0)
        types_layout.addWidget(self.other_count_label, 3, 1)
        
        content_layout.addWidget(self.types_group)
        
        # Error Statistics
        self.error_group = QGroupBox("Error Statistics")
        error_layout = QGridLayout()
        self.error_group.setLayout(error_layout)
        error_layout.setContentsMargins(8, 15, 8, 8)
        error_layout.setSpacing(4)
        error_layout.setColumnMinimumWidth(1, 120)
        
        self.encoding_errors_label = QLabel("0")
        self.invalid_chars_label = QLabel("0")
        self.msg_too_long_label = QLabel("0")
        self.other_errors_label = QLabel("0")
        
        # Set alignment for all value labels
        for label in [self.encoding_errors_label, self.invalid_chars_label,
                     self.msg_too_long_label, self.other_errors_label]:
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            label.setMinimumWidth(120)
        
        error_layout.addWidget(QLabel("Encoding Errors:"), 0, 0)
        error_layout.addWidget(self.encoding_errors_label, 0, 1)
        
        error_layout.addWidget(QLabel("Invalid Characters:"), 1, 0)
        error_layout.addWidget(self.invalid_chars_label, 1, 1)
        
        error_layout.addWidget(QLabel("Message Too Long:"), 2, 0)
        error_layout.addWidget(self.msg_too_long_label, 2, 1)
        
        error_layout.addWidget(QLabel("Other Errors:"), 3, 0)
        error_layout.addWidget(self.other_errors_label, 3, 1)
        
        content_layout.addWidget(self.error_group)
        
        # Add buttons with more spacing
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        self.refresh_btn = RetroButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_stats)
        button_layout.addWidget(self.refresh_btn)
        
        self.reset_btn = RetroButton("Reset")
        self.reset_btn.clicked.connect(self.reset_stats)
        button_layout.addWidget(self.reset_btn)
        
        button_layout.addStretch()
        
        self.close_btn = RetroButton("Close")
        self.close_btn.clicked.connect(self.hide)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        # Add a refresh timer to update stats periodically 
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_stats)
        self.refresh_timer.setInterval(5000)  # 5 seconds
        
    def showEvent(self, event):
        """Handle show event to update stats and start refresh timer."""
        super().showEvent(event)
        self.refresh_stats()
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
    
    def hideEvent(self, event):
        """Handle hide event to stop refresh timer."""
        super().hideEvent(event)
        if hasattr(self, 'refresh_timer') and self.refresh_timer.isActive():
            self.refresh_timer.stop()
    
    def refresh_stats(self):
        """Refresh the statistics display."""
        if not hasattr(self.parent(), 'stats'):
            return
            
        stats = self.parent().stats.get_stats()
        
        # Update general stats
        self.cards_processed_label.setText(f"{stats.get('cards_processed', 0):,}")
        self.total_holes_label.setText(f"{stats.get('total_holes', 0):,}")
        
        avg_msg_length = stats.get('average_message_length', 0)
        self.avg_msg_length_label.setText(f"{avg_msg_length:.2f} characters")
        
        processing_rate = stats.get('processing_rate', 0)
        self.processing_rate_label.setText(f"{processing_rate:.2f} cards/hour")
        
        most_used = stats.get('most_used_char', '')
        if most_used:
            self.most_used_char_label.setText(f"'{most_used}'")
        else:
            self.most_used_char_label.setText("None")
            
        least_used = stats.get('least_used_char', '')
        if least_used:
            self.least_used_char_label.setText(f"'{least_used}'")
        else:
            self.least_used_char_label.setText("None")
        
        # Update message types
        message_types = stats.get('message_types', {})
        self.local_count_label.setText(f"{message_types.get('Local', 0):,}")
        self.ai_count_label.setText(f"{message_types.get('AI', 0):,}")
        self.database_count_label.setText(f"{message_types.get('Database', 0):,}")
        self.other_count_label.setText(f"{message_types.get('Other', 0):,}")
        
        # Update error stats
        error_stats = stats.get('error_stats', {})
        self.encoding_errors_label.setText(f"{error_stats.get('encoding_errors', 0):,}")
        self.invalid_chars_label.setText(f"{error_stats.get('invalid_characters', 0):,}")
        self.msg_too_long_label.setText(f"{error_stats.get('message_too_long', 0):,}")
        self.other_errors_label.setText(f"{error_stats.get('other_errors', 0):,}")
    
    def reset_stats(self):
        """Reset the statistics."""
        confirm = QMessageBox.question(
            self, 
            "Reset Statistics",
            "Are you sure you want to reset all punch card statistics?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            if hasattr(self.parent(), 'stats'):
                # Create a new PunchCardStats instance with default values
                self.parent().stats = PunchCardStats()
                QMessageBox.information(
                    self, 
                    "Statistics Reset",
                    "Punch card statistics have been reset."
                )
                self.refresh_stats()
    
    def paintEvent(self, event):
        """Custom paint event to draw an angular border."""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw border
        painter.setPen(QPen(QColor(COLORS['hole_outline']), 1))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

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