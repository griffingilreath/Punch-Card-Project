#!/usr/bin/env python3
"""
Enhanced OpenAI Punch Card Display

This script provides a sophisticated GUI for the punch card display with
complete OpenAI integration, model selection, and customization options.
"""

import sys
import os
import json
import time
import random
import argparse
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Callable
import platform
import threading
import traceback
import signal
import queue
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QComboBox, QTabWidget, QSlider, QCheckBox,
    QSpinBox, QLineEdit, QGroupBox, QFormLayout, QDialog, QDialogButtonBox,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer, QSettings, QObject, pyqtSignal, pyqtSlot
from src.display.gui_display import main as gui_main

# Settings data class for type safety and easy serialization
@dataclass
class PunchCardSettings:
    # Message source settings
    message_source: str = "openai"  # "local", "openai", "database"
    
    # OpenAI settings
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_prompts: List[str] = field(default_factory=lambda: [
        "Create a short tech message about IBM punch cards",
        "Write a brief statement about vintage computing",
        "Generate a nostalgic message about early computers",
        "Write a haiku about AI and computing",
        "Create a futuristic message about computing",
        "Generate a punchy tech slogan",
        "Create a message about data processing"
    ])
    
    # Display settings
    message_prefix: str = "[AI]"
    display_delay: int = 150  # milliseconds between characters
    message_interval: int = 15  # seconds between messages
    
    # Database settings
    save_to_database: bool = True
    message_limit: int = 100  # max messages to store

# Global variables
settings = PunchCardSettings()
openai_client = None
display = None
message_thread = None
settings_filename = "punch_card_settings.json"
# Thread-safe message queue
message_queue = queue.Queue()
# Simple in-memory message database if no other DB is available
message_database = []
# Flag to signal when we're shutting down
shutting_down = False

# Thread-safe signal handler for GUI updates
class MessageSignalHandler(QObject):
    # Define a signal with message and source parameters
    message_signal = pyqtSignal(str, str, int)
    
    def __init__(self):
        super().__init__()

# Create a global signal handler
signal_handler = MessageSignalHandler()

def load_settings() -> PunchCardSettings:
    """Load settings from file."""
    global settings, settings_filename
    
    # Default settings
    settings = PunchCardSettings()
    
    # Try to load from file
    try:
        if os.path.exists(settings_filename):
            with open(settings_filename, 'r') as f:
                loaded_data = json.load(f)
                # Update settings with loaded values
                for key, value in loaded_data.items():
                    if hasattr(settings, key):
                        setattr(settings, key, value)
            print(f"✅ Settings loaded from {settings_filename}")
    except Exception as e:
        print(f"⚠️ Error loading settings: {e}")
    
    return settings

def save_settings():
    """Save settings to file."""
    global settings, settings_filename
    
    try:
        with open(settings_filename, 'w') as f:
            json.dump(asdict(settings), f, indent=2)
        print(f"✅ Settings saved to {settings_filename}")
    except Exception as e:
        print(f"⚠️ Error saving settings: {e}")

def update_api_status(message: str, success: bool = True):
    """Update API status in the console and status label."""
    global display
    
    # Format status with timestamp
    timestamp = time.strftime("%H:%M:%S")
    status_message = f"[{timestamp}] {'✅' if success else '❌'} {message}"
    print(status_message)
    
    # Update the API console if available
    if display:
        # Update status label if available
        if hasattr(display, 'api_status_label') and display.api_status_label:
            try:
                display.api_status_label.setText(status_message)
            except Exception as e:
                print(f"Error updating status label: {e}")
        
        # Add to console if available
        if hasattr(display, 'api_console'):
            try:
                # Check if it's a text widget
                if hasattr(display.api_console, 'toPlainText'):
                    # Append to console
                    current_text = display.api_console.toPlainText()
                    if current_text:
                        new_text = current_text + "\n" + status_message
                    else:
                        new_text = status_message
                    display.api_console.setPlainText(new_text)
                    # Scroll to bottom
                    display.api_console.verticalScrollBar().setValue(
                        display.api_console.verticalScrollBar().maximum()
                    )
                # If it's a window with a text area
                elif hasattr(display.api_console, 'console') and hasattr(display.api_console.console, 'append'):
                    display.api_console.console.append(status_message)
                # If it has an append method directly
                elif hasattr(display.api_console, 'append'):
                    display.api_console.append(status_message)
            except Exception as e:
                # Just log but don't crash - we don't want console updates to break functionality
                print(f"Note: API console update failed: {e}")
        
        # Show API console if hidden (optional)
        if hasattr(display, 'show_api_console') and callable(display.show_api_console):
            try:
                display.show_api_console()
            except Exception as e:
                print(f"Note: Could not show API console: {e}")

