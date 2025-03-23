#!/usr/bin/env python3
"""
PyQt6-based Punch Card Display

A modern GUI for displaying punch card messages using PyQt6.
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QTextEdit, QSplitter)
from PyQt6.QtCore import Qt, QTimer, QSize, QTime
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPalette, QBrush

# Retro color scheme
COLORS = {
    'background': QColor(25, 25, 35),
    'card_bg': QColor(0, 0, 0),  # Solid black for card background
    'grid': QColor(40, 40, 40),  # Darker grid lines
    'hole': QColor(255, 255, 255),  # White for punched holes
    'hole_outline': QColor(255, 255, 255),  # White outline for possible holes
    'text': QColor(200, 200, 200),
    'border': QColor(100, 100, 120),
    'button_bg': QColor(45, 45, 55),
    'button_hover': QColor(60, 60, 70),
    'console_bg': QColor(20, 20, 25),
    'console_text': QColor(0, 255, 0),
    'card_edge': QColor(150, 150, 170)
}

# Grid dimensions
NUM_ROWS = 12
NUM_COLS = 80

# Base dimensions
CARD_WIDTH = 800
CARD_HEIGHT = int(CARD_WIDTH * (3.25 / 7.375))  # 3.25" / 7.375" aspect ratio

# Calculate spacing and hole dimensions
HOLE_WIDTH = CARD_WIDTH // (NUM_COLS + 2)  # Leave margin on each side
HOLE_HEIGHT = CARD_HEIGHT // (NUM_ROWS + 2)  # Leave margin on each side
HOLE_SPACING_H = CARD_WIDTH // NUM_COLS
HOLE_SPACING_V = CARD_HEIGHT // NUM_ROWS

class RetroButton(QPushButton):
    """Retro-styled button."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['button_bg'].name()};
                color: {COLORS['text'].name()};
                border: 2px solid {COLORS['border'].name()};
                padding: 5px 15px;
                font-family: 'Courier New';
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['button_hover'].name()};
            }}
        """)

class ConsoleWidget(QTextEdit):
    """Retro-styled console widget."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['console_bg'].name()};
                color: {COLORS['console_text'].name()};
                font-family: 'Courier New';
                font-size: 12px;
                border: 1px solid {COLORS['border'].name()};
            }}
        """)
    
    def log(self, message):
        """Add a message to the console with timestamp."""
        current_time = QTime.currentTime()
        self.append(f"[{current_time.toString('hh:mm:ss')}] {message}")

class PunchCardWidget(QWidget):
    """Widget for displaying the punch card grid."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.num_rows = NUM_ROWS
        self.num_cols = NUM_COLS
        self.grid = [[False for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        self.setMinimumSize(CARD_WIDTH + 100, CARD_HEIGHT + 100)
        
        # Set background color
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, COLORS['background'])
        self.setPalette(palette)
        self.setAutoFillBackground(True)
    
    def set_led(self, row: int, col: int, state: bool):
        """Set a single LED in the grid."""
        if 0 <= row < self.num_rows and 0 <= col < self.num_cols:
            self.grid[row][col] = state
            self.update()
    
    def clear_grid(self):
        """Clear the entire grid."""
        self.grid = [[False for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        self.update()
    
    def paintEvent(self, event):
        """Paint the punch card grid."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Center the card
        x_offset = (self.width() - CARD_WIDTH) / 2
        y_offset = (self.height() - CARD_HEIGHT) / 2
        
        # Draw card background (solid black)
        painter.setPen(QPen(COLORS['card_edge'], 1))
        painter.setBrush(COLORS['card_bg'])
        painter.drawRect(int(x_offset), int(y_offset), 
                        CARD_WIDTH, CARD_HEIGHT)
        
        # Draw grid lines
        painter.setPen(QPen(COLORS['grid'], 1))
        
        # Draw vertical lines
        for col in range(self.num_cols + 1):
            x = x_offset + col * HOLE_SPACING_H
            painter.drawLine(int(x), int(y_offset), 
                           int(x), int(y_offset + CARD_HEIGHT))
        
        # Draw horizontal lines
        for row in range(self.num_rows + 1):
            y = y_offset + row * HOLE_SPACING_V
            painter.drawLine(int(x_offset), int(y), 
                           int(x_offset + CARD_WIDTH), int(y))
        
        # Draw row labels
        painter.setFont(QFont("Courier New", 10))
        painter.setPen(COLORS['text'])
        row_labels = ["12", "11", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        for row, label in enumerate(row_labels):
            y = y_offset + row * HOLE_SPACING_V + (HOLE_SPACING_V / 2) + 5
            painter.drawText(int(x_offset - 30), int(y), label)
        
        # Draw all possible holes (white outline, black fill)
        painter.setPen(QPen(COLORS['hole_outline'], 1))
        painter.setBrush(COLORS['card_bg'])
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                x = x_offset + col * HOLE_SPACING_H
                y = y_offset + row * HOLE_SPACING_V
                painter.drawRect(int(x - HOLE_WIDTH/2), 
                               int(y - HOLE_HEIGHT/2), 
                               HOLE_WIDTH, HOLE_HEIGHT)
        
        # Draw punched holes (solid white)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(COLORS['hole'])
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.grid[row][col]:
                    x = x_offset + col * HOLE_SPACING_H
                    y = y_offset + row * HOLE_SPACING_V
                    painter.drawRect(int(x - HOLE_WIDTH/2), 
                                   int(y - HOLE_HEIGHT/2), 
                                   HOLE_WIDTH, HOLE_HEIGHT)

class PunchCardDisplay(QMainWindow):
    """Main window for the punch card display application."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Punch Card Display System")
        self.setMinimumSize(1200, 800)
        
        # Set window style
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['background'].name()};
            }}
        """)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Punch card display
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Create punch card widget
        self.punch_card = PunchCardWidget()
        left_layout.addWidget(self.punch_card)
        
        # Create status label
        self.status_label = QLabel("SYSTEM READY")
        self.status_label.setStyleSheet(f"color: {COLORS['text'].name()}; font-family: 'Courier New';")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.status_label)
        
        # Create control buttons
        button_layout = QHBoxLayout()
        self.start_button = RetroButton("START")
        self.start_button.clicked.connect(self.start_display)
        self.stop_button = RetroButton("STOP")
        self.stop_button.clicked.connect(self.stop_display)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        left_layout.addLayout(button_layout)
        
        # Right side: Console
        self.console = ConsoleWidget()
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(self.console)
        splitter.setStretchFactor(0, 2)  # Display takes 2/3
        splitter.setStretchFactor(1, 1)  # Console takes 1/3
        
        layout.addWidget(splitter)
        
        # Initialize display variables
        self.current_message = ""
        self.current_char_index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.display_next_char)
        self.running = False
        
        # Log initial status
        self.console.log("System initialized")
    
    def display_message(self, message: str, delay: int = 100):
        """Display a message on the punch card."""
        self.current_message = message.upper()
        self.current_char_index = 0
        self.punch_card.clear_grid()
        self.timer.setInterval(delay)
        self.console.log(f"Processing message: {message}")
        self.start_display()
    
    def start_display(self):
        """Start displaying the message."""
        self.running = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.timer.start()
        self.console.log("Display sequence started")
    
    def stop_display(self):
        """Stop displaying the message."""
        self.running = False
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.console.log("Display sequence stopped")
    
    def display_next_char(self):
        """Display the next character in the message."""
        if not self.running or self.current_char_index >= len(self.current_message):
            self.stop_display()
            return
        
        char = self.current_message[self.current_char_index]
        self._display_character(char, self.current_char_index)
        self.status_label.setText(f"PROCESSING: {self.current_message[:self.current_char_index + 1]}")
        self.console.log(f"Displaying character: {char}")
        self.current_char_index += 1
    
    def _display_character(self, char: str, col: int):
        """Display a character on the punch card grid."""
        if char.isalpha():
            if char in "ABCDEFGHI":
                self.punch_card.set_led(0, col, True)  # Row 12
                digit = ord(char) - ord('A') + 1
                self.punch_card.set_led(digit + 2, col, True)
            elif char in "JKLMNOPQR":
                self.punch_card.set_led(1, col, True)  # Row 11
                digit = ord(char) - ord('J') + 1
                self.punch_card.set_led(digit + 2, col, True)
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

def main():
    """Main function."""
    app = QApplication(sys.argv)
    display = PunchCardDisplay()
    display.show()
    
    # Test messages
    messages = [
        "TEST MESSAGE",
        "HELLO WORLD",
        "PUNCH CARD DISPLAY",
        "GOODBYE"
    ]
    
    def show_next_message():
        if messages:
            display.display_message(messages.pop(0))
        else:
            app.quit()
    
    # Connect the stop button to show the next message
    display.stop_button.clicked.connect(show_next_message)
    
    # Start with the first message
    show_next_message()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 