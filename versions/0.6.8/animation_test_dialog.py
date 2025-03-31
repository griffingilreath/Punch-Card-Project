#!/usr/bin/env python3
"""
Animation Test Dialog
Provides a UI for testing animations on the punch card
"""

import os
import sys
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QComboBox, QSlider, QCheckBox, QGroupBox,
                            QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer

from src.animation.animation_manager import AnimationType, AnimationState

class AnimationTestDialog(QDialog):
    """Dialog for testing punch card animations"""
    
    def __init__(self, parent, animation_manager):
        """Initialize the animation test dialog"""
        super().__init__(parent)
        self.animation_manager = animation_manager
        self.parent_window = parent
        
        # Configure dialog
        self.setWindowTitle("Animation Test")
        self.setMinimumSize(400, 350)
        self.setup_ui()
        
        # Connect signals
        self.animation_manager.animation_started.connect(self.on_animation_started)
        self.animation_manager.animation_finished.connect(self.on_animation_finished)
        self.animation_manager.animation_step.connect(self.on_animation_step)
    
    def setup_ui(self):
        """Set up the user interface"""
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Use same styling as the main application
        self.setStyleSheet("""
            QDialog {
                background-color: black;
                color: white;
            }
            QLabel, QCheckBox, QComboBox, QGroupBox {
                color: white;
            }
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
            QGroupBox {
                border: 1px solid #555;
                border-radius: 3px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        # Add title
        title_label = QLabel("Punch Card Animation Test")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        layout.addWidget(title_label)
        
        # Add status display
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            background-color: #222;
            border: 1px solid #444;
            border-radius: 3px;
            padding: 8px;
            font-size: 14px;
        """)
        layout.addWidget(self.status_label)
        
        # Add animation controls section
        controls_group = QGroupBox("Animation Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Add animation type selection
        anim_type_layout = QHBoxLayout()
        anim_type_layout.addWidget(QLabel("Animation:"))
        
        self.animation_combo = QComboBox()
        self.animation_combo.addItem("Startup", AnimationType.STARTUP)
        self.animation_combo.addItem("Sleep", AnimationType.SLEEP)
        self.animation_combo.addItem("Wake", AnimationType.WAKE)
        self.animation_combo.addItem("Custom", AnimationType.CUSTOM)
        anim_type_layout.addWidget(self.animation_combo)
        
        controls_layout.addLayout(anim_type_layout)
        
        # Add speed control
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed:"))
        
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(50, 200)
        self.speed_slider.setValue(100)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(25)
        speed_layout.addWidget(self.speed_slider)
        
        self.speed_label = QLabel("1.0x")
        speed_layout.addWidget(self.speed_label)
        
        self.speed_slider.valueChanged.connect(
            lambda v: self.speed_label.setText(f"{v/100:.1f}x")
        )
        
        controls_layout.addLayout(speed_layout)
        
        # Add options
        options_layout = QHBoxLayout()
        
        self.interrupt_check = QCheckBox("Interrupt current animation")
        self.interrupt_check.setChecked(True)
        options_layout.addWidget(self.interrupt_check)
        
        controls_layout.addLayout(options_layout)
        
        layout.addWidget(controls_group)
        
        # Add animation control buttons
        buttons_layout = QHBoxLayout()
        
        # Play button
        self.play_button = QPushButton("Play Animation")
        self.play_button.clicked.connect(self.play_animation)
        buttons_layout.addWidget(self.play_button)
        
        # Stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_animation)
        buttons_layout.addWidget(self.stop_button)
        
        # Clear button
        self.clear_button = QPushButton("Clear Card")
        self.clear_button.clicked.connect(self.clear_card)
        buttons_layout.addWidget(self.clear_button)
        
        layout.addLayout(buttons_layout)
        
        # Add progress section
        progress_group = QGroupBox("Animation Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_label = QLabel("No animation playing")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.progress_label)
        
        layout.addWidget(progress_group)
        
        # Add spacer at the bottom
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Add close button at the bottom
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
    
    def play_animation(self):
        """Play the selected animation"""
        # Get animation type from combo box
        animation_type = self.animation_combo.currentData()
        speed = self.speed_slider.value() / 100
        interrupt = self.interrupt_check.isChecked()
        
        # Update status
        self.status_label.setText(f"Playing '{self.animation_combo.currentText()}' animation")
        
        # Play the animation
        self.animation_manager.play_animation(
            animation_type,
            speed=speed,
            interrupt=interrupt
        )
    
    def stop_animation(self):
        """Stop the current animation"""
        if hasattr(self.animation_manager, '_interrupt_current_animation'):
            self.animation_manager._interrupt_current_animation()
            self.status_label.setText("Animation stopped")
            self.progress_label.setText("No animation playing")
    
    def clear_card(self):
        """Clear the punch card"""
        if hasattr(self.parent_window, 'punch_card'):
            self.parent_window.punch_card.clear_grid()
            self.status_label.setText("Card cleared")
    
    def on_animation_started(self, animation_type):
        """Handle animation started event"""
        self.status_label.setText(f"Animation started: {animation_type.name}")
        self.progress_label.setText("Step 0/?")
    
    def on_animation_finished(self, animation_type):
        """Handle animation finished event"""
        self.status_label.setText(f"Animation completed: {animation_type.name}")
        self.progress_label.setText("No animation playing")
    
    def on_animation_step(self, current, total):
        """Handle animation step event"""
        self.progress_label.setText(f"Step {current}/{total}")


if __name__ == "__main__":
    # Only for direct testing
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # We need a parent window and animation manager
    from src.display.gui_display import PunchCardDisplay
    from src.core.punch_card import PunchCard
    from src.animation.animation_manager import AnimationManager
    
    # Create the objects
    punch_card = PunchCard()
    parent = PunchCardDisplay(punch_card)
    animation_manager = AnimationManager(punch_card)
    
    # Create and show the dialog
    dialog = AnimationTestDialog(parent, animation_manager)
    dialog.show()
    
    sys.exit(app.exec()) 