def setup_openai_client():
    """Set up the OpenAI client with the current API key."""
    global openai_client, settings
    
    # Find a suitable API key
    api_key = None
    
    # First try: Check environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        update_api_status("Found API key in environment variables", True)
        settings.openai_api_key = api_key
    
    # Second try: Check secrets file
    if not api_key:
        try:
            secrets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                       "secrets", "api_keys.json")
            if os.path.exists(secrets_path):
                with open(secrets_path, 'r') as f:
                    secrets = json.load(f)
                    api_key = secrets.get("openai", {}).get("api_key")
                    if api_key and api_key not in ["YOUR_OPENAI_API_KEY_HERE", "YOUR_ACTUAL_API_KEY_HERE"]:
                        settings.openai_api_key = api_key
                        update_api_status("Found API key in secrets file", True)
        except Exception as e:
            update_api_status(f"Error reading secrets file: {str(e)[:50]}", False)
    
    # Third try: Use existing key in settings
    if not api_key and settings.openai_api_key and settings.openai_api_key not in ["YOUR_OPENAI_API_KEY_HERE", "YOUR_ACTUAL_API_KEY_HERE"]:
        api_key = settings.openai_api_key
        update_api_status("Using existing API key from settings", True)
    
    # Safety check
    if not api_key or api_key in ["YOUR_API_KEY_HERE", "YOUR_ACTUAL_API_KEY_HERE"]:
        update_api_status("⚠️ No valid API key found. Please set your API key in the settings, secrets file, or as an environment variable.", False)
        return False
    
    try:
        openai_client = OpenAI(api_key=settings.openai_api_key)
        update_api_status("OpenAI client initialized successfully", True)
        return True
    except Exception as e:
        update_api_status(f"Error setting up OpenAI client: {e}", False)
        return False

def generate_openai_message() -> str:
    """Generate a message using OpenAI API."""
    global openai_client, settings
    
    if not openai_client and not setup_openai_client():
        update_api_status("OpenAI client not initialized", False)
        return "ERROR: OPENAI CLIENT NOT INITIALIZED"
    
    # Select a random prompt
    prompt = random.choice(settings.openai_prompts)
    print(f"Prompt: '{prompt}'")
    update_api_status(f"Using model: {settings.openai_model}", True)
    
    try:
        start_time = time.time()
        # Make the API request
        completion = openai_client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You generate short messages for an IBM punch card display. Keep your response under 70 characters. Format in UPPERCASE only."},
                {"role": "user", "content": prompt}
            ]
        )
        end_time = time.time()
        
        # Get message content
        response = completion.choices[0].message.content.strip().upper()
        
        # Replace any linebreaks with spaces
        response = response.replace("\n", " ")
        
        # Ensure it's not too long for the punch card (max 80 chars)
        if len(response) > 70:
            response = response[:67] + "..."
            
        update_api_status(f"Response received in {end_time - start_time:.2f} sec", True)
        
        return response
    except Exception as e:
        update_api_status(f"Error calling OpenAI API: {e}", False)
        return f"ERROR: OPENAI API CALL FAILED"

