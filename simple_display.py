#!/usr/bin/env python3
# Simple Punch Card Display GUI
# This version has a simpler interface and uses PyQt6
# Version 0.5.3 - MonkeyPatch Update

import os
import sys
import time
import json
import random
import signal
import argparse
from datetime import datetime
import requests
import sqlite3

# Version information
VERSION = "0.5.3 - MonkeyPatch Update"
# ASCII art for the MonkeyPatch update
MONKEY_ART = """
  ,-.-.
 ( o o )  MONKEY PATCH
 |  ^  |
 | `-' |  v0.5.3
 `-----'
"""

# ==== DIRECT OPENAI PATCHING - HIGHEST PRIORITY ====
# This must run before any other imports to ensure we properly patch OpenAI
print("====== MONKEY PATCH - HIGHEST PRIORITY ======")
print("🐒 Welcome to the Punch Card MonkeyPatch Update v0.5.3 🐒")
print(MONKEY_ART)

# Global patched client instance
openai_client = None

def create_clean_openai_client(api_key=None, **kwargs):
    """
    Create a clean OpenAI client without any problematic parameters.
    This is a monkey-patched wrapper around the official client that ensures no invalid parameters are passed.
    """
    global openai_client
    
    # Only create once if the client exists
    if openai_client is not None:
        print("🐒 Returning existing monkey-patched OpenAI client instance")
        return openai_client
    
    print(f"🐒 Creating monkey-patched OpenAI client with provided API key")
    
    try:
        # Import the module
        import openai
        
        # Clean the parameters - keep ONLY valid parameters
        valid_params = {
            'api_key': api_key
        }
        
        # Only add parameters that are not None
        valid_params = {k: v for k, v in valid_params.items() if v is not None}
        
        print(f"🐒 Creating OpenAI client with parameters: {list(valid_params.keys())}")
        
        # Create the client with minimal parameters
        openai_client = openai.OpenAI(**valid_params)
        print("✅ Successfully created monkey-patched OpenAI client")
        return openai_client
        
    except ImportError:
        print("❌ OpenAI module not installed")
        return None
    except Exception as e:
        print(f"❌ Error creating OpenAI client: {str(e)}")
        return None

# Monkey patch all potential sources of 'proxies' in settings files
def clean_proxies_from_settings():
    try:
        files_to_check = [
            "punch_card_settings.json",
            os.path.join("config", "punch_card_settings.json"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "punch_card_settings.json"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "punch_card_settings.json")
        ]
        
        for settings_file in files_to_check:
            if os.path.exists(settings_file):
                print(f"🐒 Checking settings file: {settings_file}")
                try:
                    with open(settings_file, 'r') as f:
                        config_data = json.load(f)
                        modified = False
                        
                        # Check top level
                        if 'proxies' in config_data:
                            print(f"🐒 Removing 'proxies' from settings file (top level)")
                            del config_data['proxies']
                            modified = True
                        
                        # Check in config section
                        if 'config' in config_data and isinstance(config_data['config'], dict):
                            if 'proxies' in config_data['config']:
                                print(f"🐒 Removing 'proxies' from settings file (config section)")
                                del config_data['config']['proxies']
                                modified = True
                        
                        # Check in other sections
                        for section in config_data:
                            if isinstance(config_data[section], dict) and 'proxies' in config_data[section]:
                                print(f"🐒 Removing 'proxies' from settings file (section: {section})")
                                del config_data[section]['proxies']
                                modified = True
                        
                        if modified:
                            with open(settings_file, 'w') as f_out:
                                json.dump(config_data, f_out, indent=4)
                            print(f"✅ Saved cleaned settings to {settings_file}")
                        else:
                            print(f"No problematic settings found in {settings_file}")
                except Exception as e:
                    print(f"Error checking settings file {settings_file}: {e}")
    except Exception as e:
        print(f"Error in settings cleaning: {e}")

# Run the settings cleaner
clean_proxies_from_settings()

# Monkey patch the OpenAI client creation
try:
    print("🐒 Setting up OpenAI monkey patching...")
    import openai
    
    # Replace the OpenAI class with our wrapper function
    original_OpenAI = openai.OpenAI
    
    def monkey_patched_OpenAI(*args, **kwargs):
        print("🐒 Redirecting OpenAI client creation to our monkey-patched wrapper")
        
        # Log the arguments we received
        if kwargs:
            print(f"Original parameters: {list(kwargs.keys())}")
            
            # Remove any problematic parameters
            for param in ['proxies', 'proxy', 'organization', 'org_id']:
                if param in kwargs:
                    print(f"🐒 Removing '{param}' parameter from OpenAI client creation")
                    kwargs.pop(param)
        
        # Extract the API key if present
        api_key = kwargs.get('api_key')
        
        # Use our clean wrapper instead
        return create_clean_openai_client(api_key=api_key)
    
    # Replace the OpenAI class
    openai.OpenAI = monkey_patched_OpenAI
    print("✅ Successfully monkey-patched OpenAI client creation")
except ImportError:
    print("OpenAI module not available, skipping monkey patching")
except Exception as e:
    print(f"⚠️ Error setting up OpenAI monkey patching: {e}")

print("====== MONKEY PATCH COMPLETE ======")

from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QGridLayout, 
    QLabel, QPushButton, QRadioButton, QGroupBox,
    QDialogButtonBox, QSpinBox, QCheckBox, QTextEdit, 
    QWidget, QFrame, QTabWidget, QScrollArea, QLineEdit, 
    QMessageBox, QComboBox, QFormLayout, QDoubleSpinBox,
    QMainWindow, QHBoxLayout, QDockWidget, QSlider
)
from PyQt6.QtCore import QTimer, Qt, QEvent, QObject, QKeySequence, QSize
from PyQt6.QtGui import (
    QIcon, QShortcut, QPixmap, QColor, QPainter, QPalette, 
    QFont, QKeyEvent, QTextOption, QLinearGradient, QFontMetrics,
    QSyntaxHighlighter, QTextCharFormat
)
from src.display.gui_display import main as gui_main
from openai import OpenAI, APIError

# Try to import PunchCardDisplay and monkey patch it to use our settings dialog
try:
    from src.punch_card import PunchCardDisplay
    
    # Store original method for backup
    original_show_settings = PunchCardDisplay._show_settings_menu
    
    # Define our replacement method that will be used when imported
    def patched_show_settings_menu(self):
        """
        Show the enhanced settings dialog from simple_display.py.
        
        This replaces the old terminal-based settings menu.
        """
        print("Opening enhanced settings dialog via monkey patch...")
        try:
            # Import the show_settings_dialog function if needed
            # Note: This uses relative import since we're in the patch
            from simple_display import show_settings_dialog
            
            # Call the enhanced settings dialog
            show_settings_dialog(self)
        except Exception as e:
            print(f"⚠️ Error showing enhanced settings dialog: {e}")
            print("Falling back to original terminal settings menu...")
            # Call the original method
            original_show_settings(self)
            
    # Replace the method
    PunchCardDisplay._show_settings_menu = patched_show_settings_menu
    print("✅ Successfully patched PunchCardDisplay to use enhanced settings dialog")
except ImportError:
    print("ℹ️ PunchCardDisplay not imported - terminal patching not required")
except Exception as e:
    print(f"⚠️ Failed to patch PunchCardDisplay: {e}")

# Global variables
message_source = "local"  # Default to local messages
openai_client = None  # OpenAI client
message_database = []  # Local backup if DB doesn't exist
display = None  # Global reference to display object
message_stats = {
    "total": 0,
    "local": 0,
    "openai": 0,
    "database": 0,
    "system": 0,  # Added system category for welcome messages
    "last_updated": None,
    "last_message": None,  # Store the last message
    "last_source": None    # Store the source of the last message
}

# OpenAI usage statistics
openai_usage = {
    "total_calls": 0,
    "total_tokens": 0,
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "estimated_cost": 0.0,
    "last_updated": None,
    "usage_history": [],  # List of individual API calls with usage stats
    "cost_per_model": {},  # Track cost per model
}

# OpenAI pricing per 1000 tokens (as of current pricing)
openai_pricing = {
    "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-4o": {"input": 0.01, "output": 0.03},
    "gpt-4o-mini": {"input": 0.005, "output": 0.015},
}

# Service status tracking
service_status = {
    "openai": {
        "status": "unknown",
        "last_checked": None,
        "message": "Not checked yet"
    },
    "flyio": {
        "status": "unknown",
        "last_checked": None,
        "message": "Not checked yet"
    }
}
# Configuration settings
config = {
    "interval": 15,  # seconds between messages
    "delay_factor": 1.0,  # multiplier for delay between messages (for API calls)
    "display_stats": True,  # whether to show stats in console
    "save_to_database": True,  # whether to save messages to database
    "debug_mode": False,  # enable additional debug output
    "mac_style": True,  # apply classic Mac styling
    "epa_style": True,  # apply EPA-inspired styling
    "model": "gpt-3.5-turbo"  # default OpenAI model
}

