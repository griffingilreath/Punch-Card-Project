"""
API Manager for handling OpenAI API interactions.
"""

import os
import json
import logging
from typing import Tuple, List, Optional
from openai import OpenAI, APIError

# Import SettingsManager
from src.utils.settings_manager import get_settings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('APIManager')

class APIManager:
    """Manages OpenAI API interactions and settings."""
    
    def __init__(self):
        """Initialize the API Manager."""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        # Create handlers
        file_handler = logging.FileHandler('api_manager.log')
        console_handler = logging.StreamHandler()
        
        # Create formatters and add it to handlers
        log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(log_format)
        console_handler.setFormatter(log_format)
        
        # Add handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.client = None
        self.api_key = None
        self.model = "gpt-3.5-turbo"
        self.temperature = 0.7
        self.settings = self._load_settings()
        logger.debug(f"APIManager initialized with model: {self.model}, temperature: {self.temperature}")
    
    def _load_settings(self):
        """Load API settings from the settings manager."""
        try:
            # Get settings from settings manager
            settings_manager = get_settings()
            self.logger.debug("Loading settings from settings manager")
            
            # Load API key if available
            self.api_key = settings_manager.get_api_key()
            if self.api_key:
                self.logger.debug("API key found in settings")
                try:
                    self.client = OpenAI(api_key=self.api_key)
                    self.logger.info("OpenAI client initialized successfully")
                except Exception as e:
                    self.logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            else:
                self.logger.warning("No API key found in settings")
            
            # Load model and temperature
            self.model = settings_manager.get_model()
            self.temperature = settings_manager.get_temperature()
            self.logger.debug(f"Model set to: {self.model}")
            self.logger.debug(f"Temperature set to: {self.temperature}")
            
        except Exception as e:
            self.logger.error(f"Error loading API settings: {str(e)}", exc_info=True)
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message with the specified level."""
        level = level.upper()
        if level == "DEBUG":
            self.logger.debug(message)
        elif level == "INFO":
            self.logger.info(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "ERROR":
            self.logger.error(message)
        elif level == "CRITICAL":
            self.logger.critical(message)
        else:
            self.logger.info(message)  # Default to INFO if level is not recognized
    
    def check_api_connection(self) -> bool:
        """
        Check if the API connection is working.
        
        Returns:
            True if connection is successful, False otherwise
        """
        if not self.client:
            self.logger.error("API client not initialized - no API key available")
            return False
            
        try:
            # Test the connection by listing available models
            models = self.client.models.list()
            self.logger.info(f"Successfully retrieved {len(models.data)} available models")
            self.api_ready = True
            return True
        except Exception as e:
            error_msg = str(e)
            if "Incorrect API key" in error_msg:
                self.logger.error("API key is invalid")
            elif "Connection error" in error_msg:
                self.logger.error("Failed to connect to OpenAI API - please check your internet connection")
            else:
                self.logger.error(f"API connection check failed: {error_msg}")
            self.api_ready = False
            return False
            
    def get_available_models(self) -> List[str]:
        """
        Get a list of available models from the API.
        
        Returns:
            List of model IDs
        """
        if not self.client:
            self.logger.error("API client not initialized - no API key available")
            return []
            
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            self.logger.error(f"Failed to retrieve available models: {str(e)}")
            return []
    
    def generate_message(self, prompt: str, use_web_search: bool = False) -> Tuple[bool, str]:
        """
        Generate a message using the OpenAI API.
        
        Args:
            prompt: The input prompt
            use_web_search: Whether to use the web search tool
            
        Returns: (success, message)
        """
        self.logger.info("Generating message with OpenAI API")
        self.logger.debug(f"Prompt: {prompt}")
        self.logger.debug(f"Using web search: {use_web_search}")
        
        if not self.client:
            self.logger.error("API client not initialized")
            return False, "API client not initialized"
            
        try:
            self.logger.debug(f"Using model: {self.model}, temperature: {self.temperature}")
            
            # Prepare parameters
            params = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature
            }
            
            # Add tools parameter if web search is enabled
            if use_web_search:
                params["tools"] = [{"type": "web_search_preview"}]
            
            # Make the API call
            response = self.client.chat.completions.create(**params)
            
            message = response.choices[0].message.content
            self.logger.info("Successfully generated message")
            self.logger.debug(f"Generated message: {message}")
            
            # Update usage statistics
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            settings_manager = get_settings()
            
            # Calculate approximate cost
            model = self.model
            if "gpt-4" in model:
                prompt_cost = prompt_tokens * 0.00003  # $0.03 per 1K tokens
                completion_cost = completion_tokens * 0.00006  # $0.06 per 1K tokens
            else:  # gpt-3.5-turbo
                prompt_cost = prompt_tokens * 0.000001  # $0.001 per 1K tokens
                completion_cost = completion_tokens * 0.000002  # $0.002 per 1K tokens
            cost = prompt_cost + completion_cost
            
            # Store usage data for reference
            self.last_usage = {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "cost": cost
            }
            
            settings_manager.update_usage_stats(prompt_tokens, completion_tokens, cost)
            
            return True, message
            
        except Exception as e:
            self.logger.error(f"Error generating message: {str(e)}", exc_info=True)
            return False, f"Error generating message: {str(e)}"
    
    def generate_completion(self, system_message: str, user_message: str, use_web_search: bool = False) -> str:
        """
        Generate a completion using the OpenAI API with system and user messages.
        
        Args:
            system_message: The system message/instructions
            user_message: The user's message/query
            use_web_search: Whether to use the web search tool
            
        Returns:
            The generated completion text
            
        Raises:
            Exception: If API call fails
        """
        self.logger.info("Generating completion with OpenAI API")
        self.logger.debug(f"System: {system_message}")
        self.logger.debug(f"User: {user_message}")
        self.logger.debug(f"Using web search: {use_web_search}")
        
        if not self.client:
            if not self.api_key:
                raise ValueError("No API key configured")
            
            self.logger.debug("Initializing OpenAI client")
            self.client = OpenAI(api_key=self.api_key)
            
        # Prepare parameters
        params = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            "temperature": self.temperature
        }
        
        # Add tools parameter if web search is enabled
        if use_web_search:
            params["tools"] = [{"type": "web_search_preview"}]
        
        # Make API call
        response = self.client.chat.completions.create(**params)
        
        completion = response.choices[0].message.content
        self.logger.info("Successfully generated completion")
        
        # Update usage statistics
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        settings_manager = get_settings()
        
        # Calculate approximate cost
        model = self.model
        if "gpt-4" in model:
            prompt_cost = prompt_tokens * 0.00003  # $0.03 per 1K tokens
            completion_cost = completion_tokens * 0.00006  # $0.06 per 1K tokens
        else:  # gpt-3.5-turbo
            prompt_cost = prompt_tokens * 0.000001  # $0.001 per 1K tokens
            completion_cost = completion_tokens * 0.000002  # $0.002 per 1K tokens
        cost = prompt_cost + completion_cost
        
        # Store usage data for reference
        self.last_usage = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "cost": cost
        }
        
        settings_manager.update_usage_stats(prompt_tokens, completion_tokens, cost)
        
        return completion
    
    def update_settings(self, api_key: Optional[str] = None, 
                       model: Optional[str] = None,
                       temperature: Optional[float] = None):
        """Update API settings."""
        self.logger.info("Updating API settings")
        self.logger.debug(f"New settings - API Key: {'*' * 8 if api_key else 'None'}, Model: {model}, Temperature: {temperature}")
        
        try:
            # Get settings manager
            settings_manager = get_settings()
            
            # Update settings in the manager
            settings_manager.set_openai_settings(
                api_key=api_key, 
                model=model,
                temperature=temperature
            )
            
            # Save settings to file
            settings_manager.save_settings()
            
            # Update local instance
            if api_key is not None:
                self.api_key = api_key
                try:
                    self.client = OpenAI(api_key=api_key)
                    self.logger.info("Successfully updated API key and initialized new client")
                except Exception as e:
                    self.logger.error(f"Failed to initialize new OpenAI client: {str(e)}", exc_info=True)
            
            if model is not None:
                self.model = model
                self.logger.debug(f"Updated model to: {model}")
            
            if temperature is not None:
                self.temperature = temperature
                self.logger.debug(f"Updated temperature to: {temperature}")
                
            self.logger.info("Successfully saved updated settings")
                
        except Exception as e:
            self.logger.error(f"Error updating API settings: {str(e)}", exc_info=True) 