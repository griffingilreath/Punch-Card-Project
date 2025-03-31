#!/usr/bin/env python3
"""
Animation Test with Existing GUI
Demonstrates how the AnimationManager integrates with the existing GUI
"""

import os
import sys
import time
import logging
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer

# Set up correct path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='[%(asctime)s] [%(levelname)s] %(message)s',
                    datefmt='%H:%M:%S')

# Import the required modules from src
from src.core.punch_card import PunchCard
from src.display.gui_display import PunchCardDisplay, RetroButton, COLORS
from src.animation.animation_manager import AnimationManager, AnimationType, AnimationState

class AnimationControlPanel(QDialog):
    """Panel for controlling animations in the main GUI"""
    
    def __init__(self, parent_display):
        """Initialize the animation control panel"""
        super().__init__(parent_display)
        self.parent_display = parent_display
        self.punch_card = parent_display.punch_card
        
        # Get or create the animation manager
        if hasattr(parent_display, 'animation_manager') and parent_display.animation_manager:
            self.animation_manager = parent_display.animation_manager
        else:
            self.animation_manager = AnimationManager(self.punch_card, parent_display)
            parent_display.animation_manager = self.animation_manager
            
            # Connect animation signals to parent handlers
            if hasattr(parent_display, 'on_animation_finished'):
                self.animation_manager.animation_finished.connect(parent_display.on_animation_finished)
        
        # Set up dialog properties
        self.setWindowTitle("Animation Controls")
        self.setMinimumWidth(400)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background'].name()};
                color: {COLORS['text'].name()};
            }}
            QLabel {{
                color: {COLORS['text'].name()};
            }}
        """)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        
        # Add title
        title = QLabel("Animation Control Panel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        self.layout.addWidget(title)
        
        # Add status display
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            background-color: #222;
            border: 1px solid #444;
            border-radius: 3px;
            padding: 5px;
        """)
        self.layout.addWidget(self.status_label)
        
        # Create animation control buttons
        button_layout = QHBoxLayout()
        
        # Startup animation button
        self.startup_button = RetroButton("Startup Animation")
        self.startup_button.clicked.connect(self.play_startup)
        button_layout.addWidget(self.startup_button)
        
        # Sleep animation button
        self.sleep_button = RetroButton("Sleep Animation")
        self.sleep_button.clicked.connect(self.play_sleep)
        button_layout.addWidget(self.sleep_button)
        
        # Wake animation button
        self.wake_button = RetroButton("Wake Animation")
        self.wake_button.clicked.connect(self.play_wake)
        button_layout.addWidget(self.wake_button)
        
        self.layout.addLayout(button_layout)
        
        # Create another row of buttons
        button_layout2 = QHBoxLayout()
        
        # Custom animation button
        self.custom_button = RetroButton("Custom Animation")
        self.custom_button.clicked.connect(self.play_custom)
        button_layout2.addWidget(self.custom_button)
        
        # Stop animation button
        self.stop_button = RetroButton("Stop Animation")
        self.stop_button.clicked.connect(self.stop_animation)
        button_layout2.addWidget(self.stop_button)
        
        # Clear button
        self.clear_button = RetroButton("Clear Card")
        self.clear_button.clicked.connect(self.clear_card)
        button_layout2.addWidget(self.clear_button)
        
        self.layout.addLayout(button_layout2)
        
        # Message display section
        message_label = QLabel("Message Generation")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 15px;")
        self.layout.addWidget(message_label)
        
        # Message button
        self.message_button = RetroButton("Generate Message")
        self.message_button.clicked.connect(self.generate_message)
        self.layout.addWidget(self.message_button)
        
        # Close button
        self.close_button = RetroButton("Close")
        self.close_button.clicked.connect(self.close)
        self.layout.addWidget(self.close_button)
        
        # Connect animation signals
        self.animation_manager.animation_started.connect(self.on_animation_started)
        self.animation_manager.animation_finished.connect(self.on_animation_finished)
    
    def play_startup(self):
        """Play startup animation"""
        self.status_label.setText("Playing startup animation...")
        self.animation_manager.play_animation(
            AnimationType.STARTUP,
            interrupt=True
        )
        
        # Log to console if available
        if hasattr(self.parent_display, 'console') and self.parent_display.console:
            self.parent_display.console.log("Playing startup animation", "ANIMATION")
    
    def play_sleep(self):
        """Play sleep animation"""
        self.status_label.setText("Playing sleep animation...")
        self.animation_manager.play_animation(
            AnimationType.SLEEP,
            interrupt=True
        )
        
        # Log to console if available
        if hasattr(self.parent_display, 'console') and self.parent_display.console:
            self.parent_display.console.log("Playing sleep animation", "ANIMATION")
    
    def play_wake(self):
        """Play wake animation"""
        self.status_label.setText("Playing wake animation...")
        self.animation_manager.play_animation(
            AnimationType.WAKE,
            interrupt=True
        )
        
        # Log to console if available
        if hasattr(self.parent_display, 'console') and self.parent_display.console:
            self.parent_display.console.log("Playing wake animation", "ANIMATION")
    
    def play_custom(self):
        """Play custom animation"""
        self.status_label.setText("Playing custom animation...")
        self.animation_manager.play_animation(
            AnimationType.CUSTOM,
            interrupt=True
        )
        
        # Log to console if available
        if hasattr(self.parent_display, 'console') and self.parent_display.console:
            self.parent_display.console.log("Playing custom animation", "ANIMATION")
    
    def stop_animation(self):
        """Stop the current animation"""
        if hasattr(self.animation_manager, '_interrupt_current_animation'):
            self.animation_manager._interrupt_current_animation()
            self.status_label.setText("Animation stopped")
            
            # Log to console if available
            if hasattr(self.parent_display, 'console') and self.parent_display.console:
                self.parent_display.console.log("Animation stopped", "ANIMATION")
    
    def clear_card(self):
        """Clear the punch card"""
        if hasattr(self.parent_display, 'punch_card'):
            self.parent_display.punch_card.clear_grid()
            self.status_label.setText("Card cleared")
            
            # Log to console if available
            if hasattr(self.parent_display, 'console') and self.parent_display.console:
                self.parent_display.console.log("Card cleared", "DISPLAY")
    
    def generate_message(self):
        """Generate a new message using the built-in generator"""
        if hasattr(self.parent_display, 'generate_next_message'):
            self.parent_display.generate_next_message()
            self.status_label.setText("Generating message...")
            
            # Log to console if available
            if hasattr(self.parent_display, 'console') and self.parent_display.console:
                self.parent_display.console.log("Generating new message", "MESSAGE")
    
    def on_animation_started(self, animation_type):
        """Handle animation started event"""
        self.status_label.setText(f"Animation started: {animation_type.name}")
    
    def on_animation_finished(self, animation_type):
        """Handle animation finished event"""
        self.status_label.setText(f"Animation completed: {animation_type.name}")


def run():
    """Run the application"""
    app = QApplication(sys.argv)
    
    # Create the punch card data model
    punch_card = PunchCard()
    
    # Create the main display
    gui = PunchCardDisplay(punch_card)
    
    # Create the animation manager (if not already created)
    if not hasattr(gui, 'animation_manager') or gui.animation_manager is None:
        animation_manager = AnimationManager(punch_card, gui)
        gui.animation_manager = animation_manager
        
        # Connect animation signals
        if hasattr(gui, 'on_animation_finished'):
            animation_manager.animation_finished.connect(gui.on_animation_finished)
    
    # Show the main display
    gui.show()
    
    # Create and show the animation control panel after a short delay
    def show_control_panel():
        control_panel = AnimationControlPanel(gui)
        control_panel.show()
        
        # Log to console if available
        if hasattr(gui, 'console') and gui.console:
            gui.console.log("Animation control panel opened", "ANIMATION")
            gui.console.show()  # Show the console
    
    # Schedule the control panel to appear after 1 second
    QTimer.singleShot(1000, show_control_panel)
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    run() 