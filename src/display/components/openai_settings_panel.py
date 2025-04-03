#!/usr/bin/env python3
"""
OpenAI Settings Panel Module

A panel for configuring OpenAI API settings in a modular design.
"""

import logging
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QFormLayout,
    QComboBox, QLineEdit, QTextEdit, QSlider, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor

from src.utils.colors import COLORS
from src.utils.fonts import get_font_css
from src.utils.ui_components import RetroButton
from src.utils.settings_manager import get_settings, KEYRING_AVAILABLE
from src.api.api_manager import APIManager

# Configure logging
logger = logging.getLogger('OpenAISettingsPanel')

class OpenAISettingsPanel(QFrame):
    """Panel for configuring OpenAI API settings in a modular design."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(450, 600)
        self.setMaximumHeight(600)
        self.setStyleSheet("""
            QFrame {
                background-color: black;
                color: white;
                border: 1px solid #444444;
            }
            QLabel {
                color: white;
                font-family: 'Courier New';
                font-size: 10px;
            }
            QGroupBox {
                color: white;
                border: 1px solid #444444;
                border-radius: 0px;
                margin-top: 2ex;
                font-family: 'Courier New';
                font-size: 10px;
                font-weight: bold;
                padding: 6px;
                background-color: #0a0a0a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
                color: white;
                font-family: 'Courier New';
                font-size: 10px;
                font-weight: bold;
                background-color: black;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #0a0a0a;
                color: white;
                border: 1px solid #444444;
                padding: 3px;
                font-family: 'Courier New';
                font-size: 10px;
                min-height: 18px;
                selection-background-color: #333333;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 1px solid #666666;
            }
            QSlider::groove:horizontal {
                border: 1px solid #444444;
                height: 6px;
                background: #0a0a0a;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: #666666;
                border: 1px solid #444444;
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background: #888888;
            }
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border: 1px solid #444444;
                background: #0a0a0a;
            }
            QCheckBox::indicator:checked {
                background: #666666;
                border: 1px solid #444444;
            }
            RetroButton {
                color: white;
                background-color: black;
                border: 1px solid #444444;
                padding: 3px 6px;
                font-family: 'Courier New';
                font-size: 10px;
                min-height: 18px;
                margin: 1px;
                width: 80px;
            }
            RetroButton:hover {
                background-color: #1a1a1a;
                border: 1px solid #666666;
            }
        """)
        
        # Initialize settings manager and API manager
        self.settings_manager = get_settings()
        self.api_manager = APIManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Header
        header_label = QLabel("🤖 OpenAI API Settings")
        header_label.setStyleSheet(f"{get_font_css(size=15, bold=True)} color: white;")
        layout.addWidget(header_label)
        
        # API Key Section
        self.api_key_group = QGroupBox("API Key")
        api_key_layout = QVBoxLayout()
        api_key_layout.setSpacing(4)
        api_key_layout.setContentsMargins(6, 6, 6, 6)
        self.api_key_group.setLayout(api_key_layout)
        
        # Show keychain status if available
        if KEYRING_AVAILABLE:
            keychain_label = QLabel("✅ System keychain available")
            keychain_label.setStyleSheet("color: #55AA55;")
            api_key_layout.addWidget(keychain_label)
        else:
            keychain_label = QLabel("⚠️ System keychain not available")
            keychain_label.setStyleSheet("color: #AAAA55;")
            api_key_layout.addWidget(keychain_label)
        
        # API Key input with layout
        key_input_layout = QHBoxLayout()
        key_input_layout.setSpacing(8)
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_edit.setPlaceholderText("Enter your OpenAI API key")
        key_input_layout.addWidget(self.api_key_edit)
        
        # Toggle visibility button
        toggle_btn = RetroButton("👁")
        toggle_btn.setFixedWidth(36)
        toggle_btn.clicked.connect(self.toggle_key_visibility)
        key_input_layout.addWidget(toggle_btn)
        
        api_key_layout.addLayout(key_input_layout)
        
        # API key status label
        self.api_key_status = QLabel("Status: Not verified")
        api_key_layout.addWidget(self.api_key_status)
        
        # API Key action buttons
        key_buttons_layout = QHBoxLayout()
        key_buttons_layout.setSpacing(8)
        
        verify_btn = RetroButton("Verify Key")
        verify_btn.clicked.connect(self.verify_api_key)
        key_buttons_layout.addWidget(verify_btn)
        
        save_btn = RetroButton("Save Key")
        save_btn.clicked.connect(self.save_api_key)
        key_buttons_layout.addWidget(save_btn)
        
        if KEYRING_AVAILABLE:
            delete_btn = RetroButton("Delete Key")
            delete_btn.clicked.connect(self.delete_api_key)
            key_buttons_layout.addWidget(delete_btn)
        
        api_key_layout.addLayout(key_buttons_layout)
        
        layout.addWidget(self.api_key_group)
        
        # Model Selection Group
        self.model_group = QGroupBox("Model Selection")
        model_layout = QVBoxLayout()
        model_layout.setSpacing(4)
        model_layout.setContentsMargins(6, 6, 6, 6)
        self.model_group.setLayout(model_layout)
        
        # Model dropdown with refresh button
        model_select_layout = QHBoxLayout()
        model_select_layout.setSpacing(8)
        
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
        refresh_btn.setFixedWidth(36)
        refresh_btn.clicked.connect(self.refresh_models)
        model_select_layout.addWidget(refresh_btn)
        
        model_layout.addLayout(model_select_layout)
        
        # Web search capability
        web_search_layout = QHBoxLayout()
        web_search_layout.setSpacing(8)
        
        web_search_label = QLabel("Use web search:")
        web_search_layout.addWidget(web_search_label)
        
        self.web_search_checkbox = QCheckBox()
        self.web_search_checkbox.setToolTip("Enable web search capability")
        web_search_layout.addWidget(self.web_search_checkbox)
        web_search_layout.addStretch()
        
        # Add recommended models info label
        web_search_info = QLabel("(Recommended for gpt-4o)")
        web_search_info.setStyleSheet("color: #AAAAAA; font-size: 10px;")
        web_search_layout.addWidget(web_search_info)
        
        model_layout.addLayout(web_search_layout)
        
        # Temperature setting
        temp_layout = QVBoxLayout()
        temp_layout.setSpacing(4)
        
        temp_label = QLabel("Temperature (controls creativity):")
        temp_layout.addWidget(temp_label)
        
        temp_slider_layout = QHBoxLayout()
        temp_slider_layout.setSpacing(8)
        
        self.temperature_slider = QSlider(Qt.Orientation.Horizontal)
        self.temperature_slider.setRange(0, 200)  # 0.0 to 2.0
        self.temperature_slider.setValue(70)      # Default 0.7
        self.temperature_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.temperature_slider.setTickInterval(10)
        temp_slider_layout.addWidget(self.temperature_slider)
        
        self.temp_value_label = QLabel("0.7")
        self.temp_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temp_value_label.setFixedWidth(40)
        temp_slider_layout.addWidget(self.temp_value_label)
        
        temp_layout.addLayout(temp_slider_layout)
        
        # Update temperature label when slider changes
        self.temperature_slider.valueChanged.connect(self.update_temperature_label)
        
        model_layout.addLayout(temp_layout)
        
        layout.addWidget(self.model_group)
        
        # Prompt Settings Group
        self.prompt_group = QGroupBox("Default Prompt")
        prompt_layout = QVBoxLayout()
        prompt_layout.setSpacing(4)
        prompt_layout.setContentsMargins(6, 6, 6, 6)
        self.prompt_group.setLayout(prompt_layout)
        
        # Add prompt text edit
        prompt_layout.addWidget(QLabel("Enter default prompt for message generation:"))
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Enter the default prompt for generating messages...")
        self.prompt_edit.setMinimumHeight(100)
        prompt_layout.addWidget(self.prompt_edit)
        
        layout.addWidget(self.prompt_group)
        
        # Add save and close buttons
        button_layout = QVBoxLayout()  # Changed to vertical layout
        button_layout.setSpacing(4)
        
        # Test connection and status
        test_layout = QHBoxLayout()
        test_layout.setSpacing(4)
        
        self.test_button = RetroButton("Test")
        self.test_button.clicked.connect(self.test_connection)
        self.test_button.setFixedWidth(80)
        test_layout.addWidget(self.test_button)
        
        self.connection_status = QLabel("Status: Not tested")
        self.connection_status.setStyleSheet("""
            QLabel {
                color: white;
                font-family: 'Courier New';
                font-size: 10px;
                background-color: #0a0a0a;
                padding: 3px;
                border: 1px solid #444444;
            }
        """)
        test_layout.addWidget(self.connection_status)
        test_layout.addStretch()
        
        button_layout.addLayout(test_layout)
        
        # Save and close buttons on a new line
        action_buttons = QHBoxLayout()
        action_buttons.setSpacing(4)
        action_buttons.addStretch()
        
        self.save_button = RetroButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        self.save_button.setFixedWidth(80)
        action_buttons.addWidget(self.save_button)
        
        self.close_button = RetroButton("Close")
        self.close_button.clicked.connect(self.hide)
        self.close_button.setFixedWidth(80)
        action_buttons.addWidget(self.close_button)
        
        button_layout.addLayout(action_buttons)
        
        layout.addLayout(button_layout)
        
    def showEvent(self, event):
        """Handle show event to load current settings."""
        super().showEvent(event)
        self.load_settings()
        
    def load_settings(self):
        """Load settings from the settings manager."""
        try:
            # Load API key (masked)
            api_key = self.settings_manager.get_api_key()
            if api_key:
                self.api_key_edit.setText("●●●●●●●●●●●●●●●●●●●●●●●●●●●●")
                self.api_key_status.setText("Status: Key loaded from " + 
                                          ("keychain" if KEYRING_AVAILABLE else "settings"))
            
            # Load model
            model = self.settings_manager.get_model()
            model_index = self.model_combo.findText(model)
            if model_index >= 0:
                self.model_combo.setCurrentIndex(model_index)
            else:
                # If the model isn't in the dropdown, add it
                self.model_combo.addItem(model)
                self.model_combo.setCurrentText(model)
            
            # Load web search setting
            self.web_search_checkbox.setChecked(self.settings_manager.get_use_web_search())
            
            # Load temperature
            temperature = self.settings_manager.get_temperature()
            self.temperature_slider.setValue(int(temperature * 100))
            self.update_temperature_label()
            
            # Load prompt
            self.prompt_edit.setPlainText(self.settings_manager.get_openai_prompt())
            
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
            # Get values from UI
            model = self.model_combo.currentText()
            temperature = float(self.temperature_slider.value()) / 100.0
            use_web_search = self.web_search_checkbox.isChecked()
            prompt = self.prompt_edit.toPlainText().strip()
            
            # Update settings
            self.settings_manager.set_openai_settings(
                model=model,
                temperature=temperature,
                use_web_search=use_web_search,
                prompt=prompt
            )
            
            # Save to file
            self.settings_manager.save_settings()
            
            # Update the API manager
            self.api_manager.update_settings(
                model=model,
                temperature=temperature
            )
            
            # Show success message
            QMessageBox.information(
                self,
                "Settings Saved",
                "OpenAI settings have been saved successfully."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Settings Save Error",
                f"Failed to save settings: {str(e)}"
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
                if not KEYRING_AVAILABLE:
                    self.api_key_status.setText("Status: Keychain not available - please enter API key manually")
                else:
                    self.api_key_status.setText("Status: No saved API key found in keychain")
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
        success = self.api_manager.check_api_connection()
        
        if success:
            self.api_key_status.setText(f"Status: Valid key ✅")
            self.api_key_status.setStyleSheet("color: #55AA55;")
            
            # Update model dropdown with available models
            models = self.api_manager.get_available_models()
            if models:
                self.update_model_dropdown(models)
        else:
            self.api_key_status.setText(f"Status: Invalid key ❌")
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
            
            # Update the APIManager
            self.api_manager.update_settings(api_key=api_key)
            
            # Save to file
            self.settings_manager.save_settings()
            
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
    
    def update_model_dropdown(self, models):
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
    
    def test_connection(self):
        """Test the API connection with current settings."""
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
            else:
                self.connection_status.setText(f"Status: Connection failed ❌ ({message})")
                self.connection_status.setStyleSheet("color: #FF5555;")
        except Exception as e:
            self.connection_status.setText(f"Status: Error testing connection ❌ ({str(e)})")
            self.connection_status.setStyleSheet("color: #FF5555;")
    
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
    panel = OpenAISettingsPanel()
    panel.show()
    sys.exit(app.exec()) 