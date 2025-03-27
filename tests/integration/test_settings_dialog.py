#!/usr/bin/env python3

"""
Test script for the SettingsDialog with new SettingsManager integration.

This script tests loading and saving settings through the GUI's SettingsDialog.
"""

import sys
from PyQt6.QtWidgets import QApplication
from src.display.gui_display import SettingsDialog
from src.utils.settings_manager import get_settings

def test_settings_dialog():
    """Test the SettingsDialog with our SettingsManager."""
    print("Initializing SettingsManager...")
    # Initialize the settings manager with some test values
    settings = get_settings()
    
    # Set some test values
    settings.set_led_delay(200)
    settings.set_message_interval(15)
    settings.set_message_display_time(10)
    settings.set_random_delay(True)
    
    # Set API details
    settings.set_api_key("test_api_key_for_dialog_12345")
    settings.set_model("gpt-4o")
    settings.set_temperature(0.5)
    
    # Card dimensions
    dimensions = settings.get_card_dimensions()
    dimensions["scale_factor"] = 5
    dimensions["hole_width"] = 2
    settings.set_card_dimensions(dimensions)
    
    # Save settings to file
    settings.save_settings()
    print("Test settings saved")
    
    # Initialize Qt application
    app = QApplication.instance() if QApplication.instance() else QApplication(sys.argv)
    
    # Create and show settings dialog
    print("Opening SettingsDialog...")
    dialog = SettingsDialog()
    
    # Show the dialog (this is a blocking call in a test script)
    # In a real app, you'd use dialog.exec() instead
    print("Dialog open - please interact with it and close when done")
    dialog.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    test_settings_dialog() 