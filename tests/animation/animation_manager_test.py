#!/usr/bin/env python3
"""
Animation Manager Test
Demonstrates the animation manager with a simple punch card widget
"""

import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt, QTimer

# Set up correct path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Ensure animation directories exist
os.makedirs(os.path.join(current_dir, 'assets', 'animations'), exist_ok=True)

# Import the PunchCardWidget from simple_animation_test
from simple_animation_test import PunchCardWidget

# Import our AnimationManager
from src.animation.animation_manager import AnimationManager, AnimationType, AnimationState

class TestWindow(QMainWindow):
    """Test window for animation manager demo"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Animation Manager Test")
        self.resize(800, 600)
        
        # Create central widget and layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Add title
        title = QLabel("Animation Manager Demo")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Create punch card widget
        self.punch_card = PunchCardWidget(num_rows=12, num_cols=40)
        layout.addWidget(self.punch_card)
        
        # Create animation manager with punch card
        self.animation_manager = AnimationManager(self.punch_card, self)
        
        # Set animation FPS
        self.animation_manager.set_fps(20)
        
        # Connect animation signals
        self.animation_manager.animation_started.connect(self.on_animation_started)
        self.animation_manager.animation_finished.connect(self.on_animation_finished)
        
        # Create status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; padding: 5px; background-color: #222; color: white;")
        layout.addWidget(self.status_label)
        
        # Create buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        
        # Button styles
        button_style = """
            QPushButton {
                background-color: #333;
                color: white;
                border: 1px solid #555;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #444;
            }
            QPushButton:pressed {
                background-color: #222;
            }
        """
        
        # Startup animation button
        self.startup_button = QPushButton("Startup Animation")
        self.startup_button.setStyleSheet(button_style)
        self.startup_button.clicked.connect(self.play_startup)
        button_layout.addWidget(self.startup_button)
        
        # Sleep animation button
        self.sleep_button = QPushButton("Sleep Animation")
        self.sleep_button.setStyleSheet(button_style)
        self.sleep_button.clicked.connect(self.play_sleep)
        button_layout.addWidget(self.sleep_button)
        
        # Wake animation button
        self.wake_button = QPushButton("Wake Animation")
        self.wake_button.setStyleSheet(button_style)
        self.wake_button.clicked.connect(self.play_wake)
        button_layout.addWidget(self.wake_button)
        
        # Custom animation button
        self.custom_button = QPushButton("Custom Animation")
        self.custom_button.setStyleSheet(button_style)
        self.custom_button.clicked.connect(self.play_custom)
        button_layout.addWidget(self.custom_button)
        
        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.setStyleSheet(button_style)
        self.clear_button.clicked.connect(self.clear)
        button_layout.addWidget(self.clear_button)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1a1a1a;
                color: white;
            }
        """)
    
    def play_startup(self):
        """Play startup animation"""
        self.status_label.setText("Playing startup animation...")
        self.animation_manager.play_animation(
            AnimationType.STARTUP,
            speed=1.0,
            callback=lambda: self.status_label.setText("Startup animation completed")
        )
    
    def play_sleep(self):
        """Play sleep animation"""
        self.status_label.setText("Playing sleep animation...")
        self.animation_manager.play_animation(
            AnimationType.SLEEP,
            speed=1.0,
            callback=lambda: self.status_label.setText("Sleep animation completed")
        )
    
    def play_wake(self):
        """Play wake animation"""
        self.status_label.setText("Playing wake animation...")
        self.animation_manager.play_animation(
            AnimationType.WAKE,
            speed=1.0,
            callback=lambda: self.status_label.setText("Wake animation completed")
        )
    
    def play_custom(self):
        """Play custom animation"""
        self.status_label.setText("Playing custom animation...")
        self.animation_manager.play_animation(
            AnimationType.CUSTOM,
            speed=1.0,
            callback=lambda: self.status_label.setText("Custom animation completed")
        )
    
    def clear(self):
        """Clear the punch card"""
        self.status_label.setText("Cleared")
        self.punch_card.clear_grid()
    
    def on_animation_started(self, animation_type):
        """Handle animation started event"""
        self.status_label.setText(f"Playing: {animation_type.name} animation")
    
    def on_animation_finished(self, animation_type):
        """Handle animation finished event"""
        self.status_label.setText(f"Completed: {animation_type.name} animation")


if __name__ == "__main__":
    # Create application
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = TestWindow()
    window.show()
    
    # Automatically play startup animation after a short delay
    QTimer.singleShot(500, window.play_startup)
    
    # Run application
    sys.exit(app.exec()) 