#!/usr/bin/env python3

"""
Settings Dialog for the Punch Card Project.

This module provides a dialog for configuring all settings in the application,
with keychain integration for securely storing API keys.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                           QWidget, QLabel, QFormLayout, QSpinBox, QDoubleSpinBox,
                           QCheckBox, QLineEdit, QComboBox, QSlider, QGroupBox,
                           QDialogButtonBox, QMessageBox, QFrame, QPushButton, 
                           QTextEdit, QProgressBar)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

from src.api.api_manager import APIManager
from src.utils.settings_manager import get_settings, KEYRING_AVAILABLE

# Configure logging
logger = logging.getLogger('SettingsDialog')

# Colors - copied from main application to ensure consistent styling
COLORS = {
    'background': QColor(23, 23, 23),        # Dark background
    'text': QColor(220, 220, 220),           # Light text
    'hole': QColor(0, 0, 0),                 # Black holes
    'hole_outline': QColor(60, 60, 60),      # Grey hole outlines
    'card': QColor(245, 245, 220),           # Beige card
    'button_bg': QColor(40, 40, 40),         # Button background
    'button_hover': QColor(60, 60, 60),      # Button hover
    'button_press': QColor(80, 80, 80),      # Button pressed
    'button_text': QColor(220, 220, 220),    # Button text
    'console_bg': QColor(15, 15, 15),        # Console background
    'console_text': QColor(180, 180, 180),   # Console text
    'console_highlight': QColor(50, 120, 50),# Console highlight
}

class RetroButton(QPushButton):
    """Button with a retro style for the punch card UI."""
    
    def __init__(self, text=None, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['button_bg'].name()};
                color: {COLORS['button_text'].name()};
                border: 1px solid {COLORS['hole_outline'].name()};
                border-radius: 4px;
                padding: 5px 10px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['button_hover'].name()};
                border: 1px solid {COLORS['text'].name()};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['button_press'].name()};
            }}
        """)


