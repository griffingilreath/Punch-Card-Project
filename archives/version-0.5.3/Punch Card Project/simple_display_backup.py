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
import logging
import subprocess
import math
import re

# PyQt6 imports
from PyQt6.QtCore import Qt, QTimer, QObject, QEvent, QRect, QRectF, QPoint
from PyQt6.QtGui import QFont, QPalette, QColor, QTextCursor, QPainter, QPainterPath, QPen, QBrush
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QDialog, QTabWidget, QGroupBox,
    QFormLayout, QLineEdit, QComboBox, QSlider, QSpinBox, QDoubleSpinBox,
    QCheckBox, QRadioButton, QMessageBox, QDialogButtonBox, QScrollArea,
    QFrame, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QSizePolicy
)

# Global variables
openai_client = None  # This should be defined at the top of the file
config = {}
display = None
API_CONSOLE = None
DB_CONN = None
service_status = {}
message_source = "local"  # Default message source
message_stats = {
    "total": 0,
    "local": 0,
    "openai": 0,
    "database": 0,
    "flyio": 0,
    "custom": 0,
    "last_updated": "",
    "last_message": "",
    "last_source": ""
}
openai_usage = {
    "calls": 0,
    "tokens": 0,
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "last_call": "",
    "total_calls": 0,
    "estimated_cost": 0.0,
    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "usage_history": [],
    "cost_per_model": {}
}

# Constants (for configuration)
NUM_ROWS = 12
NUM_COLS = 80
REFRESH_INTERVAL = 15000  # milliseconds (15 seconds) between messages
DEFAULT_MESSAGE_SOURCE = "local"

# Real IBM punch card dimensions (scaled up for display)
SCALE_FACTOR = 3  # Scaled for comfortable monitor viewing

# Notch dimensions (scaled)
NOTCH_WIDTH = int(3.175 * SCALE_FACTOR)   # 2/16 inch = 3.175mm
NOTCH_HEIGHT = int(6.35 * SCALE_FACTOR)   # 4/16 inch = 6.35mm

# Card dimensions
CARD_WIDTH = int(187.325 * SCALE_FACTOR)  # 7⅜ inches = 187.325mm
CARD_HEIGHT = int(82.55 * SCALE_FACTOR)   # 3¼ inches = 82.55mm

# Margins and spacing (scaled)
TOP_BOTTOM_MARGIN = int(4.2625 * SCALE_FACTOR)  # Reduced from original 4.7625mm
SIDE_MARGIN = int(4.68 * SCALE_FACTOR)          # Reduced from original 6.35mm
ROW_SPACING = int(2.24 * SCALE_FACTOR)          # Reduced from original 3.175mm
COLUMN_SPACING = int(0.8 * SCALE_FACTOR)        # Reduced from 1mm

# Hole dimensions (scaled)
HOLE_WIDTH = int(1 * SCALE_FACTOR)    # 1mm
HOLE_HEIGHT = int(3 * SCALE_FACTOR)   # 3mm

# Colors for the punch card display
COLORS = {
    'background': QColor(0, 0, 0),      # Pure black background (changed to pure black as requested)
    'card_bg': QColor(0, 0, 0),         # Black card background
    'grid': QColor(40, 40, 40),         # Grid lines
    'hole': QColor(255, 255, 255),      # White hole
    'hole_outline': QColor(255, 255, 255), # White hole outline
    'hole_fill': QColor(0, 0, 0),       # Black for unpunched holes
    'hole_punched': QColor(255, 255, 255), # White for punched holes
    'text': QColor(200, 200, 200),      # Light gray text
    'border': QColor(100, 100, 120),    # Border color
    'button_bg': QColor(45, 45, 55),    # Dark button background
    'button_hover': QColor(60, 60, 70), # Button hover color
    'console_bg': QColor(0, 0, 0),      # Black console background
    'console_text': QColor(0, 255, 0),  # Green console text
    'card_edge': QColor(150, 150, 170), # Card edge color
    'card_outline': QColor(255, 255, 255) # White card outline
}

# Version information
VERSION = "0.5.5 - OpenAI Client Fix"
MONKEY_ART = """
  ,-.-.
 ( o o )  OPENAI CLIENT FIX
 |  ^  |
 | `-' |  v0.5.5
 `-----'
"""

print("====== OPENAI CLIENT FIX - v0.5.5 ======")
print(MONKEY_ART)
print("This update implements a new approach to fix OpenAI client issues:")
print("1. Complete custom OpenAI client implementation without using the official client")
print("2. Direct API communication using httpx instead of the default client")
print("3. Automatically installs required dependencies if missing")
print("4. Enhanced error handling and detailed diagnostic messages")
print("5. Completely bypasses 'proxies' parameter issues")
print("\nIf you still encounter issues, please enable --debug mode for detailed logs.")

def setup_logging():
    """Set up logging configuration."""
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Create a timestamped log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/openai_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # Create a logger for OpenAI
    logger = logging.getLogger('openai')
    logger.setLevel(logging.DEBUG)
    
    return logger

