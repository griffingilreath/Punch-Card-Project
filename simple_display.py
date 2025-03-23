#!/usr/bin/env python3
# simple_display.py - A simplified version of the punch card display

import sys
import time
import random
import argparse
import json
import signal
import os
import requests
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QGridLayout, 
    QLabel, QPushButton, QRadioButton, QGroupBox,
    QDialogButtonBox, QSpinBox, QCheckBox, QTextEdit, QWidget, QFrame
)
from PyQt6.QtCore import QTimer, Qt, QEvent, QObject
from src.display.gui_display import main as gui_main
from openai import OpenAI
from PyQt6.QtGui import QAction, QKeyEvent  # Import QAction from QtGui, not QtWidgets

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
    "epa_style": True  # apply EPA-inspired styling
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
        """Create a classic Mac-style menu bar at the top of the window."""
        from PyQt6.QtWidgets import QMenuBar, QMenu
        from PyQt6.QtGui import QAction  # Import QAction from QtGui, not QtWidgets
        
        # Create a menu bar
        menu_bar = QMenuBar(window)
        menu_bar.setStyleSheet(f"""
            background-color: {UIStyleHelper.COLORS['button_bg']};
            color: {UIStyleHelper.COLORS['fg']};
            border-bottom: 1px solid {UIStyleHelper.COLORS['border']};
            padding: 2px;
            min-height: 24px;
        """)
        
        # Create File menu
        file_menu = QMenu("File", window)
        file_menu.setStyleSheet(f"""
            background-color: {UIStyleHelper.COLORS['bg']};
            color: {UIStyleHelper.COLORS['fg']};
        """)
        
        # Add Settings action
        settings_action = QAction("Settings", window)
        settings_action.triggered.connect(lambda: show_settings_dialog(window))
        file_menu.addAction(settings_action)
        
        # Add Exit action
        exit_action = QAction("Exit", window)
        exit_action.triggered.connect(window.close)
        file_menu.addAction(exit_action)
        
        # Add File menu to menu bar
        menu_bar.addMenu(file_menu)
        
        # Create Source menu
        source_menu = QMenu("Source", window)
        source_menu.setStyleSheet(f"""
            background-color: {UIStyleHelper.COLORS['bg']};
            color: {UIStyleHelper.COLORS['fg']};
        """)
        
        # Add source actions
        local_action = QAction("Local", window)
        local_action.triggered.connect(lambda: set_message_source(window, "local"))
        source_menu.addAction(local_action)
        
        openai_action = QAction("OpenAI", window)
        openai_action.triggered.connect(lambda: set_message_source(window, "openai"))
        source_menu.addAction(openai_action)
        
        database_action = QAction("Database", window)
        database_action.triggered.connect(lambda: set_message_source(window, "database"))
        source_menu.addAction(database_action)
        
        # Add Source menu to menu bar
        menu_bar.addMenu(source_menu)
        
        # Return the menu bar
        return menu_bar

# Replace MacStyleHelper with UIStyleHelper throughout the code
# For compatibility, create alias
MacStyleHelper = UIStyleHelper

def load_settings(settings_file="punch_card_settings.json"):
    """Load settings from a JSON file."""
    global message_source, config
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
            # If message_source is in the settings, use it
            if 'message_source' in settings:
                message_source = settings['message_source']
            
            # Load config settings if available
            if 'config' in settings:
                for key, value in settings['config'].items():
                    if key in config:
                        config[key] = value
                
            print(f"✅ Settings loaded from {settings_file}")
            return settings
    except Exception as e:
        print(f"⚠️ Error loading settings: {e}")
        return {}

def save_settings(settings_file="punch_card_settings.json"):
    """Save settings to a JSON file."""
    global message_source, config
    try:
        # Try to load existing settings first
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
        except:
            settings = {}
        
        # Update with our settings
        settings['message_source'] = message_source
        settings['config'] = config
        
        # Save back to file
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        print(f"✅ Settings saved to {settings_file}")
    except Exception as e:
        print(f"⚠️ Error saving settings: {e}")

def save_message_to_database(display, message, source):
    """Save a message to the database."""
    global message_database, config, message_stats
    
    # Check if saving is enabled
    if not config["save_to_database"]:
        print("⚠️ Message saving disabled")
        return False
    
    # Update stats
    update_stats(source)
    
    # Update last message info
    message_stats["last_message"] = message
    message_stats["last_source"] = source
    
    # Update API console if available
    update_api_console(f"Saving message from {source}: {message[:30]}...")
    
    # Try multiple approaches to save to database
    try:
        # Method 1: Use message_db if available
        if hasattr(display, 'message_db') and hasattr(display.message_db, 'add_message'):
            display.message_db.add_message(message, source)
            print(f"✅ Message saved to database via message_db: {message[:30]}...")
            update_api_console(f"✅ Message saved to database")
            return True
            
        # Method 2: Use db interface if available
        elif hasattr(display, 'db') and hasattr(display.db, 'save_message'):
            display.db.save_message(message, source)
            print(f"✅ Message saved to database via db interface: {message[:30]}...")
            update_api_console(f"✅ Message saved to database")
            return True
            
        # Method 3: Use save_message_to_history if available
        elif hasattr(display, 'save_message_to_history'):
            display.save_message_to_history(message, source)
            print(f"✅ Message saved to history: {message[:30]}...")
            update_api_console(f"✅ Message saved to history")
            return True
            
        # Method 4: Save to local backup
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message_database.append({
                "message": message,
                "source": source,
                "timestamp": timestamp
            })
            print(f"⚠️ No database found, saved to local backup: {message[:30]}...")
            update_api_console(f"⚠️ Saved to local backup (no database found)")
            return True
    except Exception as e:
        print(f"⚠️ Error saving message to database: {e}")
        update_api_console(f"⚠️ Error saving message: {str(e)[:50]}")
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
    openai_status = service_status["openai"]
    flyio_status = service_status["flyio"]
    
    text = "=== Service Status ===\n"
    text += f"OpenAI: {openai_status['status']}\n"
    text += f"Message: {openai_status['message']}\n"
    text += f"Last checked: {openai_status['last_checked'] or 'Never'}\n\n"
    
    text += f"Fly.io: {flyio_status['status']}\n"
    text += f"Message: {flyio_status['message']}\n"
    text += f"Last checked: {flyio_status['last_checked'] or 'Never'}\n"
    
    return text

