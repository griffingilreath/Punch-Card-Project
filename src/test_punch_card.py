import argparse
import time
import os
import json
from punch_card import PunchCardDisplay
from message_generator import MessageGenerator
from settings_menu import SettingsMenu, Setting
from datetime import datetime

def load_settings():
    """Load settings from file or return defaults"""
    try:
        with open('punch_card_settings.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            'led_delay': 0.5,
            'message_delay': 5.0,
            'random_delay': True,
            'brightness': 0.5,
            'debug_mode': False,
            'skip_splash': False,
            'settings_timeout': 5
        }

def save_settings(settings):
    """Save settings to file"""
    try:
        with open('punch_card_settings.json', 'w') as f:
            json.dump(settings, f)
    except Exception as e:
        print(f"Warning: Could not save settings: {e}")

def print_message_info(message_db, message_number):
    """Print information about a message from the database"""
    message = message_db.get_message(message_number)
    if message:
        print(f"\nMessage #{message_number:07d}:")
        print(f"Content: {message['content']}")
        print(f"Generated: {datetime.fromtimestamp(message['generated_at']).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Last Displayed: {datetime.fromtimestamp(message['last_displayed']).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Display Count: {message['display_count']}")

def main():
    parser = argparse.ArgumentParser(description='Test the punch card display system')
    parser.add_argument('--skip-splash', action='store_true', help='Skip the splash screen')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--settings', action='store_true', help='Show settings menu before starting')
    args = parser.parse_args()

    # Load saved settings
    saved_settings = load_settings()
    
    # Initialize settings with saved values or defaults
    settings = {
        'led_delay': Setting(
            name='LED Delay',
            value=saved_settings.get('led_delay', 0.5),
            description='Delay between LED updates in seconds',
            min_value=0.1,
            max_value=2.0,
            step=0.1
        ),
        'message_delay': Setting(
            name='Message Delay',
            value=saved_settings.get('message_delay', 5.0),
            description='Delay between messages in seconds',
            min_value=1.0,
            max_value=30.0,
            step=1.0
        ),
        'random_delay': Setting(
            name='Random Delay',
            value=saved_settings.get('random_delay', True),
            description='Enable random delays between messages'
        ),
        'brightness': Setting(
            name='Brightness',
            value=saved_settings.get('brightness', 0.5),
            description='LED brightness level',
            min_value=0.1,
            max_value=1.0,
            step=0.1
        ),
        'debug_mode': Setting(
            name='Debug Mode',
            value=args.debug or saved_settings.get('debug_mode', False),
            description='Enable debug mode for faster operation'
        ),
        'skip_splash': Setting(
            name='Skip Splash',
            value=args.skip_splash or saved_settings.get('skip_splash', False),
            description='Skip the splash screen on startup'
        ),
        'settings_timeout': Setting(
            name='Settings Timeout',
            value=saved_settings.get('settings_timeout', 5),
            description='Time in seconds to wait for settings prompt',
            min_value=1,
            max_value=30,
            step=1
        )
    }

    # Initialize display with current settings
    display = PunchCardDisplay(
        led_delay=settings['led_delay'].value,
        message_delay=settings['message_delay'].value,
        random_delay=settings['random_delay'].value,
        skip_splash=False,  # Always show splash screen
        debug_mode=args.debug
    )

    # Prompt for settings after splash screen
    if display._prompt_for_settings(settings['settings_timeout'].value):
        menu = SettingsMenu(settings)
        if menu.display_menu():
            settings_values = menu.get_settings()
            # Save new settings
            save_settings({
                'led_delay': settings_values['led_delay'],
                'message_delay': settings_values['message_delay'],
                'random_delay': settings_values['random_delay'],
                'brightness': settings_values['brightness'],
                'debug_mode': settings_values['debug_mode'],
                'skip_splash': settings_values['skip_splash'],
                'settings_timeout': settings_values['settings_timeout']
            })
            # Update display with new settings
            display.led_delay = settings_values['led_delay']
            display.message_delay = settings_values['message_delay']
            display.random_delay = settings_values['random_delay']
            display.brightness = settings_values['brightness']
            display.debug_mode = settings_values['debug_mode']

    # Initialize message generator
    message_gen = MessageGenerator()

    # Generate and display test messages
    print("\nGenerating test messages...")
    
    # Generate random messages
    for _ in range(3):
        message = message_gen.generate_random_sentence()
        display.show_message(message)
        print_message_info(display.message_db, display.message_number)
        time.sleep(1)
    
    # Generate system status messages
    for _ in range(2):
        message = message_gen.generate_system_message()
        display.show_message(message)
        print_message_info(display.message_db, display.message_number)
        time.sleep(1)
    
    # Generate diagnostic messages
    for _ in range(2):
        message = message_gen.generate_diagnostic_message()
        display.show_message(message)
        print_message_info(display.message_db, display.message_number)
        time.sleep(1)
    
    # Generate specific diagnostic messages
    display.show_message(message_gen.generate_diagnostic_message(category="CPU", key="USAGE", value="OK"))
    print_message_info(display.message_db, display.message_number)
    time.sleep(1)
    
    display.show_message(message_gen.generate_diagnostic_message(category="MEMORY", key="STATUS", value="OK"))
    print_message_info(display.message_db, display.message_number)
    time.sleep(1)
    
    # Final message
    display.show_message("SYSTEM READY")
    print_message_info(display.message_db, display.message_number)
    
    # Print summary
    print("\nMessage Database Summary:")
    print(f"Total Messages: {display.message_db.get_message_count()}")
    print(f"Current Message Number: {display.message_db.current_message_number}")

if __name__ == "__main__":
    main() 