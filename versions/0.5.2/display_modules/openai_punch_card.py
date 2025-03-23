#!/usr/bin/env python3
"""
OpenAI Punch Card Display

This script clearly demonstrates OpenAI integration with the punch card display.
It clearly marks messages as coming from the API and disables any local message generation.
"""

import sys
import time
import random
import argparse
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

# Create an OpenAI client with the API key
client = OpenAI(api_key=get_api_key())

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="OpenAI Punch Card Generator")
    parser.add_argument('--prompt', type=str, default="Write a haiku about AI",
                      help='The prompt to send to OpenAI')
    parser.add_argument('--model', type=str, default="gpt-4o-mini",
                      help='The OpenAI model to use')
    parser.add_argument('--delay', type=int, default=150,
                      help='Delay between character displays (milliseconds)')
    parser.add_argument('--prefix', type=str, default="[OPENAI]",
                      help='Prefix to add to clearly show message is from OpenAI')
    return parser.parse_args()

def generate_openai_message(prompt, model):
    """Generate a message using OpenAI API with clear logging."""
    print(f"Sending prompt to OpenAI API: '{prompt}'")
    print(f"Using model: {model}")
    
    try:
        start_time = time.time()
        # Make the API request
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You generate short messages for an IBM punch card display. Keep your response under 80 characters. Format in uppercase only."},
                {"role": "user", "content": prompt}
            ]
        )
        end_time = time.time()
        
        # Get message content
        response = completion.choices[0].message.content.strip().upper()
        
        # Replace any linebreaks with spaces
        response = response.replace("\n", " ")
        
        # Ensure it's not too long for the punch card (max 80 chars)
        if len(response) > 80:
            response = response[:77] + "..."
            
        print(f"✅ OpenAI API response received in {end_time - start_time:.2f} seconds")
        print(f"Raw response: {response}")
        
        return response
    except Exception as e:
        print(f"❌ Error calling OpenAI API: {str(e)}")
        return f"ERROR: OPENAI API CALL FAILED - {str(e)[:50]}"

def main():
    """Main function to generate OpenAI message and display it."""
    args = parse_args()
    
    # Start the GUI
    print("Starting Punch Card GUI...")
    display, app = gui_main()
    
    # Generate message from OpenAI
    print("-" * 50)
    print("Generating message from OpenAI...")
    message = generate_openai_message(args.prompt, args.model)
    
    # Add prefix if it fits
    if args.prefix and len(args.prefix) + len(message) <= 80:
        prefixed_message = f"{args.prefix} {message}"
    else:
        prefixed_message = message
    
    print("-" * 50)
    print(f"Displaying on punch card: {prefixed_message}")
    print("-" * 50)
    
    # Display the message on the punch card
    display.display_message(
        message=prefixed_message, 
        source=f"OpenAI API: {args.model}", 
        delay=args.delay
    )
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 