class KeyPressFilter(QObject):
    """Event filter to capture key presses."""
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            key_event = QKeyEvent(event)
            key = key_event.key()
            
            # Check for 'C' key press (both upper and lower case)
            if key == Qt.Key.Key_C:
                update_api_console("Console shortcut key 'C' pressed")
                # Find and ensure visibility of any console in the application
                ensure_console_visibility()
                return True
                
        # Pass other events through
        return super().eventFilter(obj, event)

def ensure_console_visibility():
    """Find and ensure visibility of any console in the application."""
    global display
    
    # Try to find any widget with 'console' in its name or object name
    console_widgets = []
    
    # Look for console in display itself
    if hasattr(display, 'debug_console') and isinstance(display.debug_console, QTextEdit):
        console_widgets.append(display.debug_console)
    
    if hasattr(display, 'api_console') and isinstance(display.api_console, QTextEdit):
        console_widgets.append(display.api_console)
    
    if hasattr(display, 'console') and isinstance(display.console, QTextEdit):
        console_widgets.append(display.console)
    
    # Find all QTextEdit widgets that might be consoles
    for widget in display.findChildren(QTextEdit):
        if "console" in widget.objectName().lower() or "log" in widget.objectName().lower():
            console_widgets.append(widget)
    
    # Make all found consoles visible and ensure they have content
    for console in console_widgets:
        try:
            console.setVisible(True)
            
            # If parent widget exists, make it visible too
            parent = console.parent()
            while parent:
                parent.setVisible(True)
                parent = parent.parent()
            
            # Add a test message to the console
            if hasattr(console, 'append'):
                timestamp = datetime.now().strftime("%H:%M:%S")
                console.append(f"[{timestamp}] Console visibility ensured")
                
                # Scroll to bottom
                console.verticalScrollBar().setValue(
                    console.verticalScrollBar().maximum()
                )
                
            print(f"✅ Made console {console.objectName()} visible")
        except Exception as e:
            print(f"⚠️ Error ensuring console visibility: {e}")
    
    # If we found consoles, update global api_console reference
    if console_widgets and not hasattr(display, 'api_console'):
        display.api_console = console_widgets[0]
        print(f"✅ Updated api_console reference to {console_widgets[0].objectName()}")
    
    # If we didn't find any consoles, create one
    if not console_widgets:
        add_api_console(display)

def setup_openai_client():
    """Initialize the OpenAI client."""
    global openai_client
    
    update_api_console("Initializing OpenAI client...")
    
    # Find a suitable API key
    api_key = None
    
    # First try: Look in environment variables
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        update_api_console("Found API key in environment variables")
    
    # Second try: Look in settings file
    if not api_key:
        try:
            with open("punch_card_settings.json", 'r') as f:
                settings = json.load(f)
                api_key = settings.get("openai_api_key")
                if api_key:
                    update_api_console("Found API key in settings file")
        except:
            update_api_console("No settings file found with API key")
    
    # Third try: Use a default key from enhanced_openai_display.py
    if not api_key:
        # Check for environment variable first
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            update_api_console("Using API key from environment variable")
        else:
            # Placeholder for user to fill in
            api_key = "YOUR_API_KEY_HERE"  # Replace with your actual API key
            update_api_console("⚠️ No API key found. Please set your API key in the settings file or as an environment variable.")
    
    if api_key and api_key != "YOUR_API_KEY_HERE":
        try:
            openai_client = OpenAI(api_key=api_key)
            print(f"✅ OpenAI client initialized")
            update_api_console("✅ OpenAI client initialized successfully")
            
            # Check OpenAI API status
            check_openai_status()
            
            return True
        except Exception as e:
            error_msg = str(e)
            print(f"⚠️ Error initializing OpenAI client: {e}")
            update_api_console(f"⚠️ Error initializing OpenAI client: {error_msg[:50]}")
    else:
        print("⚠️ No OpenAI API key found")
        update_api_console("⚠️ No OpenAI API key found")
    
    return False

def generate_local_message():
    """Generate a simple local message."""
    messages = [
        "VINTAGE COMPUTING LIVES ON",
        "PUNCH CARDS: THE ORIGINAL CODE",
        "DATA PROCESSING SIMPLIFIED",
        "COMPUTING HISTORY PRESERVED",
        "IBM SYSTEMS: COMPUTING LEGENDS",
        "MAINFRAMES: COMPUTING GIANTS",
        "BINARY LOGIC: COMPUTING FOUNDATION",
        "DIGITAL REVOLUTION BEGINNINGS",
        "TECHNOLOGY EVOLUTION SNAPSHOT",
        "PROGRAMMING PIONEERS REMEMBERED"
    ]
    return random.choice(messages)

