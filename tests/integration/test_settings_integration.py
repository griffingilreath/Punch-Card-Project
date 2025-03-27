#!/usr/bin/env python3

"""
Integration test for the SettingsManager with various application components.

This test demonstrates how the SettingsManager coordinates settings between
different parts of the application.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from src.utils.settings_manager import get_settings
from src.api.api_manager import APIManager

class TestWindow(QMainWindow):
    """Simple test window that shows settings integration."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings Integration Test")
        self.resize(600, 400)
        
        # Initialize components
        self.settings = get_settings()
        self.api_manager = APIManager()
        
        # Set up UI
        self.setup_ui()
        
        # Update display with current settings
        self.update_settings_display()
    
    def setup_ui(self):
        """Set up the UI components."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Settings display section
        self.settings_label = QLabel("Current Settings:")
        layout.addWidget(self.settings_label)
        
        self.display_delay_label = QLabel()
        layout.addWidget(self.display_delay_label)
        
        self.message_interval_label = QLabel()
        layout.addWidget(self.message_interval_label)
        
        self.card_dimensions_label = QLabel()
        layout.addWidget(self.card_dimensions_label)
        
        self.api_settings_label = QLabel()
        layout.addWidget(self.api_settings_label)
        
        self.usage_stats_label = QLabel()
        layout.addWidget(self.usage_stats_label)
        
        # Actions section
        layout.addSpacing(20)
        
        # Modify settings
        modify_button = QPushButton("Modify Display Settings")
        modify_button.clicked.connect(self.modify_display_settings)
        layout.addWidget(modify_button)
        
        # Test API
        api_button = QPushButton("Test API Connection")
        api_button.clicked.connect(self.test_api)
        layout.addWidget(api_button)
        
        # Save all settings
        save_button = QPushButton("Save All Settings")
        save_button.clicked.connect(self.save_all_settings)
        layout.addWidget(save_button)
    
    def update_settings_display(self):
        """Update the display to show current settings."""
        # Display settings
        self.display_delay_label.setText(f"LED Delay: {self.settings.get_led_delay()} ms")
        self.message_interval_label.setText(f"Message Interval: {self.settings.get_message_interval()} s")
        
        # Card dimensions
        dims = self.settings.get_card_dimensions()
        self.card_dimensions_label.setText(
            f"Card Dimensions: Scale {dims['scale_factor']}x, "
            f"Hole: {dims['hole_width']}x{dims['hole_height']} mm"
        )
        
        # API settings
        api_key = self.settings.get_api_key()
        masked_key = "●●●●●●●●●●" if api_key else "Not set"
        self.api_settings_label.setText(
            f"API: {masked_key}, Model: {self.settings.get_model()}, "
            f"Temp: {self.settings.get_temperature()}"
        )
        
        # Usage stats
        stats = self.settings.get_usage_stats()
        self.usage_stats_label.setText(
            f"Usage: {stats['total_calls']} calls, "
            f"{stats['total_tokens']} tokens, "
            f"${stats['estimated_cost']:.4f} est. cost"
        )
    
    def modify_display_settings(self):
        """Modify some display settings to demonstrate change propagation."""
        # Update settings
        current_delay = self.settings.get_led_delay()
        self.settings.set_led_delay(current_delay + 10)
        
        interval = self.settings.get_message_interval()
        self.settings.set_message_interval(interval + 1)
        
        # Update display
        self.update_settings_display()
    
    def test_api(self):
        """Test the API connection."""
        success, message, models = self.api_manager.check_api_connection()
        
        if success:
            model_count = len(models) if models else 0
            self.api_settings_label.setText(f"API: Connected ✓ ({model_count} models available)")
        else:
            self.api_settings_label.setText(f"API: Connection Failed ✗ ({message})")
        
        # Update usage stats display
        self.update_settings_display()
    
    def save_all_settings(self):
        """Save all settings to demonstrate persistence."""
        success = self.settings.save_settings()
        
        if success:
            self.setWindowTitle("Settings Integration Test - Saved ✓")
        else:
            self.setWindowTitle("Settings Integration Test - Save Failed ✗")

def run_test():
    """Run the integration test."""
    app = QApplication.instance() if QApplication.instance() else QApplication(sys.argv)
    
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    run_test() 