class UIStyleHelper:
    """Helper class for UI styling with elements from classic Mac and black punch card aesthetic."""
    
    COLORS = {
        "bg": "#000000",         # Black background to match punch card
        "fg": "#FFFFFF",         # White text for contrast
        "accent": "#4D90FE",     # Blue accent (classic Mac-inspired)
        "border": "#444444",     # Dark gray border
        "highlight": "#0055AA",  # Darkened highlight for black bg
        "console_bg": "#151515", # Slightly lighter black for console
        "console_text": "#E0E0E0", # Light text for console
        "button_bg": "#333333",   # Dark gray button background
        "button_text": "#FFFFFF", # White text for buttons
        "button_hover": "#555555", # Lighter gray hover state
        "button_press": "#4D90FE"  # Blue for pressed state
    }
    
    FONTS = {
        "system": "'Space Mono', system-ui, -apple-system, 'Helvetica Neue', Helvetica, Arial, sans-serif",
        "monospace": "'Space Mono', 'Menlo', 'Monaco', 'Courier New', monospace",
        "size_normal": "12px",
        "size_small": "11px",
        "size_large": "14px"
    }
    
    @staticmethod
    def apply_base_style(widget):
        """Apply base style to a widget with black background."""
        widget.setStyleSheet(f"""
            background-color: {UIStyleHelper.COLORS['bg']};
            color: {UIStyleHelper.COLORS['fg']};
            border: 1px solid {UIStyleHelper.COLORS['border']};
            border-radius: 2px;
            padding: 6px;
            font-family: {UIStyleHelper.FONTS['system']};
            font-size: {UIStyleHelper.FONTS['size_normal']};
            font-weight: normal;
        """)
    
    @staticmethod
    def apply_button_style(button):
        """Apply Mac-inspired styling to buttons with better visibility."""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {UIStyleHelper.COLORS['button_bg']};
                color: {UIStyleHelper.COLORS['button_text']};
                border: 1px solid {UIStyleHelper.COLORS['border']};
                border-radius: 3px;
                padding: 6px 12px;
                font-family: {UIStyleHelper.FONTS['system']};
                font-weight: normal;
                min-height: 24px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {UIStyleHelper.COLORS['button_hover']};
                border: 1px solid {UIStyleHelper.COLORS['accent']};
            }}
            QPushButton:pressed {{
                background-color: {UIStyleHelper.COLORS['button_press']};
                color: white;
            }}
        """)
    
    @staticmethod
    def apply_console_style(console):
        """Apply dark theme to console for better readability."""
        console.setStyleSheet(f"""
            background-color: {UIStyleHelper.COLORS['console_bg']};
            color: {UIStyleHelper.COLORS['console_text']};
            border: 1px solid {UIStyleHelper.COLORS['border']};
            border-radius: 3px;
            padding: 8px;
            font-family: {UIStyleHelper.FONTS['monospace']};
            font-size: {UIStyleHelper.FONTS['size_normal']};
            font-weight: normal;
        """)
    
    @staticmethod
    def apply_settings_dialog_style(dialog):
        """Apply Mac-inspired styling to settings dialog with black background."""
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {UIStyleHelper.COLORS['bg']};
                color: {UIStyleHelper.COLORS['fg']};
                font-family: {UIStyleHelper.FONTS['system']};
                font-weight: normal;
            }}
            QGroupBox {{
                font-weight: normal;
                border: 1px solid {UIStyleHelper.COLORS['border']};
                border-radius: 3px;
                margin-top: 1em;
                padding-top: 10px;
                background-color: {UIStyleHelper.COLORS['bg']};
                color: {UIStyleHelper.COLORS['fg']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
                background-color: {UIStyleHelper.COLORS['bg']};
                color: {UIStyleHelper.COLORS['fg']};
                font-weight: normal;
            }}
            QLabel {{
                font-family: {UIStyleHelper.FONTS['system']};
                background-color: transparent;
                border: none;
                color: {UIStyleHelper.COLORS['fg']};
                font-weight: normal;
            }}
            QSpinBox {{
                border: 1px solid {UIStyleHelper.COLORS['border']};
                border-radius: 3px;
                padding: 2px;
                background-color: {UIStyleHelper.COLORS['console_bg']};
                color: {UIStyleHelper.COLORS['fg']};
                min-height: 20px;
                font-weight: normal;
            }}
            QCheckBox {{
                font-family: {UIStyleHelper.FONTS['system']};
                background-color: transparent;
                spacing: 5px;
                color: {UIStyleHelper.COLORS['fg']};
                font-weight: normal;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
            }}
            QRadioButton {{
                font-family: {UIStyleHelper.FONTS['system']};
                background-color: transparent;
                spacing: 5px;
                color: {UIStyleHelper.COLORS['fg']};
                font-weight: normal;
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
            }}
        """)
    
    @staticmethod
    def apply_heading_style(label):
        """Apply Mac-inspired heading style."""
        label.setStyleSheet(f"""
            font-family: {UIStyleHelper.FONTS['system']};
            font-weight: normal;
            font-size: {UIStyleHelper.FONTS['size_large']};
            color: {UIStyleHelper.COLORS['accent']};
            background-color: transparent;
            border: none;
            padding-bottom: 4px;
        """)

    @staticmethod
    def apply_global_style(app):
        """Apply global application styling with black background."""
        app.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {UIStyleHelper.COLORS['bg']};
                color: {UIStyleHelper.COLORS['fg']};
                font-weight: normal;
            }}
            QLabel {{
                background-color: transparent;
                color: {UIStyleHelper.COLORS['fg']};
                font-family: {UIStyleHelper.FONTS['system']};
                border: none;
                font-weight: normal;
            }}
            QGroupBox {{
                background-color: {UIStyleHelper.COLORS['bg']};
                border: 1px solid {UIStyleHelper.COLORS['border']};
                border-radius: 3px;
                margin-top: 1em;
                font-weight: normal;
                color: {UIStyleHelper.COLORS['fg']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
                background-color: {UIStyleHelper.COLORS['bg']};
                color: {UIStyleHelper.COLORS['fg']};
                font-weight: normal;
            }}
            QMenuBar {{
                background-color: {UIStyleHelper.COLORS['button_bg']};
                color: {UIStyleHelper.COLORS['fg']};
                border-bottom: 1px solid {UIStyleHelper.COLORS['border']};
                font-weight: normal;
            }}
            QMenuBar::item {{
                background: transparent;
                padding: 4px 8px;
                font-weight: normal;
            }}
            QMenuBar::item:selected {{
                background-color: {UIStyleHelper.COLORS['accent']};
            }}
            QMenu {{
                background-color: {UIStyleHelper.COLORS['bg']};
                color: {UIStyleHelper.COLORS['fg']};
                border: 1px solid {UIStyleHelper.COLORS['border']};
                font-weight: normal;
            }}
            QMenu::item:selected {{
                background-color: {UIStyleHelper.COLORS['accent']};
            }}
            QLineEdit, QTextEdit, QPlainTextEdit {{
                background-color: {UIStyleHelper.COLORS['console_bg']};
                color: {UIStyleHelper.COLORS['fg']};
                border: 1px solid {UIStyleHelper.COLORS['border']};
                border-radius: 3px;
                padding: 2px;
                font-family: {UIStyleHelper.FONTS['monospace']};
                font-weight: normal;
            }}
        """)

    @staticmethod
    def create_menu_bar(window):
        """Create a menu bar for the application"""
        from PyQt6.QtWidgets import QMenuBar, QMenu
        from PyQt6.QtCore import QSize
        from PyQt6.QtGui import QAction
        
        # Create menu bar
        menu_bar = QMenuBar(window)
        menu_bar.setStyleSheet(f"""
        QMenuBar {{
            background-color: #2E2E2E;
            color: white;
            padding: 4px;
            border-bottom: 1px solid #444;
            min-height: 28px;
        }}
        QMenuBar::item {{
            background-color: transparent;
            padding: 6px 12px;
            border-radius: 4px;
            margin-right: 4px;
        }}
        QMenuBar::item:selected {{
            background-color: #3E3E3E;
        }}
        QMenuBar::item:pressed {{
            background-color: #444;
        }}
        """)
        
        # Create Apple menu (macOS style)
        apple_menu = QMenu("🍎", window)
        apple_menu.setStyleSheet("""
        QMenu {
            background-color: #333;
            color: white;
            border: 1px solid #444;
            padding: 5px;
        }
        QMenu::item {
            padding: 6px 25px 6px 20px;
            border-radius: 3px;
        }
        QMenu::item:selected {
            background-color: #444;
        }
        QMenu::separator {
            height: 1px;
            background-color: #444;
            margin: 5px 0px;
        }
        """)
        
        # Add About action
        about_action = QAction("About Punch Card", window)
        about_action.triggered.connect(lambda: show_about_dialog(window))
        apple_menu.addAction(about_action)
        
        # Add separator
        apple_menu.addSeparator()
        
        # Add Settings action
        settings_action = QAction("Settings", window)
        settings_action.setShortcut("S")
        settings_action.triggered.connect(lambda: show_settings_dialog(window))
        apple_menu.addAction(settings_action)
        
        # Add Quit action
        quit_action = QAction("Quit", window)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(lambda: QApplication.instance().quit())
        apple_menu.addAction(quit_action)
        
        # Add Apple menu to menu bar
        menu_bar.addMenu(apple_menu)
        
        # Create File menu
        file_menu = QMenu("File", window)
        file_menu.setStyleSheet(apple_menu.styleSheet())  # Use same style
        
        # Add Save Message action
        save_action = QAction("Save Current Message", window)
        save_action.triggered.connect(lambda: save_current_message(window))
        file_menu.addAction(save_action)
        
        # Add Load Message action
        load_action = QAction("Load Message", window)
        load_action.triggered.connect(lambda: load_message(window))
        file_menu.addAction(load_action)
        
        # Add File menu to menu bar
        menu_bar.addMenu(file_menu)
        
        # Create Source menu
        source_menu = QMenu("Message Source", window)
        source_menu.setStyleSheet(apple_menu.styleSheet())  # Use same style
        
        # Add Local Source action
        local_action = QAction("Local Messages", window)
        local_action.triggered.connect(lambda: set_message_source("local"))
        source_menu.addAction(local_action)
        
        # Add OpenAI Source action
        openai_action = QAction("OpenAI", window)
        openai_action.triggered.connect(lambda: set_message_source("openai"))
        source_menu.addAction(openai_action)
        
        # Add Source menu to menu bar
        menu_bar.addMenu(source_menu)
        
        # Create View menu
        view_menu = QMenu("View", window)
        view_menu.setStyleSheet(apple_menu.styleSheet())  # Use same style
        
        # Add Toggle Console action
        console_action = QAction("Toggle API Console", window)
        console_action.setShortcut("C")
        console_action.triggered.connect(lambda: toggle_api_console(window))
        view_menu.addAction(console_action)
        
        # Add View menu to menu bar
        menu_bar.addMenu(view_menu)
        
        # Create Help menu
        help_menu = QMenu("Help", window)
        help_menu.setStyleSheet(apple_menu.styleSheet())  # Use same style
        
        # Add About action to Help menu
        about_help_action = QAction("About Punch Card", window)
        about_help_action.triggered.connect(lambda: show_about_dialog(window))
        help_menu.addAction(about_help_action)
        
        # Add separator
        help_menu.addSeparator()
        
        # Add Keyboard Shortcuts action
        shortcuts_action = QAction("Keyboard Shortcuts", window)
        shortcuts_action.triggered.connect(lambda: show_shortcuts_dialog(window))
        help_menu.addAction(shortcuts_action)
        
        # Add Check API Status action
        api_status_action = QAction("Check API Status", window)
        api_status_action.triggered.connect(lambda: check_and_display_api_status(window))
        help_menu.addAction(api_status_action)
        
        # Add Help menu to menu bar
        menu_bar.addMenu(help_menu)
        
        # Return the menu bar
        return menu_bar

# Replace MacStyleHelper with UIStyleHelper throughout the code
# For compatibility, create alias
MacStyleHelper = UIStyleHelper

def load_settings(settings_file="punch_card_settings.json"):
    """Load settings from a JSON file."""
    global message_source, config, openai_usage
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
            # If message_source is in the settings, use it
            if 'message_source' in settings:
                message_source = settings['message_source']
            
            # Load config settings if available
            if 'config' in settings:
                # Clean up any legacy or invalid parameters
                if 'proxies' in settings['config']:
                    debug_log("Removing invalid 'proxies' parameter from loaded settings", "warning", False)
                    del settings['config']['proxies']
                
                for key, value in settings['config'].items():
                    if key in config:
                        config[key] = value
                
            # Load OpenAI usage if available
            if 'openai_usage' in settings:
                openai_usage = settings['openai_usage']
                
            debug_log(f"Settings loaded from {settings_file}", "system", False)
            return settings
    except Exception as e:
        debug_log(f"Error loading settings: {e}", "error", False)
        return {}

def save_settings(settings_file="punch_card_settings.json"):
    """Save settings to a JSON file."""
    global message_source, config, openai_usage
    try:
        # Try to load existing settings first
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
        except:
            settings = {}
        
        # Clean up any legacy or invalid configuration parameters
        if 'proxies' in config:
            debug_log("Removing invalid 'proxies' parameter from configuration", "warning", False)
            del config['proxies']
        
        # Update with our settings
        settings['message_source'] = message_source
        settings['config'] = config
        settings['openai_usage'] = openai_usage
        
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
            
        debug_log(f"Settings saved to {settings_file}", "system", False)
        return True
    except Exception as e:
        debug_log(f"Error saving settings: {e}", "error", False)
        return False

def save_message_to_database(message, source="local"):
    """Save a message to the database with source information."""
    global db_connection
    
    if not db_connection:
        update_api_console("⚠️ Database not initialized - message not saved", "warning")
        return False
    
    try:
        cursor = db_connection.cursor()
        
        # Get current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Insert the message with source information
        cursor.execute(
            "INSERT INTO messages (message, timestamp, source) VALUES (?, ?, ?)",
            (message, timestamp, source)
        )
        
        # Commit the changes
        db_connection.commit()
        
        # Log success
        update_api_console(f"✅ Message saved to database (source: {source})", "system")
        return True
        
    except Exception as e:
        # Log error
        update_api_console(f"❌ Error saving to database: {str(e)[:100]}", "error")
        return False

def update_stats(source):
    """Update message statistics."""
    global message_stats, config
    
    # Ensure the source exists in the stats
    if source not in message_stats:
        message_stats[source] = 0
    
    # Update counts
    message_stats["total"] += 1
    message_stats[source] += 1
    
    # Update timestamp
    message_stats["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Only print if stats display is enabled
    if config["display_stats"]:
        print(f"✅ Stats updated: Total={message_stats['total']}, {source.capitalize()}={message_stats[source]}")

def check_openai_status():
    """Check OpenAI API status and update global status tracking."""
    global service_status
    
    url = "https://status.openai.com/api/v2/status.json"
    service_status["openai"]["last_checked"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Try to make a simple API request
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        status_indicator = data.get("status", {}).get("indicator", "unknown")
        status_description = data.get("status", {}).get("description", "Unknown status")
        
        if status_indicator == "none":
            service_status["openai"]["status"] = "operational"
            service_status["openai"]["message"] = "All systems operational"
        else:
            service_status["openai"]["status"] = status_indicator
            service_status["openai"]["message"] = status_description
            
        update_api_console(f"OpenAI Status: {status_indicator} - {status_description}")
        return True
    except requests.exceptions.RequestException as e:
        service_status["openai"]["status"] = "error"
        service_status["openai"]["message"] = f"Error checking status: {str(e)[:50]}"
        update_api_console(f"OpenAI Status Check Error: {str(e)[:50]}")
        return False

def check_flyio_status():
    """Check fly.io status and update global status tracking."""
    global service_status
    
    url = "https://status.fly.io/api/v2/status.json"
    service_status["flyio"]["last_checked"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Try to make a simple API request
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        status_indicator = data.get("status", {}).get("indicator", "unknown")
        status_description = data.get("status", {}).get("description", "Unknown status")
        
        service_status["flyio"]["status"] = status_indicator
        service_status["flyio"]["message"] = status_description
            
        update_api_console(f"Fly.io Status: {status_indicator} - {status_description}")
        return True
    except requests.exceptions.RequestException as e:
        service_status["flyio"]["status"] = "error"
        service_status["flyio"]["message"] = f"Error checking status: {str(e)[:50]}"
        update_api_console(f"Fly.io Status Check Error: {str(e)[:50]}")
        return False

def get_service_status_text():
    """Get formatted text of service statuses."""
    openai_status = service_status.get("openai", {})
    flyio_status = service_status.get("flyio", {})
    
    text = "=== Service Status ===\n"
    text += f"OpenAI: {openai_status.get('status', 'Unknown')} - {openai_status.get('message', 'No message')}\n"
    text += f"Last checked: {openai_status.get('last_checked', 'Never')}\n\n"
    
    text += f"Fly.io: {flyio_status.get('status', 'Unknown')} - {flyio_status.get('message', 'No message')}\n"
    text += f"Last checked: {flyio_status.get('last_checked', 'Never')}\n"
    
    return text

class KeyPressFilter(QObject):
    """Filter to capture key events for application-wide keyboard shortcuts."""
    
    def __init__(self, parent=None):
        """Initialize the key press filter."""
        super().__init__(parent)
        print("✅ KeyPressFilter initialized")
        
    def eventFilter(self, obj, event):
        """Filter key events to handle keyboard shortcuts."""
        global display
        
        # Only process key press events
        if event.type() == QEvent.Type.KeyPress:
            # Get the key
            key = event.key()
            
            # 'C' key - Show API Console
            if key == Qt.Key.Key_C:
                print("C key pressed: Show API console")
                
                # Make sure console is visible and update it
                ensure_console_visibility()
                update_api_console("Console activated via keyboard shortcut", "system")
                
                # Return True to indicate we've handled this event
                return True
                
            # 'S' key - Show settings dialog
            elif key == Qt.Key.Key_S:
                print("S key pressed: Show settings dialog")
                update_api_console("Opening settings dialog", "system")
                
                # Make sure display is initialized
                if display:
                    # Show settings dialog
                    show_settings_dialog(display)
                else:
                    update_api_console("❌ Cannot show settings - display not initialized", "error")
                
                # Return True to indicate we've handled this event
                return True
                
            # Add other key shortcuts as needed
                
        # For all other events, let the default handler take care of it
        return super().eventFilter(obj, event)

def update_api_console(message, source="system"):
    """Update the API console with a message, ensuring visibility."""
    global display, config
    
    timestamp = time.strftime("%H:%M:%S")
    formatted_terminal_msg = f"[{timestamp}] [{source}] {message}"
    
    # Always print to terminal in debug mode
    if config.get("debug_mode", False):
        print(formatted_terminal_msg)
    
    # Check if display is initialized
    if not display:
        # Print to terminal only if not in debug mode and GUI console is not available
        if not config.get("debug_mode", False):
            print(formatted_terminal_msg)
        return False
        
    # Ensure API console exists
    if not hasattr(display, 'api_console') or display.api_console is None:
        # Print to terminal only if not in debug mode and GUI console is not available
        if not config.get("debug_mode", False):
            print(formatted_terminal_msg)
        try:
            add_api_console()
        except Exception as e:
            print(f"[ERROR] Failed to create API console: {str(e)}")
            return False
    
    # Check again if API console exists after potentially creating it
    if hasattr(display, 'api_console') and display.api_console and hasattr(display.api_console, 'append'):
        try:
            # Format the message with timestamp and make it visible
            formatted_msg = f"<span style='color:#888888;'>[{timestamp}]</span> "
            
            # Color-code based on source
            if source == "error" or "error" in message.lower() or "❌" in message:
                formatted_msg += f"<span style='color:#ff5555;'>{message}</span>"
            elif source == "system":
                formatted_msg += f"<span style='color:#55aa55;'>{message}</span>"
            elif source == "openai":
                formatted_msg += f"<span style='color:#5555ff;'>{message}</span>"
            else:
                formatted_msg += message
                
            # Append the message to the API console
            display.api_console.append(formatted_msg)
            
            # Ensure the last line is visible by scrolling to the bottom
            if hasattr(display.api_console, 'verticalScrollBar'):
                scrollbar = display.api_console.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
            
            # Force the console to be visible if we have important messages
            if "error" in message.lower() or "❌" in message:
                ensure_console_visibility()
                
            return True
        except Exception as e:
            # Print to terminal if GUI console update fails
            print(formatted_terminal_msg)
            print(f"[ERROR] Failed to update API console: {str(e)}")
            return False
    
    # Print to terminal if GUI console not available
    if not config.get("debug_mode", False):
        print(formatted_terminal_msg)
    
    return False

def debug_log(message, source="debug", use_api_console=True):
    """Unified logging function that handles both terminal and API console."""
    prefix = ""
    if message.startswith("✅"):
        prefix = ""  # Already has a prefix
    elif message.startswith("⚠️"):
        prefix = ""  # Already has a prefix
    elif message.startswith("❌"):
        prefix = ""  # Already has a prefix
    elif source == "debug":
        prefix = "✅ "
    elif source == "warning":
        prefix = "⚠️ "
    elif source == "error":
        prefix = "❌ "
    
    full_message = f"{prefix}{message}"
    
    # In debug mode or early in initialization, print directly
    if not use_api_console or not 'display' in globals() or display is None:
        print(full_message)
        return
        
    # Otherwise use the API console
    update_api_console(full_message, source)

def ensure_console_visibility():
    """Make sure the API console is visible."""
    global display
    
    if not display:
        print("[WARNING] Cannot ensure console visibility - display not initialized")
        return False
        
    # Create API console if it doesn't exist
    if not hasattr(display, 'api_console') or display.api_console is None:
        add_api_console()
        
    # Make sure the window is visible
    if hasattr(display, 'api_console_window') and display.api_console_window:
        try:
            # Show the console window
            display.api_console_window.show()
            display.api_console_window.raise_()
            
            # Bring the main window to front
            if hasattr(display, 'activate'):
                display.activate()
            elif hasattr(display, 'raise_'):
                display.raise_()
                
            return True
        except Exception as e:
            print(f"[ERROR] Failed to ensure console visibility: {str(e)}")
            return False
    
    return False

def setup_openai_client():
    """Set up the OpenAI client with improved error handling and monkey patching."""
    global openai_client, config
    
    print("\n====== setup_openai_client function started ======")
    print(f"🐒 Current config keys: {list(config.keys())}")
    debug_log("Setting up monkey-patched OpenAI client...", "system")
    
    # Check if we already have a client
    if openai_client:
        print("🐒 OpenAI client already initialized, returning existing client")
        debug_log("OpenAI client already initialized", "system")
        print("====== setup_openai_client function completed ======\n")
        return True
    
    # Check if the OpenAI module is installed
    try:
        print("🐒 Importing OpenAI and APIError...")
        from openai import OpenAI, APIError
        print("✅ Successfully imported OpenAI module")
        
    except ImportError as ie:
        print(f"❌ Failed to import OpenAI module: {ie}")
        debug_log("❌ OpenAI module not installed. Run 'pip install openai' to install it.", "error")
        print("====== setup_openai_client function failed ======\n")
        return False
    
    # Get API key from config
    api_key = config.get("openai_api_key", "")
    print(f"🐒 API key from config: {'<present>' if api_key and len(api_key) > 10 else '<missing or invalid>'}")
    
    # Try to load from secrets if not in config
    if not api_key or len(api_key.strip()) < 10:
        print("🐒 API key missing or invalid, attempting to load from secrets file...")
        try:
            secrets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "secrets", "api_keys.json")
            print(f"Looking for secrets file at: {secrets_path}")
            if os.path.exists(secrets_path):
                print("Secrets file found, loading...")
                with open(secrets_path, 'r') as f:
                    secrets = json.load(f)
                    if "openai" in secrets and "api_key" in secrets["openai"]:
                        api_key = secrets["openai"]["api_key"]
                        print("Found API key in secrets['openai']['api_key']")
                    elif "openai_api_key" in secrets:
                        api_key = secrets["openai_api_key"]
                        print("Found API key in secrets['openai_api_key']")
                    
                    # Update config with the key from secrets
                    if api_key and len(api_key.strip()) >= 10:
                        config["openai_api_key"] = api_key
                        print("Updated config with API key from secrets")
                        debug_log("ℹ️ Loaded API key from secrets file", "system")
            else:
                print(f"Secrets file not found at {secrets_path}")
        except Exception as e:
            print(f"Error loading API key from secrets: {e}")
            debug_log(f"⚠️ Could not load API key from secrets: {str(e)}", "warning")
    
    # Check if API key is valid
    if not api_key or len(api_key.strip()) < 10:
        print("API key still missing or invalid after attempting to load from secrets")
        debug_log("❌ Invalid API key. Please set a valid API key in settings.", "error")
        debug_log("To set an API key, press 'S' to open settings, go to the OpenAI tab, enter your key and click 'Save API Key'", "system")
        print("====== setup_openai_client function failed ======\n")
        return False
    
    try:
        # Initialize client with our monkey-patched wrapper function
        debug_log("🐒 Initializing monkey-patched OpenAI client with your API key...", "system")
        print("🐒 Creating OpenAI client using monkey-patched wrapper function...")
        
        # Clean the config of any problematic parameters
        problematic_params = ['proxies', 'proxy', 'organization', 'org_id']
        for param in problematic_params:
            if param in config:
                print(f"🐒 Removing '{param}' from config before client creation...")
                del config[param]
                # Save the cleaned config
                save_settings()
                print(f"Config saved without '{param}' parameter")
        
        # Create with minimal parameters using our wrapper
        print("🐒 Using create_clean_openai_client wrapper function...")
        openai_client = create_clean_openai_client(api_key=api_key)
        
        if not openai_client:
            print("❌ Failed to create OpenAI client using wrapper")
            debug_log("❌ Failed to create OpenAI client", "error")
            print("====== setup_openai_client function failed ======\n")
            return False
            
        # Test API key by listing models (lightweight call)
        try:
            print("🐒 Testing API key by calling models.list()...")
            debug_log("Testing API key validity by listing available models...", "system")
            # Call list models with a small limit
            models = openai_client.models.list(limit=5)
            print(f"✅ Successfully listed models: found {len(models.data)} models")
            
            # If we get here, the API key is valid
            debug_log(f"✅ OpenAI API key valid - found {len(models.data)} models", "system")
            
            # Set default model if not set
            if not config.get("model"):
                print("No default model set, selecting one...")
                # Find an appropriate model from the available models
                available_models = [model.id for model in models.data]
                preferred_models = ["gpt-4", "gpt-3.5-turbo"]
                
                for model in preferred_models:
                    for available in available_models:
                        if model in available:
                            config["model"] = available
                            print(f"Set default model to {config['model']}")
                            debug_log(f"Set default model to {config['model']}", "system")
                            break
                    if config.get("model"):
                        break
                
                # If no preferred model found, use the first available
                if not config.get("model") and len(models.data) > 0:
                    config["model"] = models.data[0].id
                    print(f"Set default model to first available: {config['model']}")
                    debug_log(f"Set default model to {config['model']}", "system")
                elif not config.get("model"):
                    config["model"] = "gpt-3.5-turbo"
                    print(f"Set default model to fallback: {config['model']}")
                    debug_log(f"Set default model to {config['model']} (fallback)", "system")
                
            # Save the settings with the API key and model
            print("Saving settings with updated model...")
            save_settings()
            print("Settings saved successfully")
            print("====== setup_openai_client function completed successfully ======\n")
            return True
            
        except APIError as e:
            # API errors often relate to authentication
            error_message = str(e)[:200]
            print(f"❌ API Error: {error_message}")
            debug_log(f"❌ OpenAI API Error: {error_message}", "error")
            
            if "API key" in error_message and "invalid" in error_message.lower():
                print("❌ Invalid API key error detected")
                debug_log("The API key you provided appears to be invalid. Please check the key and try again.", "error")
            elif "exceeded your current quota" in error_message.lower():
                print("❌ Quota exceeded error detected")
                debug_log("Your OpenAI account has exceeded its quota. Please check your billing information.", "error")
            elif "rate limit" in error_message.lower():
                print("⚠️ Rate limit error detected")
                debug_log("You've hit a rate limit. Please wait a moment before trying again.", "warning")
            
            openai_client = None
            print("====== setup_openai_client function failed ======\n")
            return False
            
    except Exception as e:
        # Generic error handling
        error_message = str(e)[:200]
        print(f"❌ Unexpected error: {error_message}")
        debug_log(f"❌ Error setting up OpenAI client: {error_message}", "error")
        openai_client = None
        print("====== setup_openai_client function failed ======\n")
        return False

def generate_openai_message():
    """Generate message using OpenAI API with enhanced error handling and feedback."""
    global openai_client, config, display, openai_usage
    
    # Initialize client if needed
    if not openai_client:
        update_api_console("OpenAI client not initialized. Attempting setup...", "openai")
        if not setup_openai_client():
            error_msg = "ERROR: COULD NOT INITIALIZE OPENAI CLIENT"
            update_api_console(f"❌ {error_msg}", "error")
            
            # Force display on punch card - ensure this gets shown
            if display and hasattr(display, 'punch_card'):
                try:
                    # Try to directly update the punch card with an error message
                    if hasattr(display, 'display_message'):
                        # This should update the display
                        display.display_message(error_msg)
                except Exception as e:
                    update_api_console(f"Error updating punch card directly: {str(e)[:100]}", "error")
            
            return error_msg
    
    # Select a model
    model = config.get("model", "gpt-3.5-turbo")
    
    # Select a prompt
    prompts = [
        "Create a short tech message about IBM punch cards",
        "Write a brief statement about vintage computing",
        "Generate a nostalgic message about early computers",
        "Write a haiku about AI and computing",
        "Create a futuristic message about computing",
        "Generate a punchy tech slogan about data processing",
        "Write a brief message about the history of computing",
        "Create a short message about the evolution of programming languages"
    ]
    
    prompt = random.choice(prompts)
    update_api_console(f"Using OpenAI model: {model}", "openai")
    update_api_console(f"Prompt: '{prompt}'", "openai")
    
    try:
        # Call the OpenAI API
        start_time = time.time()
        update_api_console("Waiting for OpenAI response...", "openai")
        
        # Use system message to ensure short, uppercase responses
        completion = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You generate short messages for an IBM punch card display. Keep your response under 70 characters. Format in UPPERCASE only. Use vintage computing themes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Add some randomness but not too much
            max_tokens=50     # Limit token usage
        )
        
        # Calculate response time
        end_time = time.time()
        api_time = end_time - start_time
        
        # Extract and log token usage
        usage = completion.usage.model_dump() if hasattr(completion, 'usage') else {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)
        total_tokens = usage.get('total_tokens', 0)
        
        # Calculate cost
        model_base = model.split(':')[0]  # Handle model versions like gpt-3.5-turbo:0613
        pricing = openai_pricing.get(model_base, {"input": 0.002, "output": 0.002})  # Default pricing if model not found
        prompt_cost = (prompt_tokens / 1000) * pricing["input"]
        completion_cost = (completion_tokens / 1000) * pricing["output"]
        total_cost = prompt_cost + completion_cost
        
        # Update usage statistics
        openai_usage["total_calls"] += 1
        openai_usage["prompt_tokens"] += prompt_tokens
        openai_usage["completion_tokens"] += completion_tokens
        openai_usage["total_tokens"] += total_tokens
        openai_usage["estimated_cost"] += total_cost
        openai_usage["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Update model-specific costs
        if model_base not in openai_usage["cost_per_model"]:
            openai_usage["cost_per_model"][model_base] = 0.0
        openai_usage["cost_per_model"][model_base] += total_cost
        
        # Add to usage history (keep last 100 entries)
        openai_usage["usage_history"].append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "cost": total_cost,
            "response_time": api_time
        })
        
        # Limit history size
        if len(openai_usage["usage_history"]) > 100:
            openai_usage["usage_history"] = openai_usage["usage_history"][-100:]
        
        # Log tokens and cost
        update_api_console(f"✅ Response received in {api_time:.2f} seconds", "openai")
        update_api_console(f"Tokens: {prompt_tokens} prompt + {completion_tokens} completion = {total_tokens} total", "openai")
        update_api_console(f"Estimated cost: ${total_cost:.6f} (Total: ${openai_usage['estimated_cost']:.4f})", "openai")
        
        # Get the response
        response = completion.choices[0].message.content.strip().upper()
        
        # Ensure it's not too long for the punch card (80 columns)
        if len(response) > 70:
            response = response[:67] + "..."
            
        update_api_console(f"Message generated: {response}", "openai")
        
        # Save usage to config for persistence
        config["openai_usage"] = openai_usage
        save_settings()
        
        return response
        
    except Exception as e:
        error_msg = str(e)
        print(f"⚠️ Error calling OpenAI API: {e}")
        update_api_console(f"❌ OpenAI Error: {error_msg[:150]}", "error")
        
        error_response = f"ERROR: {error_msg[:60]}"
        
        # Force display on punch card - ensure this gets shown
        if display and hasattr(display, 'punch_card'):
            try:
                # Try to directly update the punch card with an error message
                if hasattr(display, 'display_message'):
                    # This should update the display
                    display.display_message(error_response)
            except Exception as display_err:
                update_api_console(f"Error updating punch card directly: {str(display_err)[:100]}", "error")
        
        return error_response

def get_database_message():
    """Get a random message from the database."""
    global db_connection
    
    if not db_connection:
        update_api_console("⚠️ Database not initialized - cannot retrieve message", "warning")
        return "ERROR: DATABASE NOT INITIALIZED"
    
    try:
        cursor = db_connection.cursor()
        
        # Check if we have any messages
        cursor.execute("SELECT COUNT(*) FROM messages")
        count = cursor.fetchone()[0]
        
        if count == 0:
            update_api_console("⚠️ No messages in database", "warning")
            return "NO MESSAGES IN DATABASE"
        
        # Get a random message from the database
        cursor.execute("""
            SELECT message FROM messages 
            ORDER BY RANDOM() 
            LIMIT 1
        """)
        
        message = cursor.fetchone()
        
        if message and message[0]:
            update_api_console(f"✅ Retrieved message from database", "system")
            return message[0]
        else:
            update_api_console("⚠️ Failed to retrieve message from database", "warning")
            return "ERROR: COULD NOT RETRIEVE MESSAGE"
            
    except Exception as e:
        update_api_console(f"❌ Error retrieving from database: {str(e)[:100]}", "error")
        return "ERROR: DATABASE RETRIEVAL FAILED"

def get_message(source=None):
    """Get a message from the specified source."""
    global config
    
    # If source not specified, use the configured source
    if source is None:
        source = config.get("message_source", "local")
        
    update_api_console(f"Getting message from source: {source}", "system")
    
    try:
        # Get message from source
        if source == "openai":
            update_api_console("Using OpenAI API for message generation", "system")
            message = generate_openai_message()
        elif source == "database":
            update_api_console("Retrieving message from database", "system")
            message = get_database_message()
        elif source == "stats":
            update_api_console("Generating statistics message", "system")
            message = get_stats_text()
        else:  # Default is local
            update_api_console("Generating local message", "system")
            message = generate_local_message()
            
        # Make sure we have a valid message
        if not message or not isinstance(message, str) or len(message.strip()) == 0:
            update_api_console("⚠️ Invalid message received, falling back to local generation", "warning")
            message = generate_local_message()
            
        return message
        
    except Exception as e:
        update_api_console(f"❌ Error getting message: {str(e)[:100]}", "error")
        # Fallback to local message
        try:
            return generate_local_message()
        except Exception as fallback_error:
            # Last resort message
            return "ERROR: COULD NOT GENERATE MESSAGE"

def display_next_message():
    """Get and display the next message based on current settings."""
    global display, config
    
    if not display:
        debug_log("Display object not initialized", "error")
        return False
    
    # Get a message based on current source setting
    msg_source = config.get("message_source", "local")
    update_api_console(f"Getting message from source: {msg_source}", "system")
    
    # Get message from appropriate source
    message = get_message(msg_source)
    
    # Format message (ensure uppercase for punch card)
    if message:
        message = message.strip().upper()
        
        # Debug info
        debug_log(f"Displaying message: {message}", "system", True)
        
        # Display the message in multiple ways
        display_success = False
        
        # Method 1: Use display_message method if available
        if hasattr(display, 'display_message'):
            try:
                display.display_message(message)
                display_success = True
                update_api_console(f"✅ Message displayed via display_message(): {message}", "system")
            except Exception as e:
                update_api_console(f"❌ Error in display_message(): {str(e)[:100]}", "error")
        
        # Method 2: Try to update the display via the punch_card object
        # This is the more modern approach with the enhanced UI
        if not display_success and hasattr(display, 'punch_card'):
            try:
                # Try the preferred update_data method
                if hasattr(display.punch_card, 'update_data'):
                    display.punch_card.update_data(message)
                    display_success = True
                    update_api_console(f"✅ Message displayed via punch_card.update_data(): {message}", "system")
                # Fall back to setText
                elif hasattr(display.punch_card, 'setText'):
                    display.punch_card.setText(message)
                    display_success = True
                    update_api_console(f"✅ Message displayed via punch_card.setText(): {message}", "system")
                # Fall back to setPlainText
                elif hasattr(display.punch_card, 'setPlainText'):
                    display.punch_card.setPlainText(message)
                    display_success = True
                    update_api_console(f"✅ Message displayed via punch_card.setPlainText(): {message}", "system")
            except Exception as e:
                update_api_console(f"❌ Error updating punch_card directly: {str(e)[:100]}", "error")
        
        # Last resort: Check if we have display widgets directly
        if not display_success:
            update_api_console("❌ FAILED to display message - no suitable display method found", "error")
            
            # Emergency fallback to any text widget we can find
            for widget_name in ['text_display', 'textEdit', 'textBrowser', 'label']:
                if hasattr(display, widget_name):
                    try:
                        widget = getattr(display, widget_name)
                        if hasattr(widget, 'setText'):
                            widget.setText(message)
                            display_success = True
                            update_api_console(f"✅ Emergency fallback: displayed via {widget_name}.setText()", "system")
                            break
                        elif hasattr(widget, 'setPlainText'):
                            widget.setPlainText(message)
                            display_success = True
                            update_api_console(f"✅ Emergency fallback: displayed via {widget_name}.setPlainText()", "system")
                            break
                    except Exception as e:
                        update_api_console(f"❌ Emergency fallback failed for {widget_name}: {str(e)[:100]}", "error")
        
        # Save the message to the database if successful
        if display_success:
            save_message_to_database(message, msg_source)
        
        return display_success
    else:
        update_api_console("⚠️ No message to display - received empty message", "warning")
        return False

def get_stats_text():
    """Get statistics as formatted text."""
    global message_stats
    
    stats_text = f"Total: {message_stats['total']} | "
    stats_text += f"Local: {message_stats.get('local', 0)} | "
    stats_text += f"OpenAI: {message_stats.get('openai', 0)} | "
    stats_text += f"DB: {message_stats.get('database', 0)}"
    
    if message_stats["last_updated"]:
        stats_text += f"\nLast Update: {message_stats['last_updated']}"
    
    if message_stats["last_message"]:
        stats_text += f"\nLast Message: {message_stats['last_message'][:40]}..."
        if message_stats["last_source"]:
            stats_text += f" ({message_stats['last_source']})"
    
    return stats_text

class SettingsDialog(QDialog):
    """
    Comprehensive Settings Dialog - THE SINGLE SOURCE OF TRUTH FOR ALL SETTINGS
    
    This is the only settings dialog in the application and should be used for all
    settings management. Any other settings mechanisms should be removed or redirected
    to use this dialog.
    """
    def __init__(self, parent=None):
        """Initialize the settings dialog with multiple tabs for different settings categories."""
        super().__init__(parent)
        self.parent_display = parent
        
        # Set window title
        self.setWindowTitle("Punch Card Settings")
        
        # Increase size for better visibility
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create the tab widgets first
        self.general_tab = QWidget()
        self.openai_tab = QWidget()
        self.stats_tab = QWidget()
        
        # Setup tabs
        self._setup_general_tab()  # ⚙️ General tab
        self._setup_openai_tab()   # 🤖 OpenAI API tab
        self._setup_stats_tab()    # 📊 Statistics tab
        
        # Set General tab as default
        self.tab_widget.setCurrentIndex(0)  # General tab
        
        # Add OK/Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        # Load initial values from settings
        self.load_from_settings()
    
    def _setup_general_tab(self):
        """Set up the general settings tab."""
        # Add the tab to the tab widget
        self.tab_widget.addTab(self.general_tab, "⚙️ General")
        
        layout = QVBoxLayout()
        self.general_tab.setLayout(layout)
        
        # Message source group
        source_group = QGroupBox("Message Source")
        source_layout = QVBoxLayout()
        source_group.setLayout(source_layout)
        
        # Radio buttons for message source
        self.local_radio = QRadioButton("Local Generation")
        self.local_radio.setToolTip("Generate messages locally using patterns and templates")
        self.openai_radio = QRadioButton("OpenAI API")
        self.openai_radio.setToolTip("Generate messages using OpenAI's API (requires API key)")
        self.database_radio = QRadioButton("Message Database")
        self.database_radio.setToolTip("Display stored messages from database")
        
        source_layout.addWidget(self.local_radio)
        source_layout.addWidget(self.openai_radio)
        source_layout.addWidget(self.database_radio)
        
        layout.addWidget(source_group)
        
        # Display settings group
        display_group = QGroupBox("Display Settings")
        display_layout = QFormLayout()
        display_group.setLayout(display_layout)
        
        # Interval setting
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 600)  # 1 second to 10 minutes
        self.interval_spin.setSuffix(" seconds")
        self.interval_spin.setToolTip("Time between messages")
        display_layout.addRow("Message Interval:", self.interval_spin)
        
        # Delay factor setting
        self.delay_factor_spin = QDoubleSpinBox()
        self.delay_factor_spin.setRange(0.1, 5.0)
        self.delay_factor_spin.setSingleStep(0.1)
        self.delay_factor_spin.setDecimals(1)
        self.delay_factor_spin.setToolTip("Factor to adjust message timing based on length")
        display_layout.addRow("Delay Factor:", self.delay_factor_spin)
        
        layout.addWidget(display_group)
        
        # Other settings group
        other_group = QGroupBox("Other Settings")
        other_layout = QVBoxLayout()
        other_group.setLayout(other_layout)
        
        # Display statistics option
        self.display_stats_check = QCheckBox("Display Statistics")
        self.display_stats_check.setToolTip("Display statistics about message generation")
        other_layout.addWidget(self.display_stats_check)
        
        # Save to database option
        self.save_db_check = QCheckBox("Save Messages to Database")
        self.save_db_check.setToolTip("Save generated messages to the database")
        other_layout.addWidget(self.save_db_check)
        
        # Debug mode option
        self.debug_check = QCheckBox("Debug Mode")
        self.debug_check.setToolTip("Enable debug mode with additional logging")
        other_layout.addWidget(self.debug_check)
        
        layout.addWidget(other_group)
        
        # Add stretch to push everything to the top
        layout.addStretch()
    
    def _setup_openai_tab(self):
        """Set up the OpenAI API tab."""
        # Add tab to widget
        self.tab_widget.addTab(self.openai_tab, "🤖 OpenAI API")
        
        tab_layout = QVBoxLayout(self.openai_tab)
        
        # API Key section with toggle visibility button
        api_group = QGroupBox("API Configuration")
        form_layout = QFormLayout()
        api_group.setLayout(form_layout)
        
        api_key_layout = QHBoxLayout()
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_edit.setPlaceholderText("Enter your OpenAI API key here")
        
        toggle_button = QPushButton("👁️")
        toggle_button.setFixedWidth(30)
        toggle_button.setToolTip("Show/Hide API Key")
        toggle_button.clicked.connect(self.toggle_key_visibility)
        
        api_key_layout.addWidget(self.api_key_edit)
        api_key_layout.addWidget(toggle_button)
        
        form_layout.addRow("API Key:", api_key_layout)
        
        # API Key verification status
        self.api_key_status = QLabel("API key status: Not verified")
        self.api_key_status.setStyleSheet("color: #888888;")
        form_layout.addRow("", self.api_key_status)
        
        # API Key buttons: Verify and Save
        api_button_layout = QHBoxLayout()
        
        verify_button = QPushButton("Verify API Key")
        verify_button.setMinimumHeight(32)
        verify_button.clicked.connect(self.update_api_key_status)
        api_button_layout.addWidget(verify_button)
        
        save_key_button = QPushButton("Save API Key")
        save_key_button.setMinimumHeight(32)
        save_key_button.clicked.connect(self.update_api_key)
        api_button_layout.addWidget(save_key_button)
        
        form_layout.addRow("", api_button_layout)
        
        tab_layout.addWidget(api_group)
        
        # Add separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        tab_layout.addWidget(separator1)
        
        # Model selection group
        model_group = QGroupBox("Model Selection")
        model_layout = QVBoxLayout()
        model_group.setLayout(model_layout)
        
        model_select_layout = QHBoxLayout()
        
        # Model combobox
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4o-mini"
        ])
        self.model_combo.currentIndexChanged.connect(self.update_model_description)
        model_select_layout.addWidget(self.model_combo)
        
        # Refresh models button
        refresh_button = QPushButton("Refresh")
        refresh_button.setFixedWidth(80)
        refresh_button.clicked.connect(self.refresh_available_models)
        model_select_layout.addWidget(refresh_button)
        
        model_layout.addLayout(model_select_layout)
        
        # Model description
        self.model_description = QLabel("GPT 3.5 Turbo: Fast and cost-effective for most tasks")
        self.model_description.setWordWrap(True)
        model_layout.addWidget(self.model_description)
        
        # Temperature setting
        temp_layout = QHBoxLayout()
        temp_label = QLabel("Temperature:")
        temp_layout.addWidget(temp_label)
        
        self.temperature_slider = QSlider(Qt.Orientation.Horizontal)
        self.temperature_slider.setMinimum(0)
        self.temperature_slider.setMaximum(100)
        self.temperature_slider.setValue(70)  # Default 0.7
        self.temperature_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.temperature_slider.setTickInterval(10)
        self.temperature_slider.valueChanged.connect(self.update_temperature_label)
        temp_layout.addWidget(self.temperature_slider)
        
        self.temperature_label = QLabel("0.7")
        self.temperature_label.setFixedWidth(30)
        temp_layout.addWidget(self.temperature_label)
        
        model_layout.addLayout(temp_layout)
        
        # Temperature explanation
        temp_explanation = QLabel("Lower values (0.0) make output more focused and deterministic, higher values (1.0) make output more random and creative.")
        temp_explanation.setWordWrap(True)
        temp_explanation.setStyleSheet("color: #888888; font-size: 10px;")
        model_layout.addWidget(temp_explanation)
        
        tab_layout.addWidget(model_group)
        
        # Add separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        tab_layout.addWidget(separator2)
        
        # Usage and Cost tracking
        usage_group = QGroupBox("Usage and Cost Tracking")
        usage_layout = QVBoxLayout()
        usage_group.setLayout(usage_layout)
        
        # Usage statistics
        self.usage_text = QTextEdit()
        self.usage_text.setReadOnly(True)
        self.usage_text.setMinimumHeight(150)
        usage_layout.addWidget(self.usage_text)
        
        # Update and reset buttons
        button_layout = QHBoxLayout()
        
        update_usage_btn = QPushButton("Update Stats")
        update_usage_btn.clicked.connect(self.update_usage_stats)
        button_layout.addWidget(update_usage_btn)
        
        reset_usage_btn = QPushButton("Reset Usage Data")
        reset_usage_btn.clicked.connect(self.reset_usage_stats)
        button_layout.addWidget(reset_usage_btn)
        
        usage_layout.addLayout(button_layout)
        
        tab_layout.addWidget(usage_group)
        
        # Add separator
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.Shape.HLine)
        separator3.setFrameShadow(QFrame.Shadow.Sunken)
        tab_layout.addWidget(separator3)
        
        # Service status section
        service_group = QGroupBox("OpenAI Service Status")
        service_layout = QHBoxLayout()
        service_group.setLayout(service_layout)
        
        self.service_status_label = QLabel("Status: Not checked")
        service_layout.addWidget(self.service_status_label)
        
        check_status_btn = QPushButton("Check Status")
        check_status_btn.clicked.connect(self.check_openai_service)
        service_layout.addWidget(check_status_btn)
        
        tab_layout.addWidget(service_group)
        
        # Initialize the usage stats
        self.update_usage_stats()
    
    def update_temperature_label(self, value):
        """Update the temperature label when slider changes."""
        temperature = value / 100.0
        self.temperature_label.setText(f"{temperature:.1f}")
    
    def update_usage_stats(self):
        """Update the usage statistics display."""
        global openai_usage
        
        # Format usage statistics
        text = "<h3>OpenAI API Usage Statistics</h3>"
        
        # Total usage
        text += "<p><b>Total Calls:</b> " + str(openai_usage.get("total_calls", 0)) + "</p>"
        text += "<p><b>Total Tokens:</b> " + str(openai_usage.get("total_tokens", 0)) + "</p>"
        text += "<p><b>Prompt Tokens:</b> " + str(openai_usage.get("prompt_tokens", 0)) + "</p>"
        text += "<p><b>Completion Tokens:</b> " + str(openai_usage.get("completion_tokens", 0)) + "</p>"
        
        # Cost breakdown
        text += "<h4>Cost Breakdown</h4>"
        text += "<p><b>Total Estimated Cost:</b> $" + f"{openai_usage.get('estimated_cost', 0.0):.4f}" + "</p>"
        
        # Per model breakdown
        if openai_usage.get("cost_per_model"):
            text += "<p><b>Cost by Model:</b></p>"
            text += "<ul>"
            for model, cost in openai_usage.get("cost_per_model", {}).items():
                text += f"<li>{model}: ${cost:.4f}</li>"
            text += "</ul>"
        
        # Last update
        if openai_usage.get("last_updated"):
            text += "<p><b>Last Updated:</b> " + openai_usage.get("last_updated", "Never") + "</p>"
        
        # Recent history
        if openai_usage.get("usage_history"):
            text += "<h4>Recent Calls (last 5)</h4>"
            history = openai_usage.get("usage_history", [])[-5:]  # Get last 5 entries
            
            for call in reversed(history):  # Show most recent first
                text += f"<p>{call.get('timestamp')}: {call.get('model')} - "
                text += f"{call.get('total_tokens')} tokens, "
                text += f"${call.get('cost', 0.0):.4f}, "
                text += f"{call.get('response_time', 0.0):.2f}s</p>"
        
        # Update the text widget
        self.usage_text.setHtml(text)
    
    def reset_usage_stats(self):
        """Reset the OpenAI usage statistics."""
        global openai_usage
        
        reply = QMessageBox.question(
            self,
            "Reset Usage Statistics",
            "Are you sure you want to reset all OpenAI usage statistics?\nThis will clear all cost and token tracking data.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Reset usage stats
            openai_usage = {
                "total_calls": 0,
                "total_tokens": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "estimated_cost": 0.0,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "usage_history": [],
                "cost_per_model": {},
            }
            
            # Update display
            self.update_usage_stats()
            
            # Save to config
            config["openai_usage"] = openai_usage
            save_settings()
            
            QMessageBox.information(
                self,
                "Reset Complete",
                "OpenAI usage statistics have been reset."
            )
        
    def check_openai_service(self):
        """Check the OpenAI service status."""
        result = check_openai_status()
        
        if result:
            status = service_status.get("openai", {}).get("status", "unknown")
            message = service_status.get("openai", {}).get("message", "No message")
            
            self.service_status_label.setText(f"Status: {status} - {message}")
            
            # Update styling based on status
            if status == "operational" or status == "none":
                self.service_status_label.setStyleSheet("color: #55AA55;")  # Green
            elif status == "minor" or status == "major":
                self.service_status_label.setStyleSheet("color: #AAAA55;")  # Yellow
            else:
                self.service_status_label.setStyleSheet("color: #AA5555;")  # Red
        else:
            self.service_status_label.setText("Status: Error checking service")
            self.service_status_label.setStyleSheet("color: #AA5555;")  # Red
    
    def load_from_settings(self):
        """Load settings into the dialog fields."""
        global config
        
        # General tab
        # Set source radio button
        source = config.get("message_source", "local")
        if source == "local":
            self.local_radio.setChecked(True)
        elif source == "openai":
            self.openai_radio.setChecked(True)
        elif source == "database":
            self.database_radio.setChecked(True)
        
        # Set message interval
        interval = config.get("interval", 15)
        self.interval_spin.setValue(interval)
        
        # Set delay factor
        delay_factor = config.get("delay_factor", 1.0)
        self.delay_factor_spin.setValue(delay_factor)
        
        # Set save to database checkbox
        save_to_db = config.get("save_to_database", True)
        self.save_db_check.setChecked(save_to_db)
        
        # Set debug mode checkbox
        debug_mode = config.get("debug_mode", False)
        self.debug_check.setChecked(debug_mode)
        
        # OpenAI tab
        # Set API key if it exists (only display placeholder if it exists)
        api_key = config.get("openai_api_key", "")
        if api_key:
            self.api_key_edit.setText(api_key)
            self.api_key_status.setText("Status: Key loaded from settings (not verified)")
            self.api_key_status.setStyleSheet("color: #AAAAAA;")
        
        # Set model selection
        model = config.get("model", "gpt-3.5-turbo")
        index = self.model_combo.findText(model)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)
        
        # Set temperature
        temperature = config.get("temperature", 0.7)
        self.temperature_slider.setValue(int(temperature * 100))
        self.temperature_label.setText(f"{temperature:.1f}")
        
        # Stats tab
        # Update stats display
        self.stats_text.setText(get_stats_text())
        
        # Check service status
        self.refresh_service_status()
    
    def refresh_service_status(self):
        """Refresh the service status display."""
        global service_status
        
        # Update the status
        check_openai_status()
        check_flyio_status()
        
        # Update the display
        self.service_status_text.setText(get_service_status_text())
        
        QMessageBox.information(
            self,
            "Service Status",
            "Service status has been refreshed."
        )
    
    def toggle_key_visibility(self):
        """Toggle visibility of the API key."""
        if self.api_key_edit.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)

    def update_api_key_status(self):
        """Check if the API key is valid."""
        # Get API key from input
        api_key = self.api_key_edit.text()
        
        # Check if we have text entered
        if not api_key or len(api_key.strip()) < 10:
            self.api_key_status.setText("Status: Invalid key (too short)")
            self.api_key_status.setStyleSheet("color: #FF5555;")
            return
        
        # Update UI
        self.api_key_status.setText("Status: Verifying...")
        self.api_key_status.setStyleSheet("color: #AAAAAA;")
        
        # Try to initialize a client to test the key
        try:
            # Import OpenAI
            from openai import OpenAI, APIError
            
            # Create a temporary client
            temp_client = OpenAI(api_key=api_key)
            
            # Try a lightweight API call to verify the key
            try:
                models = temp_client.models.list(limit=1)
                
                # Key is valid
                self.api_key_status.setText(f"Status: Valid ✅ (found {len(models.data)} models)")
                self.api_key_status.setStyleSheet("color: #55AA55;")
                
                # Update config globally
                global config
                config["openai_api_key"] = api_key
                update_api_console("API key verified and saved", "system")
                
            except APIError as e:
                # API-specific errors (usually authentication or permissions)
                self.api_key_status.setText(f"Status: Invalid key - {str(e)[:60]}")
                self.api_key_status.setStyleSheet("color: #FF5555;")
                
        except ImportError:
            self.api_key_status.setText("Status: OpenAI module not installed")
            self.api_key_status.setStyleSheet("color: #FF5555;")
        except Exception as e:
            self.api_key_status.setText(f"Status: Error - {str(e)[:60]}")
            self.api_key_status.setStyleSheet("color: #FF5555;")
    
    def update_api_key(self):
        """Update the API key in the configuration."""
        print("\n====== update_api_key method started ======")
        api_key = self.api_key_edit.text()
        print(f"API key length: {len(api_key)}")
        
        # Skip if key is just placeholder asterisks
        if api_key == "●●●●●●●●●●●●●●●●●●●●●●●●●●●●":
            print("User provided placeholder API key, showing warning")
            QMessageBox.warning(
                self, 
                "API Key Update", 
                "Please enter your actual API key, not the placeholder."
            )
            print("====== update_api_key method aborted - placeholder provided ======\n")
            return
        
        if not api_key:
            print("User provided empty API key, showing warning")
            QMessageBox.warning(
                self, 
                "API Key Update", 
                "API key cannot be empty."
            )
            print("====== update_api_key method aborted - empty key provided ======\n")
            return
        
        # Simply update the config directly - this is safer and simpler
        try:
            print("Updating API key in configuration...")
            # Update the global config
            global config
            print(f"Config keys before update: {list(config.keys())}")
            config["openai_api_key"] = api_key
            print(f"Config keys after update: {list(config.keys())}")
            
            # Save to settings file
            print("Saving configuration with new API key...")
            save_settings()
            print("Configuration saved successfully")
            
            QMessageBox.information(
                self, 
                "API Key Update", 
                "✅ API key successfully saved to settings file."
            )
            
            # Update status
            print("Updating API key status...")
            self.update_api_key_status()
            
            # Attempt to initialize the OpenAI client with the new key
            print("Setting up new OpenAI client with updated API key...")
            global openai_client
            old_client = openai_client
            print(f"Old client exists: {old_client is not None}")
            
            # Clear the client first to force reinitialization
            print("Clearing existing OpenAI client...")
            openai_client = None
            
            # Set up a new client with the new key
            setup_result = setup_openai_client()
            print(f"setup_openai_client() result: {setup_result}")
            
            if openai_client and openai_client != old_client:
                print("New OpenAI client successfully initialized")
                QMessageBox.information(
                    self,
                    "OpenAI Client",
                    "✅ OpenAI client successfully initialized with your new API key."
                )
            else:
                print("Failed to initialize a new OpenAI client")
                if not setup_result:
                    QMessageBox.warning(
                        self,
                        "OpenAI Client",
                        "⚠️ Failed to initialize OpenAI client with your API key. Please check the console for errors."
                    )
            
            print("====== update_api_key method completed ======\n")
        except Exception as e:
            print(f"Error updating API key: {str(e)}")
            QMessageBox.critical(
                self,
                "API Key Update Error",
                f"An error occurred while updating your API key: {str(e)}"
            )
            print("====== update_api_key method failed ======\n")
    
    def get_settings(self):
        """Get all settings from the dialog."""
        settings = {}
        
        # Get message source
        if self.openai_radio.isChecked():
            settings["message_source"] = "openai"
        elif self.database_radio.isChecked():
            settings["message_source"] = "database"
        else:
            settings["message_source"] = "local"
        
        # Get OpenAI API key if set
        api_key = self.api_key_edit.text()
        if api_key and len(api_key) > 0 and api_key != "●●●●●●●●●●●●●●●●●●●●●●●●●●●●":
            settings["openai_api_key"] = api_key
            
        # Get OpenAI model
        model = self.model_combo.currentText()
        
        # Get temperature
        temperature = float(self.temperature_slider.value()) / 100.0
        
        # Get config settings
        settings["interval"] = self.interval_spin.value()
        settings["delay_factor"] = float(self.delay_factor_spin.value())
        settings["display_stats"] = self.display_stats_check.isChecked()
        settings["save_to_database"] = self.save_db_check.isChecked()
        settings["debug_mode"] = self.debug_check.isChecked()
        settings["model"] = model
        settings["temperature"] = temperature
        
        return settings

    def refresh_available_models(self):
        """Refresh the available models from the OpenAI API."""
        global openai_client
        
        # Get API key from input
        api_key = self.api_key_edit.text()
        
        # Check if we have a valid API key
        if not api_key or len(api_key.strip()) < 10:
            self.model_description.setText("Please enter a valid API key to refresh models")
            return
        
        # Try to initialize a temporary client to fetch models
        self.model_description.setText("Fetching available models...")
        
        try:
            # Import OpenAI
            from openai import OpenAI, APIError
            
            # Create a temporary client
            temp_client = OpenAI(api_key=api_key)
            
            # Fetch available models
            models = temp_client.models.list()
            
            # Filter for chat models only
            chat_models = [m.id for m in models.data if m.id.startswith("gpt")]
            
            # Update the model combo box
            current_model = self.model_combo.currentText()
            self.model_combo.clear()
            self.model_combo.addItems(sorted(chat_models))
            
            # Try to restore previous selection
            index = self.model_combo.findText(current_model)
            if index >= 0:
                self.model_combo.setCurrentIndex(index)
            
            # Update description
            self.model_description.setText(f"Successfully fetched {len(chat_models)} chat models")
            
        except ImportError:
            self.model_description.setText("OpenAI module not installed")
        except APIError as e:
            self.model_description.setText(f"API Error: {str(e)[:100]}")
        except Exception as e:
            self.model_description.setText(f"Error: {str(e)[:100]}")

    def update_model_description(self, index):
        """Update the model description when selection changes."""
        model = self.model_combo.currentText()
        
        descriptions = {
            "gpt-4o-mini": "Efficient, cost-effective version of GPT-4o with lower latency.",
            "gpt-4o": "Latest model, best for both text and vision tasks.",
            "gpt-3.5-turbo": "Faster and more cost-effective model, good for most tasks.",
            "gpt-4-turbo": "Expanded knowledge cutoff to April 2023.",
            "gpt-4": "Most capable model with a knowledge cutoff of April 2023."
        }
        
        self.model_description.setText(descriptions.get(model, "No description available"))
    
    def _setup_stats_tab(self):
        """Set up the statistics tab."""
        self.tab_widget.addTab(self.stats_tab, "📊 Statistics")
        
        layout = QVBoxLayout(self.stats_tab)
        
        # Statistics data
        stats_group = QGroupBox("Message Statistics")
        stats_layout = QVBoxLayout()
        stats_group.setLayout(stats_layout)
        
        # Statistics text display
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMinimumHeight(150)
        stats_layout.addWidget(self.stats_text)
        
        # Reset stats button
        self.reset_stats_btn = QPushButton("Reset Statistics")
        self.reset_stats_btn.clicked.connect(self.reset_stats)
        stats_layout.addWidget(self.reset_stats_btn)
        
        layout.addWidget(stats_group)
        
        # Service status
        service_group = QGroupBox("Service Status")
        service_layout = QVBoxLayout()
        service_group.setLayout(service_layout)
        
        # Service status text display
        self.service_status_text = QTextEdit()
        self.service_status_text.setReadOnly(True)
        self.service_status_text.setMinimumHeight(150)
        service_layout.addWidget(self.service_status_text)
        
        # Refresh status button
        self.refresh_status_btn = QPushButton("Refresh Status")
        self.refresh_status_btn.clicked.connect(self.refresh_service_status)
        service_layout.addWidget(self.refresh_status_btn)
        
        layout.addWidget(service_group)
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
        # Load initial stats
        self.stats_text.setText(get_stats_text())
        self.service_status_text.setText(get_service_status_text())
    
    def reset_stats(self):
        """Reset the message statistics."""
        global message_stats
        
        reply = QMessageBox.question(
            self,
            "Reset Statistics",
            "Are you sure you want to reset all message statistics?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            message_stats = {
                "total": 0,
                "local": 0,
                "openai": 0,
                "database": 0,
                "system": 0,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_message": None,
                "last_source": None
            }
            self.stats_text.setText(get_stats_text())
            QMessageBox.information(
                self,
                "Reset Statistics",
                "Message statistics have been reset."
            )

def show_settings_dialog(display_obj):
    """Show settings dialog and process results if accepted."""
    global display, config
    
    # Debug output
    print(f"Show settings dialog called with display object: {id(display_obj)}")
    print(f"Global display object ID: {id(display)}")
    
    # Ensure display is initialized
    if not display_obj:
        update_api_console("❌ Cannot show settings - invalid display object", "error")
        return
        
    # Ensure we're using the correct display object
    display_to_use = display_obj
    if display_obj != display:
        update_api_console("⚠️ Warning: Settings dialog called with different display object than global", "warning")
        display_to_use = display
    
    # Create dialog
    dialog = SettingsDialog(display_to_use)
    
    # Apply styling
    UIStyleHelper.apply_settings_dialog_style(dialog)
    
    # Apply button styling to all buttons
    for button in dialog.findChildren(QPushButton):
        UIStyleHelper.apply_button_style(button)
    
    # Ensure dialog is sized appropriately
    if dialog.width() < 600:
        dialog.resize(600, dialog.height())
    if dialog.height() < 550:
        dialog.resize(dialog.width(), 550)
    
    # Debug - print dialog tabs
    print(f"Dialog tabs: {[dialog.tab_widget.tabText(i) for i in range(dialog.tab_widget.count())]}")
    
    # Make dialog modal and execute
    dialog.setModal(True)
    if dialog.exec():
        # Dialog was accepted
        update_api_console("Settings dialog accepted - applying changes", "system")
        
        # Get settings from dialog
        new_settings = dialog.get_settings()
        
        # Update message source if changed
        if new_settings.get("message_source") != config.get("message_source"):
            set_message_source(display_to_use, new_settings["message_source"])
        
        # Update config with new settings
        config.update(new_settings)
        
        # Reinitialize OpenAI client if key changed
        if "openai_api_key" in new_settings and new_settings["openai_api_key"] != config.get("openai_api_key", ""):
            update_api_console("API key changed - reinitializing OpenAI client", "system")
            setup_openai_client()
        
        # Update message timer interval if needed
        if "interval" in new_settings and hasattr(display_to_use, 'message_timer'):
            new_interval = calculate_message_interval()
            display_to_use.message_timer.setInterval(new_interval)
            update_api_console(f"Message timer interval updated to {new_interval/1000:.1f} seconds", "system")
        
        # Save settings to permanent storage
        save_settings()
        
        # Update window title
        if hasattr(display_to_use, 'setWindowTitle'):
            source = config.get("message_source", "local").upper()
            display_to_use.setWindowTitle(f"Punch Card Display - {source} Mode")
        
        # Display source change
        if hasattr(display_to_use, 'display_message'):
            source = config.get("message_source", "local").upper()
            display_to_use.display_message(f"SOURCE: {source}")
            save_message_to_database(f"SETTINGS UPDATED - SOURCE: {source}", "system")
        
        update_api_console("✅ Settings saved and applied", "system")
    else:
        # Dialog was rejected
        update_api_console("Settings dialog canceled - no changes applied", "system")

def check_database():
    """Legacy wrapper for database initialization."""
    return initialize_database()

def initialize_database():
    """Initialize the SQLite database for message storage."""
    global db_connection, config
    
    try:
        # Get database path from config or use default
        db_path = config.get("database_path", "punch_card_messages.db")
        
        # Connect to the database
        db_connection = sqlite3.connect(db_path)
        
        # Create tables if they don't exist
        cursor = db_connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                source TEXT NOT NULL
            )
        ''')
        
        # Create stats table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        
        # Commit changes
        db_connection.commit()
        
        # Count messages for reporting
        cursor.execute("SELECT COUNT(*) FROM messages")
        message_count = cursor.fetchone()[0]
        
        update_api_console(f"✅ Database initialized with {message_count} messages", "system")
        return True
        
    except Exception as e:
        update_api_console(f"❌ Error initializing database: {str(e)[:100]}", "error")
        return False

def calculate_message_interval():
    """Calculate message interval based on source and settings."""
    global message_source, config
    
    base_interval = config["interval"] * 1000  # convert to milliseconds
    
    # If using OpenAI, might need more time for API calls
    if message_source == "openai":
        return int(base_interval * config["delay_factor"])
    
    return base_interval

def add_api_console():
    """Add an API console to the display for viewing API messages."""
    global display, config
    
    # Verify display is initialized
    if not display:
        print("[ERROR] Cannot add API console - display not initialized")
        return False
    
    # Check if console already exists to avoid duplication
    if hasattr(display, 'api_console') and display.api_console and hasattr(display, 'api_console_window') and display.api_console_window:
        # Console already exists, just make it visible
        display.api_console_window.show()
        display.api_console_window.raise_()
        print("[INFO] API console already exists - making it visible")
        return True
    
    try:
        # Create a QTextEdit as console
        console = QTextEdit()
        console.setReadOnly(True)
        console.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        # Apply console styling
        UIStyleHelper.apply_console_style(console)
        
        # Create a main window for the console
        console_window = QMainWindow()
        console_window.setWindowTitle("API Console")
        console_window.resize(800, 400)
        console_window.setCentralWidget(console)
        
        # Store the console and window in the display
        display.api_console = console
        display.api_console_window = console_window
        
        # Load console messages if there are any in history buffer
        if hasattr(display, 'console_history') and display.console_history:
            for msg in display.console_history:
                try:
                    console.append(msg)
                except Exception:
                    pass  # Ignore errors when appending old messages
            display.console_history = []  # Clear history after adding to console
        
        # Add welcome message to console
        current_time = time.strftime("%H:%M:%S")
        console.append(f"<span style='color:#888888;'>[{current_time}]</span> <span style='color:#55aa55;'>API Console Initialized</span>")
        
        # Set console font - make it easier to read
        try:
            font = console.font()
            font.setFamily("Courier New")
            font.setPointSize(10)
            console.setFont(font)
        except Exception:
            pass  # Ignore font setting errors
        
        # Show the console if debug mode is enabled
        if config.get("debug_mode", False):
            console_window.show()
            console_window.raise_()
            print("[INFO] API console created and shown")
        else:
            print("[INFO] API console created (not shown - debug mode disabled)")
        
        # Add a note to the console with keyboard shortcut info
        console.append(f"<span style='color:#888888;'>[{current_time}]</span> <span style='color:#55aa55;'>Press 'C' to toggle console visibility at any time</span>")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create API console: {str(e)}")
        return False

def style_ui_elements(display):
    """Apply EPA/Mac-style design to UI elements."""
    try:
        # Apply global styling to the application
        if QApplication.instance():
            UIStyleHelper.apply_global_style(QApplication.instance())
            print("✅ Applied global styling to application")
        
        # Apply style to any buttons in the button container
        if hasattr(display, 'button_container'):
            # Apply styling to the button container itself
            if display.button_container.layout():
                display.button_container.setStyleSheet(f"""
                    background-color: {UIStyleHelper.COLORS['bg']};
                    border: 1px solid {UIStyleHelper.COLORS['border']};
                    border-radius: 3px;
                    padding: 5px;
                """)
            
            for button in display.button_container.findChildren(QPushButton):
                UIStyleHelper.apply_button_style(button)
            print("✅ Applied button styling to buttons")
        
        # Apply style to the settings button if it exists
        if hasattr(display, 'settings_button'):
            UIStyleHelper.apply_button_style(display.settings_button)
        
        # Apply style to any existing console
        if hasattr(display, 'api_console'):
            UIStyleHelper.apply_console_style(display.api_console)
            print("✅ Applied dark theme to API console")
            
            # Make sure console and its parent are visible
            display.api_console.setVisible(True)
            if hasattr(display.api_console, 'parent') and display.api_console.parent():
                display.api_console.parent().setVisible(True)
            
            # Force an update to verify it's working
            update_api_console("Console styling applied")
            
        # Apply style to the punch card display if possible
        if hasattr(display, 'card_display'):
            display.card_display.setStyleSheet(f"""
                background-color: {UIStyleHelper.COLORS['bg']};
                color: {UIStyleHelper.COLORS['fg']};
                border: 1px solid {UIStyleHelper.COLORS['border']};
                padding: 8px;
                font-family: {UIStyleHelper.FONTS['monospace']};
                font-size: {UIStyleHelper.FONTS['size_normal']};
            """)
            
        print("✅ Applied style to card display")
        
        # Apply style to parent widgets if possible
        if hasattr(display, 'parent') and display.parent():
            display.parent().setStyleSheet(f"""
                background-color: {UIStyleHelper.COLORS['bg']};
                color: {UIStyleHelper.COLORS['fg']};
            """)
            
        # Apply style to the window
        if hasattr(display, 'setStyleSheet'):
            display.setStyleSheet(f"""
                background-color: {UIStyleHelper.COLORS['bg']};
                color: {UIStyleHelper.COLORS['fg']};
            """)
            print("✅ Applied style to main window")
            
        # Make sure menu container is visible if it exists
        if hasattr(display, 'menu_container'):
            display.menu_container.setVisible(True)
            print("✅ Ensured menu container is visible")
            
        return True
    except Exception as e:
        print(f"⚠️ Error styling UI elements: {e}")
        return False

def set_message_source(display, source):
    """Set message source from menu action."""
    global config
    
    # Only change if different
    if config.get("message_source", "local") != source:
        update_api_console(f"Changing message source from {config.get('message_source', 'local')} to {source}", "system")
        
        # If changing to OpenAI, initialize the client
        if source == "openai" and not openai_client:
            if setup_openai_client():
                update_api_console("OpenAI client initialized successfully", "system")
            else:
                update_api_console("❌ Failed to initialize OpenAI client. Check your API key in settings.", "error")
        
        # Update message source in config
        config["message_source"] = source
        
        # Update display
        if hasattr(display, 'display_message'):
            try:
                display.display_message(f"SOURCE: {source.upper()}")
                save_message_to_database(f"SOURCE: {source.upper()}", "system")
                update_api_console(f"Message source changed to {source}", "system")
            except Exception as e:
                update_api_console(f"❌ Error displaying source change: {str(e)[:100]}", "error")
        
        # Update timer interval if needed
        if hasattr(display, 'message_timer') and display.message_timer:
            new_interval = calculate_message_interval()
            display.message_timer.setInterval(new_interval)
            update_api_console(f"Message timer updated to {new_interval/1000:.1f} seconds", "system")
        
        # Update window title if possible
        if hasattr(display, 'setWindowTitle'):
            display.setWindowTitle(f"Punch Card Display - {source.upper()} Mode")
            update_api_console("Window title updated", "system")
        
        # Save settings
        save_settings()
        return True
    return False

def main():
    """Main application function."""
    global message_source, config, openai_client, display
    
    # Clean legacy settings before loading
    clean_legacy_settings()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Punch Card Display')
    parser.add_argument('--interval', type=int, default=15, help='Interval between messages in seconds')
    parser.add_argument('--openai', action='store_true', help='Start with OpenAI message source')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--epa-style', action='store_true', help='Apply EPA-inspired styling')
    parser.add_argument('--black-bg', action='store_true', help='Use black background (punch card style)')
    args = parser.parse_args()
    
    # Load settings
    load_settings()
    
    # Override interval if specified
    if args.interval != 15:  # 15 is the default in the argument parser
        config["interval"] = args.interval
    
    # Override debug mode if specified
    if args.debug:
        config["debug_mode"] = True
    
    # Override message source if --openai flag is used
    if args.openai:
        global message_source
        message_source = "openai"
    
    # Start the GUI
    try:
        global display
        display, app = gui_main()  # gui_main returns both display and app
        
        # Apply global style to the application
        UIStyleHelper.apply_global_style(app)
        debug_log("Applied global styling to application")
        
        # Install an event filter to capture key presses
        key_filter = KeyPressFilter(app)
        app.installEventFilter(key_filter)
        debug_log("KeyPressFilter initialized")
        
        # Set window title to include source
        if hasattr(display, 'setWindowTitle'):
            display.setWindowTitle(f"Punch Card Display - {message_source.upper()} Mode")
    except Exception as e:
        debug_log(f"Error starting GUI: {e}", "error")
        return
    
    # Add API console for message display - do this before adding menu bar
    # to ensure console is available for status updates
    add_api_console()
    
    # Initialize OpenAI if configured to use it
    if args.openai or message_source == "openai":
        if setup_openai_client():
            update_api_console("OpenAI client initialized successfully", "system")
        else:
            update_api_console("❌ Failed to initialize OpenAI client. Check your API key in settings.", "error")
            # Fall back to local mode if OpenAI fails
            if message_source == "openai":
                message_source = "local"
                update_api_console("⚠️ Falling back to local message source due to OpenAI initialization failure", "warning")
                if hasattr(display, 'setWindowTitle'):
                    display.setWindowTitle(f"Punch Card Display - {message_source.upper()} Mode")
    
    # Check service statuses
    check_openai_status()
    check_flyio_status()
    
    # Display service status in console
    update_api_console(get_service_status_text())
    
    # Set up status check timer
    status_timer = QTimer()
    status_timer.timeout.connect(lambda: [check_openai_status(), check_flyio_status()])
    status_timer.start(300000)  # Check every 5 minutes
    display.status_timer = status_timer
    
    # Apply styling to UI elements with black background
    style_ui_elements(display)
    
    # Check and initialize database
    check_database()
    initialize_database()
    
    # Verify database functionality
    if hasattr(display, 'message_db'):
        update_api_console(f"Database active: {len(display.message_db.messages)} messages")
    else:
        update_api_console("⚠️ Using local backup (no database)")
    
    # Set up signal handling for graceful termination
    def signal_handler(sig, frame):
        debug_log("Signal received, shutting down...")
        update_api_console("Shutting down...")
        app.quit()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Display initial message
    try:
        if hasattr(display, 'display_message'):
            debug_log("Display has display_message method")
            welcome_message = f"PUNCH CARD - {message_source.upper()} MODE"
            display.display_message(welcome_message)
            update_api_console(f"Welcome to Punch Card - {message_source.upper()} mode")
            
            # Save welcome message to database
            try:
                save_message_to_database(welcome_message, source="system")
                debug_log("Welcome message saved to database")
            except Exception as e:
                debug_log(f"Error saving welcome message: {e}", "error")
        else:
            debug_log("Display does not have display_message method", "warning")
    except Exception as e:
        debug_log(f"Error displaying initial message: {e}", "error")
    
    # Set up message timer
    interval = int(config.get("interval", 15) * 1000)  # Convert seconds to milliseconds
    message_timer = QTimer()
    message_timer.timeout.connect(display_next_message)
    message_timer.start(interval)
    display.message_timer = message_timer
    debug_log(f"Message timer started with interval: {interval/1000:.1f} seconds")
    
    # Show information about shortcuts
    update_api_console(f"Message timer started - next message in {display.message_timer.interval()/1000:.1f} seconds")
    update_api_console("Press 'C' to show API console at any time")
    update_api_console("Press 'S' to show settings dialog at any time")
    
    # Run the event loop
    debug_log("Running event loop. Press Ctrl+C to exit.")
    sys.exit(app.exec())

# Menu helper functions
def show_about_dialog(window=None):
    """Show the about dialog with version and monkey patch information."""
    global display
    about_dialog = AboutDialog(window or display.main_window if display else None)
    about_dialog.exec()

def export_messages(parent=None):
    """Export messages to a file."""
    global display, message_database
    
    try:
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import json
        from datetime import datetime
        
        update_api_console("Preparing to export messages...")
        
        # Get messages from appropriate source
        messages = []
        
        # Try to get from display's database
        if hasattr(display, 'message_db') and hasattr(display.message_db, 'messages'):
            messages = display.message_db.messages
            update_api_console(f"Exporting {len(messages)} messages from database")
        # Try backup database
        elif message_database:
            messages = message_database
            update_api_console(f"Exporting {len(messages)} messages from backup")
        else:
            update_api_console("No messages to export")
            QMessageBox.warning(parent, "Export Messages", "No messages available to export.")
            return
        
        # Get current date for filename
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Open file dialog to select save location
        file_path, _ = QFileDialog.getSaveFileName(
            parent,
            "Export Messages",
            f"punch_card_messages_{date_str}.json",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            update_api_console("Export cancelled")
            return
        
        # Save messages to file
        with open(file_path, 'w') as f:
            json.dump(messages, f, indent=2)
        
        update_api_console(f"✅ Exported {len(messages)} messages to {file_path}")
        QMessageBox.information(parent, "Export Complete", f"Successfully exported {len(messages)} messages.")
        
    except Exception as e:
        print(f"⚠️ Error exporting messages: {e}")
        update_api_console(f"Error exporting messages: {str(e)[:50]}")
        
        if parent:
            QMessageBox.critical(
                parent,
                "Export Error",
                f"An error occurred while exporting messages:\n{str(e)}"
            )

def clear_display(parent=None):
    """Clear the display."""
    global display
    
    try:
        from PyQt6.QtWidgets import QMessageBox
        
        # Ask for confirmation
        reply = QMessageBox.question(
            parent,
            "Clear Display",
            "Are you sure you want to clear the display?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            update_api_console("Clearing display...")
            
            # Display empty message
            if hasattr(display, 'display_message'):
                display.display_message("")
                update_api_console("Display cleared")
            else:
                update_api_console("⚠️ Unable to clear display - no display_message method found")
                
    except Exception as e:
        print(f"⚠️ Error clearing display: {e}")
        update_api_console(f"Error clearing display: {str(e)[:50]}")

def show_stats_dialog(parent=None):
    """Show statistics in a dialog."""
    global message_stats, service_status
    
    try:
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel
        
        # Create dialog
        dialog = QDialog(parent)
        dialog.setWindowTitle("Message Statistics")
        dialog.setMinimumSize(500, 400)
        
        # Apply styling
        UIStyleHelper.apply_settings_dialog_style(dialog)
        
        # Create layout
        layout = QVBoxLayout(dialog)
        
        # Add heading
        heading = QLabel("Message Statistics")
        UIStyleHelper.apply_heading_style(heading)
        layout.addWidget(heading)
        
        # Add stats text
        stats_text = QTextEdit()
        stats_text.setReadOnly(True)
        stats_text.setText(get_stats_text() + "\n\n" + get_service_status_text())
        UIStyleHelper.apply_console_style(stats_text)
        layout.addWidget(stats_text)
        
        # Add refresh button
        refresh_btn = QPushButton("Refresh Statistics")
        UIStyleHelper.apply_button_style(refresh_btn)
        refresh_btn.clicked.connect(lambda: stats_text.setText(get_stats_text() + "\n\n" + get_service_status_text()))
        layout.addWidget(refresh_btn)
        
        # Add close button
        close_btn = QPushButton("Close")
        UIStyleHelper.apply_button_style(close_btn)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        update_api_console("Showing statistics dialog")
        dialog.exec()
        
    except Exception as e:
        print(f"⚠️ Error showing stats dialog: {e}")
        update_api_console(f"Error showing statistics dialog: {str(e)[:50]}")

def show_shortcuts_dialog(parent=None):
    """Show keyboard shortcuts dialog."""
    try:
        from PyQt6.QtWidgets import QMessageBox
        
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle("Keyboard Shortcuts")
        
        msg_box.setText("""
        <h3>Keyboard Shortcuts</h3>
        <table>
        <tr><td><b>S</b></td><td>Show Settings Dialog</td></tr>
        <tr><td><b>C</b></td><td>Show API Console</td></tr>
        <tr><td><b>Esc</b></td><td>Close dialogs</td></tr>
        </table>
        """)
        
        # Apply styling
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {UIStyleHelper.COLORS['bg']};
                color: {UIStyleHelper.COLORS['fg']};
                font-family: {UIStyleHelper.FONTS['system']};
            }}
            QLabel {{
                color: {UIStyleHelper.COLORS['fg']};
                background-color: transparent;
            }}
            QPushButton {{
                background-color: {UIStyleHelper.COLORS['button_bg']};
                color: {UIStyleHelper.COLORS['button_text']};
                border: 1px solid {UIStyleHelper.COLORS['border']};
                border-radius: 3px;
                padding: 6px 12px;
                min-width: 80px;
            }}
        """)
        
        update_api_console("Showing keyboard shortcuts dialog")
        msg_box.exec()
        
    except Exception as e:
        print(f"⚠️ Error showing shortcuts dialog: {e}")
        update_api_console(f"Error showing shortcuts dialog: {str(e)[:50]}")