def generate_openai_message():
    """Generate message using OpenAI API."""
    global openai_client, config
    
    # Initialize client if needed
    if not openai_client and not setup_openai_client():
        update_api_console("❌ Failed to initialize OpenAI client")
        return "ERROR: COULD NOT INITIALIZE OPENAI CLIENT"
    
    # Select a prompt
    prompts = [
        "Create a short tech message about IBM punch cards",
        "Write a brief statement about vintage computing",
        "Generate a nostalgic message about early computers",
        "Write a haiku about AI and computing",
        "Create a futuristic message about computing",
        "Generate a punchy tech slogan"
    ]
    
    prompt = random.choice(prompts)
    print(f"Using OpenAI with prompt: '{prompt}'")
    update_api_console(f"Sending prompt to OpenAI: '{prompt}'")
    
    try:
        # Call the OpenAI API
        start_time = time.time()
        update_api_console("Waiting for OpenAI response...")
        
        completion = openai_client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You generate short messages for an IBM punch card display. Keep your response under 70 characters. Format in UPPERCASE only."},
                {"role": "user", "content": prompt}
            ]
        )
        end_time = time.time()
        api_time = end_time - start_time
        print(f"✅ OpenAI API response time: {api_time:.2f} seconds")
        update_api_console(f"✅ Response received in {api_time:.2f} seconds")
        
        # Adjust delay factor based on actual API response time if needed
        if api_time > 2.0 and config["delay_factor"] < 2.0:
            config["delay_factor"] = min(5.0, api_time / 2.0)
            print(f"ℹ️ Adjusted delay factor to {config['delay_factor']:.1f} based on API response time")
            update_api_console(f"ℹ️ Adjusted delay factor to {config['delay_factor']:.1f}")
            # Update timer interval if we have a display
            if display and hasattr(display, 'message_timer'):
                new_interval = calculate_message_interval()
                display.message_timer.setInterval(new_interval)
                print(f"ℹ️ Updated timer interval to {new_interval/1000:.1f} seconds")
                update_api_console(f"ℹ️ Next message in {new_interval/1000:.1f} seconds")
        
        # Get the response
        response = completion.choices[0].message.content.strip().upper()
        
        # Ensure it's not too long for the punch card
        if len(response) > 70:
            response = response[:67] + "..."
            
        update_api_console(f"Message generated: {response}")
        return response
    except Exception as e:
        print(f"⚠️ Error calling OpenAI API: {e}")
        update_api_console(f"❌ Error: {str(e)[:50]}")
        return f"ERROR: {str(e)[:60]}"

def get_database_message():
    """Get a message from the database."""
    global display, message_database, config
    
    try:
        # Try to get a message from the database
        if hasattr(display, 'message_db') and hasattr(display.message_db, 'get_random_message'):
            message = display.message_db.get_random_message()
            if message:
                print(f"✅ Retrieved message from database")
                return message
                
        # Try another approach
        elif hasattr(display, 'db') and hasattr(display.db, 'get_random_message'):
            message = display.db.get_random_message()
            if message:
                print(f"✅ Retrieved message from db interface")
                return message
                
        # Check local backup
        elif message_database:
            message_obj = random.choice(message_database)
            print(f"✅ Retrieved message from local backup")
            return message_obj["message"]
            
        # Default message if no messages found
        print("⚠️ No messages found in database")
        return "NO MESSAGES IN DATABASE"
    except Exception as e:
        print(f"⚠️ Error getting database message: {e}")
        return "ERROR: DATABASE MESSAGE RETRIEVAL FAILED"

def get_message():
    """Get a message based on the selected source."""
    global message_source
    
    if message_source == "openai":
        return generate_openai_message()
    elif message_source == "database":
        return get_database_message()
    else:  # Default to local
        return generate_local_message()

