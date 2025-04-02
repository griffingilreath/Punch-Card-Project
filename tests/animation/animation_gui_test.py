#!/usr/bin/env python3
"""
Animation GUI Integration Test
Shows how the AnimationManager integrates with the existing GUI system
"""

import os
import sys
import logging
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer

# Set up correct path imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='[%(asctime)s] [%(levelname)s] %(message)s',
                    datefmt='%H:%M:%S')

# Import the required modules from src
from src.core.punch_card import PunchCard
from src.display.gui_display import PunchCardDisplay, RetroButton, COLORS
from src.animation.animation_manager import AnimationManager, AnimationType

class AnimationControlPanel(QDialog):
    """Panel for controlling animations that integrates with the main GUI"""
    
    def __init__(self, parent_display):
        """Initialize the animation control panel"""
        super().__init__(parent_display)
        self.parent_display = parent_display
        
        # Set up dialog properties
        self.setWindowTitle("Animation Controls")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
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
        title = QLabel("Punch Card Animation Controls")
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
        
        # Add close button
        self.close_button = RetroButton("Close")
        self.close_button.clicked.connect(self.close)
        self.layout.addWidget(self.close_button)
        
        # Connect animation signals if animation manager exists
        if hasattr(self.parent_display, 'animation_manager'):
            self.animation_manager = self.parent_display.animation_manager
            self.animation_manager.animation_started.connect(self.on_animation_started)
            self.animation_manager.animation_finished.connect(self.on_animation_finished)
            self.log_to_console("Using existing animation manager")
        else:
            # Create new animation manager
            self.animation_manager = AnimationManager(
                self.parent_display.punch_card, 
                self.parent_display
            )
            # Set it on the parent to share with other components
            self.parent_display.animation_manager = self.animation_manager
            self.animation_manager.animation_started.connect(self.on_animation_started)
            self.animation_manager.animation_finished.connect(self.on_animation_finished)
            
            # Connect to parent's animation handler if it exists
            if hasattr(self.parent_display, 'on_animation_finished'):
                self.animation_manager.animation_finished.connect(
                    self.parent_display.on_animation_finished
                )
            self.log_to_console("Created new animation manager")
    
    def log_to_console(self, message, level="INFO"):
        """Log a message to the console if available"""
        if hasattr(self.parent_display, 'console') and self.parent_display.console:
            self.parent_display.console.log(message, level)
            return True
        return False
    
    def play_startup(self):
        """Play startup animation"""
        self.status_label.setText("Playing startup animation...")
        self.animation_manager.play_animation(
            AnimationType.STARTUP,
            interrupt=True
        )
        self.log_to_console("Playing startup animation", "ANIMATION")
    
    def play_sleep(self):
        """Play sleep animation"""
        self.status_label.setText("Playing sleep animation...")
        self.animation_manager.play_animation(
            AnimationType.SLEEP,
            interrupt=True
        )
        self.log_to_console("Playing sleep animation", "ANIMATION")
    
    def play_wake(self):
        """Play wake animation"""
        self.status_label.setText("Playing wake animation...")
        self.animation_manager.play_animation(
            AnimationType.WAKE,
            interrupt=True
        )
        self.log_to_console("Playing wake animation", "ANIMATION")
    
    def play_custom(self):
        """Play custom animation"""
        self.status_label.setText("Playing custom animation...")
        self.animation_manager.play_animation(
            AnimationType.CUSTOM,
            interrupt=True
        )
        self.log_to_console("Playing custom animation", "ANIMATION")
    
    def stop_animation(self):
        """Stop the current animation"""
        if hasattr(self.animation_manager, '_interrupt_current_animation'):
            self.animation_manager._interrupt_current_animation()
            self.status_label.setText("Animation stopped")
            self.log_to_console("Animation stopped", "ANIMATION")
    
    def clear_card(self):
        """Clear the punch card"""
        if hasattr(self.parent_display, 'punch_card'):
            self.parent_display.punch_card.clear_grid()
            self.status_label.setText("Card cleared")
            self.log_to_console("Card cleared", "DISPLAY")
    
    def on_animation_started(self, animation_type):
        """Handle animation started event"""
        self.status_label.setText(f"Animation started: {animation_type.name}")
        self.log_to_console(f"Animation started: {animation_type.name}", "ANIMATION")
    
    def on_animation_finished(self, animation_type):
        """Handle animation finished event"""
        self.status_label.setText(f"Animation completed: {animation_type.name}")
        self.log_to_console(f"Animation completed: {animation_type.name}", "ANIMATION")


def run():
    """Run the application with animation integration"""
    app = QApplication(sys.argv)
    
    # Create the punch card data model
    punch_card = PunchCard()
    
    # Create the main display
    print("Creating GUI display...")
    gui = PunchCardDisplay(punch_card)
    
    # Skip hardware detection to avoid delays
    # This is important for testing - ensures virtual mode is used
    if hasattr(gui, 'hardware_detector'):
        gui.hardware_detector.enable_virtual_mode()
        print("Hardware detector set to virtual mode for testing")
    
    # Stop splash animation to get to the main UI faster
    if hasattr(gui, 'showing_splash') and gui.showing_splash:
        gui.complete_splash_screen()
        print("Splash screen skipped for testing")
    
    # Make sure console is initialized
    if hasattr(gui, 'console'):
        # Make sure console is created if not already
        if gui.console is None:
            try:
                from src.display.gui_display import ConsoleWindow
                gui.console = ConsoleWindow(gui)
                print("Created console window")
            except Exception as e:
                print(f"Error creating console: {e}")
    
    # Create animation control panel but don't show it
    # It will be accessible from the menu instead
    control_panel = AnimationControlPanel(gui)
    gui.animation_control_panel = control_panel
    
    # Add animation controls to the punch card menu
    try:
        if hasattr(gui, 'menu_bar') and hasattr(gui.menu_bar, 'card_menu_popup'):
            gui.menu_bar.card_menu_popup.addSeparator()
            animation_action = gui.menu_bar.card_menu_popup.addAction("Animation Controls")
            animation_action.triggered.connect(lambda: gui.animation_control_panel.show())
            print("Added animation controls to menu")
    except Exception as e:
        print(f"Could not add to menu: {e}")
        # Add a direct button to open animation controls as fallback
        if hasattr(gui, 'button_layout'):
            animation_button = RetroButton("Animation Controls")
            animation_button.clicked.connect(lambda: gui.animation_control_panel.show())
            gui.button_layout.addWidget(animation_button)
            print("Added animation button to UI")
    
    # Show the main display
    gui.show()
    
    # Make sure console is visible if needed
    try:
        if hasattr(gui, 'console') and gui.console:
            gui.console.log("Animation integration ready - use Punch Card menu to access controls", "ANIMATION")
            # Make console visible
            gui.console.show()
            print("Console window shown")
    except Exception as e:
        print(f"Error showing console: {e}")
    
    # Run the application
    print("Starting application...")
    sys.exit(app.exec())


if __name__ == "__main__":
    print("Starting animation GUI test...")
    run() 