def debug_log(message, level="info"):
    """Log a message with appropriate formatting."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Define symbols for different log levels
    symbols = {
        "error": "❌",
        "warning": "⚠️",
        "system": "ℹ️",
        "openai": "🤖",
        "info": "✅"
    }
    
    # Get the appropriate symbol
    symbol = symbols.get(level, "ℹ️")
    
    # Format the message
    formatted_message = f"[{timestamp}] {symbol} {message}"
    
    # Log based on level
    if level == "error":
        logging.error(message)
    elif level == "warning":
        logging.warning(message)
    elif level == "system":
        logging.info(message)
    elif level == "openai":
        logging.info(message)
    else:
        logging.info(message)
    
    # Print to console with color
    if level == "error":
        print(f"\033[91m{formatted_message}\033[0m")  # Red
    elif level == "warning":
        print(f"\033[93m{formatted_message}\033[0m")  # Yellow
    elif level == "system":
        print(f"\033[94m{formatted_message}\033[0m")  # Blue
    elif level == "openai":
        print(f"\033[95m{formatted_message}\033[0m")  # Magenta
    else:
        print(f"\033[92m{formatted_message}\033[0m")  # Green

def clean_config_settings():
    """Clean problematic settings from configuration files.
    
    This function removes keys that could cause issues with the OpenAI client
    from all configuration files and the in-memory configuration.
    """
    problematic_keys = ['proxies', 'proxy', 'organization', 'org_id', 'organization_id']
    config_files = [
        'punch_card_settings.json',
        'config/punch_card_settings.json',
        os.path.expanduser('~/.punch_card/settings.json')
    ]
    
    # Clean settings in files
    for config_file in config_files:
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    settings = json.load(f)
                
                cleaned = False
                for key in problematic_keys:
                    if key in settings:
                        settings.pop(key)
                        cleaned = True
                        debug_log(f"✅ Removed problematic key '{key}' from {config_file}", "system")
                
                if cleaned:
                    with open(config_file, 'w') as f:
                        json.dump(settings, f, indent=4)
                
                debug_log(f"✅ Cleaned settings in {config_file}", "system")
        except Exception as e:
            debug_log(f"❌ Error cleaning settings in {config_file}: {e}", "error")
    
    # Clean settings in memory
    global config
    for key in problematic_keys:
        if key in config:
            config.pop(key)
            debug_log(f"✅ Removed problematic key '{key}' from in-memory config", "system")
    
    return True

def clear_proxy_env():
    """Clear proxy-related environment variables."""
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    for var in proxy_vars:
        if var in os.environ:
            del os.environ[var]
            debug_log(f"Cleared {var} environment variable", "system")

def create_openai_client(api_key):
    """Create a minimal OpenAI client implementation.
    
    Args:
        api_key (str): OpenAI API key
    
    Returns:
        client: OpenAI client or None if creation fails
    """
    global openai_client
    
    if not api_key or len(api_key) < 20:
        logging.error("❌ Invalid API key length")
        return None
    
    # Clear any proxy environment variables that might interfere
    for env_var in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
        if env_var in os.environ:
            os.environ.pop(env_var)
            logging.info(f"✅ Cleared {env_var} environment variable")
    
    # Set API key as environment variable
    os.environ["OPENAI_API_KEY"] = api_key
    
    try:
        # Import required modules
        try:
            import openai
            logging.info("✅ Successfully imported openai module")
        except ImportError as e:
            logging.info("🔄 Attempting to install openai...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
                import openai
                logging.info("✅ Successfully installed openai")
            except Exception as e:
                logging.error(f"❌ Failed to install openai: {e}")
                return None
        
        logging.info("🔄 Creating OpenAI client using simplest method...")
        
        # Create custom minimal client to avoid any configuration issues
        class MinimalOpenAIClient:
            def __init__(self, api_key):
                self.api_key = api_key
                self.base_url = "https://api.openai.com/v1"
                
                # Import httpx for HTTP requests
                try:
                    import httpx
                    self.httpx = httpx
                except ImportError:
                    try:
                        subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx"])
                        import httpx
                        self.httpx = httpx
                    except Exception as e:
                        logging.error(f"❌ Failed to install httpx: {e}")
                        raise ImportError("Could not import or install httpx") from e
                
                # Create a Chat class for chat completions
                class Chat:
                    def __init__(self, client):
                        self.client = client
                        
                        # Create a Completions class for chat.completions.create
                        class Completions:
                            def __init__(self, client):
                                self.client = client
                            
                            def create(self, model, messages, temperature=0.7, max_tokens=None, timeout=None):
                                """Create a chat completion using the OpenAI API."""
                                url = f"{self.client.base_url}/chat/completions"
                                headers = {
                                    "Authorization": f"Bearer {self.client.api_key}",
                                    "Content-Type": "application/json"
                                }
                                
                                # Prepare the request payload
                                payload = {
                                    "model": model,
                                    "messages": messages,
                                    "temperature": temperature
                                }
                                
                                if max_tokens:
                                    payload["max_tokens"] = max_tokens
                                
                                # Make the request with timeout
                                response = self.client.httpx.post(
                                    url, 
                                    json=payload, 
                                    headers=headers,
                                    timeout=timeout or 30
                                )
                                
                                if response.status_code != 200:
                                    raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
                                
                                # Return a simple object with the response data
                                data = response.json()
                                return type('ChatCompletionResponse', (), {
                                    'choices': [type('Choice', (), {
                                        'message': type('Message', (), {
                                            'content': data['choices'][0]['message']['content']
                                        })
                                    })],
                                    'usage': data.get('usage', {})
                                })
                        
                        self.completions = Completions(client)
                
                # Create a Models class for models.list
                class Models:
                    def __init__(self, client):
                        self.client = client
                    
                    def list(self, limit=None):
                        """List available models using the OpenAI API."""
                        url = f"{self.client.base_url}/models"
                        headers = {
                            "Authorization": f"Bearer {self.client.api_key}",
                            "Content-Type": "application/json"
                        }
                        
                        params = {}
                        if limit:
                            params['limit'] = limit
                            
                        response = self.client.httpx.get(url, headers=headers, params=params)
                        if response.status_code != 200:
                            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
                        
                        # Return a simple object with the response data
                        data = response.json()
                        return type('ModelsResponse', (), {
                            'data': data['data']
                        })
                
                # Assign the classes to the client
                self.chat = Chat(self)
                self.models = Models(self)
        
        # Create the minimal client
        client = MinimalOpenAIClient(api_key)
        
        # Test the client by listing models
        try:
            logging.info("🔄 Testing custom OpenAI client connection...")
            models = client.models.list()
            models_count = len(models.data) if hasattr(models, 'data') else 0
            logging.info(f"✅ Successfully connected to OpenAI API and listed {models_count} models")
            return client
        except Exception as e:
            logging.error(f"❌ Failed to test OpenAI client: {e}")
            return None
    
    except Exception as e:
        logging.error(f"❌ Error creating OpenAI client: {e}")
        return None

def setup_openai_client():
    """Set up the OpenAI client with error handling and retries."""
    global openai_client, config
    
    # Get API key from settings
    api_key = config.get("openai_api_key", "")
    
    # Try to get API key from secrets file if not in settings
    if not api_key or len(api_key) < 20:
        debug_log("🔄 API key not found in settings, checking secrets file...", "system")
        try:
            secrets_file = os.path.expanduser("~/.openai_secrets")
            if os.path.exists(secrets_file):
                with open(secrets_file, "r") as f:
                    api_key = f.read().strip()
                debug_log("✅ API key loaded from secrets file", "system")
        except Exception as e:
            debug_log(f"❌ Error loading API key from secrets file: {str(e)}", "error")
    
    # Validate API key
    if not api_key or len(api_key) < 20:
        debug_log("❌ Invalid API key: too short or not provided", "error")
        debug_log("ℹ️ Please set your OpenAI API key in the settings", "system")
        return False
    
    # Try to create client with retries
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(1, max_retries + 1):
        debug_log(f"🔄 Attempt {attempt}/{max_retries} to create OpenAI client...", "system")
        
        client = create_openai_client(api_key)
        
        if client:
            openai_client = client
            
            # Set default model if not set
            if "model" not in config:
                config["model"] = "gpt-3.5-turbo"
                debug_log(f"ℹ️ Set default model to {config['model']}", "system")
                
            return True
        else:
            debug_log(f"❌ Failed to create OpenAI client on attempt {attempt}", "error")
            
            if attempt < max_retries:
                debug_log(f"⏱️ Waiting {retry_delay} seconds before retry...", "system")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
    
    debug_log("❌ All attempts to create OpenAI client failed", "error")
    return False

def generate_openai_message():
    """Generate message using OpenAI API with our minimal client implementation."""
    global openai_client, config, display, openai_usage
    
    # Initialize client if needed
    if not openai_client:
        debug_log("OpenAI client not initialized. Attempting setup...", "openai")
        setup_result, client = setup_openai_client()
        if setup_result:
            openai_client = client  # Assign the client here, after the function call
        else:
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
    
    # Prepare the messages
    messages = [
        {"role": "system", "content": context},
        {"role": "user", "content": f"Generate a short message (max {max_length} chars) for a punch card display. Current time: {current_time}"}
    ]
    
    # Set up retry logic
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            debug_log(f"Generating message (attempt {attempt + 1}/{max_retries})...", "openai")
            
            # Make the API request
        completion = openai_client.chat.completions.create(
            model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_length,
                timeout=timeout
            )
            
            # Get the message content
            message = completion.choices[0].message.content.strip()
        
        # Update usage statistics
            if hasattr(completion, 'usage'):
                usage = completion.usage
                
                # Get current usage stats
                if 'openai_usage' not in config:
                    config['openai_usage'] = {}
                
                if model not in config['openai_usage']:
                    config['openai_usage'][model] = {
                        'prompt_tokens': 0,
                        'completion_tokens': 0,
                        'total_tokens': 0,
                        'requests': 0
                    }
                
                # Update counts
                model_usage = config['openai_usage'][model]
                model_usage['prompt_tokens'] += getattr(usage, 'prompt_tokens', 0)
                model_usage['completion_tokens'] += getattr(usage, 'completion_tokens', 0)
                model_usage['total_tokens'] += getattr(usage, 'total_tokens', 0)
                model_usage['requests'] += 1
                
                # Save updated config
        save_settings()
        
            # Save message to database with source
            save_message_to_database(message, "openai")
            
            return message
        
    except Exception as e:
            debug_log(f"❌ Error generating message: {str(e)}", "error")
            
            # Handle specific error cases
            if "timeout" in str(e).lower():
                debug_log("⚠️ Request timed out, retrying...", "warning")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return "ERROR: REQUEST TIMED OUT"
            elif "rate limit" in str(e).lower():
                debug_log("⚠️ Rate limit exceeded, retrying...", "warning")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * 2)  # Longer delay for rate limits
                    continue
                return "ERROR: RATE LIMIT EXCEEDED"
            elif "authentication" in str(e).lower():
                debug_log("❌ Authentication error - API key may be invalid", "error")
                return "ERROR: AUTHENTICATION FAILED"
            else:
                # General error handling
                max_length = 60
                debug_log(f"⚠️ API error: {str(e)[:max_length]}...", "warning")
                if attempt < max_retries - 1:
                    debug_log(f"Retrying in {retry_delay} seconds...", "system")
                    time.sleep(retry_delay)
                    continue
                return f"ERROR: {str(e)[:max_length-6]}"
    
    debug_log("❌ All retry attempts failed", "error")
    return "ERROR: ALL RETRY ATTEMPTS FAILED"

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
    """Get a message to display.
    
    This function retrieves a message from the specified source, with fallback
    mechanisms to ensure reliable message delivery even when OpenAI is loading
    or unavailable.
    
    Args:
        source (str, optional): The source to get the message from.
            Can be one of 'openai', 'local', or 'database'.
            Defaults to the configured source or 'local' if not specified.
    
    Returns:
        str: A message to display
    """
    # Get source from config if not specified
    if not source:
        source = config.get("message_source", "local")
        
    # Track whether we're attempting OpenAI connection
    trying_openai = (source == "openai")
    
    # Always check OpenAI status if we're trying to use it
    if trying_openai:
        openai_status = check_openai_status()
        if not openai_status:
            # OpenAI unavailable, fall back to database
            debug_log("⚠️ OpenAI unavailable, falling back to database", "warning")
            source = "database"
    
    # Get message from appropriate source with fallbacks
    message = None
    original_source = source
    
    try:
        if source == "openai":
            # Log the attempt
            debug_log("🔄 Requesting message from OpenAI...", "info")
            message = generate_openai_message()
            if message:
                debug_log("✅ OpenAI message generated successfully", "info")
            else:
                debug_log("⚠️ OpenAI returned empty message, trying database", "warning")
                source = "database"
                
        if source == "database" or (source == "openai" and not message):
            # Log the attempt to use database
            debug_log("🔄 Retrieving message from database...", "info")
            message = get_database_message()
            if message:
                debug_log("✅ Database message retrieved successfully", "info")
            else:
                debug_log("⚠️ No messages found in database, using local message", "warning")
                source = "local"
                
        if source == "local" or not message:
            # Final fallback to local message
            debug_log("🔄 Generating local message...", "info")
            message = get_local_message()
            if message:
                debug_log("✅ Local message generated successfully", "info")
            else:
                # Ultimate fallback
                debug_log("❌ All message sources failed", "error")
                message = "ERROR: UNABLE TO RETRIEVE MESSAGE"
        
    except Exception as e:
        # Error handling with clear source information
        debug_log(f"❌ Error getting message from {original_source}: {str(e)}", "error")
        message = f"SYSTEM ERROR: {str(e)[:50]}"
    
    # Ensure we always return something
    if not message:
        message = "PUNCH CARD SYSTEM OPERATIONAL"
        
    return message

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
        debug_log(f"Displaying message: {message}", "system")
        
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

def format_punch_card(message):
    """Format a message for the punch card display.
    
    This function converts text messages to a punch card format where:
    - 'O' represents a punched hole (LED ON)
    - ' ' represents no hole (LED OFF)
    
    Uses the classic IBM punch card encoding system with standard
    80-column encoding patterns.
    
    Args:
        message (str): The message to format
        
    Returns:
        str: The formatted punch card pattern with 'O' for holes
    """
    # Maximum message length - ensure it fits the display
    max_length = min(NUM_COLS, 80) 
    message = message.upper()[:max_length]
    
    # Pad message if needed for centering
    if len(message) < max_length:
        padding = (max_length - len(message)) // 2
        message = ' ' * padding + message + ' ' * (max_length - len(message) - padding)
    
    # Create a grid of rows x cols for the punch card
    # Initialize all positions as spaces (no holes)
    grid = [[' ' for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
    
    # Log the message being encoded
    logging.info(f"Encoding message for punch card: {message}")
    
    # Pre-compute common punch patterns for efficiency
    # These are based on IBM 029 keypunch encoding
    PATTERNS = {
        # Letters (zone + digit punches)
        'A': [(0, True), (3, True)],  # 12 + 1
        'B': [(0, True), (4, True)],  # 12 + 2
        'C': [(0, True), (5, True)],  # 12 + 3
        'D': [(0, True), (6, True)],  # 12 + 4
        'E': [(0, True), (7, True)],  # 12 + 5
        'F': [(0, True), (8, True)],  # 12 + 6
        'G': [(0, True), (9, True)],  # 12 + 7
        'H': [(0, True), (10, True)], # 12 + 8
        'I': [(0, True), (11, True)], # 12 + 9
        'J': [(1, True), (3, True)],  # 11 + 1
        'K': [(1, True), (4, True)],  # 11 + 2
        'L': [(1, True), (5, True)],  # 11 + 3
        'M': [(1, True), (6, True)],  # 11 + 4
        'N': [(1, True), (7, True)],  # 11 + 5
        'O': [(1, True), (8, True)],  # 11 + 6
        'P': [(1, True), (9, True)],  # 11 + 7
        'Q': [(1, True), (10, True)], # 11 + 8
        'R': [(1, True), (11, True)], # 11 + 9
        'S': [(2, True), (4, True)],  # 0 + 2
        'T': [(2, True), (5, True)],  # 0 + 3
        'U': [(2, True), (6, True)],  # 0 + 4
        'V': [(2, True), (7, True)],  # 0 + 5
        'W': [(2, True), (8, True)],  # 0 + 6
        'X': [(2, True), (9, True)],  # 0 + 7
        'Y': [(2, True), (10, True)], # 0 + 8
        'Z': [(2, True), (11, True)], # 0 + 9
        
        # Numbers
        '0': [(2, True)],           # 0 only
        '1': [(3, True)],           # 1 only
        '2': [(4, True)],           # 2 only
        '3': [(5, True)],           # 3 only
        '4': [(6, True)],           # 4 only
        '5': [(7, True)],           # 5 only
        '6': [(8, True)],           # 6 only
        '7': [(9, True)],           # 7 only
        '8': [(10, True)],          # 8 only
        '9': [(11, True)],          # 9 only
        
        # Special characters
        ' ': [],                    # No punches
        '.': [(1, True), (10, True)], # 11 + 8
        ',': [(2, True), (5, True)],  # 0 + 3
        '-': [(11, True)],            # 9 only
        '/': [(2, True), (3, True)],  # 0 + 1
        '&': [(2, True), (8, True)],  # 0 + 6
        ':': [(1, True), (4, True)],  # 11 + 2
        ';': [(1, True), (6, True)],  # 11 + 4
        '=': [(5, True), (8, True)],  # 3 + 6
        '+': [(1, True), (7, True)],  # 11 + 5
        '*': [(2, True), (9, True)],  # 0 + 7
        '!': [(1, True), (3, True)],  # 11 + 1
        '"': [(0, True), (4, True)],  # 12 + 2
        '#': [(2, True), (5, True)],  # 0 + 3
        '$': [(0, True), (10, True)], # 12 + 8
        '%': [(2, True), (9, True)],  # 0 + 7
        '?': [(2, True), (10, True)], # 0 + 8
        '@': [(0, True), (3, True)],  # 12 + 1
        '(': [(0, True), (6, True)],  # 12 + 4
        ')': [(0, True), (7, True)],  # 12 + 5
    }
    
    # Default pattern for unknown characters
    DEFAULT_PATTERN = [(1, True), (2, True)]  # 11 + 0
    
    # Convert characters to punch card holes using patterns
    encoded_chars = 0
    for col, char in enumerate(message):
        if col >= NUM_COLS:
            break
            
        # Get the pattern for this character
        pattern = PATTERNS.get(char, DEFAULT_PATTERN)
        
        # Apply the pattern to the grid
        for row, state in pattern:
            if 0 <= row < NUM_ROWS and state:
                grid[row][col] = 'O'
        
        encoded_chars += 1
    
    # Log success
    logging.info(f"Successfully encoded {encoded_chars} characters in punch card format")
    
    # Convert the grid to a string
    result = []
    for row in grid:
        result.append(''.join(row))
    
    return '\n'.join(result)

def print_punch_card(message):
    """
    Print a message as a punch card to the console.
    
    Args:
        message (str): The message to print
    """
    # Limit message length
    max_len = config.get('max_length', 80)
    if len(message) > max_len:
        message = message[:max_len]
    
    # Convert to uppercase if retro mode is enabled
    if config.get('retro_mode', True):
        message = message.upper()
    
    # Get terminal width
    try:
        width = os.get_terminal_size().columns
    except:
        width = 80
    
    # Create the punch card
    card_width = min(width - 4, max(len(message) + 4, 60))
    
    # Create top border with holes
    holes = "o" + " " * (card_width - 2) + "o"
    holes = holes[:5] + "o o o o o o o o" + holes[21:]
    
    # Create card header
    header = f"| PUNCH CARD SYSTEM - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |"
    header = header.ljust(card_width - 1) + "|"
    
    # Create card content
    content = f"| {message} |"
    content = content.ljust(card_width - 1) + "|"
    
    # Create bottom border
    border = "+" + "-" * (card_width - 2) + "+"
    
    # Print the card
    print("\n" + holes)
    print(border)
    print(header)
    print(border)
    print(content)
    print(border + "\n")

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
    """Settings dialog for configuring the punch card display."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)
        
        # Set dark theme
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background'].name()};
                color: {COLORS['text'].name()};
            }}
            QLabel, QSpinBox, QCheckBox {{
                color: {COLORS['text'].name()};
            }}
        """)
        
        layout = QFormLayout(self)
        
        # Display settings
        display_group = QGroupBox("Display Settings")
        display_layout = QFormLayout()
        
        self.led_delay = QSpinBox()
        self.led_delay.setRange(50, 500)
        self.led_delay.setValue(100)
        self.led_delay.setSuffix(" ms")
        display_layout.addRow("LED Update Delay:", self.led_delay)
        
        self.message_delay = QSpinBox()
        self.message_delay.setRange(1000, 10000)
        self.message_delay.setValue(3000)
        self.message_delay.setSuffix(" ms")
        display_layout.addRow("Message Delay:", self.message_delay)
        
        self.random_delay = QCheckBox()
        self.random_delay.setChecked(True)
        display_layout.addRow("Random Delay:", self.random_delay)
        
        self.show_splash = QCheckBox()
        self.show_splash.setChecked(True)
        display_layout.addRow("Show Splash Screen:", self.show_splash)
        
        self.auto_console = QCheckBox()
        self.auto_console.setChecked(True)
        display_layout.addRow("Auto-Open Console:", self.auto_console)
        
        display_group.setLayout(display_layout)
        layout.addRow(display_group)
        
        # Card dimensions settings
        card_group = QGroupBox("Card Dimensions")
        card_layout = QFormLayout()
        
        self.scale_factor = QSpinBox()
        self.scale_factor.setRange(1, 10)
        self.scale_factor.setValue(3)
        display_layout.addRow("Scale Factor:", self.scale_factor)
        
        self.top_margin = QSpinBox()
        self.top_margin.setRange(0, 50)
        self.top_margin.setValue(10)
        self.top_margin.setSuffix(" px")
        card_layout.addRow("Top Margin:", self.top_margin)
        
        self.side_margin = QSpinBox()
        self.side_margin.setRange(0, 50)
        self.side_margin.setValue(14)
        self.side_margin.setSuffix(" px")
        card_layout.addRow("Side Margin:", self.side_margin)
        
        self.row_spacing = QSpinBox()
        self.row_spacing.setRange(1, 20)
        self.row_spacing.setValue(6)
        self.row_spacing.setSuffix(" px")
        card_layout.addRow("Row Spacing:", self.row_spacing)
        
        self.column_spacing = QSpinBox()
        self.column_spacing.setRange(1, 20)
        self.column_spacing.setValue(2)
        self.column_spacing.setSuffix(" px")
        card_layout.addRow("Column Spacing:", self.column_spacing)
        
        self.hole_width = QSpinBox()
        self.hole_width.setRange(1, 20)
        self.hole_width.setValue(3)
        self.hole_width.setSuffix(" px")
        card_layout.addRow("Hole Width:", self.hole_width)
        
        self.hole_height = QSpinBox()
        self.hole_height.setRange(1, 20)
        self.hole_height.setValue(9)
        self.hole_height.setSuffix(" px")
        card_layout.addRow("Hole Height:", self.hole_height)
        
        card_group.setLayout(card_layout)
        layout.addRow(card_group)
        
        # Add buttons
        button_layout = QHBoxLayout()
        save_button = RetroButton("Save")
        cancel_button = RetroButton("Cancel")
        
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addRow(button_layout)
    
    def get_settings(self) -> dict:
        """Get the current settings values."""
        return {
            'led_delay': self.led_delay.value(),
            'message_delay': self.message_delay.value(),
            'random_delay': self.random_delay.isChecked(),
            'show_splash': self.show_splash.isChecked(),
            'auto_console': self.auto_console.isChecked(),
            'scale_factor': self.scale_factor.value(),
            'top_margin': self.top_margin.value(),
            'side_margin': self.side_margin.value(),
            'row_spacing': self.row_spacing.value(),
            'column_spacing': self.column_spacing.value(),
            'hole_width': self.hole_width.value(),
            'hole_height': self.hole_height.value()
        }

def show_settings_dialog(parent=None):
    """Show the settings dialog and apply settings if accepted."""
    # Use parent's settings dialog if available, otherwise create a new one
    settings_dialog = None
    if hasattr(parent, 'settings') and parent.settings:
        settings_dialog = parent.settings
    else:
        settings_dialog = SettingsDialog(parent)
    
    # Show the dialog and apply settings if accepted
    if settings_dialog.exec() == QDialog.DialogCode.Accepted:
        # Get the settings
        settings = settings_dialog.get_settings()
        
        # Apply to parent if it has the right attributes
        if parent and hasattr(parent, 'led_delay') and hasattr(parent, 'timer'):
            parent.led_delay = settings['led_delay']
            parent.timer.setInterval(parent.led_delay)
            
            # Update auto timer if available
            if hasattr(parent, 'auto_timer'):
                parent.auto_timer.setInterval(settings['message_delay'])
                
            # Update card dimensions if method exists
            if hasattr(parent, 'punch_card') and hasattr(parent.punch_card, 'update_dimensions'):
                card_settings = {k: v for k, v in settings.items() if k in [
                    'scale_factor', 'top_margin', 'side_margin', 
                    'row_spacing', 'column_spacing', 'hole_width', 'hole_height'
                ]}
                parent.punch_card.update_dimensions(card_settings)
        
        # Log the settings change to the console
        if hasattr(parent, 'console') and parent.console:
            parent.console.log(f"Settings updated: {settings}", "INFO")
        
        return True
    
    return False

def apply_settings(settings_dialog, display_obj):
    """Apply settings from the dialog.
    
    Args:
        settings_dialog: The settings dialog to get values from
        display_obj: The display object for updating the timer
    """
    # Update the timer
    interval = settings_dialog.interval_spinner.value()
    update_message_timer(display_obj, interval)
    
    # Update other settings
    config['interval'] = interval
    config['delay_factor'] = settings_dialog.delay_spinner.value()
    config['model'] = settings_dialog.model_dropdown.currentText()
    config['temperature'] = settings_dialog.temperature_spinner.value()
    config['max_length'] = settings_dialog.length_spinner.value()
    config['terminal_mode'] = settings_dialog.terminal_checkbox.isChecked()
    config['retro_mode'] = settings_dialog.retro_checkbox.isChecked()
    config['punch_card_mode'] = settings_dialog.punchcard_checkbox.isChecked()

def check_database():
    """Legacy wrapper for database initialization."""
    return initialize_database()

def calculate_message_interval():
    """Calculate the message interval based on settings.
    
    Returns:
        int: The message interval in milliseconds
    """
    # Get the interval from settings or use default
    interval_seconds = float(config.get('interval', 15))
    
    # Apply delay factor if available
    delay_factor = float(config.get('delay_factor', 1.0))
    interval_seconds = interval_seconds * delay_factor
    
    # Convert to milliseconds and ensure it's an integer
    interval_ms = int(interval_seconds * 1000)
    
    # Make sure it's at least 1000ms
    return max(1000, interval_ms)

def initialize_database():
    """Initialize the database with tables and basic data."""
    global DB_CONN
    
    try:
        # Check if database connection is already established
        if DB_CONN is None:
            DB_CONN = sqlite3.connect("messages.db")
            debug_log("✅ Connected to database", "system")
        
        # Create cursor
        cursor = DB_CONN.cursor()
        
        # Create messages table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
            source TEXT DEFAULT 'local',
            timestamp TEXT NOT NULL
            )
        ''')
        
        # Check if we need to add sample data
        cursor.execute("SELECT COUNT(*) FROM messages")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Add sample data if the table is empty
            debug_log("ℹ️ Database is empty, adding sample messages", "system")
            
            # Sample messages
            sample_messages = [
                "WELCOME TO THE PUNCH CARD SYSTEM",
                "IBM SYSTEM/360 MODEL 40",
                "DO NOT FOLD SPINDLE OR MUTILATE",
                "FORTRAN IV COMPILER VERSION 1.4",
                "DATA PROCESSING DEPARTMENT",
                "SYSTEM READY FOR INPUT",
                "JOB COMPLETED SUCCESSFULLY"
            ]
            
            # Insert sample messages
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for msg in sample_messages:
                cursor.execute(
                    "INSERT INTO messages (message, source, timestamp) VALUES (?, ?, ?)",
                    (msg, "local", timestamp)
                )
        
        # Commit changes
            DB_CONN.commit()
        
            # Verify count
        cursor.execute("SELECT COUNT(*) FROM messages")
            count = cursor.fetchone()[0]
        
            debug_log(f"✅ Database initialized with {count} messages", "system")
        return True
        
    except Exception as e:
        debug_log(f"❌ Error initializing database: {str(e)}", "error")
        return False

def add_api_console():
    """Add an API console window for debugging and monitoring API calls.
    
    Returns:
        tuple: (console window object, console text edit object)
    """
    global API_CONSOLE, config
    
    # Create a new console window if one doesn't exist
    if API_CONSOLE is None:
        # Create the console window
        console_window = QDialog()
        console_window.setWindowTitle("Punch Card Console")
        console_window.resize(800, 600)
        console_window.setModal(False)
        
        # Create layout
        layout = QVBoxLayout(console_window)
        
        # Create console text edit
        console = QTextEdit()
        console.setReadOnly(True)
        console.setFont(QFont("Courier New", 10))
        
        # Set console styling
        console.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #00ff00;
                border: none;
                font-family: 'Courier New', monospace;
            }
        """)
        
        # Add console to layout
        layout.addWidget(console)
        
        # Create button bar
        button_bar = QHBoxLayout()
        
        # Create buttons
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(lambda: console.clear())
        
        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(lambda: QApplication.clipboard().setText(console.toPlainText()))
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(console_window.close)
        
        # Add buttons to button bar
        button_bar.addWidget(clear_button)
        button_bar.addWidget(copy_button)
        button_bar.addStretch()
        button_bar.addWidget(close_button)
        
        # Add button bar to layout
        layout.addLayout(button_bar)
        
        # Store console window and text edit
        API_CONSOLE = (console_window, console)
        
        # Log console creation
        logging.info("✅ API console created")
        
        # Always show the console in debug mode
        if '--debug' in sys.argv:
        console_window.show()
            logging.info("Console window shown (debug mode)")
        
        # Add a welcome message
        timestamp = datetime.now().strftime("%H:%M:%S")
        console.append(f"<span style='color: #55AA55;'>[{timestamp}] PUNCH CARD CONSOLE INITIALIZED</span>")
        console.append(f"<span style='color: #CCCCCC;'>[{timestamp}] Press 'C' key to toggle console visibility</span>")
        console.append(f"<span style='color: #FFAA55;'>[{timestamp}] Starting LED matrix initialization</span>")
        
    return API_CONSOLE

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

