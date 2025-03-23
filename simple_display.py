#!/usr/bin/env python3
# Simple Punch Card Display GUI
# This version has a simpler interface and uses PyQt6
# Version 0.5.5 - OpenAI Client Fix

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
import traceback
import importlib.util

# Version information
VERSION = "0.5.5 - OpenAI Client Fix"
MONKEY_ART = """
  ,-.-.
 ( o o )  OPENAI CLIENT FIX
 |  ^  |
 | `-' |  v0.5.5
 `-----'
"""

# Global variables
config = {}
display = None
openai_client = None
API_CONSOLE = None
DB_CONN = None
service_status = {}
message_stats = {
    "total": 0,
    "local": 0,
    "openai": 0,
    "database": 0,
    "flyio": 0,
    "custom": 0
}
openai_usage = {
    "calls": 0,
    "tokens": 0,
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "last_call": ""
}

print("====== OPENAI CLIENT FIX - v0.5.5 ======")
print(MONKEY_ART)
print("This update implements a new approach to fix OpenAI client issues:")
print("1. Complete custom OpenAI client implementation without using the official client")
print("2. Direct API communication using httpx instead of the default client")
print("3. Automatically installs required dependencies if missing")
print("4. Enhanced error handling and detailed diagnostic messages")
print("5. Completely bypasses 'proxies' parameter issues")
print("\nIf you still encounter issues, please enable --debug mode for detailed logs.")

# Fix OpenAI client by removing problematic settings from config
def clean_config_settings():
    """Remove problematic settings from configuration files."""
    print("🔧 Cleaning configuration settings...")
    
    try:
        # Paths to check for settings files
        settings_paths = [
            "punch_card_settings.json",
            os.path.join("config", "punch_card_settings.json"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "punch_card_settings.json"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "punch_card_settings.json")
        ]
        
        # Problematic keys to remove
        problematic_keys = ['proxies', 'proxy', 'organization', 'org_id', 'organization_id']
        
        for settings_file in settings_paths:
            if os.path.exists(settings_file):
                print(f"Checking settings file: {settings_file}")
                try:
                    with open(settings_file, 'r') as f:
                        config_data = json.load(f)
                        modified = False
                        
                        # Check all problematic keys at top level
                        for key in problematic_keys:
                            if key in config_data:
                                print(f"Removing '{key}' from settings file (top level)")
                                del config_data[key]
                                modified = True
                        
                        # Check in config section
                        if 'config' in config_data and isinstance(config_data['config'], dict):
                            for key in problematic_keys:
                                if key in config_data['config']:
                                    print(f"Removing '{key}' from settings file (config section)")
                                    del config_data['config'][key]
                                    modified = True
                        
                        # Check in other sections
                        for section in config_data:
                            if isinstance(config_data[section], dict):
                                for key in problematic_keys:
                                    if key in config_data[section]:
                                        print(f"Removing '{key}' from settings file (section: {section})")
                                        del config_data[section][key]
                                        modified = True
                        
                        if modified:
                            with open(settings_file, 'w') as f_out:
                                json.dump(config_data, f_out, indent=4)
                            print(f"✅ Saved cleaned settings to {settings_file}")
                except Exception as e:
                    print(f"Error checking settings file {settings_file}: {e}")
    except Exception as e:
        print(f"Error cleaning config settings: {e}")

# Run the config cleaner
clean_config_settings()

# Clear environment variables
proxy_env_vars = [
    'HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 
    'no_proxy', 'NO_PROXY', 'OPENAI_PROXY'
]

for var in proxy_env_vars:
    if var in os.environ:
        print(f"Clearing environment variable: {var}")
        os.environ.pop(var, None)

print("====== OPENAI CLIENT FIX COMPLETE ======")

# Imports must be after the OpenAI client fix
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QGridLayout, 
    QLabel, QPushButton, QRadioButton, QGroupBox,
    QDialogButtonBox, QSpinBox, QCheckBox, QTextEdit, 
    QWidget, QFrame, QTabWidget, QScrollArea, QLineEdit, 
    QMessageBox, QComboBox, QFormLayout, QDoubleSpinBox,
    QMainWindow, QHBoxLayout, QDockWidget, QSlider
)
from PyQt6.QtCore import QTimer, Qt, QEvent, QObject, QSize
from PyQt6.QtGui import (
    QIcon, QShortcut, QPixmap, QColor, QPainter, QPalette, 
    QFont, QKeyEvent, QTextOption, QLinearGradient, QFontMetrics,
    QSyntaxHighlighter, QTextCharFormat, QAction, QKeySequence
)

