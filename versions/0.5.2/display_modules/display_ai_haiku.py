#!/usr/bin/env python3
"""
Punch Card AI Haiku Generator

Generates a haiku about AI using OpenAI API and displays it on the punch card GUI.
"""

import sys
import time
import os
import json
from openai import OpenAI
from src.display.gui_display import main as gui_main

def get_api_key():
    """Get API key from secure sources."""
    # First try: environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    
    # Second try: secrets file
    if not api_key:
        secrets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                   "secrets", "api_keys.json")
        if os.path.exists(secrets_path):
            try:
                with open(secrets_path, 'r') as f:
                    secrets = json.load(f)
                    api_key = secrets.get("openai", {}).get("api_key")
                    if api_key and api_key not in ["YOUR_OPENAI_API_KEY_HERE", "YOUR_ACTUAL_API_KEY_HERE"]:
                        return api_key
            except Exception as e:
                print(f"Error reading secrets file: {e}")
    
    if not api_key:
        print("⚠️ No API key found. Please set OPENAI_API_KEY environment variable or configure secrets/api_keys.json")
        exit(1)
        
    return api_key

# Create an OpenAI client instance with your API key
client = OpenAI(api_key=get_api_key())

def generate_haiku():
    """Generate a haiku about AI using OpenAI API."""
    try:
        # Make the API request
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "write a haiku about ai. format in uppercase without any line breaks, just one line."}
            ]
        )
        
        # Get the haiku text
        haiku = completion.choices[0].message.content.strip().upper()
        
        # Replace any linebreaks with spaces for single-line display
        haiku = haiku.replace("\n", " ")
        
        # Ensure it's not too long for the punch card (max 80 chars)
        if len(haiku) > 80:
            haiku = haiku[:77] + "..."
            
        return haiku
    except Exception as e:
        print(f"Error generating haiku: {str(e)}")
        return "AI HAIKU GENERATION FAILED - SYSTEM ERROR"

def main():
    """Main function to generate and display a haiku."""
    # Start the GUI
    display, app = gui_main()
    
    # Generate a haiku
    print("Generating AI haiku...")
    haiku = generate_haiku()
    print(f"Generated haiku: {haiku}")
    
    # Display the haiku on the punch card (with 150ms delay between characters)
    display.display_message(haiku, source="OpenAI API: AI Haiku", delay=150)
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 