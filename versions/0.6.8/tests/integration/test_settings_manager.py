#!/usr/bin/env python3

"""
Test script for the SettingsManager class.
"""

import os
import json
from src.utils.settings_manager import get_settings

def test_settings_manager():
    """Test basic SettingsManager functionality."""
    # Get the settings manager
    settings = get_settings()
    print(f"Settings loaded from: {settings.settings_path}")

    # Test basic getters/setters
    print("\n=== Testing Basic Getters/Setters ===")
    settings.set_led_delay(150)
    print(f"LED Delay: {settings.get_led_delay()}")
    
    settings.set_message_interval(10)
    print(f"Message Interval: {settings.get_message_interval()}")
    
    settings.set_random_delay(False)
    print(f"Random Delay: {settings.get_random_delay()}")

    # Test card dimensions
    print("\n=== Testing Card Dimensions ===")
    card_dims = settings.get_card_dimensions()
    print(f"Current card dimensions: {card_dims}")
    
    # Modify dimensions
    new_dims = card_dims.copy()
    new_dims["scale_factor"] = 4
    new_dims["hole_width"] = 2
    settings.set_card_dimensions(new_dims)
    
    # Verify changes
    print(f"New card dimensions: {settings.get_card_dimensions()}")

    # Test API settings
    print("\n=== Testing API Settings ===")
    # Save a dummy API key
    test_api_key = "test_sk_1234567890abcdefghijklmnopqrstuvwxyz"
    settings.set_api_key(test_api_key)
    retrieved_key = settings.get_api_key()
    print(f"API Key matches: {retrieved_key == test_api_key}")
    
    # Test model settings
    settings.set_model("gpt-4o-mini")
    print(f"Model: {settings.get_model()}")
    
    settings.set_temperature(0.85)
    print(f"Temperature: {settings.get_temperature()}")

    # Test saving to file
    print("\n=== Testing Save Settings ===")
    success = settings.save_settings()
    print(f"Settings saved successfully: {success}")
    
    # Verify file was created
    print(f"Settings file exists: {os.path.exists(settings.settings_path)}")
    
    # Output file contents
    if os.path.exists(settings.settings_path):
        with open(settings.settings_path, "r") as f:
            saved_settings = json.load(f)
        print(f"Settings file contains {len(saved_settings)} keys")
        
        # Check that our changes are in the file
        if "scale_factor" in saved_settings:
            print(f"scale_factor in file: {saved_settings['scale_factor']}")
        if "openai_model" in saved_settings:
            print(f"openai_model in file: {saved_settings['openai_model']}")
    
    # Reset to original state
    print("\n=== Cleanup ===")
    settings.set_card_dimensions(card_dims)  # Reset to original dimensions
    settings.save_settings()
    print("Settings reset to original state")

if __name__ == "__main__":
    test_settings_manager() 