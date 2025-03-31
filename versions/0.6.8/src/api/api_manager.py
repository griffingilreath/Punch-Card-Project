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
        """Initialize the API manager."""
        logger.info("Initializing APIManager")
        self.client = None
        self.api_key = None
        self.model = "gpt-3.5-turbo"
        self.temperature = 0.7
        self._load_settings()
        logger.debug(f"APIManager initialized with model: {self.model}, temperature: {self.temperature}")
    
    def _load_settings(self):
        """Load API settings from the settings manager."""
        try:
            # Get settings from settings manager
            settings_manager = get_settings()
            logger.debug("Loading settings from settings manager")
            
            # Load API key if available
            self.api_key = settings_manager.get_api_key()
            if self.api_key:
                logger.debug("API key found in settings")
                try:
                    self.client = OpenAI(api_key=self.api_key)
                    logger.info("OpenAI client initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            else:
                logger.warning("No API key found in settings")
            
            # Load model and temperature
            self.model = settings_manager.get_model()
            self.temperature = settings_manager.get_temperature()
            logger.debug(f"Model set to: {self.model}")
            logger.debug(f"Temperature set to: {self.temperature}")
            
        except Exception as e:
            logger.error(f"Error loading API settings: {str(e)}", exc_info=True)
    
    def check_api_connection(self) -> Tuple[bool, str, Optional[List[str]]]:
        """
        Check if the API connection is working.
        Returns: (success, status_message, available_models)
        """
        logger.info("Checking API connection")
        
        if not self.api_key:
            logger.warning("No API key configured")
            return False, "No API key configured", None
            
        try:
            if not self.client:
                logger.debug("Initializing OpenAI client")
                self.client = OpenAI(api_key=self.api_key)
            
            # Try to list models to verify the connection
            logger.debug("Attempting to list available models")
            models = self.client.models.list()
            
            # Return all available models without filtering
            available_models = [model.id for model in models.data]
            logger.info(f"Successfully retrieved {len(available_models)} available models")
            logger.debug(f"Available models: {available_models}")
            
            return True, "Connected", available_models
            
        except APIError as e:
            logger.error(f"OpenAI API Error: {str(e)}", exc_info=True)
            return False, f"API Error: {str(e)}", None
        except Exception as e:
            logger.error(f"Unexpected error during API connection check: {str(e)}", exc_info=True)
            return False, f"Connection Error: {str(e)}", None
    
    def generate_message(self, prompt: str) -> Tuple[bool, str]:
        """
        Generate a message using the OpenAI API.
        Returns: (success, message)
        """
        logger.info("Generating message with OpenAI API")
        logger.debug(f"Prompt: {prompt}")
        
        if not self.client:
            logger.error("API client not initialized")
            return False, "API client not initialized"
            
        try:
            logger.debug(f"Using model: {self.model}, temperature: {self.temperature}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature
            )
            
            message = response.choices[0].message.content
            logger.info("Successfully generated message")
            logger.debug(f"Generated message: {message}")
            
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
            logger.error(f"Error generating message: {str(e)}", exc_info=True)
            return False, f"Error generating message: {str(e)}"
    
    def generate_completion(self, system_message: str, user_message: str) -> str:
        """
        Generate a completion using the OpenAI API with system and user messages.
        
        Args:
            system_message: The system message/instructions
            user_message: The user's message/query
            
        Returns:
            The generated completion text
            
        Raises:
            Exception: If API call fails
        """
        logger.info("Generating completion with OpenAI API")
        logger.debug(f"System: {system_message}")
        logger.debug(f"User: {user_message}")
        
        if not self.client:
            if not self.api_key:
                raise ValueError("No API key configured")
            
            logger.debug("Initializing OpenAI client")
            self.client = OpenAI(api_key=self.api_key)
            
        # Make API call
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=self.temperature
        )
        
        completion = response.choices[0].message.content
        logger.info("Successfully generated completion")
        
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
        logger.info("Updating API settings")
        logger.debug(f"New settings - API Key: {'*' * 8 if api_key else 'None'}, Model: {model}, Temperature: {temperature}")
        
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
                    logger.info("Successfully updated API key and initialized new client")
                except Exception as e:
                    logger.error(f"Failed to initialize new OpenAI client: {str(e)}", exc_info=True)
            
            if model is not None:
                self.model = model
                logger.debug(f"Updated model to: {model}")
            
            if temperature is not None:
                self.temperature = temperature
                logger.debug(f"Updated temperature to: {temperature}")
                
            logger.info("Successfully saved updated settings")
                
        except Exception as e:
            logger.error(f"Error updating API settings: {str(e)}", exc_info=True) 