class PunchCardDisplay(QMainWindow):
    """Main window for the minimalist punch card display application."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Punch Card Display")
        self.setMinimumSize(900, 600)
        
        # Set window style and background color
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {COLORS['background'].name()};
                color: {COLORS['text'].name()};
                {get_font_css(bold=False, size=FONT_SIZE)}
            }}
        """)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(0)  # Reduce spacing to minimize shifts
        
        # ================== TOP SECTION ==================
        # Create a container for the top section (message label) with fixed height
        top_section = QWidget()
        top_section.setFixedHeight(60)  # Fixed height to prevent layout shifts
        top_layout = QVBoxLayout(top_section)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)
        
        # Create message display label container with proper alignment
        self.message_container = QWidget()
        message_layout = QHBoxLayout(self.message_container)
        message_layout.setContentsMargins(0, 0, 0, 0)
        message_layout.setSpacing(0)
        
        # Create message display label - left aligned
        self.message_label = QLabel("")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.message_label.setStyleSheet(f"""
            {get_font_css(bold=False, size=FONT_SIZE+2)}
            color: {COLORS['text'].name()};
            padding: 10px 0px;
        """)
        self.message_label.setFont(get_font(bold=False, size=FONT_SIZE+2))
        
        # Add message label to container with proper alignment
        message_layout.addWidget(self.message_label, 1)  # 1 = stretch factor
        top_layout.addWidget(self.message_container)
        
        # Add the top section to the main layout
        self.main_layout.addWidget(top_section)
        
        # ================== MIDDLE SECTION (PUNCH CARD) ==================
        # Create a fixed container for the punch card to ensure it stays in place
        punch_card_container = QWidget()
        punch_card_layout = QVBoxLayout(punch_card_container)
        punch_card_layout.setContentsMargins(0, 0, 0, 0)
        punch_card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create punch card widget
        self.punch_card = PunchCardWidget()
        punch_card_layout.addWidget(self.punch_card)
        
        # Add the punch card container to the main layout with stretch factor
        self.main_layout.addWidget(punch_card_container, 1)  # 1 = stretch factor
        
        # ================== BOTTOM SECTION ==================
        # Create a container for the bottom section with fixed height
        # This ensures that the punch card position remains stable
        bottom_section = QWidget()
        bottom_section.setFixedHeight(190)  # Increased from 170 to prevent button cutoff
        bottom_layout = QVBoxLayout(bottom_section)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(5)
        
        # Create status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.status_label.setStyleSheet(f"""
            {get_font_css(bold=False, size=FONT_SIZE)}
            color: {COLORS['text'].name()};
            padding: 5px 0px;
        """)
        self.status_label.setFont(get_font(bold=False, size=FONT_SIZE))
        self.status_label.setFixedHeight(40)
        bottom_layout.addWidget(self.status_label)
        
        # Create hardware status label for initialization phase
        self.hardware_status_label = QLabel("")
        self.hardware_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hardware_status_label.setStyleSheet(f"""
            {get_font_css(bold=False, size=FONT_SIZE-2)}
            color: {COLORS['text'].name()};
            padding: 5px;
        """)
        self.hardware_status_label.setFont(get_font(bold=False, size=FONT_SIZE-2))
        self.hardware_status_label.setFixedHeight(30)
        bottom_layout.addWidget(self.hardware_status_label)
        
        # Create keyboard shortcut hint label
        self.keyboard_hint_label = QLabel("Press [SPACE] to skip hardware detection and use virtual mode")
        self.keyboard_hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.keyboard_hint_label.setStyleSheet(f"""
            {get_font_css(italic=True, size=FONT_SIZE-2)}
            color: {QColor(150, 150, 150).name()};
            padding: 5px;
        """)
        self.keyboard_hint_label.setFixedHeight(30)
        bottom_layout.addWidget(self.keyboard_hint_label)
        
        # Create API status label
        self.api_status_label = QLabel("API: Unknown")
        self.api_status_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text'].name()};
                background-color: {COLORS['card_bg'].name()};
                padding: 3px 8px;
                border: 1px solid {COLORS['hole_outline'].name()};
                border-radius: 2px;
                {get_font_css(bold=True, size=10)}
            }}
        """)
        self.api_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bottom_layout.addWidget(self.api_status_label)
        
        # Create a spacer widget to maintain spacing even when elements are hidden
        spacer = QWidget()
        spacer.setFixedHeight(10)
        bottom_layout.addWidget(spacer)
        
        # Create control buttons in a container with fixed height
        self.button_container = QWidget()
        button_layout = QHBoxLayout(self.button_container)
        button_layout.setSpacing(10)
        
        self.start_button = RetroButton("DISPLAY MESSAGE")
        self.clear_button = RetroButton("CLEAR")
        self.api_button = RetroButton("API CONSOLE")
        self.exit_button = RetroButton("EXIT")
        
        self.start_button.clicked.connect(self.start_display)
        self.clear_button.clicked.connect(self.punch_card.clear_grid)
        self.api_button.clicked.connect(self.show_api_console)
        self.exit_button.clicked.connect(self.close)
        
        button_layout.addStretch(1)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.api_button)
        button_layout.addWidget(self.exit_button)
        button_layout.addStretch(1)
        
        self.button_container.setFixedHeight(60)
        bottom_layout.addWidget(self.button_container)
        
        # Add the bottom section to the main layout
        self.main_layout.addWidget(bottom_section)
        
        # Initialize display variables
        self.current_message = ""
        self.current_char_index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.display_next_char)
        self.led_delay = 100  # milliseconds
        self.running = False
        
        # Create console and settings dialogs
        self.console = ConsoleWindow(self)
        self.settings = SettingsDialog(self)
        
        # Create API console window
        self.api_console = APIConsoleWindow(self)
        
        # Show console automatically
        self.console.show()
        
        # Initialize message generator
        self.message_generator = MessageGenerator()
        
        # Set up keyboard shortcuts
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Initialize auto-timer but don't start it yet
        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(self.generate_next_message)
        
        # Initialize hardware detector
        self.hardware_detector = HardwareDetector(self.console)
        
        # Add splash screen timer
        self.splash_timer = QTimer()
        self.splash_timer.timeout.connect(self.update_splash)
        self.splash_step = 0
        self.showing_splash = True
        self.hardware_check_complete = False
        self.countdown_seconds = 10
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        
        # Hardware status update timer
        self.hardware_status_timer = QTimer()
        self.hardware_status_timer.timeout.connect(self.update_hardware_status)
        self.hardware_status_timer.start(500)  # Check every 500ms
        
        # Add more variables for animation control
        self.hardware_detection_finished = False
        self.animation_started = False
        
        # Always start with splash screen
        self.start_splash_screen()
    
    def show_api_console(self):
        """Show the API console window."""
        self.api_console.show()
        self.console.log("API Console opened", "INFO")
        
    def validate_led_state(self, row: int, col: int, expected_state: bool, phase: str):
        """Validate that an LED is in the expected state and fix if necessary."""
        actual_state = self.punch_card.grid[row][col]
        if actual_state != expected_state:
            self.console.log(f"LED STATE ERROR: LED at ({row},{col}) is {actual_state} but should be {expected_state} during {phase}", "ERROR")
            self.punch_card.set_led(row, col, expected_state)
            return False
        else:
            self.console.log(f"LED STATE VALID: LED at ({row},{col}) is correctly {expected_state} during {phase}", "INFO")
            return True
            
    def verify_top_left_corner(self, expected_state: bool, phase: str):
        """Verify that the top-left corner LED is in the expected state."""
        return self.validate_led_state(0, 0, expected_state, phase)
    
    def generate_next_message(self):
        """Generate and display the next random message."""
        if not self.running and not self.showing_splash:
            message = self.message_generator.generate_message()
            self.display_message(message)
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        if event.key() == Qt.Key.Key_C:
            self.console.show()
        elif event.key() == Qt.Key.Key_A:
            self.api_console.show()
        elif event.key() == Qt.Key.Key_S:
            show_settings_dialog(self)
        elif event.key() == Qt.Key.Key_Space and self.showing_splash and not self.hardware_check_complete:
            # Skip hardware detection and use virtual mode
            self.auto_skip_hardware_detection()
        else:
            super().keyPressEvent(event)
    
    def update_status(self, status: str):
        """Update the status label with a new status message."""
        self.status_label.setText(status)
        
        # Make sure the status always has consistent styling
        QTimer.singleShot(10, self.align_message_with_card)
            
        self.console.log(f"Status: {status}")
    
    def align_message_with_card(self):
        """Align the message label with the left edge of the punch card."""
        # This function ensures the message label text aligns with the punch card
        # by measuring the punch card position and adjusting the label margins
        try:
            # Get the global position of the punch card widget
            card_pos = self.punch_card.mapToGlobal(QPoint(0, 0))
            # Convert to position relative to the message container
            container_pos = self.message_container.mapFromGlobal(card_pos)
            # Set left margin to align with punch card's left edge
            self.message_container.layout().setContentsMargins(
                max(0, container_pos.x()), 0, 0, 0
            )
        except Exception as e:
            # Log error but don't crash
            logging.warning(f"Error aligning message with card: {e}")
    
    def update_api_status(self, status: str):
        """Update the API status label."""
        status_color = {
            "Ready": "#88ff88",  # Green
            "Error": "#ff8888",  # Red
            "Loading": "#ffff88", # Yellow
            "Offline": "#888888"  # Gray
        }.get(status, "#ffffff")  # Default white
        
        self.api_status_label.setText(f"API: {status}")
        self.api_status_label.setStyleSheet(f"""
            QLabel {{
                color: {status_color};
                background-color: {COLORS['card_bg'].name()};
                padding: 3px 8px;
                border: 1px solid {COLORS['hole_outline'].name()};
                border-radius: 2px;
                {get_font_css(bold=True, size=10)}
            }}
        """)
    
    def display_message(self, message: str, source: str = "", delay: int = 100):
        """Display a message with optional source information."""
        # Update source information if provided (including API status)
        if source:
            # Check if source includes API status
            if "API:" in source:
                api_status = source.split("|")[0].strip().replace("API: ", "")
                self.update_api_status(api_status)
                
                # Update status label with just the serial number part
                if "|" in source:
                    serial_info = source.split("|")[1].strip()
                    self.status_label.setText(serial_info)
                else:
                    self.status_label.setText("")
            else:
                # Traditional source display (backward compatibility)
                self.status_label.setText(source)
        else:
            self.status_label.setText("")
            
        # Don't display messages during splash screen
        if self.showing_splash:
            self.console.log("Ignoring message display request during splash animation", "WARNING")
            return
            
        self.current_message = message.upper()
        self.current_char_index = 0
        self.punch_card.clear_grid()
        self.led_delay = delay
        self.timer.setInterval(delay)
        self.message_label.setText(message)
        
        # Ensure the message is always aligned with the punch card
        QTimer.singleShot(10, self.align_message_with_card)
        
        self.update_status(f"PROCESSING: {message}")
        self.start_display()
    
    def start_display(self):
        """Start displaying the message."""
        if not self.running:
            self.running = True
            self.timer.start(self.led_delay)
            self.console.log(f"Starting display with delay: {self.led_delay}ms", "INFO")
            
    def display_next_char(self):
        """Display the next character of the message."""
        if self.current_char_index >= len(self.current_message):
            self.timer.stop()
            self.running = False
            self.update_status(f"DISPLAYED: {self.current_message}")
            self.console.log(f"Completed displaying message: {self.current_message}", "INFO")
            return
            
        # Get the current character
        char = self.current_message[self.current_char_index]
        
        # Move to the next character for the next call
        self.current_char_index += 1
        
        # Process the character
        self.process_character(char, self.current_char_index - 1)
        
    def process_character(self, char: str, position: int):
        """Process a character and add it to the punch card display."""
        # IBM cards had 80 columns (numbered 1-80), but we use 0-79 for programming
        col = position
        
        # Skip if column is out of range
        if col >= NUM_COLS:
            self.console.log(f"Skipping character '{char}' - column {col+1} is out of range", "WARNING")
            return
            
        self.console.log(f"Processing character '{char}' at column {col+1}", "INFO")
        
        # For numbers (0-9), punch the appropriate row
        if char.isdigit():
            row = int(char)
            self.punch_card.set_led(row, col, True)
            self.console.log(f"LED: Digit '{char}' - Row {row}", "LED")
            
        # For uppercase letters (A-Z), use row 10 + digit rows
        # For example, 'A' is row 10 (zone) + row 1 = rows 10 and 1
        elif char.isalpha():
            # Convert to uppercase
            char = char.upper()
            # Map from A-Z to 1-26 (ASCII code - 64)
            value = ord(char) - 64
            
            # IBM card encoding: letters use zone punches (10/11/12) + digit punches (1-9)
            if 1 <= value <= 9:
                # A-I: Zone 10 + digits 1-9
                self.punch_card.set_led(10, col, True)  # Zone 10
                self.punch_card.set_led(value, col, True)  # Digit 1-9
                self.console.log(f"LED: Letter '{char}' - Zone 10 + Row {value}", "LED")
            elif 10 <= value <= 18:
                # J-R: Zone 11 + digits 1-9
                self.punch_card.set_led(11, col, True)  # Zone 11
                self.punch_card.set_led(value - 9, col, True)  # Digit 1-9
                self.console.log(f"LED: Letter '{char}' - Zone 11 + Row {value-9}", "LED")
            elif 19 <= value <= 26:
                # S-Z: Zone 12 + digits 1-9
                self.punch_card.set_led(0, col, True)  # Zone 12 (row 0 in our grid)
                self.punch_card.set_led(value - 18, col, True)  # Digit 1-9
                self.console.log(f"LED: Letter '{char}' - Zone 12 + Row {value-18}", "LED")
                
        # Handle special characters with IBM card encoding
        elif char == ' ':
            # Space - no punches
            self.console.log(f"LED: Space - No punches", "LED")
            
        elif char == '.':
            # Period - rows 12+8+3
            self.punch_card.set_led(0, col, True)   # Row 12 (row 0 in our grid)
            self.punch_card.set_led(8, col, True)   # Row 8
            self.punch_card.set_led(3, col, True)   # Row 3
            self.console.log(f"LED: Period - Rows 12+8+3", "LED")
            
        elif char == ',':
            # Comma - rows 12+8+4
            self.punch_card.set_led(0, col, True)   # Row 12
            self.punch_card.set_led(8, col, True)   # Row 8
            self.punch_card.set_led(4, col, True)   # Row 4
            self.console.log(f"LED: Comma - Rows 12+8+4", "LED")
            
        elif char == '/':
            # Slash - rows 0+1
            self.punch_card.set_led(0, col, True)   # Row 0
            self.punch_card.set_led(1, col, True)   # Row 1
            self.console.log(f"LED: Slash - Rows 0+1", "LED")
            
        elif char == '-':
            # Hyphen/Minus - row 11
            self.punch_card.set_led(11, col, True)  # Row 11
            self.console.log(f"LED: Hyphen - Row 11", "LED")
            
        elif char == '+':
            # Plus - rows 12+6+8
            self.punch_card.set_led(0, col, True)   # Row 12
            self.punch_card.set_led(6, col, True)   # Row 6
            self.punch_card.set_led(8, col, True)   # Row 8
            self.console.log(f"LED: Plus - Rows 12+6+8", "LED")
            
        elif char == '=':
            # Equals - rows 11+6+8
            self.punch_card.set_led(11, col, True)  # Row 11
            self.punch_card.set_led(6, col, True)   # Row 6
            self.punch_card.set_led(8, col, True)   # Row 8
            self.console.log(f"LED: Equals - Rows 11+6+8", "LED")
            
        elif char == '*':
            # Asterisk - rows 11+4+8
            self.punch_card.set_led(11, col, True)  # Row 11
            self.punch_card.set_led(4, col, True)   # Row 4
            self.punch_card.set_led(8, col, True)   # Row 8
            self.console.log(f"LED: Asterisk - Rows 11+4+8", "LED")
            
        elif char == '!':
            # Exclamation - rows 11+3+8
            self.punch_card.set_led(11, col, True)  # Row 11
            self.punch_card.set_led(3, col, True)   # Row 3
            self.punch_card.set_led(8, col, True)   # Row 8
            self.console.log(f"LED: Exclamation - Rows 11+3+8", "LED")
            
        elif char == '?':
            # Question Mark - rows 12+2+8
            self.punch_card.set_led(0, col, True)   # Row 12
            self.punch_card.set_led(2, col, True)   # Row 2
            self.punch_card.set_led(8, col, True)   # Row 8 
            self.console.log(f"LED: Question - Rows 12+2+8", "LED")
            
        else:
            # All other characters - use a default pattern (11+1 zone)
            self.punch_card.set_led(11, col, True)  # Row 11
            self.punch_card.set_led(2, col, True)   # Row 2
            self.console.log(f"LED: Special character '{char}' - Row 11 + Row 2", "LED")
            
    def start_splash_screen(self):
        """Start the splash screen animation."""
        self.showing_splash = True
        self.splash_step = 0
        self.hardware_check_complete = False
        self.countdown_seconds = 10  # Reset countdown to 10 seconds
        self.hardware_detection_finished = False
        self.animation_started = False
        
        # Instead of hiding UI elements, just make them invisible or empty
        # This preserves their space in the layout
        self.message_label.setText("")
        self.message_label.setStyleSheet(f"""
            {get_font_css(bold=False, size=FONT_SIZE+2)}
            color: {COLORS['background'].name()};  # Make text invisible
            padding: 10px 0px;
        """)
        
        # Calculate the left edge position of the punch card - ensure it works for splash screen too
        self.align_message_with_card()
        
        self.status_label.setText("DETECTING HARDWARE...")
        
        self.hardware_status_label.setText("Starting hardware detection...")
        self.hardware_status_label.setStyleSheet(f"""
            {get_font_css(bold=False, size=FONT_SIZE-2)}
            color: {COLORS['text'].name()};
            padding: 5px;
        """)
        
        # Update keyboard hint text with countdown
        self.keyboard_hint_label.setText(f"Press [SPACE] to skip hardware detection ({self.countdown_seconds}s)")
        self.keyboard_hint_label.setStyleSheet(f"""
            {get_font_css(italic=True, size=FONT_SIZE-2)}
            color: {QColor(150, 150, 150).name()};
            padding: 5px;
        """)
        
        # Start the countdown timer
        self.countdown_timer.start(1000)  # 1000ms = 1 second
        
        # Make buttons invisible but keep their space in the layout
        for button in [self.start_button, self.clear_button, self.exit_button]:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['background'].name()};
                    color: {COLORS['background'].name()};
                    border: 0px solid {COLORS['background'].name()};
                    padding: 6px 12px;
                    {get_font_css(size=12)}
                    border-radius: 3px;
                }}
            """)
            button.setEnabled(False)
        
        self.console.log("Starting hardware detection - clearing all LEDs", "INFO")
        
        # Clear any potential artifacts
        self.punch_card.clear_grid()
        
        # Start the hardware detection process
        self.console.log("Starting hardware detection", "INFO")
        self.hardware_detector.detect_hardware()
    
    def update_countdown(self):
        """Update the countdown timer during hardware detection."""
        self.countdown_seconds -= 1
        
        # Update the keyboard hint with the remaining seconds
        self.keyboard_hint_label.setText(f"Press [SPACE] to skip hardware detection ({self.countdown_seconds}s)")
        
        # If countdown has reached zero or hardware detection is already complete
        if self.countdown_seconds <= 0 or self.hardware_detector.detection_complete:
            # Auto-skip when countdown reaches zero
            self.auto_skip_hardware_detection()
    
    def auto_skip_hardware_detection(self):
        """Skip hardware detection and enable virtual mode."""
        # Stop the countdown timer 
        self.countdown_timer.stop()
        
        # Only proceed if hardware detection is not already complete
        if not self.hardware_check_complete:
            self.console.log("Auto-skipping hardware detection - enabling virtual mode", "WARNING")
            
            # Force the hardware detector into virtual mode
            self.hardware_detector.enable_virtual_mode()
            
            # Set ALL the necessary flags to ensure we can proceed
            self.hardware_check_complete = True
            self.hardware_detection_finished = True
            
            # Update hardware status message
            self.hardware_status_label.setText("Hardware detection skipped - using virtual mode")
            self.hardware_status_label.setStyleSheet(f"""
                {get_font_css(bold=False, size=FONT_SIZE-2)}
                color: {COLORS['text'].name()};
                padding: 5px;
            """)
            
            # Update the keyboard hint message
            self.keyboard_hint_label.setText("Hardware virtualization will be used instead")
            self.keyboard_hint_label.setStyleSheet(f"""
                {get_font_css(italic=True, size=FONT_SIZE-2)}
                color: {COLORS['text'].name()};
                padding: 5px;
            """)
            
            # Start the animation immediately
            self.start_animation()
    
    def start_animation(self):
        """Start the splash animation after hardware detection is complete."""
        # If the animation is already started, don't restart it
        if self.animation_started:
            return
            
        # Set animation as started regardless of hardware detection status
        self.animation_started = True
        self.status_label.setText("STARTING ANIMATION...")
        self.console.log("Starting splash animation", "INFO")
        
        # Make sure hardware detection is considered finished
        self.hardware_detection_finished = True
        self.hardware_check_complete = True
        
        # Ensure the hardware detector is in a valid state
        if not self.hardware_detector.detection_complete:
            self.hardware_detector.enable_virtual_mode()
        
        # Start the splash animation timer
        self.splash_timer.start(100)
    
    def update_hardware_status(self):
        """Update the hardware status label."""
        # If hardware detection is complete and animation hasn't started yet
        if self.hardware_detector.detection_complete and not self.animation_started:
            # Show hardware detection results
            pi_status = self.hardware_detector.raspberry_pi_status
            led_status = self.hardware_detector.led_controller_status
            
            # Format status for display
            pi_color = "green" if pi_status == "Connected" else "yellow" if pi_status == "Virtual Mode" else "red"
            led_color = "green" if led_status == "Ready" else "yellow" if led_status == "Virtual Mode" else "red"
            
            # Update the hardware status label with colored status indicators
            self.hardware_status_label.setText(
                f'Raspberry Pi: <span style="color:{pi_color};">{pi_status}</span>, ' +
                f'LED Controller: <span style="color:{led_color};">{led_status}</span>'
            )
            
            # Set flags and start animation if not already started
            if not self.hardware_check_complete:
                self.hardware_check_complete = True
                self.hardware_detection_finished = True
                mode_type = "hardware" if not self.hardware_detector.using_virtual_mode else "virtual"
                self.console.log(f"Hardware detection complete - using {mode_type} mode", "INFO")
                
                # Update keyboard hint to show the active mode
                self.keyboard_hint_label.setText(f"System ready - using {mode_type.upper()} mode")
                color = QColor(100, 200, 100) if mode_type == "hardware" else QColor(200, 200, 100)
                self.keyboard_hint_label.setStyleSheet(f"""
                    {get_font_css(italic=True, size=FONT_SIZE-2)}
                    color: {color.name()};
                    padding: 5px;
                """)
                
                # Start the animation
                self.start_animation()
                
        # If hardware detection is still in progress and animation hasn't started
        elif not self.hardware_detector.detection_complete and not self.animation_started:
            # Hardware detection still in progress - update status
            self.hardware_status_label.setText(
                f'Raspberry Pi: <span style="color:yellow;">Detecting...</span>, ' +
                f'LED Controller: <span style="color:yellow;">Waiting...</span>'
            )
    
    def update_splash(self):
        """Update the splash screen animation."""
        if not self.showing_splash:
            return
            
        # Calculate total steps needed to cover the entire card
        total_steps = NUM_COLS + NUM_ROWS - 1  # This ensures we cover the entire diagonal
        
        # Log the current splash step to console only
        self.console.log(f"Splash step: {self.splash_step} of {total_steps*2 + 12}", "INFO")
        
        # Ensure we have hardware detection complete - critical fix
        if not self.hardware_check_complete:
            # Double-check that we're in a valid state before proceeding
            if self.hardware_detector.detection_complete or self.hardware_detector.using_virtual_mode:
                # Hardware detection completed naturally since last check
                self.hardware_check_complete = True
                self.hardware_detection_finished = True
            else:
                # Still waiting - skip again to avoid getting stuck
                self.auto_skip_hardware_detection()
                return
            
        # Phase transitions - verify top-left corner state
        if self.splash_step == 0:
            # At the very beginning, make sure top-left corner is OFF
            self.verify_top_left_corner(False, "Initial state")
        elif self.splash_step == total_steps:
            # At start of Phase 2, verify top-left corner is OFF before we turn it ON
            self.verify_top_left_corner(False, "Start of Phase 2")
        elif self.splash_step == total_steps * 2:
            # At start of Phase 3, verify that top-left corner is either ON or OFF depending on current animation
            # Logic below will ensure it gets properly set
            pass
            
        # Phase 1: Initial clearing (empty card)
        if self.splash_step < total_steps:
            # Make sure the top-left corner (0,0) is explicitly cleared first
            if self.splash_step == 0:
                self.console.log(f"LED: Explicitly clearing top-left corner (0,0)", "LED")
                self.punch_card.set_led(0, 0, False)
                # Verify it got cleared
                self.verify_top_left_corner(False, "Phase 1 start")
            
            # Clear the current diagonal
            for row in range(NUM_ROWS):
                col = self.splash_step - row
                if 0 <= col < NUM_COLS:
                    # Skip the top-left corner as we've already handled it
                    if not (row == 0 and col == 0):
                        self.console.log(f"LED: Clearing row {row}, col {col} (Phase 1)", "LED")
                        self.punch_card.set_led(row, col, False)
            
            # Only show phase information in console, not in main GUI
            self.console.log(f"SPLASH ANIMATION - CLEARING {self.splash_step}/{total_steps}", "INFO")
        
        # Phase 2: Punching holes with a 12-hole width
        elif self.splash_step < total_steps * 2:
            current_step = self.splash_step - total_steps
            
            # At the beginning of Phase 2, explicitly turn on the top-left corner
            if current_step == 0:
                self.console.log(f"LED: Explicitly turning ON top-left corner (0,0)", "LED")
                self.punch_card.set_led(0, 0, True)
                # Verify it got turned on
                self.verify_top_left_corner(True, "Phase 2 start")
            elif current_step <= 12:
                # During the first 12 steps of Phase 2, keep checking that the top-left corner is ON
                if not self.verify_top_left_corner(True, f"Phase 2 step {current_step}"):
                    # If verification failed, explicitly turn it back ON
                    self.console.log(f"LED: Re-enabling top-left corner (0,0) that was incorrectly OFF", "LED")
                    self.punch_card.set_led(0, 0, True)
            
            # Punch new holes at the current diagonal
            for row in range(NUM_ROWS):
                col = current_step - row
                if 0 <= col < NUM_COLS:
                    # Skip the top-left corner as we've already handled it
                    if not (row == 0 and col == 0):
                        self.console.log(f"LED: Setting row {row}, col {col} ON (Phase 2)", "LED")
                        self.punch_card.set_led(row, col, True)
            
            # Clear old holes (trailing diagonal pattern - 12 columns wide)
            trailing_step = max(0, current_step - 12)
            for row in range(NUM_ROWS):
                col = trailing_step - row
                if 0 <= col < NUM_COLS:
                    # Only clear top-left corner when it's definitely time to clear it
                    # This prevents it from being cleared too early
                    if row == 0 and col == 0 and current_step >= 12:
                        self.console.log(f"LED: Explicitly turning OFF top-left corner (0,0)", "LED")
                        self.punch_card.set_led(0, 0, False)
                        # Verify it got turned off
                        self.verify_top_left_corner(False, f"Phase 2 trailing step {current_step}")
                    elif not (row == 0 and col == 0):
                        self.console.log(f"LED: Setting row {row}, col {col} OFF (Phase 2 trailing)", "LED")
                        self.punch_card.set_led(row, col, False)
            
            # Only show phase information in console, not in main GUI
            self.console.log(f"SPLASH ANIMATION - ILLUMINATING {current_step}/{total_steps}", "INFO")
        
        # Phase 3: Clear the remaining 12 columns in a diagonal pattern
        elif self.splash_step < total_steps * 2 + 12:
            current_clear_step = self.splash_step - (total_steps * 2) + (total_steps - 12)
            
            # Make sure top-left corner is OFF by this phase
            if self.splash_step == total_steps * 2:
                self.console.log(f"LED: Final check - ensuring top-left corner (0,0) is OFF", "LED")
                self.punch_card.set_led(0, 0, False)
                # Verify it got turned off
                self.verify_top_left_corner(False, "Phase 3 start")
            
            for row in range(NUM_ROWS):
                col = current_clear_step - row
                if 0 <= col < NUM_COLS:
                    # Skip the top-left corner as we've already handled it
                    if not (row == 0 and col == 0):
                        self.console.log(f"LED: Setting row {row}, col {col} OFF (Phase 3)", "LED")
                        self.punch_card.set_led(row, col, False)
            
            # Only show phase information in console, not in main GUI
            remaining_steps = (total_steps * 2 + 12) - self.splash_step
            self.console.log(f"SPLASH ANIMATION - FINISHING (REMAINING: {remaining_steps})", "INFO")
        
        else:
            # Wait for hardware detection to complete before ending splash screen
            # This check is now redundant since we only start animation after hardware detection
            # but keeping it for safety
            if not self.hardware_check_complete:
                # Keep the animation paused at this step
                self.status_label.setText("WAITING FOR HARDWARE...")
                return
                
            # Stop all timers
            if self.countdown_timer.isActive():
                self.countdown_timer.stop()
            self.splash_timer.stop()
            self.hardware_status_timer.stop()
            
            # Hide all initialization messages immediately
            self.status_label.setText("")
            self.hardware_status_label.setText("")
            self.keyboard_hint_label.setText("")
            
            # Verify all LEDs are OFF before final clearing
            if self.punch_card.grid[0][0]:
                self.console.log(f"LED STATE ERROR: Top-left corner (0,0) is still ON at end of animation!", "ERROR")
            
            # Clear all LEDs and log each one
            for row in range(NUM_ROWS):
                for col in range(NUM_COLS):
                    if self.punch_card.grid[row][col]:
                        self.console.log(f"LED: Final clearing row {row}, col {col}", "LED")
                        
            # Clear the grid with a single operation after logging
            self.punch_card.clear_grid()
            self.punch_card.update()
            self.console.log("Splash animation completed, transitioning to ready state", "INFO")
            
            # Schedule actual UI reveal and message generation after a delay
            QTimer.singleShot(500, self.complete_splash_screen)
            return
        
        # Force a repaint to ensure LED changes are displayed
        self.punch_card.update()
        self.splash_step += 1
    
    def complete_splash_screen(self):
        """Complete the splash screen transition and prepare for normal operation."""
        self.showing_splash = False
        
        # Make sure countdown timer is stopped
        if self.countdown_timer.isActive():
            self.countdown_timer.stop()
        
        # First update the status text while other elements are hidden
        self.status_label.setText("READY")
        self.console.log("Splash screen completed, ready for operation", "INFO")
        
        # Determine the operation mode based on hardware detection
        mode_type = "HARDWARE" if not self.hardware_detector.using_virtual_mode else "VIRTUAL"
        
        # Pre-set the message label content before showing it
        self.message_label.setText(f"SYSTEM READY - {mode_type} MODE")
        self.message_label.setStyleSheet(f"""
            {get_font_css(bold=False, size=FONT_SIZE+2)}
            color: {COLORS['text'].name()};
            padding: 10px 0px;
        """)
        
        # Ensure message label aligns with the left edge of the punch card
        QTimer.singleShot(10, self.align_message_with_card)
        
        # Hide hardware-specific status indicators by making them transparent
        # but keep their space in the layout
        self.hardware_status_label.setStyleSheet(f"""
            {get_font_css(bold=False, size=FONT_SIZE-2)}
            color: {COLORS['background'].name()};
            padding: 5px;
        """)
        
        self.keyboard_hint_label.setStyleSheet(f"""
            {get_font_css(italic=True, size=FONT_SIZE-2)}
            color: {COLORS['background'].name()};
            padding: 5px;
        """)
        
        # Restore button styles
        for button in [self.start_button, self.clear_button, self.exit_button]:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['button_bg'].name()};
                    color: {COLORS['text'].name()};
                    border: 1px solid {COLORS['hole_outline'].name()};
                    padding: 6px 12px;
                    {get_font_css(size=12)}
                    border-radius: 3px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['button_hover'].name()};
                }}
                QPushButton:pressed {{
                    background-color: {COLORS['button_bg'].name()};
                    padding: 7px 11px 5px 13px;
                }}
            """)
            button.setEnabled(True)
        
        # Update API status
        self.update_api_status("Ready")
        
        # Show a welcome message
        welcome_message = "PUNCH CARD DISPLAY SYSTEM READY"
        
        # Use setTimeout to allow UI to fully update before showing the message
        QTimer.singleShot(500, lambda: self.display_message(welcome_message))
        
        # Schedule auto-timer to start generating messages periodically
        # Get timing from settings or use a default (5 seconds)
        auto_interval = 5000  # Default 5 seconds
        try:
            auto_interval = config.get("message_delay", 5000)
        except:
            pass
        
        # Start the auto timer with the configured interval
        self.auto_timer.setInterval(auto_interval)
        self.auto_timer.start()
        self.console.log(f"Auto message timer started with interval: {auto_interval}ms", "INFO")