def generate_local_message() -> str:
    """Generate a message locally."""
    vintage_terms = [
        "BATCH", "JOB", "TASK", "PROCESS", "QUEUE", "STACK", "BUFFER",
        "MEMORY", "STORAGE", "PROCESSOR", "COMPUTER", "SYSTEM", "PROGRAM",
        "ROUTINE", "SUBROUTINE", "FUNCTION", "MODULE", "COMPILE", "ASSEMBLE"
    ]
    
    verbs = [
        "PROCESSING", "EXECUTING", "RUNNING", "COMPILING", "LOADING", "SAVING",
        "ANALYZING", "CALCULATING", "COMPUTING", "FORMATTING", "READING"
    ]
    
    objects = [
        "DATA", "PROGRAM", "CODE", "FILE", "RECORD", "SYSTEM", "MODULE",
        "MEMORY", "DISK", "CARD", "BATCH", "JOB", "TASK"
    ]
    
    status = [
        "COMPLETE", "READY", "WAITING", "PROCESSING", "ERROR", "SUCCESS",
        "VERIFIED", "OPTIMIZED", "LOADED", "ANALYZED"
    ]
    
    # Build a message
    parts = []
    
    # 70% chance to include a term
    if random.random() < 0.7:
        parts.append(random.choice(vintage_terms))
    
    # 80% chance to include a verb
    if random.random() < 0.8:
        parts.append(random.choice(verbs))
    
    # 70% chance to include an object
    if random.random() < 0.7:
        parts.append(random.choice(objects))
    
    # 50% chance to include a status
    if random.random() < 0.5:
        parts.append(random.choice(status))
    
    # Ensure we have at least 2 parts
    while len(parts) < 2:
        parts.append(random.choice(vintage_terms))
    
    # 30% chance to add a random number
    if random.random() < 0.3:
        parts.append(str(random.randint(1, 9999)))
    
    # Assemble the message
    message = " ".join(parts)
    
    # 80% chance to add a period
    if random.random() < 0.8:
        message += "."
    
    return message

def initialize_database():
    """Initialize or create a database interface."""
    global display, message_database
    
    # Check if the display already has a database interface
    if hasattr(display, 'message_db') and display.message_db:
        update_api_status("Using existing message database", True)
        return True
        
    # If not, create a simple database interface and attach it to the display
    try:
        class SimpleMessageDB:
            def __init__(self):
                self.messages = []
                self.max_messages = 100
                
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
            display.message_db.max_messages = settings.message_limit
            update_api_status(f"Created simple message database (max {settings.message_limit} msgs)", True)
            
            # If there are existing messages in our global variable, add them to the new DB
            for msg, src in message_database:
                display.message_db.add_message(msg, src)
            
            return True
    except Exception as e:
        update_api_status(f"Error creating message database: {e}", False)
        return False

def get_random_database_message(display) -> str:
    """Get a random message from the database."""
    try:
        # Try to access the database through the display object
        if hasattr(display, 'message_db') and hasattr(display.message_db, 'get_random_message'):
            message = display.message_db.get_random_message()
            if message:
                update_api_status("Retrieved message from database", True)
                return message
            
        # Fallback approach - try to access the display's message history
        if hasattr(display, 'message_history') and display.message_history:
            message = random.choice(display.message_history)
            update_api_status("Retrieved message from history", True)
            return message
        
        # Default message if no messages found
        update_api_status("No messages found in database", False)
        return "NO MESSAGES IN DATABASE"
    except Exception as e:
        update_api_status(f"Error getting database message: {e}", False)
        return "ERROR: DATABASE MESSAGE RETRIEVAL FAILED"

def save_message_to_database(display, message: str, source: str):
    """Save a message to the database."""
    global message_database
    
    if not settings.save_to_database:
        return
    
    try:
        # Try multiple approaches to save to database
        if hasattr(display, 'message_db') and hasattr(display.message_db, 'add_message'):
            display.message_db.add_message(message, source)
            update_api_status(f"Message saved to database: {message[:20]}...", True)
            return True
            
        elif hasattr(display, 'db') and hasattr(display.db, 'save_message'):
            display.db.save_message(message, source)
            update_api_status(f"Message saved via db interface: {message[:20]}...", True)
            return True
            
        elif hasattr(display, 'save_message_to_history'):
            display.save_message_to_history(message, source)
            update_api_status(f"Message saved to history: {message[:20]}...", True)
            return True
            
        else:
            # Save to our in-memory database as a backup
            message_database.append((message, source))
            update_api_status(f"Message saved to in-memory backup: {message[:20]}...", True)
            
            # Try to create a database the next time
            initialize_database()
            return True
    except Exception as e:
        update_api_status(f"Error saving message to database: {e}", False)
        return False

