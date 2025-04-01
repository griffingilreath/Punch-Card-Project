#!/usr/bin/env python3
"""
Simple Animation Test for the Punch Card Project
Uses a standalone PunchCardWidget instead of the full application
"""

import os
import sys
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QPalette, QPainter, QPen

# Set up correct path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Create src/animation directory if it doesn't exist
os.makedirs(os.path.join(current_dir, 'src', 'animation'), exist_ok=True)
os.makedirs(os.path.join(current_dir, 'assets', 'animations'), exist_ok=True)

# Create a simple punch card widget for testing
class PunchCardWidget(QWidget):
    """Simple widget for displaying a punch card with LEDs"""
    
    # Signal emitted when card changes
    changed = pyqtSignal()
    
    def __init__(self, parent=None, num_rows=12, num_cols=80):
        """Initialize punch card widget"""
        super().__init__(parent)
        
        # Set dimensions
        self.num_rows = num_rows
        self.num_cols = num_cols
        
        # Initialize grid
        self.grid = [[False for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        # Calculate dimensions
        self.hole_width = 8
        self.hole_height = 12
        self.hole_spacing_h = 12
        self.hole_spacing_v = 18
        
        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(30, 30, 30))
        self.setPalette(palette)
        
        # Set minimum size
        self.setMinimumSize(400, 250)
    
    def paintEvent(self, event):
        """Paint the punch card grid"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate card dimensions
        card_width = self.num_cols * self.hole_spacing_h
        card_height = self.num_rows * self.hole_spacing_v
        
        # Calculate offsets to center the card
        x_offset = (self.width() - card_width) // 2
        y_offset = (self.height() - card_height) // 2
        
        # Draw card background
        painter.setPen(QPen(QColor(50, 50, 50), 1))
        painter.setBrush(QColor(20, 20, 20))
        painter.drawRect(x_offset, y_offset, card_width, card_height)
        
        # Draw grid lines
        painter.setPen(QPen(QColor(40, 40, 40), 1))
        
        # Draw vertical lines
        for col in range(self.num_cols + 1):
            x = x_offset + col * self.hole_spacing_h
            painter.drawLine(x, y_offset, x, y_offset + card_height)
        
        # Draw horizontal lines
        for row in range(self.num_rows + 1):
            y = y_offset + row * self.hole_spacing_v
            painter.drawLine(x_offset, y, x_offset + card_width, y)
        
        # Draw the holes (LEDs)
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                x = x_offset + col * self.hole_spacing_h + 2
                y = y_offset + row * self.hole_spacing_v + 3
                
                # Set the color based on LED state
                if self.grid[row][col]:
                    # ON - bright amber
                    painter.setBrush(QColor(255, 180, 0))
                    painter.setPen(QPen(QColor(255, 200, 50), 1))
                else:
                    # OFF - dark amber
                    painter.setBrush(QColor(50, 35, 0))
                    painter.setPen(QPen(QColor(100, 70, 0), 1))
                
                # Draw the hole
                painter.drawRect(x, y, self.hole_width, self.hole_height)
    
    def set_led(self, row, col, state):
        """Set the state of an LED (hole) in the grid"""
        if 0 <= row < self.num_rows and 0 <= col < self.num_cols:
            if self.grid[row][col] != state:
                self.grid[row][col] = state
                self.changed.emit()
                self.update()
                return True
        return False
    
    def get_led(self, row, col):
        """Get the state of an LED in the grid"""
        if 0 <= row < self.num_rows and 0 <= col < self.num_cols:
            return self.grid[row][col]
        return False
    
    def clear_grid(self):
        """Clear the entire grid (turn all LEDs off)"""
        changed = False
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.grid[row][col]:
                    self.grid[row][col] = False
                    changed = True
        
        if changed:
            self.changed.emit()
            self.update()
        
        return changed
    
    def get_all_leds(self):
        """Get a copy of the entire grid"""
        return [row[:] for row in self.grid]  # Deep copy

# Define the animation manager
class AnimationManager:
    """Simple animation manager"""
    
    def __init__(self, punch_card):
        """Initialize the animation manager"""
        self.punch_card = punch_card
        self.timer = QTimer()
        self.timer.timeout.connect(self._animation_step)
        self.current_step = 0
        self.steps = []
        self.callback = None
    
    def play_startup_animation(self, callback=None):
        """Play the startup animation"""
        # Generate steps for a simple diagonal animation
        self.steps = self._generate_diagonal_animation()
        self.current_step = 0
        self.callback = callback
        self.timer.start(100)  # 100ms per step (10 steps per second)
    
    def play_sleep_animation(self, callback=None):
        """Play the sleep animation"""
        # Generate steps for a simple fade out animation
        self.steps = self._generate_fade_animation(fade_out=True)
        self.current_step = 0
        self.callback = callback
        self.timer.start(100)  # 100ms per step (10 steps per second)
    
    def play_wake_animation(self, callback=None):
        """Play the wake animation"""
        # Generate steps for a simple fade in animation
        self.steps = self._generate_fade_animation(fade_out=False)
        self.current_step = 0
        self.callback = callback
        self.timer.start(100)  # 100ms per step (10 steps per second)
    
    def _animation_step(self):
        """Process a single animation step"""
        if self.current_step >= len(self.steps):
            self.timer.stop()
            if self.callback:
                self.callback()
            return
        
        # Apply current step
        step = self.steps[self.current_step]
        for row in range(min(len(step), self.punch_card.num_rows)):
            for col in range(min(len(step[row]), self.punch_card.num_cols)):
                self.punch_card.set_led(row, col, step[row][col])
        
        # Move to next step
        self.current_step += 1
    
    def _generate_diagonal_animation(self):
        """Generate steps for a diagonal animation"""
        steps = []
        rows = self.punch_card.num_rows
        cols = self.punch_card.num_cols
        
        # Start with all LEDs off
        current_state = [[False for _ in range(cols)] for _ in range(rows)]
        steps.append([row[:] for row in current_state])
        
        # First phase: diagonally filling
        for i in range(rows + cols - 1):
            for r in range(rows):
                c = i - r
                if 0 <= c < cols:
                    current_state[r][c] = True
            steps.append([row[:] for row in current_state])
        
        # Second phase: diagonally clearing
        for i in range(rows + cols - 1):
            for r in range(rows):
                c = i - r
                if 0 <= c < cols:
                    current_state[r][c] = False
            steps.append([row[:] for row in current_state])
        
        return steps
    
    def _generate_fade_animation(self, fade_out=True):
        """Generate steps for a fade animation"""
        steps = []
        rows = self.punch_card.num_rows
        cols = self.punch_card.num_cols
        
        if fade_out:
            # Start with all LEDs on
            current_state = [[True for _ in range(cols)] for _ in range(rows)]
            steps.append([row[:] for row in current_state])
            
            # Gradually turn off LEDs
            for step in range(10):
                # Calculate threshold based on step
                threshold = step / 10
                for r in range(rows):
                    for c in range(cols):
                        # Use position to determine when to turn off
                        position = (r + c) / (rows + cols)
                        if position < threshold:
                            current_state[r][c] = False
                steps.append([row[:] for row in current_state])
        else:
            # Start with all LEDs off
            current_state = [[False for _ in range(cols)] for _ in range(rows)]
            steps.append([row[:] for row in current_state])
            
            # Gradually turn on LEDs
            for step in range(10):
                # Calculate threshold based on step
                threshold = step / 10
                for r in range(rows):
                    for c in range(cols):
                        # Use position to determine when to turn on
                        position = (r + c) / (rows + cols)
                        if position < threshold:
                            current_state[r][c] = True
                steps.append([row[:] for row in current_state])
        
        return steps


class TestWindow(QMainWindow):
    """Main test window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Animation Test")
        self.resize(800, 600)
        
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Create layout
        layout = QVBoxLayout(central)
        
        # Create punch card widget
        self.punch_card = PunchCardWidget(num_rows=12, num_cols=40)
        layout.addWidget(self.punch_card)
        
        # Create animation manager
        self.animation_manager = AnimationManager(self.punch_card)
        
        # Create status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Create buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        
        # Startup animation button
        self.startup_button = QPushButton("Startup Animation")
        self.startup_button.clicked.connect(self.play_startup)
        button_layout.addWidget(self.startup_button)
        
        # Sleep animation button
        self.sleep_button = QPushButton("Sleep Animation")
        self.sleep_button.clicked.connect(self.play_sleep)
        button_layout.addWidget(self.sleep_button)
        
        # Wake animation button
        self.wake_button = QPushButton("Wake Animation")
        self.wake_button.clicked.connect(self.play_wake)
        button_layout.addWidget(self.wake_button)
        
        # Pattern button
        self.pattern_button = QPushButton("Checkerboard Pattern")
        self.pattern_button.clicked.connect(self.show_pattern)
        button_layout.addWidget(self.pattern_button)
        
        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear)
        button_layout.addWidget(self.clear_button)
    
    def play_startup(self):
        """Play startup animation"""
        self.status_label.setText("Playing startup animation...")
        self.animation_manager.play_startup_animation(
            callback=lambda: self.status_label.setText("Startup animation completed"))
    
    def play_sleep(self):
        """Play sleep animation"""
        self.status_label.setText("Playing sleep animation...")
        self.animation_manager.play_sleep_animation(
            callback=lambda: self.status_label.setText("Sleep animation completed"))
    
    def play_wake(self):
        """Play wake animation"""
        self.status_label.setText("Playing wake animation...")
        self.animation_manager.play_wake_animation(
            callback=lambda: self.status_label.setText("Wake animation completed"))
    
    def show_pattern(self):
        """Show checkerboard pattern"""
        self.status_label.setText("Showing checkerboard pattern")
        for row in range(self.punch_card.num_rows):
            for col in range(self.punch_card.num_cols):
                self.punch_card.set_led(row, col, (row + col) % 2 == 0)
    
    def clear(self):
        """Clear the punch card"""
        self.status_label.setText("Cleared")
        self.punch_card.clear_grid()


if __name__ == "__main__":
    # Create application
    app = QApplication(sys.argv)
    
    # Create main window
    window = TestWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec()) 