def check_and_display_api_status(parent=None):
    """Check API status and display results."""
    global service_status
    
    try:
        from PyQt6.QtWidgets import QMessageBox
        
        update_api_console("Checking API status...")
        
        # Check OpenAI and Fly.io status
        check_openai_status()
        check_flyio_status()
        
        # Create message with status info
        status_text = get_service_status_text()
        
        # Show in message box
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle("API Status")
        msg_box.setText(status_text.replace("\n", "<br>"))
        
        # Apply styling
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {UIStyleHelper.COLORS['bg']};
                color: {UIStyleHelper.COLORS['fg']};
                font-family: {UIStyleHelper.FONTS['system']};
            }}
            QLabel {{
                color: {UIStyleHelper.COLORS['fg']};
                background-color: transparent;
            }}
            QPushButton {{
                background-color: {UIStyleHelper.COLORS['button_bg']};
                color: {UIStyleHelper.COLORS['button_text']};
                border: 1px solid {UIStyleHelper.COLORS['border']};
                border-radius: 3px;
                padding: 6px 12px;
                min-width: 80px;
            }}
        """)
        
        update_api_console("Showing API status dialog")
        msg_box.exec()
        
    except Exception as e:
        print(f"⚠️ Error checking API status: {e}")
        update_api_console(f"Error checking API status: {str(e)[:50]}")

def generate_local_message():
    """Generate a local message for display on the punch card."""
    # Vintage computing messages inspired by IBM mainframes and early computing
    messages = [
        # System status messages
        "SYSTEM READY FOR INPUT",
        "BATCH PROCESSING COMPLETE",
        "DATA PROCESSING INITIALIZED",
        "MAINFRAME OPERATIONS NORMAL",
        "SYSTEM EXECUTING AT OPTIMAL CAPACITY",
        "ALL SUBSYSTEMS OPERATIONAL",
        "DIAGNOSTICS: ALL SYSTEMS NOMINAL",
        "PROCESSING QUEUE: READY",
        "SYSTEM IDLE - AWAITING INSTRUCTIONS",
        "1401 PROCESSING UNIT ONLINE",
        
        # Historical computing references
        "IBM SYSTEM/360: COMPUTING MILESTONE",
        "COBOL: COMMON BUSINESS ORIENTED LANGUAGE",
        "FORTRAN: FORMULA TRANSLATION",
        "VACUUM TUBES AT FULL POWER",
        "CORE MEMORY INITIALIZED",
        "MAGNETIC TAPE BACKUP COMPLETE",
        "HOLLERITH ENCODING ACTIVATED",
        "ENIAC: ELECTRONIC NUMERICAL INTEGRATOR AND COMPUTER",
        "UNIVAC: UNIVERSAL AUTOMATIC COMPUTER",
        "COMPUTING PIONEERS REMEMBERED",
        
        # Punch card specific references
        "80 COLUMNS OF ENGINEERING EXCELLENCE",
        "DO NOT FOLD, SPINDLE OR MUTILATE",
        "KEYPUNCH OPERATOR ON DUTY",
        "CARD READER CALIBRATED",
        "PUNCH PRECISION: 0.087 × 0.187 INCHES",
        "PUNCH CARD CAPACITY: 80 CHARACTERS",
        "BINARY DATA ENCODED SUCCESSFULLY",
        "HOLLERITH CODE TRANSLATION COMPLETE",
        "CARD DECK READY FOR PROCESSING",
        "VINTAGE COMPUTING LIVES ON",
        
        # Philosophical/reflective computing messages
        "TECHNOLOGY EVOLUTION SNAPSHOT",
        "COMPUTING HISTORY PRESERVED",
        "DIGITAL ARCHAEOLOGY: EXPLORING THE PAST",
        "HUMAN-MACHINE INTERFACE TIMELINE",
        "MECHANICAL COMPUTING TO QUANTUM: THE JOURNEY",
        "PROGRAMMING PARADIGMS THROUGH TIME",
        "BINARY LOGIC: COMPUTING FOUNDATION",
        "HARDWARE-SOFTWARE SYMBIOSIS",
        "DATA PROCESSING EVOLUTION",
        "IBM SYSTEMS: COMPUTING LEGENDS",
        
        # Fun/creative messages
        "CYBERNETICS RESEARCH ONGOING",
        "ARTIFICIAL INTELLIGENCE SEEDS PLANTED",
        "QUANTUM COMPUTING ON THE HORIZON",
        "SILICON REVOLUTION REMEMBERED",
        "DIGITAL DAWN: COMPUTING'S EARLY LIGHT",
        "COMPUTATIONAL THINKING PATTERNS",
        "DIGITAL TO ANALOG CONVERSION COMPLETE",
        "PUNCH CARD V3: VINTAGE REIMAGINED",
        "RETRO COMPUTING AESTHETIC INITIALIZED",
        "COMPUTING ANACHRONISM ACTIVATED"
    ]
    
    # Select a random message
    message = random.choice(messages)
    
    # Logging
    update_api_console(f"Generated local message: {message}", "system")
    
    return message

def clean_legacy_settings(settings_file="punch_card_settings.json"):
    """Clean up any legacy or invalid parameters in the settings file."""
    try:
        if not os.path.exists(settings_file):
            return
            
        # Load the settings file
        with open(settings_file, 'r') as f:
            settings = json.load(f)
            
        needs_save = False
        
        # Check for legacy parameters in config
        if 'config' in settings:
            if 'proxies' in settings['config']:
                debug_log("Removing invalid 'proxies' parameter from settings file", "warning", False)
                del settings['config']['proxies']
                needs_save = True
                
        # Save the cleaned settings if needed
        if needs_save:
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            debug_log("✅ Legacy settings cleaned successfully", "system", False)
            
    except Exception as e:
        debug_log(f"Error cleaning legacy settings: {e}", "error", False)

class AboutDialog(QDialog):
    """Dialog to display information about the application and version."""
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.setWindowTitle(f"About Punch Card v{VERSION}")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("<h1>Punch Card Display</h1>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Version
        version_label = QLabel(f"<h3>Version {VERSION}</h3>")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        # ASCII art
        if "MonkeyPatch" in VERSION:
            art_label = QLabel(f"<pre>{MONKEY_ART}</pre>")
            art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            art_label.setStyleSheet("font-family: monospace; font-size: 16px;")
            layout.addWidget(art_label)
        
        # Description
        about_text = """
        <p>Punch Card Display is a retro-themed message display application that simulates 
        the look of old IBM punch cards.</p>
        
        <p>This application can display messages from multiple sources:</p>
        <ul>
            <li>Local pre-defined messages</li>
            <li>OpenAI-generated messages</li>
            <li>Custom user messages</li>
        </ul>
        """
        about_label = QLabel(about_text)
        about_label.setWordWrap(True)
        layout.addWidget(about_label)
        
        # MonkeyPatch info
        if "MonkeyPatch" in VERSION:
            monkeypatch_text = """
            <h3>About the MonkeyPatch Update</h3>
            <p>The MonkeyPatch Update (v0.5.3) addresses issues with the OpenAI client initialization
            by implementing a technique called "monkey patching".</p>
            
            <p><b>What is Monkey Patching?</b><br>
            Monkey patching is a technique to change the behavior of existing code at runtime without 
            modifying the original source code. It's named "monkey patch" because it involves "patching" 
            or modifying part of the running code in a way that might be considered a bit cheeky or 
            mischievous - like what a monkey might do!</p>
            
            <p>In this update, we use monkey patching to replace the standard OpenAI client creation with 
            our own implementation that removes problematic parameters that were causing errors.</p>
            """
            monkeypatch_label = QLabel(monkeypatch_text)
            monkeypatch_label.setWordWrap(True)
            layout.addWidget(monkeypatch_label)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(layout)

if __name__ == '__main__':
    main() 