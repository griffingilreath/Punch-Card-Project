#!/usr/bin/env python3

"""
Test the new settings dialog implementation.

This script creates a simple application window with a button to open
the settings dialog, to verify that our implementation works correctly.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

# Import our settings_dialog implementation
from src.display.settings_dialog import SettingsDialog
from src.utils.settings_manager import get_settings

class TestWindow(QMainWindow):
    """Simple test window for the settings dialog."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings Dialog Test")
        self.resize(600, 400)
        
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Create layout
        layout = QVBoxLayout(central)
        
        # Create button to open settings dialog
        settings_button = QPushButton("Open Settings")
        settings_button.setMinimumHeight(50)
        settings_button.clicked.connect(self.show_settings_dialog)
        layout.addWidget(settings_button)
        
        # Add a settings display button
        display_button = QPushButton("Display Current Settings")
        display_button.clicked.connect(self.display_settings)
        layout.addWidget(display_button)
    
    def show_settings_dialog(self):
        """Show the settings dialog."""
        # Create the dialog
        dialog = SettingsDialog(self)
        
        # Show the dialog modally (blocks until closed)
        if dialog.exec() == SettingsDialog.DialogCode.Accepted:
            print("Settings were accepted and saved")
            
            # Get the settings manager
            settings = get_settings()
            
            # Display some sample settings
            print(f"LED Delay: {settings.get_led_delay()}")
            print(f"Message Display Time: {settings.get_message_display_time()}")
            print(f"Card Dimensions: {settings.get_card_dimensions()}")
            
            # If an API key is set, show that we have one (but not the actual key)
            if settings.get_api_key():
                print(f"API Key is set: Yes")
                print(f"API Model: {settings.get_model()}")
                print(f"API Temperature: {settings.get_temperature()}")
            else:
                print("API Key is not set")
        else:
            print("Settings dialog was canceled")
    
    def display_settings(self):
        """Display the current settings values."""
        # Get the settings manager
        settings = get_settings()
        
        # Display current settings
        print("\nCurrent Settings:")
        print("-" * 40)
        print(f"LED Delay: {settings.get_led_delay()}")
        print(f"Message Interval: {settings.get_message_interval()}")
        print(f"Message Display Time: {settings.get_message_display_time()}")
        print(f"Random Delay: {settings.get_random_delay()}")
        print(f"Show Splash: {settings.get_show_splash()}")
        print(f"Auto Console: {settings.get_auto_console()}")
        
        print("\nCard Dimensions:")
        print("-" * 40)
        width, height = settings.get_card_size()
        print(f"Card Size: {width}x{height} pixels")
        print(f"Card Dimensions: {settings.get_card_dimensions()}")
        
        print("\nAPI Settings:")
        print("-" * 40)
        if settings.get_api_key():
            print(f"API Key: [SECURED]")
            print(f"API Model: {settings.get_model()}")
            print(f"API Temperature: {settings.get_temperature()}")
        else:
            print("API Key is not set")
            
        print("\nUsage Statistics:")
        print("-" * 40)
        usage = settings.get_usage_stats()
        print(f"Total API Calls: {usage.get('total_calls', 0)}")
        print(f"Total Tokens: {usage.get('total_tokens', 0)}")
        print(f"Estimated Cost: ${usage.get('estimated_cost', 0):.4f}")
        print(f"Last Updated: {usage.get('last_updated', 'Never')}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec()) 