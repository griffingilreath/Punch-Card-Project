#!/usr/bin/env python3
"""
Complete Rewrite Script - Replace the generate_message function with a clean version.
"""

import os
import re
import shutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Target file
MAIN_FILE = "simple_display.py"
BACKUP_SUFFIX = ".bak_complete_rewrite"

def create_backup():
    """Create a backup of the main file."""
    backup_file = f"{MAIN_FILE}{BACKUP_SUFFIX}"
    
    if not os.path.exists(MAIN_FILE):
        logging.error(f"Cannot find {MAIN_FILE}")
        return False
    
    try:
        shutil.copy2(MAIN_FILE, backup_file)
        logging.info(f"Created backup at {backup_file}")
        return True
    except Exception as e:
        logging.error(f"Failed to create backup: {e}")
        return False

def rewrite_function():
    """Rewrite the generate_message function with correct syntax."""
    try:
        # Read the file
        with open(MAIN_FILE, 'r') as f:
            content = f.read()
        
        # Locate all occurrences of the generate_message function
        pattern = r"def generate_message\(.*?\):.*?(?=^\s*def|\Z)"
        matches = list(re.finditer(pattern, content, re.DOTALL | re.MULTILINE))
        
        if not matches:
            logging.error("Could not find the generate_message function")
            return False
        
        # Generate a clean version of the function
        clean_function = '''def generate_message(prompt, system_message=None, attempt=0):
    """Generate a response using the OpenAI API.
    
    Args:
        prompt: The prompt to send to the API
        system_message: Optional system message to include
        attempt: Current retry attempt (defaults to 0)
    
    Returns:
        The generated message or an error message
    """
    try:
        # Load OpenAI API key from settings
        api_key = config.get('openai_api_key', '')
        if not api_key:
            debug_log("❌ OpenAI API key not found in settings", "error")
            return "ERROR: API KEY NOT FOUND"
        
        # Set up the OpenAI client
        client = OpenAI(api_key=api_key)
        debug_log(f"🔄 Generating response (attempt {attempt+1}/{max_retries})...", "api")
        
        # Set up the messages for the API
        messages = []
        
        # Add system message if provided
        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })
        
        # Add user prompt
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Make the API call
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        # Extract the message from the response
        message = completion.choices[0].message.content.strip()
        debug_log(f"✅ Successfully generated response: {message[:50]}...", "api")
        
        # Save token usage stats if available
        if hasattr(completion, 'usage'):
            usage = completion.usage
            
            # Get current usage stats
            if 'openai_usage' not in config:
                config['openai_usage'] = {}
            
            current_usage = config['openai_usage']
            
            # Update token counts
            current_usage['prompt_tokens'] = current_usage.get('prompt_tokens', 0) + usage.get('prompt_tokens', 0)
            current_usage['completion_tokens'] = current_usage.get('completion_tokens', 0) + usage.get('completion_tokens', 0)
            current_usage['total_tokens'] = current_usage.get('total_tokens', 0) + usage.get('total_tokens', 0)
            
            # Save updated stats
            config['openai_usage'] = current_usage
        
        save_settings()
        
        # Save message to database with source
        save_message_to_database(message, "openai")
        
        return message
    except Exception as e:
        error_msg = str(e).lower()
        debug_log(f"❌ Error generating message: {error_msg}", "error")
        
        # Handle specific error cases
        if "timeout" in error_msg:
            debug_log("⚠️ Request timed out, retrying...", "warning")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                # continue removed - retry handled elsewhere
            return "ERROR: REQUEST TIMED OUT"
        elif "rate limit" in error_msg:
            debug_log("⚠️ Rate limit exceeded, retrying...", "warning")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * 2)  # Longer delay for rate limits
                # continue removed - retry handled elsewhere
            return "ERROR: RATE LIMIT EXCEEDED"
        elif "authentication" in error_msg:
            debug_log("❌ Authentication error - API key may be invalid", "error")
            return "ERROR: AUTHENTICATION FAILED"
        elif "api key" in error_msg:
            debug_log("❌ API key error - key may be invalid", "error")
            return "ERROR: INVALID API KEY"
        elif "permission" in error_msg:
            debug_log("❌ Permission error - account may not have access", "error")
            return "ERROR: PERMISSION DENIED"
        else:
            debug_log(f"❌ Unknown error: {error_msg}", "error")
            return f"ERROR: {error_msg[:50]}"
'''
        
        # Apply indentation to match the file style
        indentation = re.match(r'^\s*', matches[0].group(0)).group(0)
        if indentation:
            clean_function = '\n'.join(indentation + line if line.strip() else line 
                                      for line in clean_function.split('\n'))
        
        # Replace all occurrences of the function with the clean version
        for match in matches:
            content = content[:match.start()] + clean_function + content[match.end():]
        
        # Write the updated content back to the file
        with open(MAIN_FILE, 'w') as f:
            f.write(content)
        
        logging.info(f"Replaced {len(matches)} occurrences of the generate_message function")
        return True
    
    except Exception as e:
        logging.error(f"Failed to rewrite function: {e}")
        return False

def main():
    """Main function to rewrite the generate_message function."""
    print("IBM 026 Punch Card Display - Complete Rewrite")
    print("------------------------------------------")
    
    # Create backup
    if not create_backup():
        print("Failed to create backup. Aborting.")
        return
    
    # Rewrite function
    if rewrite_function():
        print("✅ Successfully replaced the generate_message function with a clean version")
    else:
        print("❌ Failed to replace the function")
    
    print("\nYou can now run the main program:")
    print("python3 simple_display.py")
    print("If you encounter issues, you can restore from backup:")
    print(f"cp {MAIN_FILE}{BACKUP_SUFFIX} {MAIN_FILE}")

if __name__ == "__main__":
    main() 