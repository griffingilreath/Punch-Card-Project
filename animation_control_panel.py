#!/usr/bin/env python3
"""
Standalone Animation Control Panel
Works with the PunchCardDisplay but has less dependencies
"""

import os
import sys
import logging
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QWidget, QComboBox, QSlider)
from PyQt6.QtCore import Qt, QTimer

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='[%(asctime)s] [%(levelname)s] %(message)s',
                    datefmt='%H:%M:%S')

class SimpleButton(QPushButton):
    """Simple button with consistent styling"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: white;
                border: 1px solid #555;
                padding: 6px 12px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #444;
            }
            QPushButton:pressed {
                background-color: #222;
            }
        """)


class StandaloneAnimationPanel(QDialog):
    """Standalone animation control panel for Punch Card Display"""
    
    def __init__(self, parent_display=None):
        super().__init__(parent_display)
        self.parent_display = parent_display
        
        # Find the punch card
        self.punch_card = None
        if hasattr(parent_display, 'punch_card'):
            self.punch_card = parent_display.punch_card
        
        # Find or create the animation manager
        self.animation_manager = None
        if hasattr(parent_display, 'animation_manager') and parent_display.animation_manager:
            self.animation_manager = parent_display.animation_manager
            print("Using existing animation manager")
        elif self.punch_card:
            try:
                # Try to import animation manager
                from src.animation.animation_manager import AnimationManager, AnimationType, AnimationState
                # Create a new animation manager
                self.animation_manager = AnimationManager(self.punch_card, parent_display)
                if parent_display:
                    parent_display.animation_manager = self.animation_manager
                print("Created new animation manager")
            except Exception as e:
                print(f"Error creating animation manager: {e}")
        
        # Set up dialog properties
        self.setWindowTitle("Animation Controls")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background-color: black;
                color: white;
            }
            QLabel {
                color: white;
            }
            QComboBox {
                background-color: #333;
                color: white;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 3px;
            }
            QSlider {
                background-color: transparent;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #333;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: #666;
                border: 1px solid #777;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }
        """)
        
        # Create the layout
        self.setup_ui()
        
        # Connect animation signals if available
        if self.animation_manager:
            try:
                self.animation_manager.animation_started.connect(self.on_animation_started)
                self.animation_manager.animation_finished.connect(self.on_animation_finished)
                self.animation_manager.animation_step.connect(self.on_animation_step)
            except Exception as e:
                print(f"Error connecting animation signals: {e}")
                self.status_label.setText(f"Signal Error: {e}")
    
    def setup_ui(self):
        """Set up the user interface"""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # Add title
        title = QLabel("Punch Card Animation Controls")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title)
        
        # Add status display
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            background-color: #222;
            border: 1px solid #444;
            border-radius: 3px;
            padding: 8px;
        """)
        main_layout.addWidget(self.status_label)
        
        # Add animation selection
        if self.animation_manager:
            # Add animation type selector
            type_layout = QHBoxLayout()
            type_layout.addWidget(QLabel("Animation:"))
            
            self.animation_combo = QComboBox()
            # Get animation types
            try:
                from src.animation.animation_manager import AnimationType
                self.animation_combo.addItem("Startup", AnimationType.STARTUP)
                self.animation_combo.addItem("Sleep", AnimationType.SLEEP)
                self.animation_combo.addItem("Wake", AnimationType.WAKE)
                self.animation_combo.addItem("Custom", AnimationType.CUSTOM)
            except Exception as e:
                print(f"Error setting up animation types: {e}")
                self.animation_combo.addItem("Error")
                
            type_layout.addWidget(self.animation_combo)
            main_layout.addLayout(type_layout)
            
            # Add speed control
            speed_layout = QHBoxLayout()
            speed_layout.addWidget(QLabel("Speed:"))
            
            self.speed_slider = QSlider(Qt.Orientation.Horizontal)
            self.speed_slider.setRange(50, 200)
            self.speed_slider.setValue(100)
            speed_layout.addWidget(self.speed_slider)
            
            self.speed_label = QLabel("1.0x")
            speed_layout.addWidget(self.speed_label)
            
            self.speed_slider.valueChanged.connect(
                lambda v: self.speed_label.setText(f"{v/100:.1f}x")
            )
            
            main_layout.addLayout(speed_layout)
        
        # Add button row 1
        button_layout1 = QHBoxLayout()
        
        self.startup_button = SimpleButton("Startup Animation")
        self.startup_button.clicked.connect(self.play_startup)
        button_layout1.addWidget(self.startup_button)
        
        self.sleep_button = SimpleButton("Sleep Animation")
        self.sleep_button.clicked.connect(self.play_sleep)
        button_layout1.addWidget(self.sleep_button)
        
        self.wake_button = SimpleButton("Wake Animation")
        self.wake_button.clicked.connect(self.play_wake)
        button_layout1.addWidget(self.wake_button)
        
        main_layout.addLayout(button_layout1)
        
        # Add button row 2
        button_layout2 = QHBoxLayout()
        
        self.custom_button = SimpleButton("Custom Animation")
        self.custom_button.clicked.connect(self.play_custom)
        button_layout2.addWidget(self.custom_button)
        
        self.stop_button = SimpleButton("Stop Animation")
        self.stop_button.clicked.connect(self.stop_animation)
        button_layout2.addWidget(self.stop_button)
        
        self.clear_button = SimpleButton("Clear Card")
        self.clear_button.clicked.connect(self.clear_card)
        button_layout2.addWidget(self.clear_button)
        
        main_layout.addLayout(button_layout2)
        
        # Add progress tracking
        self.progress_label = QLabel("No animation playing")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.progress_label)
        
        # Add close button
        self.close_button = SimpleButton("Close")
        self.close_button.clicked.connect(self.close)
        main_layout.addWidget(self.close_button)
    
    def log_to_console(self, message, level="INFO"):
        """Log a message to the console if available"""
        # First, try our simple console
        if hasattr(self, 'simple_console') and self.simple_console:
            try:
                self.simple_console.log(message, level)
                return True
            except Exception as e:
                print(f"Error logging to simple console: {e}")
        
        # Fall back to parent's console if available
        if hasattr(self.parent_display, 'console') and self.parent_display.console:
            try:
                self.parent_display.console.log(message, level)
                return True
            except Exception as e:
                print(f"Error logging to parent console: {e}")
                
        # Fall back to checking for simple_console on parent
        if hasattr(self.parent_display, 'simple_console') and self.parent_display.simple_console:
            try:
                self.parent_display.simple_console.log(message, level)
                return True
            except Exception as e:
                print(f"Error logging to parent's simple console: {e}")
        
        # Last resort, print to standard output
        print(f"[{level}] {message}")
        return False
    
    def play_startup(self):
        """Play startup animation"""
        if not self.animation_manager:
            self.status_label.setText("Error: No animation manager available")
            return
            
        try:
            from src.animation.animation_manager import AnimationType
            
            # Get the current speed value
            speed = self.speed_slider.value()/100 if hasattr(self, 'speed_slider') else 1.0
            
            # Ensure animation step calculations are reset when starting
            if hasattr(self.animation_manager, 'animation_timer'):
                self.animation_manager.animation_timer.stop()
                
                # Make sure we use a clean interval based on FPS and speed
                # This helps prevent graphic anomalies when changing speed
                self.animation_manager.set_fps(self.animation_manager.fps)
            
            self.status_label.setText("Playing startup animation...")
            
            # Log the speed being used
            if hasattr(self, 'simple_console'):
                self.simple_console.log(f"Animation speed set to {speed:.2f}x", "ANIMATION")
            
            # Force redraw and clear before starting animation
            if hasattr(self.parent_display, 'punch_card'):
                self.parent_display.punch_card.update()
            
            # Start the animation with a small delay to ensure UI is ready
            self.animation_manager.play_animation(
                AnimationType.STARTUP,
                interrupt=True,
                speed=speed
            )
            
            self.log_to_console("Playing startup animation", "ANIMATION")
        except Exception as e:
            self.status_label.setText(f"Error playing animation: {e}")
            print(f"Error playing startup animation: {e}")
    
    def play_sleep(self):
        """Play sleep animation"""
        if not self.animation_manager:
            self.status_label.setText("Error: No animation manager available")
            return
            
        try:
            from src.animation.animation_manager import AnimationType
            
            # Get the current speed value
            speed = self.speed_slider.value()/100 if hasattr(self, 'speed_slider') else 1.0
            
            # Ensure animation step calculations are reset when starting
            if hasattr(self.animation_manager, 'animation_timer'):
                self.animation_manager.animation_timer.stop()
                
                # Make sure we use a clean interval based on FPS and speed
                self.animation_manager.set_fps(self.animation_manager.fps)
            
            self.status_label.setText("Playing sleep animation...")
            
            # Log the speed being used
            if hasattr(self, 'simple_console'):
                self.simple_console.log(f"Animation speed set to {speed:.2f}x", "ANIMATION")
            
            # Force redraw and clear before starting animation
            if hasattr(self.parent_display, 'punch_card'):
                self.parent_display.punch_card.update()
            
            # Start the animation
            self.animation_manager.play_animation(
                AnimationType.SLEEP,
                interrupt=True,
                speed=speed
            )
            
            self.log_to_console("Playing sleep animation", "ANIMATION")
        except Exception as e:
            self.status_label.setText(f"Error playing animation: {e}")
            print(f"Error playing sleep animation: {e}")
    
    def play_wake(self):
        """Play wake animation"""
        if not self.animation_manager:
            self.status_label.setText("Error: No animation manager available")
            return
            
        try:
            from src.animation.animation_manager import AnimationType
            
            # Get the current speed value
            speed = self.speed_slider.value()/100 if hasattr(self, 'speed_slider') else 1.0
            
            # Ensure animation step calculations are reset when starting
            if hasattr(self.animation_manager, 'animation_timer'):
                self.animation_manager.animation_timer.stop()
                
                # Make sure we use a clean interval based on FPS and speed
                self.animation_manager.set_fps(self.animation_manager.fps)
            
            self.status_label.setText("Playing wake animation...")
            
            # Log the speed being used
            if hasattr(self, 'simple_console'):
                self.simple_console.log(f"Animation speed set to {speed:.2f}x", "ANIMATION")
            
            # Force redraw and clear before starting animation
            if hasattr(self.parent_display, 'punch_card'):
                self.parent_display.punch_card.update()
            
            # Start the animation
            self.animation_manager.play_animation(
                AnimationType.WAKE,
                interrupt=True,
                speed=speed
            )
            
            self.log_to_console("Playing wake animation", "ANIMATION")
        except Exception as e:
            self.status_label.setText(f"Error playing animation: {e}")
            print(f"Error playing wake animation: {e}")
    
    def play_custom(self):
        """Play custom animation"""
        if not self.animation_manager:
            self.status_label.setText("Error: No animation manager available")
            return
            
        try:
            from src.animation.animation_manager import AnimationType
            
            # Get the current speed value
            speed = self.speed_slider.value()/100 if hasattr(self, 'speed_slider') else 1.0
            
            # Ensure animation step calculations are reset when starting
            if hasattr(self.animation_manager, 'animation_timer'):
                self.animation_manager.animation_timer.stop()
                
                # Make sure we use a clean interval based on FPS and speed
                self.animation_manager.set_fps(self.animation_manager.fps)
            
            self.status_label.setText("Playing custom animation...")
            
            # Log the speed being used
            if hasattr(self, 'simple_console'):
                self.simple_console.log(f"Animation speed set to {speed:.2f}x", "ANIMATION")
            
            # Force redraw and clear before starting animation
            if hasattr(self.parent_display, 'punch_card'):
                self.parent_display.punch_card.update()
            
            # Start the animation
            self.animation_manager.play_animation(
                AnimationType.CUSTOM,
                interrupt=True,
                speed=speed
            )
            
            self.log_to_console("Playing custom animation", "ANIMATION")
        except Exception as e:
            self.status_label.setText(f"Error playing animation: {e}")
            print(f"Error playing custom animation: {e}")
    
    def play_selected_animation(self):
        """Play the animation selected in the combo box"""
        if not hasattr(self, 'animation_combo') or not self.animation_manager:
            return
            
        try:
            animation_type = self.animation_combo.currentData()
            speed = self.speed_slider.value()/100 if hasattr(self, 'speed_slider') else 1.0
            
            self.status_label.setText(f"Playing '{self.animation_combo.currentText()}'...")
            self.animation_manager.play_animation(
                animation_type,
                interrupt=True,
                speed=speed
            )
            self.log_to_console(f"Playing {self.animation_combo.currentText()}", "ANIMATION")
        except Exception as e:
            self.status_label.setText(f"Error playing animation: {e}")
            print(f"Error playing selected animation: {e}")
    
    def stop_animation(self):
        """Stop the current animation"""
        if not self.animation_manager:
            return
            
        try:
            if hasattr(self.animation_manager, '_interrupt_current_animation'):
                self.animation_manager._interrupt_current_animation()
                self.status_label.setText("Animation stopped")
                self.progress_label.setText("No animation playing")
                self.log_to_console("Animation stopped", "ANIMATION")
        except Exception as e:
            self.status_label.setText(f"Error stopping animation: {e}")
            print(f"Error stopping animation: {e}")
    
    def clear_card(self):
        """Clear the punch card"""
        if self.punch_card:
            try:
                self.punch_card.clear_grid()
                self.status_label.setText("Card cleared")
                self.log_to_console("Card cleared", "DISPLAY")
            except Exception as e:
                self.status_label.setText(f"Error clearing card: {e}")
                print(f"Error clearing card: {e}")
    
    def on_animation_started(self, animation_type):
        """Handle animation started event"""
        try:
            self.status_label.setText(f"Animation started: {animation_type.name}")
            self.progress_label.setText("Step 0/?")
        except Exception as e:
            print(f"Error handling animation start: {e}")
    
    def on_animation_finished(self, animation_type):
        """Handle animation finished event"""
        try:
            self.status_label.setText(f"Animation completed: {animation_type.name}")
            self.progress_label.setText("No animation playing")
        except Exception as e:
            print(f"Error handling animation completion: {e}")
    
    def on_animation_step(self, current, total):
        """Handle animation step event"""
        try:
            self.progress_label.setText(f"Step {current}/{total}")
        except Exception as e:
            print(f"Error updating step progress: {e}")


if __name__ == "__main__":
    # Only for direct testing
    app = QApplication(sys.argv)
    
    # Create standalone panel
    panel = StandaloneAnimationPanel()
    panel.show()
    
    sys.exit(app.exec()) 