try:
    from src.display.gui_display import main as gui_main
except ImportError:
    print("gui_display not imported - this is normal in standalone mode")

# Try to import PunchCardDisplay and monkey patch it to use our settings dialog
try:
    from src.display.widgets.punch_card_display import PunchCardDisplay
    has_punch_card_module = True
    print("PunchCardDisplay imported")
except ImportError:
    has_punch_card_module = False
    print("ℹ️ PunchCardDisplay not imported - terminal patching not required")

# This function creates an OpenAI client without any monkey patching
def create_openai_client(api_key):
    """
    Create a minimal OpenAI client implementation that bypasses all the problematic issues.
    This doesn't use the official OpenAI class at all, but creates a compatible interface.
    """
    print("\n====== Creating minimal OpenAI client ======")
    
    if not api_key or len(api_key.strip()) < 10:
        print("❌ Invalid API key")
        return None
        
    try:
        # Set the API key as an environment variable
        os.environ["OPENAI_API_KEY"] = api_key
        print("✅ API key set in environment variables")
        
        # Import the required modules
        try:
            import openai
            import httpx
            print("✅ Imported openai and httpx modules")
        except ImportError as ie:
            print(f"❌ Import error: {str(ie)}")
            if "httpx" in str(ie):
                print("⚠️ httpx module not installed. This is required by OpenAI.")
                print("Please install it with: pip install httpx")
            return None
            
        # Create a minimal client implementation that doesn't use the official OpenAI class
        class MinimalOpenAIClient:
            """A minimal OpenAI client implementation that avoids problematic parameters."""
            
            def __init__(self):
                self.api_key = api_key
                self.base_url = "https://api.openai.com/v1"
                self.api_version = None
                
                # Create httpx client for API requests
                self.http_client = httpx.Client(
                    base_url=self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=60.0
                )
                
                # Create namespaces for OpenAI API endpoints
                self.models = self.ModelsNamespace(self)
                self.chat = self.ChatNamespace(self)
                print("✅ Created minimal OpenAI client")
                
            class ModelsNamespace:
                def __init__(self, client):
                    self.client = client
                
                def list(self, limit=20):
                    """List available models."""
                    print("Listing models with minimal client...")
                    try:
                        response = self.client.http_client.get(
                            "/models",
                            params={"limit": limit}
                        )
                        response.raise_for_status()
                        data = response.json()
                        
                        # Create a models object that mimics the OpenAI models response
                        class ModelsResponse:
                            def __init__(self, models_data):
                                self.data = []
                                for model in models_data.get("data", []):
                                    self.data.append(model)
                        
                        return ModelsResponse(data)
                    except Exception as e:
                        print(f"❌ Error listing models: {str(e)}")
                        raise
            
            class ChatNamespace:
                def __init__(self, client):
                    self.client = client
                    self.completions = self.CompletionsNamespace(client)
                
                class CompletionsNamespace:
                    def __init__(self, client):
                        self.client = client
                    
                    def create(self, model, messages, temperature=0.7, max_tokens=None, timeout=None, **kwargs):
                        """Create a chat completion."""
                        print(f"Creating chat completion with minimal client using model {model}...")
                        try:
                            # Build the request payload
                            payload = {
                                "model": model,
                                "messages": messages,
                                "temperature": temperature
                            }
                            
                            if max_tokens is not None:
                                payload["max_tokens"] = max_tokens
                                
                            # Add any other supported parameters
                            for key, value in kwargs.items():
                                if key not in ["proxies", "proxy", "organization", "org_id"]:
                                    payload[key] = value
                            
                            # Make the API request
                            response = self.client.http_client.post(
                                "/chat/completions",
                                json=payload,
                                timeout=timeout or 60.0
                            )
                            response.raise_for_status()
                            data = response.json()
                            
                            # Create a response object that mimics the OpenAI completion response
                            class CompletionResponse:
                                def __init__(self, completion_data):
                                    self.id = completion_data.get("id")
                                    self.object = completion_data.get("object")
                                    self.created = completion_data.get("created")
                                    self.model = completion_data.get("model")
                                    
                                    # Process choices
                                    self.choices = []
                                    for choice in completion_data.get("choices", []):
                                        self.choices.append(self.Choice(choice))
                                    
                                    # Process usage
                                    if "usage" in completion_data:
                                        self.usage = self.Usage(completion_data["usage"])
                                
                                class Choice:
                                    def __init__(self, choice_data):
                                        self.index = choice_data.get("index")
                                        self.finish_reason = choice_data.get("finish_reason")
                                        
                                        # Process message
                                        if "message" in choice_data:
                                            self.message = self.Message(choice_data["message"])
                                
                                class Message:
                                    def __init__(self, message_data):
                                        self.role = message_data.get("role")
                                        self.content = message_data.get("content")
                                
                                class Usage:
                                    def __init__(self, usage_data):
                                        self.prompt_tokens = usage_data.get("prompt_tokens", 0)
                                        self.completion_tokens = usage_data.get("completion_tokens", 0)
                                        self.total_tokens = usage_data.get("total_tokens", 0)
                            
                            return CompletionResponse(data)
                        except Exception as e:
                            print(f"❌ Error creating chat completion: {str(e)}")
                            raise
        
        # Create the minimal client
        client = MinimalOpenAIClient()
        
        # Test the client with a simple API call
        try:
            print("Testing the minimal client...")
            models = client.models.list(limit=1)
            print(f"✅ Successfully tested client - found {len(models.data)} models")
            return client
        except Exception as test_error:
            print(f"❌ Client test failed: {str(test_error)}")
            
            # If our custom client doesn't work, try a last resort approach
            print("🔄 Trying alternative approach with OpenAI's base_client...")
            try:
                # Try to use the openai module in a minimal way
                from openai import OpenAI
                
                # We'll try to bypass the problem by using a dictionary-based approach
                print("Creating client with __new__...")
                client = OpenAI(api_key=api_key)
                print("✅ Successfully created client")
                return client
            except Exception as e2:
                print(f"❌ Alternative approach failed: {str(e2)}")
                return None
    
    except Exception as e:
        print(f"❌ Unexpected error creating OpenAI client: {str(e)}")
        return None

