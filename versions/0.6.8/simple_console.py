#!/usr/bin/env python3
"""
Simple Console for Animation Testing
A standalone console window for displaying animation and LED control messages
"""

import sys
import time
import datetime
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QTextEdit, 
                            QPushButton, QHBoxLayout, QLabel)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QTextCursor, QColor, QTextCharFormat

class SimpleConsole(QDialog):
    """Simple console window for displaying animation messages"""
    
    def __init__(self, parent=None):
        """Initialize the console window"""
        super().__init__(parent)
        self.parent = parent
        
        # Setup window properties
        self.setWindowTitle("Animation Console")
        self.resize(600, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: black;
                color: white;
            }
            QTextEdit {
                background-color: #111;
                color: #CCC;
                border: 1px solid #333;
                font-family: 'Courier New', monospace;
                font-size: 12pt;
            }
            QPushButton {
                background-color: #222;
                color: white;
                border: 1px solid #444;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #333;
            }
            QLabel {
                color: white;
            }
        """)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create title
        title = QLabel("Animation & LED Control Console")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 14pt; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Create text area for log messages
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # Create button bar
        button_layout = QHBoxLayout()
        
        # Clear button
        self.clear_button = QPushButton("Clear Console")
        self.clear_button.clicked.connect(self.clear_log)
        button_layout.addWidget(self.clear_button)
        
        # Save button
        self.save_button = QPushButton("Save Log")
        self.save_button.clicked.connect(self.save_log)
        button_layout.addWidget(self.save_button)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.hide)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Initialize with timestamp
        self.log("Console initialized", "SYSTEM")
        self.log("Ready for animation messages", "INFO")
    
    def log(self, message, level="INFO"):
        """Log a message to the console with the specified level"""
        # Define colors for different message levels
        level_colors = {
            "INFO": QColor(200, 200, 200),     # Light gray for info
            "ERROR": QColor(255, 100, 100),    # Red for errors
            "WARNING": QColor(255, 200, 100),  # Orange for warnings
            "SYSTEM": QColor(100, 200, 255),   # Blue for system messages
            "ANIMATION": QColor(100, 255, 180),# Green for animation messages
            "LED": QColor(255, 255, 100),      # Yellow for LED-specific messages
            "LED_green": QColor(100, 255, 100),# Bright green for LED ON messages
            "LED_gray": QColor(150, 150, 150), # Gray for LED OFF messages
            "LED_changes": QColor(255, 180, 80),# Orange for LED change summaries
            "HARDWARE": QColor(200, 150, 255)  # Purple for hardware messages
        }
        
        # Get color for this level
        color = level_colors.get(level, QColor(200, 200, 200))
        
        # Create timestamp
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Format message prefix
        formatted_prefix = f"[{timestamp}] [{level.split('_')[0]}] "
        
        # Special handling for LED messages to color-code ON/OFF statuses
        if level == "LED" and "LEDs:" in message:
            # Create text format with level color for the prefix
            text_format = QTextCharFormat()
            text_format.setForeground(color)
            
            # Move cursor to end and insert prefix with level format
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.log_text.setTextCursor(cursor)
            cursor.insertText(formatted_prefix, text_format)
            
            # Parse the LED message to extract ON and OFF counts
            try:
                # Extract parts of the message
                parts = message.split("LEDs: ")[1].split(", ")
                on_part = parts[0]  # "X on"
                off_part = parts[1]  # "Y off"
                
                # Insert ON count in green
                on_format = QTextCharFormat()
                on_format.setForeground(QColor(100, 255, 100))  # Bright green
                cursor.insertText(on_part + ", ", on_format)
                
                # Insert OFF count in gray
                off_format = QTextCharFormat()
                off_format.setForeground(QColor(150, 150, 150))  # Gray
                cursor.insertText(off_part, off_format)
                
                # Add newline
                cursor.insertText("\n")
            except Exception as e:
                # If parsing fails, fall back to normal formatting
                cursor.insertText(message + "\n", text_format)
                print(f"Error parsing LED message: {e}")
        
        # Special handling for LED_green (ON) messages
        elif level == "LED_green" and "LED" in message and "ON" in message:
            text_format = QTextCharFormat()
            text_format.setForeground(color)
            
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.log_text.setTextCursor(cursor)
            
            # Insert the message with bright green color
            cursor.insertText(formatted_prefix + message + "\n", text_format)
        
        # Special handling for LED_gray (OFF) messages
        elif level == "LED_gray" and "LED" in message and "OFF" in message:
            text_format = QTextCharFormat()
            text_format.setForeground(color)
            
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.log_text.setTextCursor(cursor)
            
            # Insert the message with gray color
            cursor.insertText(formatted_prefix + message + "\n", text_format)
        
        # Special handling for LED_changes messages
        elif level == "LED_changes" and "Changed LEDs:" in message:
            text_format = QTextCharFormat()
            text_format.setForeground(color)
            
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.log_text.setTextCursor(cursor)
            
            # Insert the changes summary with formatted counts
            cursor.insertText(formatted_prefix, text_format)
            
            # Try to parse and colorize the ON/OFF counts
            try:
                # Extract parts like "X turned ON, Y turned OFF"
                parts = message.split("Changed LEDs: ")[1].split(", ")
                on_part = parts[0]  # "X turned ON"
                off_part = parts[1]  # "Y turned OFF"
                
                # Insert ON count in green
                on_format = QTextCharFormat()
                on_format.setForeground(QColor(100, 255, 100))  # Bright green
                cursor.insertText(on_part + ", ", on_format)
                
                # Insert OFF count in gray
                off_format = QTextCharFormat()
                off_format.setForeground(QColor(150, 150, 150))  # Gray
                cursor.insertText(off_part, off_format)
                
                # Add newline
                cursor.insertText("\n")
            except Exception as e:
                # Fallback if parsing fails
                cursor.insertText(message + "\n", text_format)
                print(f"Error parsing LED changes message: {e}")
        
        else:
            # Normal message formatting for all other messages
            text_format = QTextCharFormat()
            text_format.setForeground(color)
            
            # Move cursor to end and insert text with format
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.log_text.setTextCursor(cursor)
            
            # Insert the message
            cursor.insertText(formatted_prefix + message + "\n", text_format)
        
        # Auto-scroll to bottom
        self.log_text.ensureCursorVisible()
        
        # Print to console for debugging (but skip individual LED changes if there are too many)
        if not (level.startswith("LED_") and message.startswith("LED (")):
            print(formatted_prefix + message)
    
    def clear_log(self):
        """Clear the log text area"""
        self.log_text.clear()
        self.log("Console cleared", "SYSTEM")
    
    def save_log(self):
        """Save the log to a file"""
        try:
            # Generate filename with timestamp
            filename = f"console_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            # Save to file
            with open(filename, 'w') as f:
                f.write(self.log_text.toPlainText())
            
            self.log(f"Log saved to {filename}", "SYSTEM")
        except Exception as e:
            self.log(f"Error saving log: {e}", "ERROR")


if __name__ == "__main__":
    # Stand-alone test
    app = QApplication(sys.argv)
    console = SimpleConsole()
    console.show()
    
    # Add some test messages
    def add_test_messages():
        console.log("Starting animation sequence", "ANIMATION")
        console.log("LED grid initialized", "LED")
        console.log("Row 3, column 5 activated", "LED")
        console.log("Testing hardware connection...", "HARDWARE")
        console.log("Animation completed successfully", "ANIMATION")
    
    # Add messages after a short delay
    QTimer.singleShot(1000, add_test_messages)
    
    sys.exit(app.exec()) 