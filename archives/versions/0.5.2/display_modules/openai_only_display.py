#!/usr/bin/env python3
"""
OpenAI-Only Punch Card Display

This script completely replaces the default message generation system
with OpenAI-generated messages. It disables all local message generation.
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
    parser = argparse.ArgumentParser(description="OpenAI-Only Punch Card Generator")
    parser.add_argument('--model', type=str, default="gpt-4o-mini",
                      help='The OpenAI model to use')
    parser.add_argument('--delay', type=int, default=150,
                      help='Delay between character displays (milliseconds)')
    parser.add_argument('--interval', type=int, default=10,
                      help='Interval between messages in seconds')
    parser.add_argument('--prefix', type=str, default="[AI]",
                      help='Prefix for OpenAI messages')
    return parser.parse_args()

def generate_openai_message(model):
    """Generate a message using OpenAI API."""
    # Use different prompts for variety
    prompts = [
        "Create a short tech message about IBM punch cards",
        "Write a brief statement about vintage computing",
        "Generate a nostalgic message about early computers",
        "Write a haiku about AI and computing",
        "Create a futuristic message about computing",
        "Generate a punchy tech slogan",
        "Create a message about data processing"
    ]
    
    prompt = random.choice(prompts)
    print(f"Prompt: '{prompt}'")
    print(f"Using model: {model}")
    
    try:
        start_time = time.time()
        # Make the API request
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You generate short messages for an IBM punch card display. Keep your response under 70 characters. Format in UPPERCASE only."},
                {"role": "user", "content": prompt}
            ]
        )
        end_time = time.time()
        
        # Get message content
        response = completion.choices[0].message.content.strip().upper()
        
        # Replace any linebreaks with spaces
        response = response.replace("\n", " ")
        
        # Ensure it's not too long for the punch card (max 80 chars)
        if len(response) > 70:
            response = response[:67] + "..."
            
        print(f"✅ OpenAI API response in {end_time - start_time:.2f} sec: {response}")
        
        return response
    except Exception as e:
        print(f"❌ Error calling OpenAI API: {str(e)}")
        return f"ERROR: OPENAI API CALL FAILED"

def continuous_message_display(display, args):
    """Loop displaying only OpenAI-generated messages."""
    try:
        message_count = 0
        while True:
            message_count += 1
            print("-" * 50)
            print(f"Generating message #{message_count} from OpenAI...")
            
            # Generate message from OpenAI
            message = generate_openai_message(args.model)
            
            # Add prefix if it fits
            if args.prefix and len(args.prefix) + len(message) + 1 <= 80:
                prefixed_message = f"{args.prefix} {message}"
            else:
                prefixed_message = message
            
            print(f"Displaying: {prefixed_message}")
            print("-" * 50)
            
            # Display the message on the punch card
            display.display_message(
                message=prefixed_message, 
                source=f"OpenAI API #{message_count}", 
                delay=args.delay
            )
            
            # Wait for next message
            print(f"Waiting {args.interval} seconds before next message...")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nExiting message generation loop.")

def main():
    """Main function to continuously display OpenAI messages."""
    args = parse_args()
    
    # Start the GUI with an initial blank state
    print("Starting Punch Card GUI (OpenAI-only mode)...")
    display, app = gui_main()
    
    # Try multiple methods to disable automatic message generation
    if hasattr(display, 'disable_auto_messages'):
        display.disable_auto_messages()
        print("Disabled automatic message generation via method")
    
    # Direct attribute access - attempt to disable any timers or automatic behavior
    if hasattr(display, 'message_timer'):
        display.message_timer.stop()
        print("Stopped message timer")
    
    if hasattr(display, 'auto_generate'):
        display.auto_generate = False
        print("Disabled auto-generate flag")
        
    # Try to access any QTimers and stop them
    import types
    for attr_name in dir(display):
        attr = getattr(display, attr_name)
        if attr_name.endswith('timer') or attr_name.endswith('Timer'):
            if hasattr(attr, 'stop'):
                attr.stop()
                print(f"Stopped timer: {attr_name}")
    
    # Display a clear message that we're taking over message generation
    display.display_message(
        message="OPENAI MESSAGE GENERATOR ACTIVATED - DISABLING LOCAL MESSAGES", 
        source="System Control", 
        delay=50
    )
    time.sleep(2)
    
    # Use our own threading to control message display
    # This allows the GUI to remain responsive while we control message generation
    import threading
    message_thread = threading.Thread(
        target=continuous_message_display,
        args=(display, args),
        daemon=True  # Thread will exit when main program exits
    )
    
    # Start our OpenAI message display thread
    message_thread.start()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 