def signal_handler_function(sig, frame):
    """Handle termination signals gracefully."""
    global shutting_down
    
    print("\nReceived termination signal. Exiting safely...")
    shutting_down = True
    
    # Give threads a chance to exit
    time.sleep(1)
    sys.exit(0)

def message_producer():
    """Generate messages in a background thread and put them in the queue."""
    global settings, message_queue, shutting_down
    
    try:
        message_count = 0
        while not shutting_down:
            try:
                message_count += 1
                print("-" * 50)
                print(f"Generating message #{message_count}...")
                
                # Generate message based on selected source
                if settings.message_source == "openai":
                    message = generate_openai_message()
                    source = f"OpenAI: {settings.openai_model}"
                elif settings.message_source == "database":
                    message = get_random_database_message(display)
                    source = "Database"
                else:  # Local generation
                    message = generate_local_message()
                    source = "Local Generator"
                
                # Add prefix if it fits
                if settings.message_prefix and len(settings.message_prefix) + len(message) + 1 <= 80:
                    prefixed_message = f"{settings.message_prefix} {message}"
                else:
                    prefixed_message = message
                
                print(f"Generating: {prefixed_message}")
                print(f"Source: {source}")
                print("-" * 50)
                
                # Check if we're shutting down
                if shutting_down:
                    break
                
                # Instead of directly calling display_message, use the signal
                # This safely communicates between threads
                try:
                    signal_handler.message_signal.emit(
                        prefixed_message, 
                        source, 
                        settings.display_delay
                    )
                except Exception as e:
                    print(f"Failed to emit signal: {e}")
                    # Try direct update as a fallback, but in the main thread
                    QTimer.singleShot(0, lambda: direct_update_message(prefixed_message, source))
                
                # Save to database if enabled and not already from database
                if settings.message_source != "database" and settings.save_to_database:
                    # We can't directly call save_message_to_database here
                    # Instead, add the message to the queue for processing in the main thread
                    message_queue.put((prefixed_message, source))
                
                # Wait for next message
                print(f"Waiting {settings.message_interval} seconds before next message...")
                for _ in range(settings.message_interval):
                    if shutting_down:
                        break
                    time.sleep(1)
            except Exception as e:
                # Catch exceptions within the loop to keep the thread alive
                update_api_status(f"Error generating message #{message_count}: {e}", False)
                print(f"Exception details: {traceback.format_exc()}")
                # Wait a bit before retrying
                time.sleep(5)
    except Exception as e:
        update_api_status(f"Thread terminated with error: {e}", False)
        print(f"Thread exception details: {traceback.format_exc()}")

def direct_update_message(message, source):
    """Update the message directly in the main thread."""
    global display
    
    try:
        if display and hasattr(display, 'message_label'):
            display.message_label.setText(message)
            if hasattr(display, 'source_label'):
                display.source_label.setText(source)
                
        update_api_status(f"Direct message update: {message[:30]}...", True)
    except Exception as e:
        print(f"Error in direct message update: {e}")

def restart_message_thread():
    """Restart the message thread with new settings."""
    global message_thread
    
    # Stop existing thread if running
    if message_thread and message_thread.is_alive():
        # This doesn't actually stop the thread, but we'll create a new one
        print("Restarting message thread with new settings")
    
    # Create a new thread
    message_thread = threading.Thread(
        target=message_producer,
        daemon=True
    )
    
    # Start the thread
    message_thread.start()

def show_settings_dialog(parent=None):
    """Show the settings dialog."""
    global settings
    
    dialog = SettingsDialog(parent)
    result = dialog.exec()
    
    if result == QDialog.DialogCode.Accepted:
        dialog.save_to_settings()
        return True
    return False