def gui_main():
    """Initialize and run the GUI application."""
    # Create application and display
    app = QApplication(sys.argv)
    apply_styling(app)
    
    global display
    display = PunchCardDisplay()
    
    # Show the display
    display.show()
    
    # Connect signal handlers for clean exit
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start the splash animation by default
    display.start_splash_screen()
    
    # Execute the application
    sys.exit(app.exec())

def main():
    """Main function to run the application."""
    try:
        # Parse command-line arguments
        args = parse_args()
        
        # Setup logging
        setup_logging()
        
        # Setup OpenAI client if needed
        setup_openai_client()
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Log startup
        logging.info("Starting Punch Card Display System")
        
        # Initialize and run the GUI
        main_window, app = gui_main()
        
        # Run the event loop
        logging.info("Running event loop. Press Ctrl+C to exit.")
        sys.exit(app.exec())
    
    except Exception as e:
        logging.error(f"❌ Error in main function: {e}")
        traceback.print_exc()
        sys.exit(1)

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
            update_api_console("Clearing display...", "system")
            
            # Display empty message
            if hasattr(display, 'display_message'):
                display.display_message("")
                update_api_console("Display cleared", "system")
            else:
                update_api_console("⚠️ Unable to clear display - no display_message method found", "warning")
                
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
        
        update_api_console("Showing statistics dialog", "system")
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
        
        update_api_console("Showing keyboard shortcuts dialog", "system")
        msg_box.exec()
        
    except Exception as e:
        print(f"⚠️ Error showing shortcuts dialog: {e}")
        update_api_console(f"Error showing shortcuts dialog: {str(e)[:50]}")