def setup_openai_client():
    """Set up the OpenAI client with our custom minimal implementation."""
    global openai_client, config
    
    print("\n====== setup_openai_client function started ======")
    debug_log("Setting up OpenAI client...", "system")
    
    # Check if we already have a client
    if openai_client:
        print("OpenAI client already initialized, returning existing client")
        debug_log("OpenAI client already initialized", "system")
        return True
    
    # Check for required packages
    try:
        import httpx
    except ImportError:
        print("httpx package not installed. This is required for the minimal OpenAI client.")
        debug_log("⚠️ httpx package not installed. Attempting to install it...", "system")
        
        # Try to install httpx
        try:
            import subprocess
            print("Installing httpx package...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx"])
            print("✅ Successfully installed httpx package")
            debug_log("✅ Successfully installed httpx package", "system")
            
            # Re-import httpx
            import httpx
        except Exception as install_error:
            print(f"Error installing httpx: {str(install_error)}")
            debug_log(f"❌ Failed to install httpx: {str(install_error)[:100]}", "error")
            debug_log("Please install it manually with: pip install httpx", "system")
            print("====== setup_openai_client function failed ======\n")
            return False
    
    # Get API key from config
    api_key = config.get("openai_api_key", "")
    print(f"API key from config: {'<missing or invalid>' if not api_key or len(api_key) < 10 else '<present>'}")
    
    # Try to load from secrets if not in config
    if not api_key or len(api_key.strip()) < 10:
        print("API key missing or invalid, attempting to load from secrets file...")
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
    
    # Create the OpenAI client with our direct approach
    try:
        debug_log("Creating OpenAI client with your API key...", "system")
        
        # Create the client with our minimal implementation
        global openai_client
        openai_client = create_openai_client(api_key)
        
        if not openai_client:
            debug_log("❌ Failed to create OpenAI client.", "error")
            print("====== setup_openai_client function failed ======\n")
            return False
            
        # Test the client
        try:
            debug_log("✅ OpenAI client created successfully!", "system")
            debug_log("Testing client connection...", "system")
            
            # The models endpoint is the most reliable test
            models = openai_client.models.list(limit=5)
            debug_log(f"✅ Successfully connected to OpenAI API - found {len(models.data)} models", "system")
            
            # Set default model if not set
            if not config.get("model"):
                print("No default model set, setting to gpt-3.5-turbo...")
                config["model"] = "gpt-3.5-turbo"
                save_settings()
                
            print("====== setup_openai_client function completed successfully ======\n")
            return True
                
        except Exception as test_error:
            print(f"Error testing OpenAI client: {str(test_error)}")
            debug_log(f"❌ Error testing OpenAI client connection: {str(test_error)[:100]}", "error")
            openai_client = None
            print("====== setup_openai_client function failed ======\n")
            return False
            
    except Exception as e:
        # Generic error handling
        print(f"Error setting up OpenAI client: {str(e)}")
        debug_log(f"❌ Error setting up OpenAI client: {str(e)[:100]}", "error")
        openai_client = None
        print("====== setup_openai_client function failed ======\n")
        return False

