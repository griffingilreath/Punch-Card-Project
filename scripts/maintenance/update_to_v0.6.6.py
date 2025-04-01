#!/usr/bin/env python3
"""
Update Script for Punch Card Project v0.6.6

This script helps migrate settings from previous versions to v0.6.6.
It handles API key migration to the secure keychain and updates the settings format.
"""

import os
import json
import sys
import keyring
from pathlib import Path

# Define application ID for keyring
APP_NAME = "PunchCardProject"
API_KEY_SERVICE = f"{APP_NAME}_API"
API_KEY_USERNAME = "openai"

def migrate_settings():
    """Migrate settings from older versions to v0.6.6 format."""
    print("Punch Card Project - Update to v0.6.6")
    print("=" * 50)
    print("This script will migrate your settings to v0.6.6 format.")
    print("It will securely store your API key in the system keychain.")
    print("=" * 50)

    # Find settings file
    settings_paths = [
        Path("punch_card_settings.json"),
        Path("src/punch_card_settings.json"),
        Path.home() / ".punch_card_settings.json"
    ]
    
    settings_file = None
    for path in settings_paths:
        if path.exists():
            settings_file = path
            break
    
    if not settings_file:
        print("No settings file found. Creating a new one.")
        settings_file = Path("punch_card_settings.json")
        settings = {"version": "0.6.6"}
    else:
        print(f"Found settings file at: {settings_file}")
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
        except json.JSONDecodeError:
            print("Error: Settings file is corrupt. Creating a new one.")
            settings = {"version": "0.6.6"}
    
    # Migrate API key to keychain if it exists in settings
    api_key = settings.get("openai_api_key", "")
    if api_key and len(api_key) > 10:  # Only migrate if the key looks valid
        print("API key found in settings file. Migrating to secure keychain...")
        try:
            keyring.set_password(API_KEY_SERVICE, API_KEY_USERNAME, api_key)
            print("API key successfully stored in system keychain.")
            
            # Remove the key from the settings file
            settings["openai_api_key"] = ""
            print("Removed API key from settings file for security.")
        except Exception as e:
            print(f"Error storing API key in keychain: {e}")
            print("API key will remain in settings file.")
    
    # Update version
    settings["version"] = "0.6.6"
    
    # Ensure all required settings exist with defaults
    defaults = {
        "openai_model": "gpt-4o-mini",
        "temperature": 0.85,
        "led_delay": 190,
        "interval": 5,
        "message_display_time": 3,
        "delay_factor": 1.0,
        "random_delay": False,
        "show_splash": True,
        "auto_console": True,
        "card_width": 300,
        "card_height": 200,
        "scale_factor": 3,
        "top_margin": 4,
        "side_margin": 5,
        "row_spacing": 2,
        "column_spacing": 1,
        "hole_width": 1,
        "hole_height": 3,
        "theme": "dark",
        "font_size": 12
    }
    
    # Apply defaults for missing settings
    for key, value in defaults.items():
        if key not in settings:
            settings[key] = value
            print(f"Added missing setting: {key}")
    
    # Initialize openai_usage if it doesn't exist
    if "openai_usage" not in settings:
        from datetime import datetime
        settings["openai_usage"] = {
            "total_calls": 0,
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "estimated_cost": 0.0,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "history": []
        }
        print("Initialized OpenAI usage tracking.")
    
    # Save updated settings
    try:
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
        print(f"Settings successfully updated and saved to {settings_file}")
        print("Update to v0.6.6 completed successfully.")
    except Exception as e:
        print(f"Error saving settings: {e}")
        print("Update failed.")
        return False
    
    return True

def check_requirements():
    """Check if all required packages are installed."""
    try:
        import keyring
        import json
        return True
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please install required packages: pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    print("Checking requirements...")
    if check_requirements():
        migrate_settings()
    else:
        sys.exit(1) 