def check_and_display_api_status(parent=None):
    """Check API status and display results."""
    global service_status
    
    try:
        from PyQt6.QtWidgets import QMessageBox
        
        update_api_console("Checking API status...", "system")
        
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
        
        update_api_console("Showing API status dialog", "system")
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

def load_settings():
    """Load settings from the configuration file."""
    global config
    
    try:
        # Default settings
        default_settings = {
            "message_source": "local",
            "interval": 15,
            "delay_factor": 1.0,
            "display_stats": True,
            "save_to_database": True,
            "debug_mode": False,
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_length": 80,
            "terminal_mode": True,
            "retro_mode": True,
            "punch_card_mode": True
        }
        
        # Try to load settings from file
        settings_files = [
            "punch_card_settings.json",
            "config/punch_card_settings.json",
            os.path.expanduser("~/.punch_card/settings.json")
        ]
        
        for file in settings_files:
            try:
                if os.path.exists(file):
                    with open(file, 'r') as f:
                        file_settings = json.load(f)
                        # Update config with file settings
                        config.update(file_settings)
                        debug_log(f"✅ Loaded settings from {file}", "system")
                        break
            except Exception as e:
                debug_log(f"⚠️ Error loading {file}: {str(e)}", "warning")
        
        # Ensure all default settings are present
        for key, value in default_settings.items():
            if key not in config:
                config[key] = value
                debug_log(f"Using default setting for {key}: {value}", "system")
        
        debug_log("✅ Settings loaded successfully", "system")
        return True
        
    except Exception as e:
        debug_log(f"❌ Error loading settings: {str(e)}", "error")
        return False