class SettingsDialog(QDialog):
    """Dialog for configuring punch card settings."""

    def __init__(self, parent=None):
        """Initialize the settings dialog."""
        super().__init__(parent)
        self.setWindowTitle("Punch Card Settings")
        self.resize(550, 650)  # Make dialog larger to accommodate tabs
        
        # Initialize API manager
        self.api_manager = APIManager()
        
        # Get the settings manager
        self.settings_manager = get_settings()
        
        # Set dark theme
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background'].name()};
                color: {COLORS['text'].name()};
            }}
            QLabel, QSpinBox, QCheckBox, QLineEdit, QComboBox, QTextEdit, QSlider {{
                color: {COLORS['text'].name()};
            }}
            QTabWidget::pane {{
                border: 1px solid {COLORS['hole_outline'].name()};
                background-color: {COLORS['background'].name()};
            }}
            QTabBar::tab {{
                background-color: {COLORS['button_bg'].name()};
                color: {COLORS['text'].name()};
                padding: 6px 12px;
                border: 1px solid {COLORS['hole_outline'].name()};
                border-bottom: none;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['button_hover'].name()};
            }}
        """)
        
        # Create the main layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.display_tab = QWidget()
        self.card_tab = QWidget()
        self.openai_tab = QWidget()
        self.stats_tab = QWidget()  # Stats tab
        
        # Set up tabs
        self._setup_display_tab()
        self._setup_card_tab()
        self._setup_openai_tab()
        self._setup_stats_tab()
        
        # Add tabs to widget
        self.tab_widget.addTab(self.display_tab, "Display")
        self.tab_widget.addTab(self.card_tab, "Card Dimensions")
        self.tab_widget.addTab(self.openai_tab, "🤖 OpenAI API")
        self.tab_widget.addTab(self.stats_tab, "📊 Statistics")
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.layout.addWidget(button_box)
        
        # Load settings from settings manager into UI components
        self._load_settings_from_manager()
        
        # Initialize message stats if not exists
        self._initialize_message_stats()

    def _initialize_message_stats(self):
        """Initialize global message stats variable if it doesn't exist."""
        # Define globals at the start of the method
        global message_stats, service_status
        
        # Initialize message stats if not exists
        if 'message_stats' not in globals():
            message_stats = {
                "total": 0,
                "local": 0,
                "openai": 0,
                "database": 0,
                "system": 0,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_message": "",
                "last_source": ""
            }
        
        # Initialize service status tracking
        if 'service_status' not in globals():
            service_status = {
                "openai": {
                    "status": "unknown",
                    "message": "Not checked yet",
                    "last_checked": "Never"
                },
                "flyio": {
                    "status": "unknown",
                    "message": "Not checked yet",
                    "last_checked": "Never"
                }
            }

    def _setup_display_tab(self):
        """Set up the display settings tab."""
        layout = QFormLayout()
        self.display_tab.setLayout(layout)
        
        # LED Update Delay
        self.led_delay = QSpinBox()
        self.led_delay.setRange(10, 1000)
        self.led_delay.setValue(100)
        self.led_delay.setSuffix(" ms")
        layout.addRow("LED Update Delay:", self.led_delay)
        
        # Message interval
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setSuffix(" seconds")
        layout.addRow("Message interval:", self.interval_spin)
        
        # Message display time
        self.display_time_spin = QSpinBox()
        self.display_time_spin.setRange(1, 30)
        self.display_time_spin.setSuffix(" seconds")
        layout.addRow("Message display time:", self.display_time_spin)
        
        # Delay factor
        self.delay_factor_spin = QDoubleSpinBox()
        self.delay_factor_spin.setRange(0.1, 5.0)
        self.delay_factor_spin.setSingleStep(0.1)
        layout.addRow("Typing delay factor:", self.delay_factor_spin)
        
        # Random Delay
        self.random_delay = QCheckBox()
        self.random_delay.setChecked(True)
        layout.addRow("Random Delay:", self.random_delay)
        
        # Show Splash Screen
        self.show_splash = QCheckBox()
        self.show_splash.setChecked(True)
        layout.addRow("Show Splash Screen:", self.show_splash)
        
        # Auto-Open Console
        self.auto_console = QCheckBox()
        self.auto_console.setChecked(True)
        layout.addRow("Auto-Open Console:", self.auto_console)
        
        # Window Settings Group
        window_group = QGroupBox("Window Settings")
        window_layout = QFormLayout()
        window_group.setLayout(window_layout)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        window_layout.addRow("Theme:", self.theme_combo)
        
        # Font size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setSuffix(" pt")
        window_layout.addRow("Font Size:", self.font_size_spin)
        
        # Add window group to main layout
        layout.addRow(window_group)

    def _setup_card_tab(self):
        """Set up the card dimensions tab."""
        layout = QFormLayout()
        self.card_tab.setLayout(layout)
        
        # Card Size Group
        size_group = QGroupBox("Card Size")
        size_layout = QFormLayout()
        size_group.setLayout(size_layout)
        
        # Width
        self.card_width_spin = QSpinBox()
        self.card_width_spin.setRange(100, 1000)
        self.card_width_spin.setSuffix(" px")
        size_layout.addRow("Card Width:", self.card_width_spin)
        
        # Height
        self.card_height_spin = QSpinBox()
        self.card_height_spin.setRange(50, 500)
        self.card_height_spin.setSuffix(" px")
        size_layout.addRow("Card Height:", self.card_height_spin)
        
        # Scale Factor
        self.scale_factor = QSpinBox()
        self.scale_factor.setRange(1, 10)
        self.scale_factor.setValue(3)
        self.scale_factor.setSuffix("x")
        size_layout.addRow("Scale Factor:", self.scale_factor)
        
        layout.addRow(size_group)
        
        # Card Dimensions Group
        dims_group = QGroupBox("Card Dimensions")
        dims_layout = QFormLayout()
        dims_group.setLayout(dims_layout)
        
        # Top/Bottom Margin
        self.top_margin = QSpinBox()
        self.top_margin.setRange(0, 20)
        self.top_margin.setValue(4)
        self.top_margin.setSuffix(" mm")
        dims_layout.addRow("Top/Bottom Margin:", self.top_margin)
        
        # Side Margin
        self.side_margin = QSpinBox()
        self.side_margin.setRange(0, 20)
        self.side_margin.setValue(5)
        self.side_margin.setSuffix(" mm")
        dims_layout.addRow("Side Margin:", self.side_margin)
        
        # Row Spacing
        self.row_spacing = QSpinBox()
        self.row_spacing.setRange(1, 10)
        self.row_spacing.setValue(2)
        self.row_spacing.setSuffix(" mm")
        dims_layout.addRow("Row Spacing:", self.row_spacing)
        
        # Column Spacing
        self.column_spacing = QSpinBox()
        self.column_spacing.setRange(1, 5)
        self.column_spacing.setValue(1)
        self.column_spacing.setSuffix(" mm")
        dims_layout.addRow("Column Spacing:", self.column_spacing)
        
        # Hole Width
        self.hole_width = QSpinBox()
        self.hole_width.setRange(1, 5)
        self.hole_width.setValue(1)
        self.hole_width.setSuffix(" mm")
        dims_layout.addRow("Hole Width:", self.hole_width)
        
        # Hole Height
        self.hole_height = QSpinBox()
        self.hole_height.setRange(1, 10)
        self.hole_height.setValue(3)
        self.hole_height.setSuffix(" mm")
        dims_layout.addRow("Hole Height:", self.hole_height)
        
        layout.addRow(dims_group)

    def _setup_openai_tab(self):
        """Set up the OpenAI API tab."""
        layout = QVBoxLayout()
        self.openai_tab.setLayout(layout)
        
        # API Key Section
        api_key_group = QGroupBox("API Key")
        api_key_layout = QVBoxLayout()
        api_key_group.setLayout(api_key_layout)
        
        # Show keychain status if available
        if KEYRING_AVAILABLE:
            keychain_label = QLabel("✅ System keychain available for secure API key storage")
            keychain_label.setStyleSheet("color: #55AA55;")
            api_key_layout.addWidget(keychain_label)
        else:
            keychain_label = QLabel("⚠️ System keychain not available - API key will be stored in settings file")
            keychain_label.setStyleSheet("color: #AAAA55;")
            api_key_layout.addWidget(keychain_label)
        
        # API Key input with layout
        key_input_layout = QHBoxLayout()
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_edit.setPlaceholderText("Enter your OpenAI API key")
        key_input_layout.addWidget(self.api_key_edit)
        
        # Toggle visibility button
        toggle_btn = RetroButton("👁")
        toggle_btn.setMaximumWidth(30)
        toggle_btn.clicked.connect(self.toggle_key_visibility)
        key_input_layout.addWidget(toggle_btn)
        
        api_key_layout.addLayout(key_input_layout)
        
        # API key status label
        self.api_key_status = QLabel("Status: Not verified")
        api_key_layout.addWidget(self.api_key_status)
        
        # API Key action buttons
        key_buttons_layout = QHBoxLayout()
        
        verify_btn = RetroButton("Verify Key")
        verify_btn.clicked.connect(self.verify_api_key)
        key_buttons_layout.addWidget(verify_btn)
        
        save_btn = RetroButton("Save Key")
        save_btn.clicked.connect(self.save_api_key)
        key_buttons_layout.addWidget(save_btn)
        
        if KEYRING_AVAILABLE:
            delete_btn = RetroButton("Delete Key from Keychain")
            delete_btn.clicked.connect(self.delete_api_key)
            key_buttons_layout.addWidget(delete_btn)
        
        api_key_layout.addLayout(key_buttons_layout)
        
        # Add the API key group to the main layout
        layout.addWidget(api_key_group)
        
        # Add separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator1)
        
        # Model Selection Section
        model_group = QGroupBox("Model Selection")
        model_layout = QVBoxLayout()
        model_group.setLayout(model_layout)
        
        # Model dropdown with refresh button
        model_select_layout = QHBoxLayout()
        
        model_layout.addWidget(QLabel("Select OpenAI Model:"))
        self.model_combo = QComboBox()
        
        # Add default models
        default_models = [
            "gpt-3.5-turbo", 
            "gpt-3.5-turbo-16k", 
            "gpt-4o", 
            "gpt-4o-mini",
            "gpt-4"
        ]
        self.model_combo.addItems(default_models)
        model_select_layout.addWidget(self.model_combo)
        
        # Refresh models button
        refresh_btn = RetroButton("🔄")
        refresh_btn.setMaximumWidth(30)
        refresh_btn.clicked.connect(self.refresh_models)
        model_select_layout.addWidget(refresh_btn)
        
        model_layout.addLayout(model_select_layout)
        
        # Temperature setting
        temp_layout = QVBoxLayout()
        temp_label = QLabel("Temperature (creativity):")
        temp_layout.addWidget(temp_label)
        
        self.temperature_slider = QSlider(Qt.Orientation.Horizontal)
        self.temperature_slider.setRange(0, 200)  # 0.0 to 2.0
        self.temperature_slider.setValue(70)      # Default 0.7
        self.temperature_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.temperature_slider.setTickInterval(10)
        temp_layout.addWidget(self.temperature_slider)
        
        # Temperature value display
        temp_value_layout = QHBoxLayout()
        temp_value_layout.addWidget(QLabel("0.0"))
        
        self.temp_value_label = QLabel("0.7")
        self.temp_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        temp_value_layout.addWidget(self.temp_value_label)
        
        temp_value_layout.addWidget(QLabel("2.0"))
        temp_layout.addLayout(temp_value_layout)
        
        # Update temperature label when slider changes
        self.temperature_slider.valueChanged.connect(self.update_temperature_label)
        
        model_layout.addLayout(temp_layout)
        
        # Add model selection group to main layout
        layout.addWidget(model_group)
        
        # Add separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator2)
        
        # Test connection section
        test_group = QGroupBox("Test API Connection")
        test_layout = QVBoxLayout()
        test_group.setLayout(test_layout)
        
        test_btn = RetroButton("Test API Connection")
        test_btn.clicked.connect(self.test_api_connection)
        test_layout.addWidget(test_btn)
        
        self.connection_status = QLabel("Status: Not tested")
        test_layout.addWidget(self.connection_status)
        
        # Add test connection group to main layout
        layout.addWidget(test_group)

    def _setup_stats_tab(self):
        """Set up the statistics tab."""
        layout = QVBoxLayout()
        self.stats_tab.setLayout(layout)
        
        # API Usage Statistics
        usage_group = QGroupBox("API Usage Statistics")
        usage_layout = QFormLayout()
        usage_group.setLayout(usage_layout)
        
        # Total API calls
        self.total_calls_label = QLabel("0")
        usage_layout.addRow("Total API Calls:", self.total_calls_label)
        
        # Total tokens
        self.total_tokens_label = QLabel("0")
        usage_layout.addRow("Total Tokens Used:", self.total_tokens_label)
        
        # Prompt tokens
        self.prompt_tokens_label = QLabel("0")
        usage_layout.addRow("Prompt Tokens:", self.prompt_tokens_label)
        
        # Completion tokens
        self.completion_tokens_label = QLabel("0")
        usage_layout.addRow("Completion Tokens:", self.completion_tokens_label)
        
        # Estimated cost
        self.cost_label = QLabel("$0.00")
        usage_layout.addRow("Estimated Cost:", self.cost_label)
        
        # Last updated
        self.last_updated_label = QLabel("Never")
        usage_layout.addRow("Last Updated:", self.last_updated_label)
        
        # Add reset button
        reset_button = RetroButton("Reset Usage Statistics")
        reset_button.clicked.connect(self.reset_usage_stats)
        usage_layout.addRow("", reset_button)
        
        layout.addWidget(usage_group)
        
        # Message Statistics Group
        message_group = QGroupBox("Message Statistics")
        message_layout = QFormLayout()
        message_group.setLayout(message_layout)
        
        # Total messages
        self.total_messages_label = QLabel("0")
        message_layout.addRow("Total Messages:", self.total_messages_label)
        
        # Messages by source
        self.local_messages_label = QLabel("0")
        message_layout.addRow("Local Messages:", self.local_messages_label)
        
        self.openai_messages_label = QLabel("0")
        message_layout.addRow("OpenAI Messages:", self.openai_messages_label)
        
        self.database_messages_label = QLabel("0")
        message_layout.addRow("Database Messages:", self.database_messages_label)
        
        self.system_messages_label = QLabel("0")
        message_layout.addRow("System Messages:", self.system_messages_label)
        
        layout.addWidget(message_group)

    def _load_settings_from_manager(self):
        """Load settings from the settings manager into UI components."""
        try:
            # Load display settings
            self.led_delay.setValue(self.settings_manager.get_led_delay())
            self.interval_spin.setValue(self.settings_manager.get_message_interval())
            self.display_time_spin.setValue(self.settings_manager.get_message_display_time())
            self.delay_factor_spin.setValue(self.settings_manager.get_typing_delay_factor())
            self.random_delay.setChecked(self.settings_manager.get_random_delay())
            self.show_splash.setChecked(self.settings_manager.get_show_splash())
            self.auto_console.setChecked(self.settings_manager.get_auto_console())
            
            # Load window settings
            theme_index = self.theme_combo.findText(self.settings_manager.get_theme())
            if theme_index >= 0:
                self.theme_combo.setCurrentIndex(theme_index)
            self.font_size_spin.setValue(self.settings_manager.get_font_size())
            
            # Load card dimensions
            card_width, card_height = self.settings_manager.get_card_size()
            self.card_width_spin.setValue(card_width)
            self.card_height_spin.setValue(card_height)
            
            card_dims = self.settings_manager.get_card_dimensions()
            self.scale_factor.setValue(card_dims.get("scale_factor", 3))
            self.top_margin.setValue(card_dims.get("top_margin", 4))
            self.side_margin.setValue(card_dims.get("side_margin", 5))
            self.row_spacing.setValue(card_dims.get("row_spacing", 2))
            self.column_spacing.setValue(card_dims.get("column_spacing", 1))
            self.hole_width.setValue(card_dims.get("hole_width", 1))
            self.hole_height.setValue(card_dims.get("hole_height", 3))
            
            # Load OpenAI settings
            api_key = self.settings_manager.get_api_key()
            if api_key:
                self.api_key_edit.setText("●●●●●●●●●●●●●●●●●●●●●●●●●●●●")
                self.api_key_status.setText("Status: Key loaded from " + 
                                          ("keychain" if KEYRING_AVAILABLE else "settings"))
                
            model = self.settings_manager.get_model()
            model_index = self.model_combo.findText(model)
            if model_index >= 0:
                self.model_combo.setCurrentIndex(model_index)
            else:
                # If the model isn't in the dropdown, add it
                self.model_combo.addItem(model)
                self.model_combo.setCurrentText(model)
                
            temperature = self.settings_manager.get_temperature()
            self.temperature_slider.setValue(int(temperature * 100))
            self.update_temperature_label()
            
            # Load statistics
            self.update_stats_display()
            
        except Exception as e:
            logger.error(f"Error loading settings from manager: {str(e)}")
            QMessageBox.warning(
                self,
                "Settings Load Error",
                f"Failed to load some settings: {str(e)}"
            )

    def update_temperature_label(self):
        """Update the temperature value label based on slider position."""
        temp_value = float(self.temperature_slider.value()) / 100.0
        self.temp_value_label.setText(f"{temp_value:.1f}")

    def toggle_key_visibility(self):
        """Toggle visibility of the API key field."""
        if self.api_key_edit.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)

    def verify_api_key(self):
        """Check if the API key is valid."""
        # Get API key from input
        api_key = self.api_key_edit.text()
        
        # If the input field contains the masked placeholder, use the saved key
        if api_key == "●●●●●●●●●●●●●●●●●●●●●●●●●●●●":
            api_key = self.settings_manager.get_api_key()
            if not api_key:
                self.api_key_status.setText("Status: No saved API key found")
                self.api_key_status.setStyleSheet("color: #FF5555;")
                return
        # Otherwise check the entered key
        elif not api_key or len(api_key.strip()) < 10:
            self.api_key_status.setText("Status: Invalid key (too short)")
            self.api_key_status.setStyleSheet("color: #FF5555;")
            return
        
        # Update UI
        self.api_key_status.setText("Status: Verifying...")
        self.api_key_status.setStyleSheet("color: #AAAAAA;")
        
        # Update API manager with the key for testing
        self.api_manager.update_settings(api_key=api_key)
        
        # Test the connection
        success, message, models = self.api_manager.check_api_connection()
        
        if success:
            self.api_key_status.setText(f"Status: Valid key ✅")
            self.api_key_status.setStyleSheet("color: #55AA55;")
            
            # Update model dropdown with available models
            if models:
                self.update_model_dropdown(models)
            
            # Store the key securely (user will need to explicitly click "Save Key")
        else:
            self.api_key_status.setText(f"Status: Invalid key ❌ ({message})")
            self.api_key_status.setStyleSheet("color: #FF5555;")

    def save_api_key(self):
        """Update the API key in the configuration."""
        api_key = self.api_key_edit.text()
        
        # Skip if key is just placeholder asterisks
        if api_key == "●●●●●●●●●●●●●●●●●●●●●●●●●●●●":
            QMessageBox.warning(
                self, 
                "API Key Update", 
                "Please enter your actual API key, not the placeholder. If you want to keep using the current key, simply cancel and reopen settings."
            )
            return
        
        if not api_key or len(api_key.strip()) < 10:
            QMessageBox.warning(
                self, 
                "API Key Update", 
                "API key cannot be empty or too short."
            )
            return
        
        # Save the API key to settings
        try:
            # Save to settings manager (uses keychain if available)
            self.settings_manager.set_api_key(api_key)
            
            # Get values from UI
            model = self.model_combo.currentText()
            temperature = float(self.temperature_slider.value()) / 100.0
            
            # Update other OpenAI settings
            self.settings_manager.set_model(model)
            self.settings_manager.set_temperature(temperature)
            
            # Save to file
            self.settings_manager.save_settings()
            
            # Update the APIManager
            self.api_manager.update_settings(
                api_key=api_key,
                model=model,
                temperature=temperature
            )
            
            # Update UI
            secure_storage = "keychain" if KEYRING_AVAILABLE else "settings file"
            self.api_key_status.setText(f"Status: API Key Saved to {secure_storage} ✅")
            self.api_key_status.setStyleSheet("color: #55AA55;")
            
            # Test the connection with the new key
            self.verify_api_key()
            
            # Replace the entered key with a placeholder for security
            self.api_key_edit.setText("●●●●●●●●●●●●●●●●●●●●●●●●●●●●")
            
            # Show success message
            QMessageBox.information(
                self,
                "API Key Update",
                f"API key has been securely saved to {secure_storage} and will be used for all API requests."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "API Key Update Error",
                f"Failed to save API key: {str(e)}"
            )
            self.api_key_status.setText("Status: Save failed ❌")
            self.api_key_status.setStyleSheet("color: #FF5555;")

    def delete_api_key(self):
        """Delete the API key from the system keychain."""
        if not KEYRING_AVAILABLE:
            QMessageBox.warning(
                self,
                "Keychain Unavailable",
                "System keychain is not available on this system."
            )
            return
            
        reply = QMessageBox.question(
            self,
            "Delete API Key",
            "Are you sure you want to delete the API key from the system keychain?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.settings_manager.delete_api_key()
                if success:
                    # Update UI
                    self.api_key_edit.clear()
                    self.api_key_status.setText("Status: API Key Deleted ✅")
                    self.api_key_status.setStyleSheet("color: #55AA55;")
                    
                    # Also update the API manager
                    self.api_manager.update_settings(api_key="")
                    
                    QMessageBox.information(
                        self,
                        "API Key Deleted",
                        "API key has been successfully deleted from the system keychain."
                    )
                else:
                    self.api_key_status.setText("Status: Failed to delete key ❌")
                    self.api_key_status.setStyleSheet("color: #FF5555;")
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "API Key Delete Error",
                    f"Failed to delete API key: {str(e)}"
                )
                self.api_key_status.setText("Status: Delete failed ❌")
                self.api_key_status.setStyleSheet("color: #FF5555;")

    def refresh_models(self):
        """Refresh the available models list from the API."""
        # Check if we have a valid API key
        api_key = self.settings_manager.get_api_key()
        if not api_key:
            QMessageBox.warning(
                self,
                "API Key Required",
                "A valid API key is required to refresh models list."
            )
            return
            
        try:
            # Test the connection
            success, message, models = self.api_manager.check_api_connection()
            
            if success and models:
                self.update_model_dropdown(models)
                QMessageBox.information(
                    self,
                    "Models Updated",
                    f"Successfully retrieved {len(models)} models from the API."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Models Update Failed",
                    f"Failed to retrieve models: {message}"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Models Update Error",
                f"Error refreshing models: {str(e)}"
            )

    def update_model_dropdown(self, models: List[str]):
        """Update the model dropdown with the available models from the API."""
        if not models:
            return
            
        # Remember the current selection
        current_model = self.model_combo.currentText()
        
        # Clear the dropdown
        self.model_combo.clear()
        
        # Sort and filter models
        gpt_models = sorted([m for m in models if m.startswith("gpt-")])
        
        # Add the models to the dropdown
        self.model_combo.addItems(gpt_models)
        
        # Try to restore the previous selection if it exists
        index = self.model_combo.findText(current_model)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)
        elif gpt_models:
            # Select the first gpt-4 model by default, or the first model if no gpt-4
            for i, model in enumerate(gpt_models):
                if "gpt-4" in model:
                    self.model_combo.setCurrentIndex(i)
                    break
            else:
                self.model_combo.setCurrentIndex(0)

    def test_api_connection(self):
        """Test the API connection with current settings."""
        # Define globals at the start of the method
        global service_status
        
        # Check if we have a valid API key
        api_key = self.settings_manager.get_api_key()
        if not api_key:
            self.connection_status.setText("Status: No API key configured")
            self.connection_status.setStyleSheet("color: #FF5555;")
            return
            
        # Update UI
        self.connection_status.setText("Status: Testing connection...")
        self.connection_status.setStyleSheet("color: #AAAAAA;")
        
        try:
            # Test the connection
            success, message, models = self.api_manager.check_api_connection()
            
            if success:
                self.connection_status.setText(f"Status: Connection successful ✅ ({len(models)} models available)")
                self.connection_status.setStyleSheet("color: #55AA55;")
                
                # Also update service status for the main app
                if 'service_status' in globals():
                    service_status["openai"] = {
                        "status": "ok",
                        "message": "Connection successful",
                        "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
            else:
                self.connection_status.setText(f"Status: Connection failed ❌ ({message})")
                self.connection_status.setStyleSheet("color: #FF5555;")
                
                # Update service status
                if 'service_status' in globals():
                    service_status["openai"] = {
                        "status": "error",
                        "message": message,
                        "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
        except Exception as e:
            self.connection_status.setText(f"Status: Error testing connection ❌ ({str(e)})")
            self.connection_status.setStyleSheet("color: #FF5555;")

    def update_stats_display(self):
        """Update the statistics display with current values."""
        try:
            # Update OpenAI usage stats
            usage_stats = self.settings_manager.get_usage_stats()
            
            self.total_calls_label.setText(f"{usage_stats.get('total_calls', 0):,}")
            self.total_tokens_label.setText(f"{usage_stats.get('total_tokens', 0):,}")
            self.prompt_tokens_label.setText(f"{usage_stats.get('prompt_tokens', 0):,}")
            self.completion_tokens_label.setText(f"{usage_stats.get('completion_tokens', 0):,}")
            
            cost = usage_stats.get('estimated_cost', 0.0)
            self.cost_label.setText(f"${cost:.4f}")
            
            last_updated = usage_stats.get('last_updated', 'Never')
            self.last_updated_label.setText(last_updated)
            
            # Update message stats
            global message_stats
            if 'message_stats' in globals():
                self.total_messages_label.setText(f"{message_stats.get('total', 0):,}")
                self.local_messages_label.setText(f"{message_stats.get('local', 0):,}")
                self.openai_messages_label.setText(f"{message_stats.get('openai', 0):,}")
                self.database_messages_label.setText(f"{message_stats.get('database', 0):,}")
                self.system_messages_label.setText(f"{message_stats.get('system', 0):,}")
            
        except Exception as e:
            logger.error(f"Error updating stats display: {str(e)}")

    def reset_usage_stats(self):
        """Reset the usage statistics."""
        reply = QMessageBox.question(
            self,
            "Reset Usage Statistics",
            "Are you sure you want to reset all API usage statistics?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Reset stats in the settings manager
                self.settings_manager.reset_usage_stats()
                
                # Save to file
                self.settings_manager.save_settings()
                
                # Update the display
                self.update_stats_display()
                
                QMessageBox.information(
                    self,
                    "Statistics Reset",
                    "API usage statistics have been reset."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Statistics Reset Error",
                    f"Failed to reset statistics: {str(e)}"
                )

    def accept(self):
        """Save all settings when OK is clicked."""
        try:
            # Get display settings from UI
            self.settings_manager.set_led_delay(self.led_delay.value())
            self.settings_manager.set_message_interval(self.interval_spin.value())
            self.settings_manager.set_message_display_time(self.display_time_spin.value())
            self.settings_manager.set_typing_delay_factor(self.delay_factor_spin.value())
            self.settings_manager.set_random_delay(self.random_delay.isChecked())
            self.settings_manager.set_show_splash(self.show_splash.isChecked())
            self.settings_manager.set_auto_console(self.auto_console.isChecked())
            
            # Get window settings
            self.settings_manager.set_theme(self.theme_combo.currentText())
            self.settings_manager.set_font_size(self.font_size_spin.value())
            
            # Get card size
            self.settings_manager.set_card_size(
                self.card_width_spin.value(),
                self.card_height_spin.value()
            )
            
            # Get card dimensions
            card_settings = {
                "scale_factor": self.scale_factor.value(),
                "top_margin": self.top_margin.value(),
                "side_margin": self.side_margin.value(),
                "row_spacing": self.row_spacing.value(),
                "column_spacing": self.column_spacing.value(),
                "hole_width": self.hole_width.value(),
                "hole_height": self.hole_height.value()
            }
            self.settings_manager.set_card_dimensions(card_settings)
            
            # Set OpenAI settings (don't set API key here, it's managed by save_api_key)
            model = self.model_combo.currentText()
            temperature = float(self.temperature_slider.value()) / 100.0
            self.settings_manager.set_model(model)
            self.settings_manager.set_temperature(temperature)
            
            # Save all settings to file
            self.settings_manager.save_settings()
            
            # Update APIManager with new settings
            self.api_manager.update_settings(
                model=model,
                temperature=temperature
            )
            
            # Show success message
            QMessageBox.information(
                self,
                "Settings Saved",
                "All settings have been saved successfully."
            )
            
            # Call parent accept method to close dialog
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Settings Save Error",
                f"Failed to save settings: {str(e)}"
            )
            # Don't close dialog on error

# For testing
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.show()
    sys.exit(app.exec()) 