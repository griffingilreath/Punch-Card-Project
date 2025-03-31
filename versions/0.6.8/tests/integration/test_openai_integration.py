#!/usr/bin/env python3
"""
Test OpenAI API Integration for Punch Card Project
This script helps diagnose issues with OpenAI API integration.
"""

import json
import os
import sys
from datetime import datetime
from src.core.message_generator import MessageGenerator
from openai import OpenAI

try:
    from openai import OpenAI
    print("✅ OpenAI module imported successfully")
except ImportError:
    print("❌ Error: OpenAI module not installed. Try running 'pip install --upgrade openai'")
    sys.exit(1)

def load_settings():
    """Load settings from the configuration file."""
    try:
        settings_path = os.path.join("config", "punch_card_settings.json")
        if not os.path.exists(settings_path):
            settings_path = "punch_card_settings.json"
        
        if not os.path.exists(settings_path):
            print(f"❌ Settings file not found at {settings_path}")
            return None
            
        with open(settings_path, "r") as f:
            settings = json.load(f)
        return settings
    except Exception as e:
        print(f"❌ Error loading settings: {e}")
        return None

def test_openai_api():
    """Test direct OpenAI API access"""
    print("\nTesting direct OpenAI API access...")
    
    # Load settings
    try:
        with open('config/punch_card_settings.json', 'r') as f:
            settings = json.load(f)
            api_key = settings.get('openai_api_key')
            model = settings.get('openai_model', 'gpt-3.5-turbo')
    except Exception as e:
        print(f"❌ Error loading settings: {e}")
        return False
    
    if not api_key:
        print("❌ No API key found in settings")
        return False
    
    print(f"✓ Found API key (first 10 chars): {api_key[:10]}...")
    print(f"✓ Using model: {model}")
    
    # Test API connection with minimal configuration
    try:
        client = OpenAI(
            api_key=api_key
        )
        
        print("✓ OpenAI client initialized")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello!"}
            ],
            max_tokens=10
        )
        message = response.choices[0].message.content
        print(f"✅ API test successful! Response: {message}")
        return True
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        return False

def test_openai_integration():
    print("Testing OpenAI Integration...")
    
    # Initialize message generator
    generator = MessageGenerator(
        config_path="config/config.yaml",
        credentials_path="config/credentials.yaml"
    )
    
    # Test OpenAI message generation
    print("\nTrying to generate a message using OpenAI...")
    message = generator.generate_openai_message()
    
    if message:
        print(f"✅ Success! Generated message: {message}")
        return True
    else:
        print("❌ Failed to generate message using OpenAI")
        return False

if __name__ == "__main__":
    # Add the project root to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    print("=" * 60)
    print("OpenAI API Integration Test")
    print("=" * 60)
    
    success = test_openai_api()
    
    if success:
        print("\n✅ All tests PASSED!")
        sys.exit(0)
    else:
        print("\n❌ Tests FAILED")
        print("\nTroubleshooting steps:")
        print("1. Check if your API key is valid")
        print("2. Verify the model name is correct (should be 'gpt-3.5-turbo' or 'gpt-4')")
        print("3. Check your internet connection")
        print("4. Make sure your OpenAI account has available credits")
        sys.exit(1) 