def save_settings():
    """Save settings to the configuration file."""
    global config
    
    try:
        # Create config directory if it doesn't exist
        config_dir = os.path.expanduser("~/.punch_card")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        # Save to user's home directory
        settings_file = os.path.join(config_dir, "settings.json")
        
        with open(settings_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        debug_log(f"✅ Settings saved to {settings_file}", "system")
        return True
        
    except Exception as e:
        debug_log(f"❌ Error saving settings: {str(e)}", "error")
        return False

def update_api_console(message, level="info"):
    """Update the API console with a message.
    
    This function appends a formatted message to the API console with appropriate
    color coding based on the message level. LED state messages are specially 
    formatted and aggregated where possible for better organization.
    
    Args:
        message (str): The message to display
        level (str): The message level (info, warning, error, led, system)
    """
    if not API_CONSOLE or not API_CONSOLE[1]:
        # Console doesn't exist
        return
    
    console = API_CONSOLE[1]
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Define color and icon mapping for different message levels
    level_formatting = {
        "info": {"color": "#AAAAFF", "icon": "ℹ️"},      # Blue for general info
        "warning": {"color": "#FFAA55", "icon": "⚠️"},   # Orange for warnings
        "error": {"color": "#FF5555", "icon": "❌"},      # Red for errors
        "led": {"color": "#AAFFAA", "icon": "💡"},       # Green for LED operations
        "system": {"color": "#55AAFF", "icon": "🖥️"},    # Light blue for system events
        "success": {"color": "#55FF55", "icon": "✅"}     # Bright green for success
    }
    
    # Get the formatting for this level (default to info)
    format_info = level_formatting.get(level.lower(), level_formatting["info"])
    color = format_info["color"]
    icon = format_info["icon"]
    
    # Special handling for LED messages to reduce verbosity
    if level.lower() == "led" and "LED" in message:
        # Extract LED position if available (format: RxCy)
        led_match = re.search(r"R(\d+)C(\d+)", message)
        if led_match:
            row, col = led_match.groups()
            # Format LED messages with a consistent, compact style
            if "ON" in message and "OFF" in message:
                # State change message
                console.append(f"<span style='color: {color};'>[{timestamp}] 💡 LED change: R{row}C{col} ({message.split(':')[0].strip()})</span>")
            else:
                # Simple state message
                state = "ON" if "ON" in message else "OFF"
                console.append(f"<span style='color: {color};'>[{timestamp}] 💡 LED {state}: R{row}C{col}</span>")
            return
        elif "Clearing" in message:
            # Handle grid clearing messages with count
            count_match = re.search(r"Clearing (\d+) LEDs", message)
            if count_match:
                led_count = count_match.group(1)
                console.append(f"<span style='color: {color};'>[{timestamp}] 🧹 Cleared {led_count} LEDs</span>")
                return
    
    # For all other messages, use standard formatting
    console.append(f"<span style='color: {color};'>[{timestamp}] {icon} {message}</span>")

def check_openai_status():
    """Check the status of the OpenAI API."""
    global service_status
    
    try:
        # Try to make a simple API call
        if not openai_client:
            service_status["openai"] = {
                "status": "error",
                "message": "Client not initialized"
            }
            return False
        
        # Test the connection
        models = openai_client.models.list(limit=1)
        
        service_status["openai"] = {
            "status": "operational",
            "message": f"Connected - {len(models.data)} models available"
        }
        return True
        
    except Exception as e:
        service_status["openai"] = {
            "status": "error",
            "message": str(e)
        }
        return False

def parse_args():
    """Parse command-line arguments.
    
    Returns:
        argparse.Namespace: The parsed arguments
    """
    parser = argparse.ArgumentParser(description='Punch Card Display')
    parser.add_argument('--interval', type=int, help='Interval between messages in seconds')
    parser.add_argument('--openai', action='store_true', help='Use OpenAI for message generation')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--version', action='store_true', help='Show version information and exit')
    
    return parser.parse_args()

def apply_styling(app):
    """Apply styling to the application.
    
    Args:
        app: The QApplication instance
    """
    # Define the global style
    global_style = """
    QMainWindow, QWidget {
        background-color: #222222;
        color: #EEEEEE;
        font-family: "Courier New", monospace;
    }
    
    QPushButton {
        background-color: #444444;
        color: #EEEEEE;
        border: 1px solid #666666;
        border-radius: 3px;
        padding: 5px 10px;
    }
    
    QPushButton:hover {
        background-color: #555555;
    }
    
    QPushButton:pressed {
        background-color: #333333;
    }
    
    QLineEdit, QTextEdit, QComboBox {
        background-color: #333333;
        color: #EEEEEE;
        border: 1px solid #666666;
        border-radius: 3px;
        padding: 3px;
    }
    
    QLabel {
        color: #EEEEEE;
    }
    
    QCheckBox {
        color: #EEEEEE;
    }
    
    QCheckBox::indicator {
        width: 15px;
        height: 15px;
        background-color: #333333;
        border: 1px solid #666666;
    }
    
    QCheckBox::indicator:checked {
        background-color: #00AA00;
    }
    """
    
    # Apply the style sheet to the application
    app.setStyleSheet(global_style)
    
    # Log the styling
    logging.info("Applied global styling to application")
    
    return True

def update_message_timer(display_obj, interval=None):
    """Update the message timer interval.
    
    Args:
        display_obj: The display object with the message timer
        interval (int, optional): The new interval in seconds
    """
    if not hasattr(display_obj, 'message_timer'):
        logging.error("❌ Display object has no message_timer attribute")
        return False
    
    # Calculate interval if not provided
    if interval is None:
        interval_ms = calculate_message_interval()
    else:
        # Convert seconds to milliseconds and ensure it's an integer
        interval_ms = int(float(interval) * 1000)
    
    # Update the timer
    try:
        display_obj.message_timer.setInterval(interval_ms)
        logging.info(f"Message timer updated to {interval_ms/1000:.1f} seconds")
        return True
    except Exception as e:
        logging.error(f"❌ Error updating message timer: {e}")
        return False

def signal_handler(sig, frame):
    """
    Handle signals (like Ctrl+C) to gracefully shutdown the application.
    """
    debug_log(f"Received signal {sig}, shutting down...", "system")
    
    # Save settings
    save_settings()
    
    # Close any database connections
    global DB_CONN
    if DB_CONN:
        try:
            DB_CONN.close()
            debug_log("Database connection closed", "system")
        except Exception as e:
            debug_log(f"Error closing database: {str(e)}", "error")
    
    # Exit gracefully
    debug_log("Exiting application...", "system")
    sys.exit(0)

class PunchCardWidget(QWidget):
    """Widget for displaying the minimalist punch card."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.num_rows = NUM_ROWS
        self.num_cols = NUM_COLS
        self.grid = [[False for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        self.status_label = None  # Reference to status label for updates
        
        # Animation state
        self.current_message = ""
        self.is_animating = False
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animation_step)
        
        # Initialize dimensions
        self.update_dimensions()
        
        # Set black background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, COLORS['background'])
        self.setPalette(palette)
        
        # Ensure widget maintains a consistent size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Set minimum size to prevent collapse during layout changes
        window_margin = 40
        self.setMinimumSize(self.card_width + 2*window_margin, self.card_height + 2*window_margin)
    
    def update_dimensions(self, settings=None):
        """Update the card dimensions based on settings."""
        if settings:
            scale = settings.get('scale_factor', SCALE_FACTOR)
            self.card_width = int(187.325 * scale)  # 7⅜ inches = 187.325mm
            self.card_height = int(82.55 * scale)   # 3¼ inches = 82.55mm
            self.top_margin = int(settings.get('top_margin', TOP_BOTTOM_MARGIN) * scale)
            self.side_margin = int(settings.get('side_margin', SIDE_MARGIN) * scale)
            self.row_spacing = int(settings.get('row_spacing', ROW_SPACING) * scale)
            self.column_spacing = int(settings.get('column_spacing', COLUMN_SPACING) * scale)
            self.hole_width = int(settings.get('hole_width', HOLE_WIDTH) * scale)
            self.hole_height = int(settings.get('hole_height', HOLE_HEIGHT) * scale)
        else:
            # Use default dimensions
            self.card_width = CARD_WIDTH
            self.card_height = CARD_HEIGHT
            self.top_margin = TOP_BOTTOM_MARGIN
            self.side_margin = SIDE_MARGIN
            self.row_spacing = ROW_SPACING
            self.column_spacing = COLUMN_SPACING
            self.hole_width = HOLE_WIDTH
            self.hole_height = HOLE_HEIGHT
        
        # Update minimum size
        window_margin = 40
        self.setMinimumSize(self.card_width + 2*window_margin, self.card_height + 2*window_margin)
        self.update()
    
    def resizeEvent(self, event):
        """Handle resize events to maintain consistent appearance."""
        super().resizeEvent(event)
        # No additional logic needed here as paintEvent will handle proper centering
    
    def set_led(self, row: int, col: int, state: bool):
        """Set a single LED in the grid with optimized logging."""
        if 0 <= row < self.num_rows and 0 <= col < self.num_cols:
            # Only update if the state is actually changing
            if self.grid[row][col] != state:
                self.grid[row][col] = state
                
                # Log the change with row/column identifiers for clearer logs
                led_identifier = f"R{row}C{col}"
                logging.info(f"LED: {led_identifier} turned {'ON' if state else 'OFF'}")
                
                # Calculate hole position for targeted update
                card_x = (self.width() - self.card_width) // 2
                card_y = (self.height() - self.card_height) // 2
                
                # Calculate usable area for holes
                usable_width = self.card_width - (2 * self.side_margin)
                usable_height = self.card_height - (2 * self.top_margin)
                
                # Calculate spacing between holes
                col_spacing = (usable_width - (NUM_COLS * self.hole_width)) / (NUM_COLS - 1)
                row_spacing = (usable_height - (NUM_ROWS * self.hole_height)) / (NUM_ROWS - 1)
                
                # Calculate the exact position of this LED
                x = card_x + self.side_margin + col * (self.hole_width + col_spacing)
                y = card_y + self.top_margin + row * (self.hole_height + row_spacing)
                
                # Add a small margin for the update region to include the hole outline
                margin = 2
                update_rect = QRect(int(x - margin), int(y - margin), 
                                   int(self.hole_width + 2*margin), int(self.hole_height + 2*margin))
                
                # Update only the region of this LED for better performance
                self.update(update_rect)
    
    def clear_grid(self):
        """Clear the entire grid efficiently."""
        # Count how many LEDs are currently ON
        leds_on = sum(sum(row) for row in self.grid)
        
        if leds_on > 0:
            # Log the grid clearing operation
            logging.info(f"Clearing grid - turning off {leds_on} LEDs")
            
            # Reset the grid
            self.grid = [[False for _ in range(self.num_cols)] for _ in range(self.num_rows)]
            self.update()
    
    def paintEvent(self, event):
        """Paint the punch card with exact IBM specifications."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate the centered position of the card
        card_x = (self.width() - self.card_width) // 2
        card_y = (self.height() - self.card_height) // 2
        
        # Create the card path with notched corner
        card_path = QPainterPath()
        
        # Start from the top-left corner (after the notch)
        card_path.moveTo(card_x + NOTCH_WIDTH, card_y)
        
        # Draw the notch
        card_path.lineTo(card_x, card_y + NOTCH_HEIGHT)
        
        # Complete the card outline
        card_path.lineTo(card_x, card_y + self.card_height)  # Left side
        card_path.lineTo(card_x + self.card_width, card_y + self.card_height)  # Bottom
        card_path.lineTo(card_x + self.card_width, card_y)  # Right side
        card_path.lineTo(card_x + NOTCH_WIDTH, card_y)  # Top
        
        # Fill card background (black)
        painter.fillPath(card_path, QBrush(COLORS['card_bg']))
        
        # Draw card outline (white) with thinner stroke
        painter.setPen(QPen(COLORS['card_outline'], 0.3))
        painter.drawPath(card_path)
        
        # Calculate usable area for holes
        usable_width = self.card_width - (2 * self.side_margin)
        usable_height = self.card_height - (2 * self.top_margin)
        
        # Calculate spacing between holes
        col_spacing = (usable_width - (NUM_COLS * self.hole_width)) / (NUM_COLS - 1)
        row_spacing = (usable_height - (NUM_ROWS * self.hole_height)) / (NUM_ROWS - 1)
        
        # Draw all holes
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                # Calculate hole position
                x = card_x + self.side_margin + col * (self.hole_width + col_spacing)
                y = card_y + self.top_margin + row * (self.hole_height + row_spacing)
                
                # Create the hole path
                hole_rect = QRectF(x, y, self.hole_width, self.hole_height)
                
                # Set fill color based on hole state
                if self.grid[row][col]:
                    painter.fillRect(hole_rect, COLORS['hole_punched'])
                else:
                    painter.fillRect(hole_rect, COLORS['hole_fill'])
                
                # Draw hole outline (white) with thinner stroke
                painter.setPen(QPen(COLORS['hole_outline'], 0.15))
                painter.drawRect(hole_rect)
    
    def display_message(self, message):
        """Display a message on the punch card.
        
        Args:
            message (str): The message to display
        """
        # Skip if we're already animating
        if self.is_animating:
            update_api_console("⚠️ Animation already in progress, ignoring new message request", "warning")
            return
            
        # Store the message (in uppercase for punch card aesthetic)
        self.current_message = message.upper()
        
        # Clear the grid first
        self.clear_grid()
        
        logging.info(f"Displaying message: {message}")
        
        # Format the message as a punch card
        punch_card = format_punch_card(message)
        
        # Start the animation
        self.animate_punch_card(punch_card)
        
        # Update status label if available
        if self.status_label:
            self.status_label.setText(f"DISPLAYING: {message}")
    
    def animate_punch_card(self, punch_card):
        """Animate the punch card display using a 12-column wide diagonal pattern.
        
        This implementation is based on version 0.5.2's diagonal animation system,
        which creates a smooth, consistent animation across the entire grid.
        
        Args:
            punch_card (str): The formatted punch card with 'O' for holes
        """
        # Don't start a new animation if one is already in progress
        if self.is_animating:
            logging.warning("Animation already in progress, ignoring new request")
            return
        
        # Clear all LEDs before starting animation
        self.clear_grid()
        
        # Set animation flag
        self.is_animating = True
        
        # Parse the punch card
        rows = punch_card.strip().split('\n')
        logging.info(f"Starting animation with {len(rows)} rows")
        
        # Create a matrix for hole positions
        self.hole_matrix = [[False for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        # Convert punch card format to hole matrix
        hole_count = 0
        for i, row in enumerate(rows):
            if i < self.num_rows:
                for j, char in enumerate(row):
                    if j < self.num_cols and char == 'O':
                        self.hole_matrix[i][j] = True
                        hole_count += 1
        
        logging.info(f"Found {hole_count} holes in the punch card")
        
        # Animation parameters
        self.diagonal_width = 12  # Width of the diagonal pattern (12 columns wide)
        self.current_diagonal = 0  # Start at the first diagonal
        
        # Calculate total diagonals needed for complete coverage
        # Total diagonals = rows + cols - 1 (to cover every position once)
        # Add extra steps for full right side coverage (+10)
        self.total_diagonals = self.num_rows + self.num_cols - 1 + 10
        
        # Start animation timer
        self.animation_timer.setInterval(30)  # Consistent speed of 30ms for smooth animation
        self.animation_timer.start()
        
        logging.info(f"Animation started with {self.total_diagonals} frames at 30ms interval")
    
    def _animation_step(self):
        """Process one step of the diagonal animation."""
        # Skip if animation not in progress
        if not self.is_animating:
            logging.warning("Animation step called when not animating, ignoring")
            return
        
        # Check if animation is complete
        if self.current_diagonal >= self.total_diagonals:
            # Stop the animation
            self.animation_timer.stop()
            self.is_animating = False
            
            # Clear the grid at completion
            self.clear_grid()
            
            logging.info("✅ Animation completed successfully")
            
            # Update status if available
            if self.status_label:
                self.status_label.setText(f"DISPLAY COMPLETE: {self.current_message}")
            
            return
        
        # Log progress at key points
        if self.current_diagonal % 10 == 0 or self.current_diagonal == self.total_diagonals - 1:
            progress = (self.current_diagonal / self.total_diagonals) * 100
            logging.info(f"Animation progress: {progress:.0f}% (frame {self.current_diagonal}/{self.total_diagonals})")
        
        # Clear the grid for this animation frame
        self.clear_grid()
        
        # Calculate the leading edge of the diagonal
        leading_diagonal = self.current_diagonal
        
        # Illuminate LEDs in the current diagonal band based on hole positions
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                # Calculate position's diagonal value (row + col)
                position_diagonal = row + col
                
                # Check if this position is within the current diagonal band
                is_in_current_diagonal = (position_diagonal <= leading_diagonal) and \
                                         (position_diagonal > leading_diagonal - self.diagonal_width)
                
                # Turn on the LED if it's in the current diagonal band AND it's a hole position
                if is_in_current_diagonal and self.hole_matrix[row][col]:
                    self.set_led(row, col, True)
        
        # Move to next diagonal
        self.current_diagonal += 1
        
        # Force update to ensure smooth display
        self.update()

def get_local_message():
    """Get a local message for display.
    
    Returns:
        str: A message for display
    """
    return generate_local_message()

def generate_local_message():
    """Generate a local message without using OpenAI.
    
    Returns:
        str: A randomly generated message
    """
    logging.info("Generating local message")
    
    # List of sample messages
    messages = [
        "SYSTEM OPERATING WITHIN PARAMETERS",
        "VACUUM TUBES AT FULL POWER",
        "PROCESSING UNIT ONLINE",
        "CALCULATING TRAJECTORY",
        "PUNCH CARD INSERTED",
        "DATA PROCESSING INITIALIZED",
        "COMPUTING PIONEERS REMEMBERED",
        "MECHANICAL COMPUTING TO QUANTUM: THE JOURNEY",
        "DIGITAL ARCHAEOLOGY: EXPLORING THE PAST",
        "PROCESSING QUEUE: READY",
        "ARTIFICIAL INTELLIGENCE SEEDS PLANTED",
        "MAINFRAME CONNECTION ESTABLISHED",
        "TERMINAL READY FOR INPUT",
        "HISTORICAL COMPUTING SIMULATION ACTIVE",
        "BINARY CALCULATIONS COMPLETE",
        "HISTORICAL MODE ENGAGED",
        "1401 PROCESSING UNIT ONLINE",
        "TECHNOLOGY EVOLUTION TIMELINE DISPLAYED",
        "COMPUTATION HISTORY: LOADING FACTS",
        "PUNCH CARD READER: OPERATIONAL"
    ]
    
    # Select a random message
    message = random.choice(messages)
    logging.info(f"Generated local message: {message}")
    
    return message

def update_message_stats(message, source):
    """Update message statistics.
    
    Args:
        message (str): The message that was displayed
        source (str): The source of the message
    """
    global message_stats
    
    # Update counts
    message_stats["total"] += 1
    
    # Update source-specific count
    if source in message_stats:
        message_stats[source] += 1
    
    # Update timestamp
    message_stats["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message_stats["last_message"] = message
    message_stats["last_source"] = source
    
    # Save message to database
    save_message_to_database(message, source)

def save_message_to_database(message, source="local"):
    """
    Save a message to the database.
    
    Args:
        message (str): The message to save
        source (str): The source of the message
    
    Returns:
        bool: Whether the message was saved successfully
    """
    global DB_CONN
    
    try:
        # If database isn't initialized or saving is disabled, skip
        if not DB_CONN or not config.get('save_to_database', True):
            debug_log("⚠️ Not saving message (database disabled)", "warning")
            return False
        
        # Create cursor
        cursor = DB_CONN.cursor()
        
        # Insert message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO messages (message, source, timestamp) VALUES (?, ?, ?)",
            (message, source, timestamp)
        )
        
        # Commit changes
        DB_CONN.commit()
        
        debug_log(f"✅ Message saved to database: {message[:20]}...", "system")
        return True
        
    except Exception as e:
        debug_log(f"❌ Error saving message to database: {str(e)}", "error")
        return False

# Font configuration - adding from v0.5.2
FONT_FAMILY = "Space Mono, Courier New, monospace"
FONT_SIZE = 12  # Use consistent font size throughout the application

def get_font(bold=False, italic=False, size=FONT_SIZE) -> QFont:
    """Get a font with the specified style."""
    font = QFont()
    font.setFamily("Space Mono")
    font.setPointSize(size)
    font.setBold(bold)
    font.setItalic(italic)
    font.setStyleHint(QFont.StyleHint.Monospace)  # Fallback to any monospace font
    return font

def get_font_css(bold=False, italic=False, size=FONT_SIZE) -> str:
    """Get CSS font styling with the specified style."""
    weight = "bold" if bold else "normal"
    style = "italic" if italic else "normal"
    return f"font-family: {FONT_FAMILY}; font-size: {size}px; font-weight: {weight}; font-style: {style};"

class ClassicTitleBar(QWidget):
    """Classic Macintosh-style title bar from v0.5.2."""
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.setFixedHeight(20)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['button_bg'].name()};
                color: {COLORS['text'].name()};
                {get_font_css(bold=True, size=12)}
            }}
        """)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Set font for title
        painter.setFont(get_font(bold=True, size=12))
        
        # Draw title
        painter.setPen(COLORS['text'])
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.title)
        
        # Draw decorative lines
        line_y = self.height() // 2
        line_width = 20
        spacing = 40
        
        # Left lines
        for i in range(3):
            x = 10 + (i * spacing)
            painter.setPen(QPen(COLORS['border'], 1))
            painter.drawLine(x, line_y - 1, x + line_width, line_y - 1)
            painter.drawLine(x, line_y + 1, x + line_width, line_y + 1)
        
        # Right lines
        for i in range(3):
            x = self.width() - 10 - line_width - (i * spacing)
            painter.setPen(QPen(COLORS['border'], 1))
            painter.drawLine(x, line_y - 1, x + line_width, line_y - 1)
            painter.drawLine(x, line_y + 1, x + line_width, line_y + 1)

class RetroButton(QPushButton):
    """Minimalist styled button from v0.5.2."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['button_bg'].name()};
                color: {COLORS['text'].name()};
                border: 1px solid {COLORS['hole_outline'].name()};
                padding: 6px 12px;
                {get_font_css(size=12)}
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['button_hover'].name()};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['button_bg'].name()};
                padding: 7px 11px 5px 13px;
            }}
        """)

class ConsoleWindow(QDialog):
    """Console window for displaying system information and debug data from v0.5.2."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Console")
        self.setMinimumSize(600, 400)
        
        # Set dark theme
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['console_bg'].name()};
                color: {COLORS['console_text'].name()};
            }}
            QTextEdit {{
                background-color: {COLORS['console_bg'].name()};
                color: {COLORS['console_text'].name()};
                {get_font_css(size=12)}
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        # Create console text area
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        layout.addWidget(self.console)
        
        # Add buttons layout
        button_layout = QHBoxLayout()
        
        # Add save button
        save_button = RetroButton("Save Log")
        save_button.clicked.connect(self.save_log)
        button_layout.addWidget(save_button)
        
        # Add clear button
        clear_button = RetroButton("Clear")
        clear_button.clicked.connect(self.clear_log)
        button_layout.addWidget(clear_button)
        
        # Add close button
        close_button = RetroButton("Close")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def log(self, message: str, level: str = "INFO"):
        """Add a message to the console with timestamp and level."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        level_color = {
            "INFO": "white",
            "LED": "cyan",
            "WARNING": "yellow",
            "ERROR": "red",
            "SUCCESS": "green",
            "SYSTEM": "magenta"
        }.get(level, "white")
        
        self.console.append(f'<span style="color: gray">[{timestamp}]</span> '
                          f'<span style="color: {level_color}">[{level}]</span> '
                          f'<span style="color: white">{message}</span>')
        self.console.verticalScrollBar().setValue(
            self.console.verticalScrollBar().maximum()
        )

    def save_log(self):
        """Save the console log to a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"console_log_{timestamp}.txt"
        try:
            with open(filename, 'w') as f:
                f.write(self.console.toPlainText())
            self.log(f"Log saved to {filename}", "SUCCESS")
        except Exception as e:
            self.log(f"Error saving log: {str(e)}", "ERROR")
    
    def clear_log(self):
        """Clear the console log."""
        self.console.clear()
        self.log("Console cleared", "INFO")

class APIConsoleWindow(QDialog):
    """Console window specifically for API activity, requests, and error logging."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API Console")
        self.setMinimumSize(600, 400)
        
        # Set dark theme with accent color for API
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['console_bg'].name()};
                color: {COLORS['console_text'].name()};
            }}
            QTextEdit {{
                background-color: {COLORS['console_bg'].name()};
                color: {COLORS['console_text'].name()};
                {get_font_css(size=12)}
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        # Create console text area
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        layout.addWidget(self.console)
        
        # Add buttons layout
        button_layout = QHBoxLayout()
        
        # Add save button
        save_button = RetroButton("Save Log")
        save_button.clicked.connect(self.save_log)
        button_layout.addWidget(save_button)
        
        # Add clear button
        clear_button = RetroButton("Clear")
        clear_button.clicked.connect(self.clear_log)
        button_layout.addWidget(clear_button)
        
        # Add close button
        close_button = RetroButton("Close")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def log(self, message: str, level: str = "INFO"):
        """Add a message to the console with timestamp and level."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        level_color = {
            "INFO": "white",
            "SYSTEM": "cyan",
            "WARNING": "yellow",
            "ERROR": "red",
            "SUCCESS": "green",
            "REQUEST": "magenta",
            "RESPONSE": "#8888ff"
        }.get(level, "white")
        
        self.console.append(f'<span style="color: gray">[{timestamp}]</span> '
                          f'<span style="color: {level_color}">[{level}]</span> '
                          f'<span style="color: white">{message}</span>')
        self.console.verticalScrollBar().setValue(
            self.console.verticalScrollBar().maximum()
        )
        
    def save_log(self):
        """Save the console log to a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_log_{timestamp}.txt"
        try:
            with open(filename, 'w') as f:
                f.write(self.console.toPlainText())
            self.log(f"Log saved to {filename}", "SUCCESS")
        except Exception as e:
            self.log(f"Error saving log: {str(e)}", "ERROR")
    
    def clear_log(self):
        """Clear the console log."""
        self.console.clear()
        self.log("Console cleared", "INFO")

class HardwareDetector:
    """Detects and monitors hardware components like Raspberry Pi and LED controller."""
    
    def __init__(self, console_logger=None):
        self.console_logger = console_logger
        self.raspberry_pi_status = "Detecting..."
        self.led_controller_status = "Detecting..."
        self.is_hardware_ready = False
        self.using_virtual_mode = False
        self.raspberry_pi_ip = "192.168.1.10"  # Default IP - can be configured
        self.raspberry_pi_port = 5555          # Default port - can be configured
        self.detection_complete = False
        
    def log(self, message, level="INFO"):
        """Log a message if console logger is available."""
        if self.console_logger:
            self.console_logger.log(message, level)
        else:
            print(f"[{level}] {message}")
    
    def detect_hardware(self):
        """Start hardware detection in a background thread."""
        import threading
        self.log("Starting hardware detection process", "INFO")
        threading.Thread(target=self._run_detection, daemon=True).start()
    
    def _run_detection(self):
        """Run the detection process for Raspberry Pi and LED controller."""
        import socket
        # Check for Raspberry Pi connection
        self.raspberry_pi_status = "Detecting..."
        self.log(f"Attempting to connect to Raspberry Pi at {self.raspberry_pi_ip}:{self.raspberry_pi_port}", "INFO")
        
        try:
            # Try to establish a socket connection to the Pi
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)  # 3 second timeout
            s.connect((self.raspberry_pi_ip, self.raspberry_pi_port))
            
            # If connection successful, check LED controller
            self.raspberry_pi_status = "Connected"
            self.log("Successfully connected to Raspberry Pi", "SUCCESS")
            
            # Send a command to query LED controller status
            s.sendall(b"CHECK_LED_CONTROLLER")
            response = s.recv(1024).decode('utf-8')
            
            if "READY" in response:
                self.led_controller_status = "Ready"
                self.log("LED controller is ready", "SUCCESS")
                self.is_hardware_ready = True
            else:
                self.led_controller_status = "Error: " + response
                self.log(f"LED controller error: {response}", "ERROR")
            
            s.close()
            
        except (socket.timeout, socket.error) as e:
            self.raspberry_pi_status = "Not Found"
            self.led_controller_status = "Not Available"
            self.log(f"Failed to connect to Raspberry Pi: {str(e)}", "ERROR")
            self.log("Will use virtual mode for testing", "WARNING")
            self.using_virtual_mode = True
        
        # Mark detection as complete
        self.detection_complete = True
        self.log("Hardware detection complete", "INFO")
    
    def enable_virtual_mode(self):
        """Explicitly enable virtual mode for testing."""
        self.log("Virtual mode enabled for testing", "WARNING")
        self.raspberry_pi_status = "Virtual Mode"
        self.led_controller_status = "Virtual Mode"
        self.using_virtual_mode = True
        self.is_hardware_ready = True
        self.detection_complete = True

class MessageGenerator:
    """Generates random messages for display."""
    def __init__(self):
        self.messages = [
            "HELLO WORLD",
            "WELCOME TO THE PUNCH CARD DISPLAY",
            "IBM PUNCH CARD SYSTEM",
            "DO NOT FOLD SPINDLE OR MUTILATE",
            "COMPUTING THE FUTURE",
            "BINARY DREAMS",
            "PAPER TAPES AND PUNCH CARDS",
            "FROM MECHANICAL TO DIGITAL",
            "HISTORY IN HOLES",
            "DATA PUNCHED IN TIME"
        ]
    
    def generate_message(self) -> str:
        """Generate a random message."""
        return random.choice(self.messages)

if __name__ == '__main__':
    main() 