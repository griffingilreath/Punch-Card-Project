#!/usr/bin/env python3
"""
Sound Settings Dialog Module

A dialog for configuring sound settings, including volume and sound mappings.
"""

import os
import json
from typing import Dict

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QComboBox, QSlider, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from src.utils.fonts import get_font_css
from src.utils.colors import COLORS

class SoundSettingsDialog(QDialog):
    """Dialog for configuring sound settings."""
    
    # Define signals
    volume_changed = pyqtSignal(int)
    mute_changed = pyqtSignal(bool)
    sound_mappings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sound Settings")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Set dark theme matching main application
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background'].name()};
                color: {COLORS['text'].name()};
                border: none;
            }}
            QLabel {{
                color: {COLORS['text'].name()};
                {get_font_css(size=12)}
            }}
            QGroupBox {{
                color: {COLORS['text'].name()};
                border: 1px solid {COLORS['hole_outline'].name()};
                border-radius: 0px;
                margin-top: 1.5ex;
                {get_font_css(size=12)}
            }}
            QCheckBox {{
                color: {COLORS['text'].name()};
                {get_font_css(size=12)}
            }}
            QComboBox {{
                background-color: {COLORS['button_bg'].name()};
                color: {COLORS['text'].name()};
                border: 1px solid {COLORS['hole_outline'].name()};
                border-radius: 3px;
                padding: 5px;
                min-width: 200px;
                {get_font_css(size=12)}
            }}
            QComboBox:hover {{
                background-color: {COLORS['button_hover'].name()};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: none;
            }}
            QPushButton {{
                background-color: {COLORS['button_bg'].name()};
                color: {COLORS['text'].name()};
                border: 1px solid {COLORS['hole_outline'].name()};
                border-radius: 3px;
                padding: 5px 15px;
                {get_font_css(size=12)}
            }}
            QPushButton:hover {{
                background-color: {COLORS['button_hover'].name()};
            }}
            QSlider::groove:horizontal {{
                background: {COLORS['button_bg'].name()};
                height: 4px;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {COLORS['text'].name()};
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }}
            QSlider::sub-page:horizontal {{
                background: {COLORS['text'].name()};
                height: 4px;
                border-radius: 2px;
            }}
        """)
        
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Volume Control Section
        volume_group = QGroupBox("Volume Control")
        volume_layout = QVBoxLayout(volume_group)
        volume_layout.setSpacing(10)
        
        # Volume slider with label and value
        volume_slider_layout = QHBoxLayout()
        volume_label = QLabel("Volume:")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_value = QLabel("100%")
        volume_slider_layout.addWidget(volume_label)
        volume_slider_layout.addWidget(self.volume_slider)
        volume_slider_layout.addWidget(self.volume_value, 0, Qt.AlignmentFlag.AlignRight)
        volume_layout.addLayout(volume_slider_layout)
        
        # Mute checkbox
        self.mute_checkbox = QCheckBox("Mute all sounds")
        volume_layout.addWidget(self.mute_checkbox)
        
        layout.addWidget(volume_group)
        
        # Sound Selection Section
        sound_group = QGroupBox("Sound Selection")
        sound_layout = QVBoxLayout(sound_group)
        sound_layout.setSpacing(15)
        
        # Create sound selection controls
        self.sound_controls = {}
        sound_types = {
            "punch": "Punch/Typing Sound",
            "complete": "Message Complete Sound",
            "clear": "Clear Card Sound",
            "startup": "Startup Sound",
            "eject": "Card Ejection Sound",
            "insert": "Card Insertion Sound",
            "error": "Error Sound",
            "success": "Success Sound"
        }
        
        # Get available sounds from sound manager
        available_sounds = ["Tink", "Glass", "Pop", "Hero", "Bottle", "Frog", "Funk",
                          "Morse", "Ping", "Purr", "Sosumi", "Submarine"]
        
        for sound_type, label in sound_types.items():
            control_layout = QHBoxLayout()
            control_layout.setSpacing(10)
            
            # Label with fixed width for alignment
            sound_label = QLabel(f"{label}:")
            sound_label.setFixedWidth(150)
            control_layout.addWidget(sound_label)
            
            # Combo box for sound selection
            combo = QComboBox()
            combo.addItems(available_sounds)
            
            # Set default sound based on type
            default_sound = {
                "punch": "Tink",
                "complete": "Glass",
                "clear": "Pop",
                "startup": "Hero"
            }.get(sound_type, "Tink")
            
            combo.setCurrentText(default_sound)
            self.sound_controls[sound_type] = combo
            control_layout.addWidget(combo)
            
            # Test button
            test_button = QPushButton("Test")
            test_button.setFixedWidth(60)
            test_button.clicked.connect(lambda checked, s=sound_type: self.test_sound(s))
            control_layout.addWidget(test_button)
            
            sound_layout.addLayout(control_layout)
        
        layout.addWidget(sound_group)
        
        # Add spacer
        layout.addStretch()
        
        # Buttons at the bottom
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # System sound settings button (left-aligned)
        system_button = QPushButton("System Sound Settings...")
        system_button.clicked.connect(self.open_system_settings)
        button_layout.addWidget(system_button)
        
        button_layout.addStretch()
        
        # Save and Cancel buttons (right-aligned)
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        self.mute_checkbox.stateChanged.connect(self.on_mute_changed)
        
        # Initialize with current settings if parent has sound manager
        if parent and hasattr(parent, 'sound_manager'):
            volume = int(parent.sound_manager.volume * 100)
            self.volume_slider.setValue(volume)
            self.volume_value.setText(f"{volume}%")
            self.mute_checkbox.setChecked(parent.sound_manager.muted)
            
            # Set sound mappings
            for sound_type, combo in self.sound_controls.items():
                mapped_sound = parent.sound_manager.sound_mappings.get(sound_type)
                if mapped_sound:
                    index = combo.findText(mapped_sound)
                    if index >= 0:
                        combo.setCurrentIndex(index)
    
    def on_volume_changed(self, value):
        """Handle volume slider value changes."""
        self.volume_value.setText(f"{value}%")
        self.volume_changed.emit(value)
        
        # Play test sound if not muted
        if not self.mute_checkbox.isChecked():
            self.test_sound("punch")
    
    def on_mute_changed(self, state):
        """Handle mute checkbox state changes."""
        is_muted = state == Qt.CheckState.Checked.value
        self.mute_changed.emit(is_muted)
        
        # Update UI to reflect muted state
        self.volume_slider.setEnabled(not is_muted)
        for combo in self.sound_controls.values():
            combo.setEnabled(not is_muted)
    
    def test_sound(self, sound_type):
        """Test the selected sound."""
        if self.parent() and hasattr(self.parent(), 'sound_manager'):
            sound_name = self.sound_controls[sound_type].currentText()
            self.parent().sound_manager.play_sound(sound_name)
    
    def open_system_settings(self):
        """Open system sound settings."""
        if self.parent() and hasattr(self.parent(), 'sound_manager'):
            self.parent().sound_manager.open_sound_settings()
    
    def save_settings(self):
        """Save the current sound settings."""
        # Get current sound mappings
        mappings = {
            sound_type: combo.currentText()
            for sound_type, combo in self.sound_controls.items()
        }
        
        # Emit signals with current settings
        self.volume_changed.emit(self.volume_slider.value())
        self.mute_changed.emit(self.mute_checkbox.isChecked())
        self.sound_mappings_changed.emit(mappings)
        
        # Save settings to file
        try:
            settings_path = "punch_card_settings.json"
            existing_settings = {}
            
            # Load existing settings if available
            if os.path.exists(settings_path):
                try:
                    with open(settings_path, "r") as f:
                        existing_settings = json.load(f)
                except Exception:
                    pass
            
            # Update sound settings
            existing_settings["volume"] = self.volume_slider.value() / 100.0
            existing_settings["muted"] = self.mute_checkbox.isChecked()
            existing_settings["sound_mappings"] = mappings
            
            # Save settings
            with open(settings_path, "w") as f:
                json.dump(existing_settings, f, indent=4)
            
        except Exception as e:
            if hasattr(self.parent(), 'console'):
                self.parent().console.log(f"Error saving sound settings: {str(e)}", "ERROR")
        
        # Close dialog
        self.accept() 