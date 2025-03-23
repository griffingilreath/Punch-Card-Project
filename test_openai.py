import os
import json
from openai import OpenAI

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

try:
    # Make the API request to create a completion
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "write a haiku about ai"}
        ]
    )
    
    # Print the response
    print(completion.choices[0].message)
    
    # Get just the content for the punch card
    haiku = completion.choices[0].message.content
    print("\nHaiku content:", haiku)
    
except Exception as e:
    print(f"Error occurred: {str(e)}") 