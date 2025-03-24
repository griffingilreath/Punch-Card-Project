#!/usr/bin/env python3
"""
Test script to demonstrate message display time functionality.
This is a simplified version of the punch card display focused only
on demonstrating the message display and clear timing.
"""

import sys
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QSpinBox, QFormLayout
from PyQt6.QtCore import Qt, QTimer

# Default settings
DEFAULT_SETTINGS = {
    "message_interval": 60,  # How often to show a new message (seconds)
    "message_display_time": 5,  # How long to display each message before clearing (seconds)
}

class SimpleMessageDisplay(QMainWindow):
    """Simple display to demonstrate message display time functionality."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Message Display Time Test")
        self.setGeometry(100, 100, 800, 400)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create message label
        self.message_label = QLabel("Ready")
        self.message_label.setStyleSheet("font-size: 24px; color: white;")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.message_label)
        
        # Create settings area
        settings_widget = QWidget()
        settings_layout = QFormLayout(settings_widget)
        
        # Display time setting
        self.display_time_spin = QSpinBox()
        self.display_time_spin.setRange(1, 60)
        self.display_time_spin.setSuffix(" seconds")
        self.display_time_spin.setValue(DEFAULT_SETTINGS["message_display_time"])
        self.display_time_spin.setToolTip("How long each message is displayed before being cleared")
        settings_layout.addRow("Display Time:", self.display_time_spin)
        
        # Interval setting
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 120)
        self.interval_spin.setSuffix(" seconds")
        self.interval_spin.setValue(DEFAULT_SETTINGS["message_interval"])
        self.interval_spin.setToolTip("How often to display a new message")
        settings_layout.addRow("Message Interval:", self.interval_spin)
        
        # Add settings to main layout
        layout.addWidget(settings_widget)
        
        # Create control buttons
        button_widget = QWidget()
        button_layout = QVBoxLayout(button_widget)
        
        # Display message button
        self.display_button = QPushButton("Display Message")
        self.display_button.clicked.connect(self.display_message)
        button_layout.addWidget(self.display_button)
        
        # Clear message button
        self.clear_button = QPushButton("Clear Message")
        self.clear_button.clicked.connect(self.clear_message)
        button_layout.addWidget(self.clear_button)
        
        # Toggle auto button
        self.auto_button = QPushButton("Start Auto Display")
        self.auto_button.clicked.connect(self.toggle_auto_display)
        button_layout.addWidget(self.auto_button)
        
        # Add buttons to main layout
        layout.addWidget(button_widget)
        
        # Style the window
        self.setStyleSheet("""
            QMainWindow {
                background-color: black;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background-color: #333333;
                color: white;
                border: 1px solid #444444;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QSpinBox {
                background-color: #333333;
                color: white;
                border: 1px solid #444444;
                padding: 4px;
            }
            QWidget {
                background-color: black;
            }
        """)
        
        # Initialize timers
        self.message_timer = QTimer()
        self.message_timer.timeout.connect(self.display_message)
        
        self.clear_timer = QTimer()
        self.clear_timer.timeout.connect(self.clear_message)
        
        # Message counter
        self.message_counter = 0
        
        # Auto display flag
        self.auto_display = False
        
        # Load settings
        self.load_settings()
        
        # Show the window
        self.show()
    
    def display_message(self):
        """Display a test message on the screen."""
        self.message_counter += 1
        message = f"TEST MESSAGE #{self.message_counter}"
        self.message_label.setText(message)
        print(f"Message displayed: {message}")
        
        # Set a timer to clear the message after the specified display time
        display_time = self.display_time_spin.value() * 1000  # Convert to milliseconds
        if self.clear_timer.isActive():
            self.clear_timer.stop()
        self.clear_timer.start(display_time)
        print(f"Message will be cleared after {display_time/1000} seconds")
    
    def clear_message(self):
        """Clear the currently displayed message."""
        self.message_label.setText("")
        print("Message cleared")
        
        # Stop the clear timer
        if self.clear_timer.isActive():
            self.clear_timer.stop()
    
    def toggle_auto_display(self):
        """Toggle automatic message display."""
        if not self.auto_display:
            # Start auto display
            interval = self.interval_spin.value() * 1000  # Convert to milliseconds
            self.message_timer.start(interval)
            self.auto_button.setText("Stop Auto Display")
            self.auto_display = True
            print(f"Auto display started with interval: {interval/1000} seconds")
        else:
            # Stop auto display
            self.message_timer.stop()
            self.auto_button.setText("Start Auto Display")
            self.auto_display = False
            print("Auto display stopped")
    
    def load_settings(self):
        """Load settings from file if available."""
        try:
            with open("punch_card_settings.json", "r") as f:
                settings = json.load(f)
                # Set message display time if available
                if "message_display_time" in settings:
                    self.display_time_spin.setValue(settings["message_display_time"])
                # Set message interval if available
                if "message_interval" in settings:
                    self.interval_spin.setValue(settings["message_interval"])
                print("Settings loaded from punch_card_settings.json")
        except:
            print("Using default settings")

def main():
    app = QApplication(sys.argv)
    display = SimpleMessageDisplay()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 