#!/usr/bin/env python3
"""
API Key Update Utility

This script helps you securely update your OpenAI API key by:
1. Storing it in the secrets/api_keys.json file (which is .gitignore'd)
2. Never printing the key to the console
3. Providing clear instructions

Your API key is never committed to GitHub when using this method.
"""

import os
import json
import sys
import getpass

def main():
    # Get the root directory of the project
    root_dir = os.path.dirname(os.path.abspath(__file__))
    secrets_dir = os.path.join(root_dir, "secrets")
    api_keys_file = os.path.join(secrets_dir, "api_keys.json")
    
    # Ensure the secrets directory exists
    if not os.path.exists(secrets_dir):
        os.makedirs(secrets_dir)
        print(f"Created secrets directory at {secrets_dir}")
    
    # Initialize the API keys structure
    api_keys = {
        "openai": {
            "api_key": "",
            "organization_id": ""
        },
        "other_services": {
            "service1_key": "",
            "service2_key": ""
        }
    }
    
    # Load existing API keys if the file exists
    if os.path.exists(api_keys_file):
        try:
            with open(api_keys_file, 'r') as f:
                api_keys = json.load(f)
            print("Loaded existing API keys file.")
        except Exception as e:
            print(f"Error loading existing API keys: {e}")
            print("Creating a new API keys file.")
    
    # Prompt for the OpenAI API key
    print("\n=== OpenAI API Key Update ===")
    print("Your API key will be stored in the secrets directory, which is excluded from Git.")
    print("This ensures your key won't be accidentally committed to GitHub.")
    print("\nEnter your OpenAI API key below (input will be hidden):")
    
    # Use getpass to hide the API key input
    api_key = getpass.getpass("> ")
    
    if not api_key:
        print("No API key entered. Exiting without changes.")
        return
    
    # Update the API key
    api_keys["openai"]["api_key"] = api_key
    
    # Optionally update organization ID
    org_id = input("\nEnter your OpenAI organization ID (optional, press Enter to skip): ")
    if org_id:
        api_keys["openai"]["organization_id"] = org_id
    
    # Save the API keys
    try:
        with open(api_keys_file, 'w') as f:
            json.dump(api_keys, f, indent=2)
        print(f"\n✅ API key successfully saved to {api_keys_file}")
        print("Your key is now securely stored and will be used by the application.")
    except Exception as e:
        print(f"\n❌ Error saving API key: {e}")
        return
    
    # Set up environment variable for current session
    print("\nTo use your API key in other environments, you can set this environment variable:")
    print("\nOn macOS/Linux:")
    print(f"export OPENAI_API_KEY=your-api-key-here")
    print("\nOn Windows:")
    print(f"set OPENAI_API_KEY=your-api-key-here")
    
    print("\n=== Security Reminder ===")
    print("✓ Your API key is stored in a directory that's excluded from Git")
    print("✓ The key is never printed to the console")
    print("✓ The application will automatically find and use this key")
    print("✓ Remember to keep your API key confidential")

if __name__ == "__main__":
    main() 