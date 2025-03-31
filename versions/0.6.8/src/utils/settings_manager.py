"""
Settings Manager for the Punch Card Project.

This module provides a centralized way to handle application settings,
including secure storage of API keys using keychain.
"""

import os
import json
import logging
import platform
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SettingsManager')

# Try to import keyring for secure API key storage
try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False
    logger.warning("Keyring package not available. API keys will be stored in plain text.")

# Singleton instance
_settings_instance = None

def get_settings(settings_path: str = "punch_card_settings.json") -> 'SettingsManager':
    """
    Get the singleton instance of the SettingsManager.
    
    Args:
        settings_path: Optional custom path for settings file
        
    Returns:
        The SettingsManager instance
    """
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = SettingsManager(settings_path)
    return _settings_instance

class SettingsManager:
    """
    Manages application settings, providing a central interface for
    reading, writing, and validating configuration values.
    
    Securely stores sensitive information like API keys using the system keychain
    when available.
    """
    
    # Service name for keychain
    KEYCHAIN_SERVICE = "PunchCardProject"
    API_KEY_USERNAME = "openai_api_key"
    
    def __init__(self, settings_path: str = "punch_card_settings.json"):
        """
        Initialize the settings manager.
        
        Args:
            settings_path: Path to the settings JSON file
        """
        self.settings_path = settings_path
        self.settings = self._load_settings()
        logger.info(f"Settings loaded from {settings_path}")
        logger.debug(f"SettingsManager initialized with {len(self.settings)} settings")
    
    def _load_settings(self) -> Dict[str, Any]:
        """
        Load settings from file or return defaults if file doesn't exist.
        
        Returns:
            Dictionary containing all settings
        """
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, "r") as f:
                    settings = json.load(f)
                return settings
        except Exception as e:
            logger.error(f"Error loading settings: {str(e)}")
        
        # Return defaults if file doesn't exist or loading fails
        return self._get_default_settings()
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """
        Get default settings for all application parameters.
        
        Returns:
            Dictionary containing default settings
        """
        return {
            # Display settings
            "led_delay": 100,                  # Delay between LED updates in ms
            "interval": 5,                     # Interval between messages in seconds
            "message_display_time": 3,         # Time to display each message in seconds
            "delay_factor": 1.0,               # Factor for typing speed simulation
            "random_delay": True,              # Use random delay between characters
            "show_splash": True,               # Show splash screen on startup
            "auto_console": True,              # Auto-open console panel
            
            # Card settings
            "card_width": 300,                 # Width of the punch card in pixels
            "card_height": 200,                # Height of the punch card in pixels
            "scale_factor": 3,                 # Scale factor for the punch card display
            "top_margin": 4,                   # Top margin in pixels
            "side_margin": 5,                  # Side margin in pixels
            "row_spacing": 2,                  # Spacing between rows in pixels
            "column_spacing": 1,               # Spacing between columns in pixels
            "hole_width": 1,                   # Width of the holes in pixels
            "hole_height": 3,                  # Height of the holes in pixels
            
            # API settings
            "openai_api_key": "",              # Will be overridden by keychain if available
            "openai_model": "gpt-3.5-turbo",   # Default model
            "temperature": 0.7,                # Default temperature for API calls
            
            # Usage statistics
            "openai_usage": {
                "total_calls": 0,
                "total_tokens": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "estimated_cost": 0.0,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "history": []
            },
            
            # Window settings
            "window_size": [800, 600],         # Default window size [width, height]
            "window_position": [100, 100],     # Default window position [x, y]
            "theme": "dark",                   # UI theme (dark/light)
            "font_size": 12,                   # Font size for UI elements
            
            # Additional settings
            "last_directory": "",              # Last directory accessed
            "recent_files": [],                # List of recently accessed files
            "auto_save": True,                 # Auto-save settings on exit
            "debug_mode": False                # Enable debug mode
        }
    
    def save_settings(self) -> bool:
        """
        Save current settings to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure sensitive data is not saved to file if keychain is available
            settings_to_save = self.settings.copy()
            
            # Don't save API key to file if using keychain
            if KEYRING_AVAILABLE and "openai_api_key" in settings_to_save:
                settings_to_save["openai_api_key"] = ""
            
            with open(self.settings_path, "w") as f:
                json.dump(settings_to_save, f, indent=4)
            
            logger.info(f"Settings saved to {self.settings_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {str(e)}")
            return False
    
    # -------------------------------------------------------------------------
    # API Key Management with Keychain Support
    # -------------------------------------------------------------------------
    
    def get_api_key(self) -> str:
        """
        Get the OpenAI API key, preferring the keychain if available.
        
        Returns:
            API key as string
        """
        # Try to get from keychain first
        if KEYRING_AVAILABLE:
            key = keyring.get_password(self.KEYCHAIN_SERVICE, self.API_KEY_USERNAME)
            if key:
                return key
        
        # Fall back to settings file
        return self.settings.get("openai_api_key", "")
    
    def set_api_key(self, api_key: str) -> None:
        """
        Set the OpenAI API key, storing in keychain if available.
        
        Args:
            api_key: The API key to store
        """
        # Store in keychain if available
        if KEYRING_AVAILABLE and api_key:
            try:
                keyring.set_password(self.KEYCHAIN_SERVICE, self.API_KEY_USERNAME, api_key)
                logger.info("API key stored in system keychain")
                
                # Keep empty string in settings file for reference
                self.settings["openai_api_key"] = ""
            except Exception as e:
                logger.error(f"Failed to store API key in keychain: {str(e)}")
                # Fall back to settings file
                self.settings["openai_api_key"] = api_key
        else:
            # Store in settings file
            self.settings["openai_api_key"] = api_key
    
    def delete_api_key(self) -> bool:
        """
        Delete the stored API key from keychain and settings.
        
        Returns:
            True if successful, False otherwise
        """
        success = True
        
        # Remove from keychain if available
        if KEYRING_AVAILABLE:
            try:
                keyring.delete_password(self.KEYCHAIN_SERVICE, self.API_KEY_USERNAME)
                logger.info("API key deleted from system keychain")
            except Exception as e:
                logger.error(f"Failed to delete API key from keychain: {str(e)}")
                success = False
        
        # Clear from settings
        self.settings["openai_api_key"] = ""
        
        return success
    
    # -------------------------------------------------------------------------
    # OpenAI API Settings
    # -------------------------------------------------------------------------
    
    def get_model(self) -> str:
        """Get the OpenAI model name."""
        return self.settings.get("openai_model", "gpt-3.5-turbo")
    
    def set_model(self, model: str) -> None:
        """Set the OpenAI model name."""
        self.settings["openai_model"] = model
    
    def get_temperature(self) -> float:
        """Get the OpenAI temperature setting."""
        return self.settings.get("temperature", 0.7)
    
    def set_temperature(self, temperature: float) -> None:
        """Set the OpenAI temperature setting."""
        self.settings["temperature"] = max(0.0, min(2.0, temperature))  # Clamp between 0 and 2
    
    def set_openai_settings(self, api_key: Optional[str] = None, 
                           model: Optional[str] = None,
                           temperature: Optional[float] = None) -> None:
        """
        Update multiple OpenAI settings at once.
        
        Args:
            api_key: Optional API key to update
            model: Optional model name to update
            temperature: Optional temperature value to update
        """
        if api_key is not None:
            self.set_api_key(api_key)
        
        if model is not None:
            self.set_model(model)
        
        if temperature is not None:
            self.set_temperature(temperature)
    
    # -------------------------------------------------------------------------
    # Usage Statistics
    # -------------------------------------------------------------------------
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get the OpenAI API usage statistics."""
        return self.settings.get("openai_usage", {
            "total_calls": 0,
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "estimated_cost": 0.0,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "history": []
        })
    
    def update_usage_stats(self, prompt_tokens: int, completion_tokens: int, 
                         cost: Optional[float] = None) -> None:
        """
        Update usage statistics with a new API call.
        
        Args:
            prompt_tokens: Number of tokens in the prompt
            completion_tokens: Number of tokens in the completion
            cost: Optional cost of the API call
        """
        if "openai_usage" not in self.settings:
            self.settings["openai_usage"] = {
                "total_calls": 0,
                "total_tokens": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "estimated_cost": 0.0,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "history": []
            }
        
        usage = self.settings["openai_usage"]
        
        # Calculate cost if not provided
        # Using approximate costs based on gpt-3.5-turbo pricing
        if cost is None:
            model = self.get_model()
            if "gpt-4" in model:
                prompt_cost = prompt_tokens * 0.00003  # $0.03 per 1K tokens
                completion_cost = completion_tokens * 0.00006  # $0.06 per 1K tokens
            else:  # gpt-3.5-turbo
                prompt_cost = prompt_tokens * 0.000001  # $0.001 per 1K tokens
                completion_cost = completion_tokens * 0.000002  # $0.002 per 1K tokens
            cost = prompt_cost + completion_cost
        
        # Update statistics
        usage["total_calls"] += 1
        usage["total_tokens"] += (prompt_tokens + completion_tokens)
        usage["prompt_tokens"] += prompt_tokens
        usage["completion_tokens"] += completion_tokens
        usage["estimated_cost"] += cost
        usage["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Add to history (keep last 100 entries)
        usage["history"].append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "cost": cost,
            "model": self.get_model()
        })
        
        # Trim history to last 100 entries
        if len(usage["history"]) > 100:
            usage["history"] = usage["history"][-100:]
    
    def reset_usage_stats(self) -> None:
        """Reset all usage statistics to zero."""
        self.settings["openai_usage"] = {
            "total_calls": 0,
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "estimated_cost": 0.0,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "history": []
        }
    
    # -------------------------------------------------------------------------
    # Display Settings
    # -------------------------------------------------------------------------
    
    def get_led_delay(self) -> int:
        """Get the LED display delay in milliseconds."""
        return self.settings.get("led_delay", 100)
    
    def set_led_delay(self, delay: int) -> None:
        """Set the LED display delay in milliseconds."""
        self.settings["led_delay"] = max(10, min(1000, delay))  # Clamp between 10 and 1000
    
    def get_message_interval(self) -> int:
        """Get the message interval in seconds."""
        return self.settings.get("interval", 5)
    
    def set_message_interval(self, interval: int) -> None:
        """Set the message interval in seconds."""
        self.settings["interval"] = max(1, min(60, interval))  # Clamp between 1 and 60
    
    def get_message_display_time(self) -> int:
        """Get the message display time in seconds."""
        return self.settings.get("message_display_time", 3)
    
    def set_message_display_time(self, display_time: int) -> None:
        """Set the message display time in seconds."""
        self.settings["message_display_time"] = max(1, min(30, display_time))  # Clamp between 1 and 30
    
    def get_typing_delay_factor(self) -> float:
        """Get the typing delay factor."""
        return self.settings.get("delay_factor", 1.0)
    
    def set_typing_delay_factor(self, factor: float) -> None:
        """Set the typing delay factor."""
        self.settings["delay_factor"] = max(0.1, min(5.0, factor))  # Clamp between 0.1 and 5.0
    
    def get_random_delay(self) -> bool:
        """Get whether random delay is enabled."""
        return self.settings.get("random_delay", True)
    
    def set_random_delay(self, random_delay: bool) -> None:
        """Set whether random delay is enabled."""
        self.settings["random_delay"] = bool(random_delay)
    
    def get_show_splash(self) -> bool:
        """Get whether splash screen is shown on startup."""
        return self.settings.get("show_splash", True)
    
    def set_show_splash(self, show_splash: bool) -> None:
        """Set whether splash screen is shown on startup."""
        self.settings["show_splash"] = bool(show_splash)
    
    def get_auto_console(self) -> bool:
        """Get whether console is automatically opened."""
        return self.settings.get("auto_console", True)
    
    def set_auto_console(self, auto_console: bool) -> None:
        """Set whether console is automatically opened."""
        self.settings["auto_console"] = bool(auto_console)
    
    # -------------------------------------------------------------------------
    # Card Dimensions Settings
    # -------------------------------------------------------------------------
    
    def get_card_dimensions(self) -> Dict[str, int]:
        """
        Get all card dimension settings.
        
        Returns:
            Dictionary with all card dimension settings
        """
        return {
            "scale_factor": self.settings.get("scale_factor", 3),
            "top_margin": self.settings.get("top_margin", 4),
            "side_margin": self.settings.get("side_margin", 5),
            "row_spacing": self.settings.get("row_spacing", 2),
            "column_spacing": self.settings.get("column_spacing", 1),
            "hole_width": self.settings.get("hole_width", 1),
            "hole_height": self.settings.get("hole_height", 3)
        }
    
    def set_card_dimensions(self, dimensions: Dict[str, int]) -> None:
        """
        Set card dimension settings.
        
        Args:
            dimensions: Dictionary with card dimension settings to update
        """
        if "scale_factor" in dimensions:
            self.settings["scale_factor"] = max(1, min(10, dimensions["scale_factor"]))
        
        if "top_margin" in dimensions:
            self.settings["top_margin"] = max(0, min(20, dimensions["top_margin"]))
        
        if "side_margin" in dimensions:
            self.settings["side_margin"] = max(0, min(20, dimensions["side_margin"]))
        
        if "row_spacing" in dimensions:
            self.settings["row_spacing"] = max(1, min(10, dimensions["row_spacing"]))
        
        if "column_spacing" in dimensions:
            self.settings["column_spacing"] = max(1, min(5, dimensions["column_spacing"]))
        
        if "hole_width" in dimensions:
            self.settings["hole_width"] = max(1, min(5, dimensions["hole_width"]))
        
        if "hole_height" in dimensions:
            self.settings["hole_height"] = max(1, min(10, dimensions["hole_height"]))
    
    def get_card_size(self) -> Tuple[int, int]:
        """
        Get the card size in pixels.
        
        Returns:
            Tuple of (width, height)
        """
        return (
            self.settings.get("card_width", 300),
            self.settings.get("card_height", 200)
        )
    
    def set_card_size(self, width: int, height: int) -> None:
        """
        Set the card size in pixels.
        
        Args:
            width: Card width in pixels
            height: Card height in pixels
        """
        self.settings["card_width"] = max(100, min(1000, width))
        self.settings["card_height"] = max(50, min(500, height))
    
    # -------------------------------------------------------------------------
    # Window Settings
    # -------------------------------------------------------------------------
    
    def get_window_size(self) -> Tuple[int, int]:
        """
        Get the window size.
        
        Returns:
            Tuple of (width, height)
        """
        size = self.settings.get("window_size", [800, 600])
        return (size[0], size[1])
    
    def set_window_size(self, width: int, height: int) -> None:
        """
        Set the window size.
        
        Args:
            width: Window width
            height: Window height
        """
        self.settings["window_size"] = [width, height]
    
    def get_window_position(self) -> Tuple[int, int]:
        """
        Get the window position.
        
        Returns:
            Tuple of (x, y)
        """
        pos = self.settings.get("window_position", [100, 100])
        return (pos[0], pos[1])
    
    def set_window_position(self, x: int, y: int) -> None:
        """
        Set the window position.
        
        Args:
            x: Window x position
            y: Window y position
        """
        self.settings["window_position"] = [x, y]
    
    def get_theme(self) -> str:
        """Get the UI theme."""
        return self.settings.get("theme", "dark")
    
    def set_theme(self, theme: str) -> None:
        """Set the UI theme."""
        if theme in ["dark", "light"]:
            self.settings["theme"] = theme
    
    def get_font_size(self) -> int:
        """Get the font size."""
        return self.settings.get("font_size", 12)
    
    def set_font_size(self, size: int) -> None:
        """Set the font size."""
        self.settings["font_size"] = max(8, min(24, size))
    
    # -------------------------------------------------------------------------
    # File and Directory Settings
    # -------------------------------------------------------------------------
    
    def get_last_directory(self) -> str:
        """Get the last accessed directory."""
        return self.settings.get("last_directory", "")
    
    def set_last_directory(self, directory: str) -> None:
        """Set the last accessed directory."""
        if os.path.isdir(directory):
            self.settings["last_directory"] = directory
    
    def get_recent_files(self) -> List[str]:
        """Get the list of recently accessed files."""
        return self.settings.get("recent_files", [])
    
    def add_recent_file(self, file_path: str) -> None:
        """
        Add a file to the recent files list.
        
        Args:
            file_path: Path to the file
        """
        if not os.path.isfile(file_path):
            return
        
        recent_files = self.get_recent_files()
        
        # Remove if already exists
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Add to front of list
        recent_files.insert(0, file_path)
        
        # Limit to 10 recent files
        recent_files = recent_files[:10]
        
        self.settings["recent_files"] = recent_files
    
    def clear_recent_files(self) -> None:
        """Clear the recent files list."""
        self.settings["recent_files"] = []
    
    # -------------------------------------------------------------------------
    # Miscellaneous Settings
    # -------------------------------------------------------------------------
    
    def get_auto_save(self) -> bool:
        """Get whether auto-save is enabled."""
        return self.settings.get("auto_save", True)
    
    def set_auto_save(self, auto_save: bool) -> None:
        """Set whether auto-save is enabled."""
        self.settings["auto_save"] = bool(auto_save)
    
    def get_debug_mode(self) -> bool:
        """Get whether debug mode is enabled."""
        return self.settings.get("debug_mode", False)
    
    def set_debug_mode(self, debug_mode: bool) -> None:
        """Set whether debug mode is enabled."""
        self.settings["debug_mode"] = bool(debug_mode)
    
    # -------------------------------------------------------------------------
    # Direct Setting Access
    # -------------------------------------------------------------------------
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a setting by key.
        
        Args:
            key: Setting key
            default: Default value if key doesn't exist
            
        Returns:
            Setting value or default
        """
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> None:
        """
        Set a setting by key.
        
        Args:
            key: Setting key
            value: Setting value
        """
        self.settings[key] = value 