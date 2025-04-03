#!/usr/bin/env python3
"""
Display Settings Panel Module

A panel for configuring display settings in a modular design.
"""

import logging
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QFormLayout,
    QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QColor

from src.utils.colors import COLORS
from src.utils.fonts import get_font_css
from src.utils.ui_components import RetroButton
from src.utils.settings_manager import get_settings

# Configure logging
logger = logging.getLogger('DisplaySettingsPanel')

class DisplaySettingsPanel(QFrame):
    """Panel for configuring display settings in a modular design."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(450, 650)
        self.setStyleSheet("""
            QFrame {
                background-color: black;
                color: white;
                border: 1px solid #444444;
            }
            QLabel {
                color: white;
                font-family: 'Courier New';
                font-size: 12px;
                padding: 1px;
            }
            QGroupBox {
                color: white;
                border: 1px solid #444444;
                border-radius: 0px;
                margin-top: 1.5ex;
                font-family: 'Courier New';
                font-size: 12px;
                font-weight: bold;
                padding: 4px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: white;
                font-family: 'Courier New';
                font-size: 12px;
                font-weight: bold;
            }
            QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #101010;
                color: white;
                border: 1px solid #444444;
                padding: 2px;
            }
        """)
        
        # Initialize settings manager
        self.settings_manager = get_settings()
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Header
        header_label = QLabel("🖥️ Display Settings")
        header_label.setStyleSheet(f"{get_font_css(size=14, bold=True)}")
        layout.addWidget(header_label)
        
        # Settings content layout
        content_layout = QVBoxLayout()
        content_layout.setSpacing(8)
        layout.addLayout(content_layout)
        
        # Animation Settings Group
        self.animation_group = QGroupBox("Animation Settings")
        animation_layout = QFormLayout()
        self.animation_group.setLayout(animation_layout)
        
        # LED Update Delay
        self.led_delay = QSpinBox()
        self.led_delay.setRange(10, 1000)
        self.led_delay.setValue(100)
        self.led_delay.setSuffix(" ms")
        self.led_delay.setToolTip("Delay between LED updates in milliseconds")
        animation_layout.addRow("LED Update Delay:", self.led_delay)
        
        # Message interval
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setSuffix(" seconds")
        self.interval_spin.setToolTip("Time between new messages")
        animation_layout.addRow("Message interval:", self.interval_spin)
        
        # Message display time
        self.display_time_spin = QSpinBox()
        self.display_time_spin.setRange(1, 30)
        self.display_time_spin.setSuffix(" seconds")
        self.display_time_spin.setToolTip("How long each message is displayed")
        animation_layout.addRow("Message display time:", self.display_time_spin)
        
        # Delay factor
        self.delay_factor_spin = QDoubleSpinBox()
        self.delay_factor_spin.setRange(0.1, 5.0)
        self.delay_factor_spin.setSingleStep(0.1)
        self.delay_factor_spin.setToolTip("Multiplier for typing animation speed")
        animation_layout.addRow("Typing delay factor:", self.delay_factor_spin)
        
        # Random Delay
        self.random_delay = QCheckBox()
        self.random_delay.setChecked(True)
        self.random_delay.setToolTip("Add random variations to typing speed")
        animation_layout.addRow("Random Delay:", self.random_delay)
        
        # Add animation group to content layout
        content_layout.addWidget(self.animation_group)
        
        # Window Settings Group
        self.window_group = QGroupBox("Window Settings")
        window_layout = QFormLayout()
        self.window_group.setLayout(window_layout)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.setToolTip("Application color theme")
        window_layout.addRow("Theme:", self.theme_combo)
        
        # Font size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setSuffix(" pt")
        self.font_size_spin.setToolTip("Font size for text display")
        window_layout.addRow("Font Size:", self.font_size_spin)
        
        # Add window group to content layout
        content_layout.addWidget(self.window_group)
        
        # Behavior Settings Group
        self.behavior_group = QGroupBox("Behavior Settings")
        behavior_layout = QFormLayout()
        self.behavior_group.setLayout(behavior_layout)
        
        # Show Splash Screen
        self.show_splash = QCheckBox()
        self.show_splash.setChecked(True)
        self.show_splash.setToolTip("Show splash screen on startup")
        behavior_layout.addRow("Show Splash Screen:", self.show_splash)
        
        # Auto-Open Console
        self.auto_console = QCheckBox()
        self.auto_console.setChecked(True)
        self.auto_console.setToolTip("Automatically open console on startup")
        behavior_layout.addRow("Auto-Open Console:", self.auto_console)
        
        # Debug Mode
        self.debug_mode = QCheckBox()
        self.debug_mode.setChecked(False)
        self.debug_mode.setToolTip("Enable debug logging and features")
        behavior_layout.addRow("Debug Mode:", self.debug_mode)
        
        # Add behavior group to content layout
        content_layout.addWidget(self.behavior_group)
        
        # Auto-save settings
        self.auto_save = QCheckBox()
        self.auto_save.setChecked(True)
        self.auto_save.setToolTip("Automatically save settings on exit")
        behavior_layout.addRow("Auto-save settings:", self.auto_save)
        
        # Add save and close buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        self.save_btn = RetroButton("Save Settings")
        self.save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_btn)
        
        button_layout.addStretch()
        
        self.close_btn = RetroButton("Close")
        self.close_btn.clicked.connect(self.hide)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
    def showEvent(self, event):
        """Handle show event to load current settings."""
        super().showEvent(event)
        self.load_settings()
        
    def load_settings(self):
        """Load settings from the settings manager."""
        try:
            # Load animation settings
            self.led_delay.setValue(self.settings_manager.get_led_delay())
            self.interval_spin.setValue(self.settings_manager.get_message_interval())
            self.display_time_spin.setValue(self.settings_manager.get_message_display_time())
            self.delay_factor_spin.setValue(self.settings_manager.get_typing_delay_factor())
            self.random_delay.setChecked(self.settings_manager.get_random_delay())
            
            # Load window settings
            theme_index = self.theme_combo.findText(self.settings_manager.get_theme())
            if theme_index >= 0:
                self.theme_combo.setCurrentIndex(theme_index)
            self.font_size_spin.setValue(self.settings_manager.get_font_size())
            
            # Load behavior settings
            self.show_splash.setChecked(self.settings_manager.get_show_splash())
            self.auto_console.setChecked(self.settings_manager.get_auto_console())
            self.debug_mode.setChecked(self.settings_manager.get_debug_mode())
            self.auto_save.setChecked(self.settings_manager.get_auto_save())
            
        except Exception as e:
            logger.error(f"Error loading settings: {str(e)}")
            QMessageBox.warning(
                self,
                "Settings Load Error",
                f"Failed to load some settings: {str(e)}"
            )
    
    def save_settings(self):
        """Save current settings."""
        try:
            # Save animation settings
            self.settings_manager.set_led_delay(self.led_delay.value())
            self.settings_manager.set_message_interval(self.interval_spin.value())
            self.settings_manager.set_message_display_time(self.display_time_spin.value())
            self.settings_manager.set_typing_delay_factor(self.delay_factor_spin.value())
            self.settings_manager.set_random_delay(self.random_delay.isChecked())
            
            # Save window settings
            self.settings_manager.set_theme(self.theme_combo.currentText())
            self.settings_manager.set_font_size(self.font_size_spin.value())
            
            # Save behavior settings
            self.settings_manager.set_show_splash(self.show_splash.isChecked())
            self.settings_manager.set_auto_console(self.auto_console.isChecked())
            self.settings_manager.set_debug_mode(self.debug_mode.isChecked())
            self.settings_manager.set_auto_save(self.auto_save.isChecked())
            
            # Save to file
            self.settings_manager.save_settings()
            
            # Show success message
            QMessageBox.information(
                self,
                "Settings Saved",
                "Display settings have been saved successfully."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Settings Save Error",
                f"Failed to save settings: {str(e)}"
            )
    
    def paintEvent(self, event):
        """Custom paint event to draw an angular border."""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw border
        painter.setPen(QPen(QColor(COLORS['hole_outline']), 1))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

# For testing
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    panel = DisplaySettingsPanel()
    panel.show()
    sys.exit(app.exec()) 