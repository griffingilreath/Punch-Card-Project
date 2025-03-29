#!/usr/bin/env python3
"""
Animation System Test Script
Shows how to use the new animation system with different animations
"""

import sys
import os
import time

# Set up correct path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel
    from PyQt6.QtCore import Qt, QTimer, QSize
    from PyQt6.QtGui import QColor, QPalette
    from src.animation.animation_manager import AnimationManager, AnimationType, AnimationState
    from src.display.gui_display import PunchCardWidget
except ImportError as e:
    print(f"Import error: {e}")
    print("Installing required dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt6"])
    
    # Try import again
    from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel
    from PyQt6.QtCore import Qt, QTimer, QSize
    from PyQt6.QtGui import QColor, QPalette
    from src.animation.animation_manager import AnimationManager, AnimationType, AnimationState
    from src.display.gui_display import PunchCardWidget


class AnimationTestWindow(QMainWindow):
    """Test window for the animation system"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Animation System Test")
        self.setMinimumSize(900, 600)
        
        # Create central widget and layout
        central = QWidget()
        main_layout = QVBoxLayout(central)
        self.setCentralWidget(central)
        
        # Create punch card widget
        self.punch_card = PunchCardWidget(parent=central)
        main_layout.addWidget(self.punch_card)
        
        # Create animation manager
        self.animation_manager = AnimationManager(self.punch_card, self)
        self.animation_manager.animation_finished.connect(self.on_animation_finished)
        self.animation_manager.animation_started.connect(self.on_animation_started)
        
        # Create status label
        self.status_label = QLabel("Animation System Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16pt; color: white; background-color: #111; padding: 10px;")
        main_layout.addWidget(self.status_label)
        
        # Create buttons
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)
        
        button_style = """
            QPushButton {
                background-color: #333;
                color: white;
                border: 1px solid #555;
                padding: 10px;
                font-size: 14pt;
            }
            QPushButton:hover {
                background-color: #444;
            }
            QPushButton:pressed {
                background-color: #222;
            }
        """
        
        # Create buttons for each animation type
        self.startup_button = QPushButton("Startup Animation")
        self.startup_button.clicked.connect(lambda: self.play_animation(AnimationType.STARTUP))
        self.startup_button.setStyleSheet(button_style)
        button_layout.addWidget(self.startup_button)
        
        self.sleep_button = QPushButton("Sleep Animation")
        self.sleep_button.clicked.connect(lambda: self.play_animation(AnimationType.SLEEP))
        self.sleep_button.setStyleSheet(button_style)
        button_layout.addWidget(self.sleep_button)
        
        self.wake_button = QPushButton("Wake Animation")
        self.wake_button.clicked.connect(lambda: self.play_animation(AnimationType.WAKE))
        self.wake_button.setStyleSheet(button_style)
        button_layout.addWidget(self.wake_button)
        
        self.custom_button = QPushButton("Custom Animation")
        self.custom_button.clicked.connect(self.play_custom_animation)
        self.custom_button.setStyleSheet(button_style)
        button_layout.addWidget(self.custom_button)
        
        # Stop button
        self.stop_button = QPushButton("Stop Animation")
        self.stop_button.clicked.connect(self.stop_animation)
        self.stop_button.setStyleSheet(button_style)
        button_layout.addWidget(self.stop_button)
        
        # Initialize by filling the punch card with a pattern
        self.initialize_pattern()
        
    def initialize_pattern(self):
        """Initialize the punch card with a checkerboard pattern"""
        print("Initializing punch card with checkerboard pattern")
        for row in range(self.punch_card.num_rows):
            for col in range(self.punch_card.num_cols):
                if (row + col) % 2 == 0:
                    self.punch_card.grid[row][col] = True
        self.punch_card.update()
        
    def play_animation(self, animation_type):
        """Play an animation"""
        print(f"Playing animation: {animation_type}")
        self.animation_manager.play_animation(animation_type, interrupt=True)
        
    def play_custom_animation(self):
        """Play a custom animation from file"""
        print("Attempting to play custom animation")
        # This would load a custom animation by name
        # For now, we'll just use a placeholder
        available = self.animation_manager.get_available_animations()
        print(f"Available animations: {available}")
        
        # Check if we have a custom animation loaded
        if "Custom Diagonal" in available:
            self.status_label.setText("Playing Custom Animation")
            self.animation_manager.play_animation("Custom Diagonal", interrupt=True)
        else:
            self.status_label.setText("No custom animations found")
    
    def stop_animation(self):
        """Stop the current animation"""
        print("Stopping animation")
        self.animation_manager._interrupt_current_animation()
        self.status_label.setText("Animation Stopped")
    
    def on_animation_started(self, animation_type):
        """Handle animation start event"""
        print(f"Animation started: {animation_type}")
        self.status_label.setText(f"Playing: {animation_type}")
    
    def on_animation_finished(self, animation_type):
        """Handle animation finish event"""
        print(f"Animation finished: {animation_type}")
        self.status_label.setText(f"Completed: {animation_type}")
        
        # If it was a sleep animation, restore the pattern
        if animation_type == AnimationType.SLEEP:
            QTimer.singleShot(1000, self.initialize_pattern)


def main():
    """Main function to run the test window"""
    # Create application
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for better cross-platform appearance
    
    # Set dark palette
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    app.setPalette(dark_palette)
    
    # Create and show the main window
    window = AnimationTestWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 