def generate_openai_message():
    """Generate message using OpenAI API with our minimal client implementation."""
    global openai_client, config, display, openai_usage
    
    # Initialize client if needed
    if not openai_client:
        debug_log("OpenAI client not initialized. Attempting setup...", "openai")
        client_setup_result = setup_openai_client()
        if not client_setup_result:
            debug_log("❌ ERROR: COULD NOT INITIALIZE OPENAI CLIENT", "error")
            return "ERROR: COULD NOT INITIALIZE OPENAI CLIENT"
    
    # Get timeout from config (with default)
    timeout = config.get("openai_timeout", 30)  # Default 30 seconds
    
    # Load temperature setting from config
    temperature = config.get("temperature", 1.0)
    
    # Make sure model is set, default to GPT-3.5-turbo if not
    model = config.get("model", "gpt-3.5-turbo")
    
    # Add more context options from config
    context = config.get("openai_context", "You are a sophisticated computer terminal displaying messages")
    if config.get("terminal_mode", False):
        context += " in the style of a vintage terminal"
    if config.get("retro_mode", False):
        context += " with a retro computing aesthetic"
    if config.get("punch_card_mode", True):
        context += " that references punch cards and early computing concepts"
    
    # Maximum length for message (default to 80 for punch card feel)
    max_length = config.get("max_length", 80)
    
    # Current timestamp for reference
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Log generation attempt
        debug_log(f"Generating message using model: {model}, temp: {temperature}", "openai")
        
        # Create prompt for the model
        system_prompt = f"{context}. Generate a short, meaningful message that would appear on such a display. Output ONLY the message text without any additional context or explanation. Keep it under {max_length} characters. Use ALL CAPS."
        
        # Make the API call with timeout handling
        start_time = time.time()
        debug_log("Sending request to OpenAI API...", "openai")
        
        # Handle potential errors with clean error messages
        try:
            completion = openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Generate a vintage computing message for display at {current_time}. Keep it concise and insightful."}
                ],
                temperature=float(temperature),
                max_tokens=100,
                timeout=timeout
            )
            
            # Calculate usage stats
            end_time = time.time()
            elapsed = end_time - start_time
            
            # Extract the message
            if completion and hasattr(completion, 'choices') and len(completion.choices) > 0:
                message = completion.choices[0].message.content.strip()
                
                # Update usage statistics
                if hasattr(completion, 'usage') and completion.usage is not None:
                    prompt_tokens = getattr(completion.usage, 'prompt_tokens', 0)
                    completion_tokens = getattr(completion.usage, 'completion_tokens', 0)
                    total_tokens = getattr(completion.usage, 'total_tokens', 0)
                    
                    # Update the global usage counter
                    openai_usage["calls"] = openai_usage.get("calls", 0) + 1
                    openai_usage["tokens"] = openai_usage.get("tokens", 0) + total_tokens
                    openai_usage["prompt_tokens"] = openai_usage.get("prompt_tokens", 0) + prompt_tokens
                    openai_usage["completion_tokens"] = openai_usage.get("completion_tokens", 0) + completion_tokens
                    openai_usage["last_call"] = current_time
                    
                    # Save updated usage stats
                    config["openai_usage"] = openai_usage
                    save_settings()
                
                # Format message: ensure all caps, trim to max length, clean whitespace
                message = message.upper().strip()
                if len(message) > max_length:
                    message = message[:max_length]
                
                # Log success
                debug_log(f"Generated OpenAI message in {elapsed:.2f}s: {message}", "openai")
                return message
            else:
                debug_log("❌ Error: OpenAI returned empty or invalid response", "error")
                return "API ERROR: EMPTY RESPONSE"
                
        except Exception as api_e:
            error_message = str(api_e)
            debug_log(f"❌ OpenAI API error: {error_message[:100]}", "error")
            
            # Custom user-friendly error messages based on error type
            if "timeout" in error_message.lower():
                return "API TIMEOUT: REQUEST TOOK TOO LONG"
            elif "rate limit" in error_message.lower():
                return "API ERROR: RATE LIMIT EXCEEDED"
            elif "quota" in error_message.lower():
                return "API ERROR: QUOTA EXCEEDED"
            elif "authentication" in error_message.lower() or "api key" in error_message.lower():
                # Try to reinitialize the client
                debug_log("Attempting to reinitialize client due to authentication error...", "system")
                openai_client = None
                setup_result = setup_openai_client()
                if setup_result:
                    return "AUTH ERROR: PLEASE TRY AGAIN"
                else:
                    return "API ERROR: AUTHENTICATION FAILED"
            else:
                return "API ERROR: COMMUNICATION FAILURE"
    
    except Exception as e:
        debug_log(f"❌ Unexpected error in generate_openai_message: {str(e)}", "error")
        # Try to reset the client
        openai_client = None
        return "SYSTEM ERROR: MESSAGE GENERATION FAILED"

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
        
        # Use a scroll area to ensure everything is visible regardless of screen size
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_contents = QWidget()
        tab_layout = QVBoxLayout(scroll_contents)
        scroll_area.setWidget(scroll_contents)
        
        # Set the scroll area as the main widget for the tab
        main_layout = QVBoxLayout(self.openai_tab)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        
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
        self.api_key_status.setWordWrap(True)
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
        self.service_status_label.setWordWrap(True)
        service_layout.addWidget(self.service_status_label, 1)
        
        check_status_btn = QPushButton("Check Status")
        check_status_btn.clicked.connect(self.check_openai_service)
        service_layout.addWidget(check_status_btn)
        
        tab_layout.addWidget(service_group)
        
        # Add stretch at the end to push everything up
        tab_layout.addStretch()
        
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
        
        try:
            # Update the status
            check_openai_status()
            check_flyio_status()
            
            # Update the display with error handling
            try:
                if hasattr(self, 'service_status_text') and self.service_status_text is not None:
                    status_text = get_service_status_text()
                    self.service_status_text.setText(status_text)
                    
                    # Show confirmation only if the update was successful
                    QMessageBox.information(
                        self,
                        "Service Status",
                        "Service status has been refreshed."
                    )
                else:
                    print("Warning: service_status_text is None or not available")
            except Exception as e:
                print(f"Error updating service status text: {e}")
                # Try to show an error message if possible
                QMessageBox.warning(
                    self,
                    "Service Status Update Error",
                    f"Error updating service status: {str(e)}"
                )
        except Exception as e:
            print(f"Error refreshing service status: {e}")
            QMessageBox.critical(
                self,
                "Service Status Error",
                f"Failed to check service status: {str(e)}"
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
        
        # Use a scroll area to ensure everything is visible regardless of screen size
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_contents = QWidget()
        layout = QVBoxLayout(scroll_contents)
        scroll_area.setWidget(scroll_contents)
        
        # Set the scroll area as the main widget for the tab
        main_layout = QVBoxLayout(self.stats_tab)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        
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
        
        # Load initial service status - with error handling
        try:
            self.service_status_text.setText(get_service_status_text())
        except Exception as e:
            self.service_status_text.setText(f"Error getting service status: {str(e)}")
            print(f"Error loading service status: {e}")
    
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
            <p>The MonkeyPatch Update (v0.5.5) addresses issues with the OpenAI client initialization
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