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

# Import components
from src.display.components.punch_card_widget import PunchCardWidget
from src.display.components.console_window import ConsoleWindow
from src.display.components.menu_bar import InAppMenuBar, WiFiStatusWidget
from src.display.components.stats_panel import StatsPanel
from src.display.components.settings.sound_settings_dialog import SoundSettingsDialog
from src.display.components.message_generator import MessageGenerator
from src.display.components.hardware_detector import HardwareDetector
from src.display.components.api_console_window import APIConsoleWindow
from src.display.components.console_logger import ConsoleLogger

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

class PunchCardDisplay(QMainWindow):
    """Main window for the minimalist punch card display application."""
    
    def __init__(self, punch_card=None, enable_animations=True, animation_fps=30):
        """Initialize the punch card display application."""
        super().__init__()
        
        # Various state flags
        self.running = False
        self.showing_splash = True
        self.animation_started = False
        self.sleeping = False
        
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
        self.led_delay = 100
        self.message_delay = 3000
        self.message_display_time = 5  # Default 5 seconds for message display
        self.current_message = ""
        self.current_char_index = 0
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
            self.position_text_elements()
        
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
        """Show card dimensions settings tab."""
        # Create a new settings dialog instance each time
        settings_dialog = SettingsDialog(self)
        settings_dialog.tab_widget.setCurrentIndex(1)  # "Card Dimensions" tab index
        if settings_dialog.exec() == QDialog.DialogCode.Accepted:
            settings = settings_dialog.get_settings()
            # Apply the settings
            self.led_delay = settings.get('led_delay', self.led_delay)
            self.message_display_time = settings.get('message_display_time', self.message_display_time)
            self.timer.setInterval(self.led_delay)
            if hasattr(self, 'punch_card'):
                card_settings = {k: v for k, v in settings.items() if k in [
                    'scale_factor', 'top_margin', 'side_margin', 'row_spacing',
                    'column_spacing', 'hole_width', 'hole_height'
                ]}
                self.punch_card.update_dimensions(card_settings)
            self.console.log(f"Settings updated: {settings}", "INFO")
        
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
            # Create and show the settings dialog
            settings_dialog = SettingsDialog(self)
            if settings_dialog.exec() == QDialog.DialogCode.Accepted:
                settings = settings_dialog.get_settings()
                self.led_delay = settings.get('led_delay', self.led_delay)
                self.message_display_time = settings.get('message_display_time', self.message_display_time)
                self.timer.setInterval(self.led_delay)
                self.console.log(f"Settings updated: {settings}", "INFO")
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
                
                # Update sound mappings with all necessary sounds
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