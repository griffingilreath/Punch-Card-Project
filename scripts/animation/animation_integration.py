#!/usr/bin/env python3
"""
Animation Integration Module for Punch Card Project
Connects the animation system to the main application
"""

import os
import sys
import importlib.util
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QDialog, QMenu
from PyQt6.QtCore import Qt, QTimer

# Make sure the current directory is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import and run the patch module first
try:
    from src.animation.patch_module import patch
    patch()
except Exception as e:
    print(f"Warning: Patch module error: {e}")

# Import animation system
from src.animation.animation_manager import AnimationManager, AnimationType, AnimationState
from src.core.punch_card import PunchCard
from src.display.gui_display import PunchCardDisplay


class AnimationTesterDialog(QDialog):
    """Dialog for testing animations in the main application"""
    
    def __init__(self, parent, animation_manager):
        super().__init__(parent)
        self.setWindowTitle("Animation Tester")
        self.setMinimumSize(500, 300)
        self.animation_manager = animation_manager
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create status label
        self.status_label = QLabel("Animation System Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16pt; color: white; background-color: #111; padding: 10px;")
        layout.addWidget(self.status_label)
        
        # Create buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        
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
        
        # Connect signals
        self.animation_manager.animation_finished.connect(self.on_animation_finished)
        self.animation_manager.animation_started.connect(self.on_animation_started)
        
    def play_animation(self, animation_type):
        """Play an animation"""
        print(f"Playing animation: {animation_type}")
        self.animation_manager.play_animation(animation_type, interrupt=True)
        
    def play_custom_animation(self):
        """Play a custom animation from file"""
        print("Attempting to play custom animation")
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
    
    def initialize_pattern(self):
        """Initialize the punch card with a checkerboard pattern"""
        print("Initializing punch card with checkerboard pattern")
        punch_card = self.animation_manager.punch_card
        for row in range(punch_card.num_rows):
            for col in range(punch_card.num_cols):
                if (row + col) % 2 == 0:
                    punch_card.set_led(row, col, True)
                else:
                    punch_card.set_led(row, col, False)
        punch_card.changed.emit()


def integrate_animations(app_instance):
    """
    Integrate animations with the main application
    
    Args:
        app_instance: The main PunchCardDisplay instance
    
    Returns:
        AnimationManager: The animation manager instance
    """
    # Get the punch card from the app instance
    punch_card = app_instance.punch_card
    
    # Create animation manager
    animation_manager = AnimationManager(punch_card, app_instance)
    
    # Store animation manager in app instance
    app_instance.animation_manager = animation_manager
    
    # Create the animation finished handler method
    def on_animation_finished(self, animation_type):
        """Handle animation completion events"""
        if hasattr(self, 'console'):
            self.console.log(f"Animation finished: {animation_type}", "INFO")
            
        # Handle specific animation completion events
        if animation_type == AnimationType.STARTUP:
            # Play final sound
            if hasattr(self, 'card_eject_sound'):
                self.card_eject_sound.play()
        elif animation_type == AnimationType.SLEEP:
            # Update status
            if hasattr(self, 'update_status'):
                self.update_status("SLEEPING")
        elif animation_type == AnimationType.WAKE:
            # Update status
            if hasattr(self, 'update_status'):
                self.update_status("READY")
    
    # Add the on_animation_finished method to the app instance
    app_instance.on_animation_finished = lambda animation_type: on_animation_finished(app_instance, animation_type)
    
    # Connect signals
    animation_manager.animation_finished.connect(app_instance.on_animation_finished)
    
    # Override the splash screen behavior to use our animations
    def new_start_splash_screen(self):
        """Replacement for start_splash_screen that uses our animation system"""
        # Set initial state
        self.showing_splash = True
        if hasattr(self, 'message_label'):
            self.message_label.setText("")
        if hasattr(self, 'status_label'):
            self.status_label.setText("INITIALIZING SYSTEM...")
        
        # Clear the punch card grid
        self.punch_card.clear_grid()
        
        # Disable buttons during splash
        button_names = ['start_button', 'clear_button', 'exit_button']
        for button_name in button_names:
            if hasattr(self, button_name):
                button = getattr(self, button_name)
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
        if hasattr(self, 'animation_started'):
            self.animation_started = False
        
        # Load the punch card sounds if not already loaded
        if hasattr(self, 'load_punch_card_sounds'):
            self.load_punch_card_sounds()
        
        # Console log for debugging
        if hasattr(self, 'console'):
            self.console.log("Splash screen started using animation manager", "INFO")
            
        # Start the startup animation
        self.animation_manager.play_animation(AnimationType.STARTUP, 
                                             callback=self.complete_splash_screen if hasattr(self, 'complete_splash_screen') else None)
        
        # Schedule post-wake setup after animation completes (if waking from sleep)
        if hasattr(self, 'sleeping') and not self.sleeping and hasattr(self, 'post_wake_setup'):
            QTimer.singleShot(5000, self.post_wake_setup)
    
    # Override start_splash_screen method if it exists
    if hasattr(app_instance, 'start_splash_screen'):
        original_start_splash = app_instance.start_splash_screen
        app_instance.start_splash_screen = lambda: new_start_splash_screen(app_instance)
    
    # Create animation tester dialog
    tester_dialog = AnimationTesterDialog(app_instance, animation_manager)
    app_instance.animation_tester = tester_dialog
    
    # Add method to show animation tester
    app_instance.show_animation_tester = lambda: tester_dialog.show()
    
    # Try to add menu option to show animation tester in menu
    try:
        # Try to find or create a "Tools" menu
        if hasattr(app_instance, 'menuBar'):
            menu_bar = app_instance.menuBar()
            tools_menu = None
            
            # Find existing Tools menu if it exists
            for action in menu_bar.actions():
                if action.text() == "Tools":
                    tools_menu = action.menu()
                    break
            
            # Create Tools menu if it doesn't exist
            if tools_menu is None:
                tools_menu = QMenu("Tools", menu_bar)
                menu_bar.addMenu(tools_menu)
            
            # Add animation tester action
            tools_menu.addAction("Animation Tester", app_instance.show_animation_tester)
            print("Added Animation Tester to Tools menu")
    except Exception as e:
        print(f"Could not add menu option: {e}")
    
    return animation_manager


if __name__ == "__main__":
    # This script is designed to be imported rather than run directly
    print("This script is meant to be imported into the main application.")
    print("To use, run the main application with --enable-animations flag.")
    sys.exit(0) 