class SettingsDialog(QDialog):
    """Settings dialog for punch card display."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Punch Card Settings")
        self.setMinimumWidth(500)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Create tabs
        self.source_tab = QWidget()
        self.openai_tab = QWidget()
        self.display_tab = QWidget()
        self.database_tab = QWidget()
        
        # Add tabs to widget
        self.tabs.addTab(self.source_tab, "Message Source")
        self.tabs.addTab(self.openai_tab, "OpenAI")
        self.tabs.addTab(self.display_tab, "Display")
        self.tabs.addTab(self.database_tab, "Database")
        
        # Set up each tab
        self._setup_source_tab()
        self._setup_openai_tab()
        self._setup_display_tab()
        self._setup_database_tab()
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        layout.addWidget(buttons)
        self.setLayout(layout)
        
        # Load current settings
        self.load_from_settings()
    
    def _setup_source_tab(self):
        """Set up the message source tab."""
        layout = QVBoxLayout()
        
        # Message source group
        group = QGroupBox("Message Source")
        group_layout = QVBoxLayout()
        
        # Radio buttons
        self.local_radio = QCheckBox("Local Generation")
        self.openai_radio = QCheckBox("OpenAI Generation")
        self.database_radio = QCheckBox("Database Messages")
        
        group_layout.addWidget(self.local_radio)
        group_layout.addWidget(self.openai_radio)
        group_layout.addWidget(self.database_radio)
        
        # Connect signals
        self.local_radio.clicked.connect(lambda: self._source_selected("local"))
        self.openai_radio.clicked.connect(lambda: self._source_selected("openai"))
        self.database_radio.clicked.connect(lambda: self._source_selected("database"))
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        layout.addStretch()
        
        self.source_tab.setLayout(layout)
    
    def _source_selected(self, source):
        """Handle source selection."""
        # Uncheck others
        if source == "local":
            self.openai_radio.setChecked(False)
            self.database_radio.setChecked(False)
        elif source == "openai":
            self.local_radio.setChecked(False)
            self.database_radio.setChecked(False)
        elif source == "database":
            self.local_radio.setChecked(False)
            self.openai_radio.setChecked(False)
    
    def _setup_openai_tab(self):
        """Set up the OpenAI tab."""
        layout = QVBoxLayout()
        
        # API Key group
        api_group = QGroupBox("API Key")
        api_layout = QVBoxLayout()
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("Enter your OpenAI API key")
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addWidget(self.api_key_edit)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # Model selection group
        model_group = QGroupBox("Model Selection")
        model_layout = QVBoxLayout()
        
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-3.5-turbo-0125"
        ])
        model_layout.addWidget(self.model_combo)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Prompt customization (TODO in a future version)
        
        layout.addStretch()
        self.openai_tab.setLayout(layout)
    
    def _setup_display_tab(self):
        """Set up the display tab."""
        layout = QVBoxLayout()
        
        # Message prefix
        prefix_group = QGroupBox("Message Prefix")
        prefix_layout = QVBoxLayout()
        
        self.prefix_edit = QLineEdit()
        self.prefix_edit.setPlaceholderText("Enter message prefix (e.g., [AI])")
        prefix_layout.addWidget(self.prefix_edit)
        
        prefix_group.setLayout(prefix_layout)
        layout.addWidget(prefix_group)
        
        # Display delay
        delay_group = QGroupBox("Display Delay (milliseconds)")
        delay_layout = QVBoxLayout()
        
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(10, 500)
        self.delay_spin.setSingleStep(10)
        delay_layout.addWidget(self.delay_spin)
        
        delay_group.setLayout(delay_layout)
        layout.addWidget(delay_group)
        
        # Message interval
        interval_group = QGroupBox("Message Interval (seconds)")
        interval_layout = QVBoxLayout()
        
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(5, 120)
        self.interval_spin.setSingleStep(5)
        interval_layout.addWidget(self.interval_spin)
        
        interval_group.setLayout(interval_layout)
        layout.addWidget(interval_group)
        
        layout.addStretch()
        self.display_tab.setLayout(layout)
    
    def _setup_database_tab(self):
        """Set up the database tab."""
        layout = QVBoxLayout()
        
        # Save to database
        save_group = QGroupBox("Database Options")
        save_layout = QVBoxLayout()
        
        self.save_check = QCheckBox("Save Messages to Database")
        save_layout.addWidget(self.save_check)
        
        save_group.setLayout(save_layout)
        layout.addWidget(save_group)
        
        # Message limit
        limit_group = QGroupBox("Message Limit")
        limit_layout = QVBoxLayout()
        
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(10, 1000)
        self.limit_spin.setSingleStep(10)
        limit_layout.addWidget(self.limit_spin)
        
        limit_group.setLayout(limit_layout)
        layout.addWidget(limit_group)
        
        layout.addStretch()
        self.database_tab.setLayout(layout)
    
    def load_from_settings(self):
        """Load current settings into dialog."""
        global settings
        
        # Message source
        if settings.message_source == "local":
            self.local_radio.setChecked(True)
        elif settings.message_source == "openai":
            self.openai_radio.setChecked(True)
        elif settings.message_source == "database":
            self.database_radio.setChecked(True)
        
        # OpenAI
        self.api_key_edit.setText(settings.openai_api_key)
        index = self.model_combo.findText(settings.openai_model)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)
        
        # Display
        self.prefix_edit.setText(settings.message_prefix)
        self.delay_spin.setValue(settings.display_delay)
        self.interval_spin.setValue(settings.message_interval)
        
        # Database
        self.save_check.setChecked(settings.save_to_database)
        self.limit_spin.setValue(settings.message_limit)
    
    def save_to_settings(self):
        """Save dialog values to settings."""
        global settings
        
        # Message source
        if self.local_radio.isChecked():
            settings.message_source = "local"
        elif self.openai_radio.isChecked():
            settings.message_source = "openai"
        elif self.database_radio.isChecked():
            settings.message_source = "database"
        
        # OpenAI
        settings.openai_api_key = self.api_key_edit.text()
        settings.openai_model = self.model_combo.currentText()
        
        # Display
        settings.message_prefix = self.prefix_edit.text()
        settings.display_delay = self.delay_spin.value()
        settings.message_interval = self.interval_spin.value()
        
        # Database
        settings.save_to_database = self.save_check.isChecked()
        settings.message_limit = self.limit_spin.value()
        
        # Save to file
        save_settings()

def process_database_queue():
    """Process any messages waiting to be saved to the database."""
    global message_queue

    # Process up to 10 items per cycle (to avoid blocking)
    for _ in range(10):
        if message_queue.empty():
            return
        
        try:
            message, source = message_queue.get_nowait()
            save_message_to_database(display, message, source)
            message_queue.task_done()
        except queue.Empty:
            return
        except Exception as e:
            update_api_status(f"Error processing message for database: {e}", False)

class SafeTimer(QObject):
    """A safer timer implementation for message generation."""
    
    timeout = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.emit_timeout)
        
    def emit_timeout(self):
        try:
            self.timeout.emit()
        except Exception as e:
            print(f"Error in timer emission: {e}")
            
    def start(self, interval):
        self.timer.start(interval)
        
    def stop(self):
        self.timer.stop()

def main():
    """Main entry point."""
    global display, settings, signal_handler, shutting_down
    
    # Set up signal handlers for graceful termination
    signal.signal(signal.SIGINT, signal_handler_function)
    signal.signal(signal.SIGTERM, signal_handler_function)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Enhanced Punch Card Display")
    parser.add_argument('--settings', action='store_true',
                      help='Show settings dialog at startup')
    parser.add_argument('--debug', action='store_true',
                      help='Enable debug mode')
    parser.add_argument('--safe-mode', action='store_true',
                      help='Run in safe mode with minimal features')
    parser.add_argument('--no-openai', action='store_true',
                      help='Disable OpenAI API calls')
    args = parser.parse_args()
    
    # Honor safe mode and no-openai flags
    if args.safe_mode:
        update_api_status("Running in safe mode", True)
        settings.message_source = "local"
    
    if args.no_openai:
        update_api_status("OpenAI API calls disabled", True)
        settings.message_source = "local"
    
    try:
        # Initialize Qt application
        app = QApplication(sys.argv)
        
        # Load settings
        load_settings()
        
        # Start the GUI first so we have access to the console
        print("Starting Punch Card GUI...")
        display, _ = gui_main()  # No need to capture app as we already created one
        
        # Enable exception hook to catch unhandled exceptions
        def exception_hook(exctype, value, tb):
            update_api_status(f"Unhandled exception: {value}", False)
            traceback.print_exception(exctype, value, tb)
            # Don't exit - let the app continue if possible
        
        sys.excepthook = exception_hook
        
        # Initialize OpenAI client after GUI is available for console updates
        if not args.no_openai:
            setup_openai_client()
        
        # Connect the message signal to the display_message method
        # This ensures display_message is called in the main GUI thread
        try:
            signal_handler.message_signal.connect(display.display_message)
            update_api_status("Connected message signaling system", True)
        except Exception as e:
            update_api_status(f"Failed to connect signal: {e}", False)
        
        # Initialize or connect to the database
        initialize_database()
        
        # Try to disable any automatic message generation
        for attr_name in dir(display):
            attr = getattr(display, attr_name)
            if attr_name.endswith('timer') or attr_name.endswith('Timer'):
                if hasattr(attr, 'stop'):
                    try:
                        attr.stop()
                        update_api_status(f"Stopped timer: {attr_name}", True)
                    except Exception as e:
                        update_api_status(f"Error stopping timer {attr_name}: {e}", False)
        
        # Check display console capabilities
        if args.debug:
            console_info = []
            if hasattr(display, 'api_console'):
                console_info.append("API console exists")
                for attr in ['toPlainText', 'append', 'console']:
                    if hasattr(display.api_console, attr):
                        console_info.append(f"  - Has {attr}")
                
                # Check if it's a window
                if hasattr(display.api_console, 'console'):
                    console_info.append("  - Console is a window with a text area")
                    for attr in ['append', 'setText', 'toPlainText']:
                        if hasattr(display.api_console.console, attr):
                            console_info.append(f"    - Console has {attr}")
            else:
                console_info.append("No API console found")
                
            update_api_status("Console detection: " + ", ".join(console_info), True)
        
        # Check display capabilities
        display_info = []
        for attr in ['message_label', 'source_label', 'display_message', 'punch_card']:
            if hasattr(display, attr):
                display_info.append(f"Has {attr}")
                
        update_api_status("Display capabilities: " + ", ".join(display_info), True)
        
        # Show welcome message - safely in the main thread
        try:
            display.display_message(
                message="ENHANCED PUNCH CARD SYSTEM INITIALIZED", 
                source="System", 
                delay=50
            )
            update_api_status("Welcome message displayed via display_message", True)
        except Exception as e:
            update_api_status(f"Error displaying welcome message: {e}", False)
            # Try a direct update
            direct_update_message("ENHANCED PUNCH CARD SYSTEM INITIALIZED", "System")
        
        # Save welcome message to database
        save_message_to_database(display, "ENHANCED PUNCH CARD SYSTEM INITIALIZED", "System")
        
        # Create a timer to process database queue every second
        # Use our safer timer implementation
        db_timer = SafeTimer()
        db_timer.timeout.connect(process_database_queue)
        db_timer.start(1000)  # Every 1 second
        
        # Try to add settings button to the UI
        if hasattr(display, 'add_control_button'):
            # When settings are saved, restart the message thread
            display.add_control_button("Settings", lambda: show_settings_dialog() and restart_message_thread())
            update_api_status("Added settings button to display", True)
        else:
            # Try to find the button container or create our own
            try:
                if hasattr(display, 'button_container'):
                    settings_button = QPushButton("Settings")
                    settings_button.clicked.connect(lambda: show_settings_dialog() and restart_message_thread())
                    display.button_container.layout().addWidget(settings_button)
                    update_api_status("Added settings button to button container", True)
            except Exception as e:
                update_api_status(f"Could not add settings button: {e}", False)
        
        # Show API console if requested or in debug mode
        if args.debug and hasattr(display, 'show_api_console'):
            try:
                if callable(display.show_api_console):
                    display.show_api_console()
                    update_api_status("API console shown (debug mode)", True)
            except Exception as e:
                update_api_status(f"Could not show API console: {e}", False)
        
        # Give UI time to update before showing settings
        QTimer.singleShot(1000, lambda: show_settings_dialog() if args.settings else None)
        
        # Start message thread
        if not args.safe_mode or args.safe_mode and settings.message_source == "local":
            restart_message_thread()
        
        # Start event loop - wrapped in try/except for safety
        try:
            sys.exit(app.exec())
        except Exception as e:
            update_api_status(f"Event loop terminated with error: {e}", False)
            print(f"Event loop exception: {traceback.format_exc()}")
    except Exception as e:
        print(f"Fatal error in main function: {e}")
        print(f"Exception details: {traceback.format_exc()}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code if exit_code is not None else 0)
    except Exception as e:
        print(f"Unhandled exception in main: {e}")
        traceback.print_exc()
        sys.exit(1) 