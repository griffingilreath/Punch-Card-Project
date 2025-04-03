#!/usr/bin/env python3
"""
Message Generator Component

Generates messages for display using OpenAI integration when available.
"""

import random
import logging
from typing import Optional, Dict, Any

from src.utils.message_bus import (
    get_message_bus, EVENT_NEW_MESSAGE, EVENT_API_STATUS_CHANGED,
    MessagePriority, Message
)

class MessageGenerator:
    """Generates messages for display using OpenAI integration when available."""
    
    def __init__(self):
        # Fallback messages when API is not available
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
        
        # Initialize API manager reference (will be set later)
        self.api_manager = None
        self.console_logger = None
        self.use_api = True
        self.api_status = "Not initialized"
        
        # Get the message bus
        self.message_bus = get_message_bus()
            
        self.init_api_manager()
    
    def init_api_manager(self):
        """Initialize the API manager reference."""
        try:
            from src.api.api_manager import APIManager
            self.api_manager = APIManager()
            self.log(f"API manager initialized", "INFO")
            
            # Test API connection
            success = self.api_manager.check_api_connection()
            self.api_status = "Connected" if success else "Not connected"
            self.use_api = success
            
            if success:
                self.log(f"API connection successful", "INFO")
                # Publish API status change event with high priority
                self.message_bus.publish(
                    EVENT_API_STATUS_CHANGED,
                    {"status": "connected", "message": "API connection successful"},
                    source="MessageGenerator",
                    priority=MessagePriority.HIGH
                )
            else:
                self.log(f"API connection failed. Using fallback messages.", "WARNING")
                self.use_api = False
                # Publish API status change event with normal priority
                self.message_bus.publish(
                    EVENT_API_STATUS_CHANGED,
                    {"status": "error", "message": "API connection failed"},
                    source="MessageGenerator",
                    priority=MessagePriority.NORMAL
                )
                
        except Exception as e:
            self.api_status = f"Error: {str(e)}"
            self.log(f"Failed to initialize API manager: {str(e)}. Using fallback messages.", "ERROR")
            self.use_api = False
            # Publish API status change event with high priority for errors
            self.message_bus.publish(
                EVENT_API_STATUS_CHANGED,
                {"status": "error", "message": str(e)},
                source="MessageGenerator",
                priority=MessagePriority.HIGH
            )
    
    def check_api_status(self):
        """Check API status and update internal state."""
        try:
            success = self.api_manager.check_api_connection()
            
            # Update internal state
            self.use_api = success
            self.api_status = "Connected" if success else "Not connected"
            
            # Log status
            if success:
                self.log("API connection successful", "INFO")
            else:
                self.log("API not available", "WARNING")
                
            # Publish API status change event
            self.message_bus.publish(EVENT_API_STATUS_CHANGED, {
                "status": "connected" if success else "error",
                "message": "API connection successful" if success else "API connection failed"
            })
            
            return success
            
        except Exception as e:
            self.log(f"Error checking API status: {str(e)}", "ERROR")
            return False

    def get_prompt_from_settings(self) -> str:
        """Get the prompt from settings or return a default prompt."""
        try:
            from src.utils.settings_manager import get_settings
            settings = get_settings()
            return settings.get("openai_prompt", "Generate a short, punchy message about computing history.")
        except Exception as e:
            self.log(f"Error getting prompt from settings: {str(e)}", "WARNING")
            return "Generate a short, punchy message about computing history."
            
    def get_web_search_enabled(self) -> bool:
        """Check if web search is enabled in settings."""
        try:
            from src.utils.settings_manager import get_settings
            settings = get_settings()
            return settings.get_use_web_search()
        except Exception as e:
            self.log(f"Error checking web search setting: {str(e)}", "WARNING")
            return False

    def generate_message(self, prompt=None):
        """Generate a message using OpenAI API or fallback to local messages."""
        try:
            # Check if we should use the API
            if self.use_api and self.api_manager:
                # Get prompt from settings or use default
                if not prompt:
                    prompt = self.get_prompt_from_settings()
                
                # Check if web search is enabled
                use_web_search = self.get_web_search_enabled()
                if use_web_search:
                    self.log("Web search is enabled for message generation", "INFO")
                
                # Generate message using API
                success, message = self.api_manager.generate_message(prompt, use_web_search=use_web_search)
                
                if success:
                    # Clean and format message
                    message = self.clean_message(message)
                    
                    # Determine source based on whether web search was used
                    source = "AI+Web" if use_web_search else "AI"
                    
                    # Log success with appropriate source
                    self.log(f"Generated message via API: {message}", "INFO")
                    
                    # Publish message to bus
                    self.message_bus.publish(EVENT_NEW_MESSAGE, {
                        "message": message,
                        "source": source
                    })
                    
                    return message
                else:
                    self.log(f"API generation failed: {message}", "WARNING")
            
            # Use fallback message if API not available or failed
            message = self.get_fallback_message()
            self.log(f"Using fallback message (API status: {self.api_status})", "INFO")
            
            # Publish message to bus
            self.message_bus.publish(EVENT_NEW_MESSAGE, {
                "message": message,
                "source": "Local"
            })
            
            return message
            
        except Exception as e:
            self.log(f"Error generating message: {str(e)}", "ERROR")
            return self.get_fallback_message()
    
    def log(self, message: str, level: str = "INFO") -> None:
        """Log a message using the console logger if available."""
        if self.console_logger:
            self.console_logger.log(message, level)
        else:
            logging.log(
                getattr(logging, level),
                f"[MessageGenerator] {message}"
            )
    
    def get_fallback_message(self) -> str:
        """Get a fallback message from the list of predefined messages."""
        return random.choice(self.messages)

    def clean_message(self, message: str) -> str:
        """Clean and format the message for display."""
        # Clean up message: remove quotes, limit length, convert to uppercase
        message = message.strip()
        if message.startswith('"') and message.endswith('"'):
            message = message[1:-1]
            
        # Ensure message isn't too long (80 chars max for punch card)
        if len(message) > 80:
            self.log(f"Message too long ({len(message)} chars), truncating", "WARNING")
            message = message[:77] + "..."
            
        # Convert to uppercase
        message = message.upper()
        
        return message 