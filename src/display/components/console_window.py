#!/usr/bin/env python3
"""
Console Window Module

A console window for displaying system information and debug data.
"""

import datetime
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QListWidgetItem, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from src.utils.fonts import get_font_css
from src.utils.colors import COLORS
from src.utils.ui_components import RetroButton

class ConsoleWindow(QDialog):
    """Console window for displaying system information and debug data."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Console")
        self.setMinimumSize(600, 400)
        
        # Initialize auto-save flag
        self.save_to_file = False
        
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
        
        # Add auto-save toggle button
        self.auto_save_button = RetroButton("Auto-Save: Off")
        self.auto_save_button.clicked.connect(self.toggle_auto_save)
        button_layout.addWidget(self.auto_save_button)
        
        # Add clear button
        clear_button = RetroButton("Clear")
        clear_button.clicked.connect(self.clear_log)
        button_layout.addWidget(clear_button)
        
        # Add close button
        close_button = RetroButton("Close")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Initialize log file
        self.log_file = None
    
    # Define color mapping for log levels
    LOG_COLORS = {
        "DEBUG": "gray",
        "INFO": "white",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "darkred"
    }

    def log(self, message: str, level: str = "INFO"):
        """Log a message with a specified level."""
        try:
            # Get timestamp
            timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
            
            # Format message with timestamp and level
            formatted_message = f"{timestamp} [{level}] {message}"
            
            # Get color for level (default to white if not found)
            color = self.LOG_COLORS.get(level.upper(), "white")
            
            # Create text item with color
            text_item = QListWidgetItem(formatted_message)
            text_item.setForeground(QColor(color))
            
            # Add to list
            self.console.append(formatted_message)
            
            # Scroll to bottom
            self.console.verticalScrollBar().setValue(
                self.console.verticalScrollBar().maximum()
            )
            
            # Save to file if enabled
            if self.save_to_file:
                self.save_log_to_file(formatted_message)
            
        except Exception as e:
            print(f"Error logging message: {str(e)}")

    def save_log_to_file(self, message: str):
        """Save a log message to file."""
        try:
            if not self.log_file:
                # Create logs directory if it doesn't exist
                os.makedirs("logs", exist_ok=True)
                
                # Create new log file with timestamp
                filename = f"logs/punch_card_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                self.log_file = open(filename, "a")
                self.log(f"Log saved to {filename}", "INFO")
            
            # Write message to file
            self.log_file.write(message + "\n")
            self.log_file.flush()
            
        except Exception as e:
            print(f"Error saving log to file: {str(e)}")

    def save_log(self):
        """Save the console log to a file."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"console_log_{timestamp}.txt"
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

    def toggle_auto_save(self):
        """Toggle auto-save functionality."""
        self.save_to_file = not self.save_to_file
        
        if self.save_to_file:
            self.auto_save_button.setText("Auto-Save: On")
            # Create a new log file if one doesn't exist
            if not self.log_file:
                self.log_file = open(f"console_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "w")
                self.log("Auto-save enabled", "INFO")
        else:
            self.auto_save_button.setText("Auto-Save: Off")
            # Close the log file if it exists
            if self.log_file:
                self.log_file.close()
                self.log_file = None
                self.log("Auto-save disabled", "INFO") 