def display_next_message(display, count):
    """Display a message and increment the count."""
    print(f"--------------------------------------------------")
    print(f"Displaying message #{count}...")
    
    # Get message based on source
    message = get_message()
    print(f"Message source: {message_source}")
    print(f"Message: {message}")
    
    try:
        if hasattr(display, 'display_message'):
            # No AI prefix - just display the raw message
            display.display_message(message)
            print(f"✅ Message displayed")
            
            # Save message to database
            save_message_to_database(display, message, message_source)
        else:
            print(f"⚠️ Display does not have display_message method")
    except Exception as e:
        print(f"⚠️ Error displaying message: {e}")
    
    print(f"--------------------------------------------------")
    
    # Recalculate interval for next message if necessary
    if hasattr(display, 'message_timer'):
        current_interval = display.message_timer.interval()
        calculated_interval = calculate_message_interval()
        
        # If there's a significant difference, update the timer
        if abs(current_interval - calculated_interval) > 1000:  # 1 second difference
            display.message_timer.setInterval(calculated_interval)
            print(f"ℹ️ Adjusted message interval to {calculated_interval/1000:.1f} seconds")
    
    return count + 1

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
    """Consolidated settings dialog."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Punch Card Settings")
        self.setMinimumWidth(400)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Message Source Group
        source_group = QGroupBox("Message Source")
        source_layout = QVBoxLayout()
        
        # Radio buttons
        self.local_radio = QRadioButton("Local Generation")
        self.openai_radio = QRadioButton("OpenAI Generation")
        self.database_radio = QRadioButton("Database Messages")
        
        # Set current selection
        global message_source
        if message_source == "openai":
            self.openai_radio.setChecked(True)
        elif message_source == "database":
            self.database_radio.setChecked(True)
        else:
            self.local_radio.setChecked(True)
        
        source_layout.addWidget(self.local_radio)
        source_layout.addWidget(self.openai_radio)
        source_layout.addWidget(self.database_radio)
        source_group.setLayout(source_layout)
        main_layout.addWidget(source_group)
        
        # Timing Settings Group
        timing_group = QGroupBox("Timing Settings")
        timing_layout = QGridLayout()
        
        # Interval spinner
        timing_layout.addWidget(QLabel("Message Interval (seconds):"), 0, 0)
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(5, 60)
        self.interval_spin.setValue(config["interval"])
        timing_layout.addWidget(self.interval_spin, 0, 1)
        
        # Delay factor spinner
        timing_layout.addWidget(QLabel("API Delay Factor:"), 1, 0)
        self.delay_factor_spin = QSpinBox()
        self.delay_factor_spin.setRange(1, 5)
        self.delay_factor_spin.setValue(int(config["delay_factor"]))
        timing_layout.addWidget(self.delay_factor_spin, 1, 1)
        
        timing_group.setLayout(timing_layout)
        main_layout.addWidget(timing_group)
        
        # Options Group
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        
        # Display stats checkbox
        self.display_stats_check = QCheckBox("Display Statistics in Console")
        self.display_stats_check.setChecked(config["display_stats"])
        options_layout.addWidget(self.display_stats_check)
        
        # Save to database checkbox
        self.save_db_check = QCheckBox("Save Messages to Database")
        self.save_db_check.setChecked(config["save_to_database"])
        options_layout.addWidget(self.save_db_check)
        
        # Debug mode checkbox
        self.debug_check = QCheckBox("Debug Mode")
        self.debug_check.setChecked(config["debug_mode"])
        options_layout.addWidget(self.debug_check)
        
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # Stats display
        stats_group = QGroupBox("Message Statistics")
        stats_layout = QVBoxLayout()
        self.stats_label = QLabel(get_stats_text())
        stats_layout.addWidget(self.stats_label)
        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        self.setLayout(main_layout)
    
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
        
        # Get config settings
        settings["config"] = {
            "interval": self.interval_spin.value(),
            "delay_factor": float(self.delay_factor_spin.value()),
            "display_stats": self.display_stats_check.isChecked(),
            "save_to_database": self.save_db_check.isChecked(),
            "debug_mode": self.debug_check.isChecked()
        }
        
        return settings

def show_settings_dialog(display):
    """Show the settings dialog and update settings."""
    global message_source, config
    
    dialog = SettingsDialog()
    
    # Apply EPA-inspired style to the dialog
    UIStyleHelper.apply_settings_dialog_style(dialog)
    
    # Apply button style to buttons
    for button in dialog.findChildren(QPushButton):
        UIStyleHelper.apply_button_style(button)
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        # Get all settings
        settings = dialog.get_settings()
        
        # Get the new message source
        new_source = settings["message_source"]
        
        # If changing to OpenAI, initialize the client
        if new_source == "openai" and message_source != "openai":
            setup_openai_client()
        
        # Update the message source and config
        message_source = new_source
        config.update(settings["config"])
        
        # Update message timer interval
        if hasattr(display, 'message_timer') and display.message_timer:
            new_interval = calculate_message_interval()
            display.message_timer.setInterval(new_interval)
            print(f"✅ Message timer interval updated to {new_interval/1000:.1f} seconds")
            update_api_console(f"Message timer updated to {new_interval/1000:.1f} seconds")
        
        # Save settings
        save_settings()
        
        # Show what source was selected
        display.display_message(f"SOURCE: {message_source.upper()}")
        save_message_to_database(display, f"SOURCE: {message_source.upper()}", "system")
        update_api_console(f"Message source changed to {message_source}")
        return True
    return False

def check_database(display):
    """Check if the database is available and functioning."""
    # Check if display has a message_db attribute
    if hasattr(display, 'message_db'):
        db = display.message_db
        if db:
            db_info = str(db)
            print(f"✅ Database found: {db_info}")
            return True
    
    # Check if display has a db attribute
    if hasattr(display, 'db'):
        db = display.db
        if db:
            db_info = str(db)
            print(f"✅ Database found: {db_info}")
            return True
    
    # No database found, create a simple one
    print("⚠️ No database found, will use local backup")
    return False

def initialize_database(display):
    """Initialize or create a database interface."""
    # Check if the display already has a database interface
    if hasattr(display, 'message_db') and display.message_db:
        print("✅ Using existing message database")
        return True
        
    # If not, create a simple database interface and attach it to the display
    try:
        class SimpleMessageDB:
            def __init__(self):
                self.messages = []
                self.max_messages = 1000
                
            def add_message(self, message, source="Unknown"):
                """Add a message to the database."""
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                self.messages.append({
                    "message": message,
                    "source": source,
                    "timestamp": timestamp
                })
                # Keep only the latest N messages
                if len(self.messages) > self.max_messages:
                    self.messages = self.messages[-self.max_messages:]
                return True
                
            def get_random_message(self):
                """Get a random message from the database."""
                if not self.messages:
                    return None
                message_obj = random.choice(self.messages)
                return message_obj["message"]
                
            def get_messages(self, limit=10):
                """Get the latest messages."""
                return self.messages[-limit:]
                
            def __str__(self):
                return f"SimpleMessageDB with {len(self.messages)} messages"
        
        # Create and attach the database
        if not hasattr(display, 'message_db'):
            display.message_db = SimpleMessageDB()
            display.message_db.max_messages = 1000
            print(f"✅ Created simple message database (max 1000 msgs)")
            
            # If there are existing messages in our global variable, add them to the new DB
            global message_database
            for msg in message_database:
                display.message_db.add_message(msg["message"], msg["source"])
            
            return True
    except Exception as e:
        print(f"⚠️ Error creating message database: {e}")
        return False

def calculate_message_interval():
    """Calculate message interval based on source and settings."""
    global message_source, config
    
    base_interval = config["interval"] * 1000  # convert to milliseconds
    
    # If using OpenAI, might need more time for API calls
    if message_source == "openai":
        return int(base_interval * config["delay_factor"])
    
    return base_interval

def update_api_console(message):
    """Update the API console with a message."""
    global display, config
    
    # Always update console regardless of debug mode
    # Print to terminal as well to aid debugging
    print(f"API Console: {message}")
    
    # First try to find any debug console that appears when pressing 'C'
    if hasattr(display, 'debug_console') and hasattr(display.debug_console, 'append'):
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            display.debug_console.setVisible(True)
            display.debug_console.append(f"[{timestamp}] {message}")
            
            # Make sure to scroll to the bottom
            try:
                display.debug_console.verticalScrollBar().setValue(
                    display.debug_console.verticalScrollBar().maximum()
                )
            except Exception as e:
                print(f"⚠️ Error scrolling debug_console: {e}")
            
            # If parent is hidden, make it visible
            if hasattr(display.debug_console, 'parent') and display.debug_console.parent():
                display.debug_console.parent().setVisible(True)
            
            return True
        except Exception as e:
            print(f"⚠️ Error updating debug console: {e}")
    
    # Then try normal api_console
    try:
        # Method 1: Use api_console if available
        if hasattr(display, 'api_console') and hasattr(display.api_console, 'append'):
            timestamp = datetime.now().strftime("%H:%M:%S")
            # Force console to be visible if it's not
            display.api_console.setVisible(True)
            
            # Add the message
            display.api_console.append(f"[{timestamp}] {message}")
            
            # Make sure to scroll to the bottom to show the latest message
            try:
                display.api_console.verticalScrollBar().setValue(
                    display.api_console.verticalScrollBar().maximum()
                )
            except Exception as e:
                print(f"⚠️ Error scrolling console: {e}")
                
            # If parent is hidden, make it visible
            if hasattr(display.api_console, 'parent') and display.api_console.parent():
                display.api_console.parent().setVisible(True)
                
            return True
            
        # Method 2: Use console_output if available
        elif hasattr(display, 'console_output') and hasattr(display.console_output, 'append'):
            timestamp = datetime.now().strftime("%H:%M:%S")
            display.console_output.setVisible(True)
            display.console_output.append(f"[{timestamp}] {message}")
            
            # Make sure to scroll to the bottom
            try:
                display.console_output.verticalScrollBar().setValue(
                    display.console_output.verticalScrollBar().maximum()
                )
            except Exception as e:
                print(f"⚠️ Error scrolling console_output: {e}")
                
            return True
            
        # Method 3: Update status_label if available
        elif hasattr(display, 'status_label') and hasattr(display.status_label, 'setText'):
            timestamp = datetime.now().strftime("%H:%M:%S")
            current_text = display.status_label.text()
            # Limit to last 5 lines
            lines = current_text.split('\n')[-4:] if current_text else []
            lines.append(f"[{timestamp}] {message}")
            display.status_label.setText('\n'.join(lines))
            display.status_label.setVisible(True)
            return True
            
        # Method 4: Look for any console-like widget
        for widget in display.findChildren(QTextEdit):
            if "console" in widget.objectName().lower() or "log" in widget.objectName().lower():
                timestamp = datetime.now().strftime("%H:%M:%S")
                widget.setVisible(True)
                if hasattr(widget, 'append'):
                    widget.append(f"[{timestamp}] {message}")
                    
                    # Make sure to scroll to the bottom
                    try:
                        widget.verticalScrollBar().setValue(
                            widget.verticalScrollBar().maximum()
                        )
                    except Exception as e:
                        print(f"⚠️ Error scrolling found console: {e}")
                    
                    return True
    except Exception as e:
        print(f"⚠️ Error updating API console: {e}")
    
    return False

def add_api_console(display):
    """Add an API console to the display."""
    from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QWidget, QLabel, QFrame
    
    # Check if display already has an api_console
    if hasattr(display, 'api_console'):
        print("✅ Display already has an API console")
        update_api_console("API Console ready")
        
        # Make sure it's visible
        display.api_console.setVisible(True)
        if hasattr(display.api_console, 'parent') and display.api_console.parent():
            display.api_console.parent().setVisible(True)
            
        return True
        
    # Check if display has debug_console (used by 'C' key)
    if hasattr(display, 'debug_console'):
        print("✅ Using existing debug_console as API console")
        display.api_console = display.debug_console
        update_api_console("API Console ready (using debug console)")
        
        # Make sure it's visible
        display.api_console.setVisible(True)
        if hasattr(display.api_console, 'parent') and display.api_console.parent():
            display.api_console.parent().setVisible(True)
            
        return True
    
    try:
        # Create a console widget with more visibility
        console = QTextEdit()
        console.setObjectName("api_console")
        console.setReadOnly(True)
        console.setMinimumHeight(200)
        console.setMaximumHeight(300)
        
        # Add initial text to make it obvious
        console.setText("=== API CONSOLE ===\n\nInitialized: " + 
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                        "\n\nThis console shows API status and messages.\n\n")
        
        # Apply dark style to console for better readability
        UIStyleHelper.apply_console_style(console)
        
        # Add a heading
        heading = QLabel("API Console")
        heading.setObjectName("api_console_heading")
        UIStyleHelper.apply_heading_style(heading)
        
        # Create a container with a border to make it more visible
        console_container = QFrame()
        console_container.setObjectName("api_console_container")
        console_container.setFrameShape(QFrame.Shape.Box)
        console_container.setFrameShadow(QFrame.Shadow.Raised)
        console_container.setLineWidth(2)
        console_container.setStyleSheet(f"""
            background-color: {UIStyleHelper.COLORS['bg']};
            border: 2px solid {UIStyleHelper.COLORS['accent']};
            border-radius: 5px;
            margin: 5px;
        """)
        
        console_layout = QVBoxLayout(console_container)
        console_layout.setContentsMargins(10, 5, 10, 10)
        console_layout.addWidget(heading)
        console_layout.addWidget(console)
        
        # If the display has a layout, try to add the console to it
        added = False
        if hasattr(display, 'layout') and display.layout():
            try:
                # Try to add to the main layout
                display.layout().insertWidget(0, console_container)
                display.api_console = console
                print("✅ Added API console to main layout")
                added = True
            except Exception as e:
                print(f"⚠️ Error adding to main layout: {e}")
        
        # If there's a control layout and we haven't added it yet
        if not added and hasattr(display, 'control_layout'):
            try:
                display.control_layout.insertWidget(0, console_container)
                display.api_console = console
                print("✅ Added API console to control layout")
                added = True
            except Exception as e:
                print(f"⚠️ Error adding to control layout: {e}")
            
        # If there's a button container and we haven't added it yet
        if not added and hasattr(display, 'button_container') and display.button_container.parentWidget():
            try:
                parent = display.button_container.parentWidget()
                parent_layout = parent.layout()
                
                if parent_layout:
                    parent_layout.insertWidget(0, console_container)
                    display.api_console = console
                    print("✅ Added API console next to button container")
                    added = True
            except Exception as e:
                print(f"⚠️ Error adding next to button container: {e}")
        
        # Last resort - try to add it to a central widget
        if not added and hasattr(display, 'centralWidget') and display.centralWidget():
            try:
                central_widget = display.centralWidget()
                if central_widget.layout():
                    central_widget.layout().insertWidget(0, console_container)
                    display.api_console = console
                    print("✅ Added API console to central widget")
                    added = True
            except Exception as e:
                print(f"⚠️ Error adding to central widget: {e}")
        
        if not added:
            print("⚠️ Could not find a suitable place to add API console")
            return False
        
        # Add service status information
        update_api_console(get_service_status_text())
        
        # Make sure to verify the console was added
        if hasattr(display, 'api_console'):
            # Force update with a test message
            update_api_console("API Console initialization confirmed")
            return True
        else:
            print("⚠️ API console was not properly attached to display")
            return False
    except Exception as e:
        print(f"⚠️ Error adding API console: {e}")
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
    global message_source, config
    
    # Only change if different
    if message_source != source:
        # If changing to OpenAI, initialize the client
        if source == "openai" and not openai_client:
            setup_openai_client()
        
        # Update message source
        message_source = source
        
        # Update display
        if hasattr(display, 'display_message'):
            display.display_message(f"SOURCE: {source.upper()}")
            save_message_to_database(display, f"SOURCE: {source.upper()}", "system")
            update_api_console(f"Message source changed to {source}")
        
        # Update timer interval if needed
        if hasattr(display, 'message_timer') and display.message_timer:
            new_interval = calculate_message_interval()
            display.message_timer.setInterval(new_interval)
            print(f"✅ Message timer interval updated to {new_interval/1000:.1f} seconds")
            update_api_console(f"Message timer updated to {new_interval/1000:.1f} seconds")
        
        # Save settings
        save_settings()
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description='Simple Punch Card Display')
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
        setup_openai_client()
    
    # Start the GUI
    try:
        global display
        display, app = gui_main()  # gui_main returns both display and app
        
        # Apply global style to the application
        UIStyleHelper.apply_global_style(app)
        
        # Install an event filter to capture key presses
        key_filter = KeyPressFilter(app)
        app.installEventFilter(key_filter)
        
        # Set window title to include source
        if hasattr(display, 'setWindowTitle'):
            display.setWindowTitle(f"Punch Card Display - {message_source.upper()} Mode")
    except Exception as e:
        print(f"⚠️ Error starting GUI: {e}")
        return
    
    # Add API console for message display - do this before adding menu bar
    # to ensure console is available for status updates
    add_api_console(display)
    
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
    
    # Find out if display is a QMainWindow (supports menu bar)
    from PyQt6.QtWidgets import QMainWindow
    is_main_window = isinstance(display, QMainWindow)
    print(f"Display is a QMainWindow: {is_main_window}")
    
    # Add menu bar (classic Mac style)
    try:
        if is_main_window and hasattr(display, 'setMenuBar'):
            menu_bar = UIStyleHelper.create_menu_bar(display)
            display.setMenuBar(menu_bar)
            print("✅ Added classic Mac-style menu bar")
            update_api_console("Added Mac-style menu bar")
        else:
            print("⚠️ Cannot add menu bar (not a QMainWindow)")
            update_api_console("Creating button toolbar instead of menu bar")
            
            # Create a more visible button toolbar at the top
            from PyQt6.QtWidgets import QHBoxLayout, QWidget, QPushButton, QFrame
            
            # Create a frame with a border for visibility
            menu_container = QFrame()
            menu_container.setFrameShape(QFrame.Shape.Panel)
            menu_container.setFrameShadow(QFrame.Shadow.Raised)
            menu_container.setLineWidth(2)
            menu_layout = QHBoxLayout(menu_container)
            menu_layout.setContentsMargins(5, 5, 5, 5)
            menu_layout.setSpacing(5)
            
            # Apply distinct styling to make it visible
            menu_container.setStyleSheet(f"""
                background-color: {UIStyleHelper.COLORS['button_bg']};
                border: 2px solid {UIStyleHelper.COLORS['accent']};
                border-bottom: 1px solid {UIStyleHelper.COLORS['border']};
                margin: 0px;
                padding: 5px;
                min-height: 40px;
            """)
            
            # Add menu-style buttons with fixed sizes to prevent cutting off
            settings_btn = QPushButton("Settings")
            settings_btn.setFixedSize(100, 30)  # Fixed size to prevent cutting off
            settings_btn.clicked.connect(lambda: show_settings_dialog(display))
            UIStyleHelper.apply_button_style(settings_btn)
            menu_layout.addWidget(settings_btn)
            
            # Add a console toggle button
            console_btn = QPushButton("Console")
            console_btn.setFixedSize(100, 30)
            console_btn.clicked.connect(lambda: ensure_console_visibility())
            UIStyleHelper.apply_button_style(console_btn)
            menu_layout.addWidget(console_btn)
            
            # Add source buttons with fixed sizes
            local_btn = QPushButton("Local")
            local_btn.setFixedSize(100, 30)
            local_btn.clicked.connect(lambda: set_message_source(display, "local"))
            UIStyleHelper.apply_button_style(local_btn)
            menu_layout.addWidget(local_btn)
            
            openai_btn = QPushButton("OpenAI")
            openai_btn.setFixedSize(100, 30)
            openai_btn.clicked.connect(lambda: set_message_source(display, "openai"))
            UIStyleHelper.apply_button_style(openai_btn)
            menu_layout.addWidget(openai_btn)
            
            db_btn = QPushButton("Database")
            db_btn.setFixedSize(100, 30)
            db_btn.clicked.connect(lambda: set_message_source(display, "database"))
            UIStyleHelper.apply_button_style(db_btn)
            menu_layout.addWidget(db_btn)
            
            # Add spacer to push buttons to the left
            menu_layout.addStretch()
            
            # Try different approaches to add it to the top of the layout
            added = False
            
            # Approach 1: Add to main layout if it exists
            if hasattr(display, 'layout') and display.layout():
                try:
                    display.layout().insertWidget(0, menu_container)
                    added = True
                    print("✅ Added menu button bar to main layout")
                except Exception as e:
                    print(f"⚠️ Error adding menu to main layout: {e}")
            
            # Approach 2: Add to the central widget if it exists
            if not added and hasattr(display, 'centralWidget') and display.centralWidget():
                try:
                    central_widget = display.centralWidget()
                    if central_widget.layout():
                        central_widget.layout().insertWidget(0, menu_container)
                        added = True
                        print("✅ Added menu button bar to central widget")
                except Exception as e:
                    print(f"⚠️ Error adding menu to central widget: {e}")
            
            # Approach 3: If display has a parent, try adding to parent
            if not added and hasattr(display, 'parent') and display.parent():
                try:
                    parent = display.parent()
                    if parent.layout():
                        parent.layout().insertWidget(0, menu_container)
                        added = True
                        print("✅ Added menu button bar to parent widget")
                except Exception as e:
                    print(f"⚠️ Error adding menu to parent widget: {e}")
            
            if added:
                # Store reference
                display.menu_container = menu_container
                update_api_console("Added button toolbar at top")
            else:
                print("⚠️ Could not add menu button bar to any layout")
                update_api_console("Failed to add button toolbar")
    except Exception as e:
        print(f"⚠️ Error adding menu bar: {e}")
        update_api_console(f"Error adding menu bar: {str(e)[:50]}")

    # Apply styling to UI elements with black background
    style_ui_elements(display)
    
    # Check and initialize database
    check_database(display)
    initialize_database(display)
    
    # Verify database functionality
    if hasattr(display, 'message_db'):
        update_api_console(f"Database active: {len(display.message_db.messages)} messages")
    else:
        update_api_console("⚠️ Using local backup (no database)")
    
    # Set up signal handling for graceful termination
    def signal_handler(sig, frame):
        print("Signal received, shutting down...")
        update_api_console("Shutting down...")
        app.quit()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Disable auto-messages and stop timers
    print("✅ Disabling auto-messages and stopping timers")
    try:
        if hasattr(display, 'disable_auto_messages'):
            display.disable_auto_messages()
        
        # Stop any timers
        for attr_name in dir(display):
            if attr_name.endswith('_timer') and hasattr(getattr(display, attr_name), 'stop'):
                timer = getattr(display, attr_name)
                timer.stop()
                print(f"✅ Stopped timer: {attr_name}")
    except Exception as e:
        print(f"⚠️ Error disabling auto-messages: {e}")
    
    # If we added a menu bar, we don't need to add separate Settings button
    if not hasattr(display, 'menu_container') and not hasattr(display, 'setMenuBar'):
        # Add Settings button if display has button_container
        if hasattr(display, 'add_control_button'):
            display.add_control_button("Settings", lambda: show_settings_dialog(display))
            print("✅ Added Settings button via add_control_button")
            
            # Apply style to any buttons added by add_control_button
            control_buttons = display.findChildren(QPushButton)
            for button in control_buttons:
                UIStyleHelper.apply_button_style(button)
                # Make sure button is sized properly
                button.setMinimumSize(100, 30)
                
        elif hasattr(display, 'button_container'):
            try:
                # Create settings button with clear styling
                settings_button = QPushButton("Settings")
                settings_button.setFixedSize(100, 30)  # Fixed size to prevent cutting off
                settings_button.clicked.connect(lambda: show_settings_dialog(display))
                
                # Add button to container
                display.button_container.layout().addWidget(settings_button)
                
                # Apply styling
                UIStyleHelper.apply_button_style(settings_button)
                
                # Make button accessible
                settings_button.setToolTip("Open settings dialog")
                
                # Store reference
                display.settings_button = settings_button
                print("✅ Added Settings button to button container")
            except Exception as e:
                print(f"⚠️ Error adding settings button: {e}")
    
    # Apply styling to entire window and all widgets for black background
    try:
        # Import all widget types we need to style
        from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QTextEdit, QMainWindow
        
        # Explicitly set background for all widgets
        for widget in display.findChildren(QWidget):
            if not isinstance(widget, QPushButton):  # Skip buttons as they have specific styling
                widget.setStyleSheet(f"""
                    background-color: {UIStyleHelper.COLORS['bg']};
                    color: {UIStyleHelper.COLORS['fg']};
                """)
        
        # Make sure the main window background is black
        if hasattr(display, 'setStyleSheet'):
            display.setStyleSheet(f"""
                background-color: {UIStyleHelper.COLORS['bg']};
                color: {UIStyleHelper.COLORS['fg']};
                border: none;
            """)
        
        # Apply style to the central widget if it exists
        if hasattr(display, 'centralWidget') and display.centralWidget():
            display.centralWidget().setStyleSheet(f"""
                background-color: {UIStyleHelper.COLORS['bg']};
                color: {UIStyleHelper.COLORS['fg']};
                border: none;
            """)
            
        # Ensure all labels have white text
        for label in display.findChildren(QLabel):
            label.setStyleSheet(f"""
                color: {UIStyleHelper.COLORS['fg']};
                background-color: transparent;
                border: none;
            """)
            
        # Make sure any QTextEdit components have the proper styling
        for text_edit in display.findChildren(QTextEdit):
            UIStyleHelper.apply_console_style(text_edit)
            
        # Apply styling to all buttons to ensure they're not cut off
        for button in display.findChildren(QPushButton):
            UIStyleHelper.apply_button_style(button)
            if not button.minimumWidth() or button.minimumWidth() < 80:
                button.setMinimumWidth(80)
            if not button.minimumHeight() or button.minimumHeight() < 28:
                button.setMinimumHeight(28)
                
        # Special style for the card display area if it exists
        if hasattr(display, 'card_display'):
            display.card_display.setStyleSheet(f"""
                background-color: {UIStyleHelper.COLORS['bg']};
                color: {UIStyleHelper.COLORS['fg']};
                border: 1px solid {UIStyleHelper.COLORS['border']};
                font-family: {UIStyleHelper.FONTS['monospace']};
                font-size: {UIStyleHelper.FONTS['size_large']};
                padding: 10px;
            """)
            
        print("✅ Applied black background to all components")
    except Exception as e:
        print(f"⚠️ Error applying black background: {e}")
    
    # Additional styling for the content area to ensure black background
    try:
        # Find content/display widgets and ensure they're black
        content_widgets = [w for w in display.findChildren(QWidget) 
                         if any(name in w.objectName().lower() 
                               for name in ['content', 'display', 'card', 'message'])]
        
        for widget in content_widgets:
            widget.setStyleSheet(f"""
                background-color: {UIStyleHelper.COLORS['bg']};
                color: {UIStyleHelper.COLORS['fg']};
                border: none;
            """)
        
        # If there's a layout, ensure all widgets in it have proper styling
        if hasattr(display, 'layout') and display.layout():
            for i in range(display.layout().count()):
                item = display.layout().itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if not isinstance(widget, QPushButton):
                        widget.setStyleSheet(f"""
                            background-color: {UIStyleHelper.COLORS['bg']};
                            color: {UIStyleHelper.COLORS['fg']};
                            border: none;
                        """)
    except Exception as e:
        print(f"⚠️ Error applying additional styling: {e}")
        
    # Display initial message
    try:
        if hasattr(display, 'display_message'):
            print("✅ Display has display_message method")
            welcome_message = f"PUNCH CARD - {message_source.upper()} MODE"
            display.display_message(welcome_message)
            update_api_console(f"Welcome to Punch Card - {message_source.upper()} mode")
            
            # Save welcome message to database with correct source format
            try:
                save_message_to_database(display, welcome_message, "system")
                print("✅ Welcome message saved to database")
            except Exception as e:
                print(f"⚠️ Error saving welcome message: {e}")
        else:
            print("⚠️ Display does not have display_message method")
    except Exception as e:
        print(f"⚠️ Error displaying initial message: {e}")

    # Create a message counter that persists across timer callbacks
    message_count = [0]
    
    # Set up a timer for displaying messages with dynamic interval
    message_timer = QTimer()
    message_timer.timeout.connect(lambda: message_count.__setitem__(0, display_next_message(display, message_count[0])))
    
    # Store message timer in display for later adjustment
    display.message_timer = message_timer
    
    # Start timer with calculated interval
    interval_ms = calculate_message_interval()
    message_timer.start(interval_ms)
    
    print(f"✅ Message timer started with {interval_ms/1000:.1f} second interval")
    update_api_console(f"Message timer started ({interval_ms/1000:.1f}s interval)")
    update_api_console("Press 'C' to show API console at any time")
    print("✅ Running event loop. Press Ctrl+C to exit.")
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 