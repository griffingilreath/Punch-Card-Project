#!/usr/bin/env python3

"""
Test script for the APIManager with new SettingsManager integration.
"""

import os
import sys
from src.api.api_manager import APIManager
from src.utils.settings_manager import get_settings

def test_api_manager():
    """Test the APIManager with our SettingsManager."""
    print("Testing APIManager with SettingsManager integration")
    
    # First, get the settings manager and set up test values
    settings = get_settings()
    
    # Check if an API key is already set
    current_key = settings.get_api_key()
    if current_key:
        print(f"Using existing API key: {current_key[:5]}...{current_key[-5:]}")
    else:
        test_key = input("Enter a valid OpenAI API key for testing (or press Enter to skip API calls): ")
        if test_key.strip():
            settings.set_api_key(test_key)
            settings.save_settings()
            print("API key saved")
        else:
            print("No API key provided - skipping actual API calls")
    
    # Set other OpenAI settings
    settings.set_model("gpt-3.5-turbo")  # Use a cheaper model for testing
    settings.set_temperature(0.7)
    settings.save_settings()
    
    # Create an API manager instance
    api_manager = APIManager()
    print(f"API manager initialized with model: {api_manager.model}")
    
    # Check if we can make an API call
    if settings.get_api_key():
        print("\nTesting API connection...")
        success, message, models = api_manager.check_api_connection()
        print(f"Connection test: {'Success' if success else 'Failed'}")
        print(f"Message: {message}")
        if models:
            print(f"Models available: {len(models)}")
            print(f"First few models: {models[:3]}...")
        
        if success and input("\nDo you want to test a chat completion? (y/n): ").lower() == 'y':
            print("\nTesting chat completion...")
            try:
                response = api_manager.generate_completion(
                    system_message="You are a helpful assistant that responds in one short sentence.",
                    user_message="What's the capital of France?"
                )
                print(f"Response: {response}")
                print(f"Usage stats: {api_manager.last_usage}")
                
                # Verify that usage stats were updated
                usage_stats = settings.get_usage_stats()
                print(f"\nUpdated usage stats: {usage_stats['total_calls']} calls, "
                      f"{usage_stats['total_tokens']} total tokens, "
                      f"${usage_stats['estimated_cost']:.6f} estimated cost")
                
            except Exception as e:
                print(f"Error during completion: {e}")
    else:
        print("Skipping API tests due to missing API key")
    
    print("\nTest completed")

if __name__ == "__main__":
    test_api_manager() 