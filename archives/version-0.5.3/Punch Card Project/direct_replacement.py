#!/usr/bin/env python3
"""
Direct Replacement Script - Directly replaces the problematic section of code with a properly structured try-except block.
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
BACKUP_SUFFIX = ".bak_direct_replacement"

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

def direct_replacement():
    """Directly replace the problematic section of code."""
    try:
        # Read the entire file as text
        with open(MAIN_FILE, 'r') as f:
            content = f.read()
        
        # Look for patterns to identify the problematic section
        pattern = r"(def generate_message.*?)(?=def |class |\Z)"
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            logging.error("Could not find the generate_message function")
            return False
        
        function_code = match.group(1)
        
        # Check if there's a problem with the try-except structure
        if "return message\n    except Exception as e:" in function_code:
            logging.info("Found the problematic try-except structure")
            
            # Define the corrected structure with proper indentation
            fixed_function_code = function_code.replace(
                "return message\n    except Exception as e:",
                """return message
    except Exception as e:"""
            )
            
            # Apply additional fixes to the function code
            # Fix indentation in the except block
            fixed_function_code = re.sub(
                r"except Exception as e:(.*?)(?=def |class |\Z)",
                lambda m: "except Exception as e:" + re.sub(r"^(\s*)(\S)", r"        \2", m.group(1), flags=re.MULTILINE),
                fixed_function_code,
                flags=re.DOTALL
            )
            
            # Write the fixed content back to the file
            fixed_content = content.replace(function_code, fixed_function_code)
            with open(MAIN_FILE, 'w') as f:
                f.write(fixed_content)
            
            logging.info("Successfully replaced the problematic section")
            return True
        
        else:
            # If we didn't find the exact pattern, let's try completely rewriting the function
            logging.info("Exact pattern not found, attempting complete rewrite")
            
            # Find the function definition line
            func_def_match = re.search(r"def generate_message\(.*?\):", function_code)
            if not func_def_match:
                logging.error("Could not find the function definition")
                return False
                
            func_def = func_def_match.group(0)
            
            # Create a completely new implementation with proper structure - using raw string to avoid escape issues
            new_function = f"""{func_def}
    \"\"\"Generate a response using the OpenAI API.
    
    Args:
        prompt: The prompt to send to the API
        system_message: Optional system message to include
        attempt: Current retry attempt (defaults to 0)
    
    Returns:
        The generated message or an error message
    \"\"\"
    try:
        # Load OpenAI API key from settings
        api_key = config.get('openai_api_key', '')
        if not api_key:
            debug_log("❌ OpenAI API key not found in settings", "error")
            return "ERROR: API KEY NOT FOUND"
        
        # Set up the OpenAI client
        client = OpenAI(api_key=api_key)
        debug_log(f"🔄 Generating response (attempt {{attempt+1}}/{{max_retries}})...", "api")
        
        # Set up the messages for the API
        messages = []
        
        # Add system message if provided
        if system_message:
            messages.append({{
                "role": "system",
                "content": system_message
            }})
        
        # Add user prompt
        messages.append({{
            "role": "user",
            "content": prompt
        }})
        
        # Make the API call
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        # Extract the message from the response
        message = completion.choices[0].message.content.strip()
        debug_log(f"✅ Successfully generated response: {{message[:50]}}...", "api")
        
        # Save token usage stats if available
        if hasattr(completion, 'usage'):
            usage = completion.usage
            
            # Get current usage stats
            if 'openai_usage' not in config:
                config['openai_usage'] = {{}}
            
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
        debug_log(f"❌ Error generating message: {{error_msg}}", "error")
        
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
            debug_log(f"❌ Unknown error: {{error_msg}}", "error")
            return f"ERROR: {{error_msg[:50]}}"
"""
            
            # Replace the old function with the new one
            fixed_content = content.replace(function_code, new_function)
            with open(MAIN_FILE, 'w') as f:
                f.write(fixed_content)
            
            logging.info("Successfully rewrote the generate_message function")
            return True
    
    except Exception as e:
        logging.error(f"Failed to replace the problematic section: {e}")
        return False

def main():
    """Main function to replace the problematic section."""
    print("IBM 026 Punch Card Display - Direct Replacement")
    print("---------------------------------------------")
    
    # Create backup
    if not create_backup():
        print("Failed to create backup. Aborting.")
        return
    
    # Replace the problematic section
    if direct_replacement():
        print("✅ Successfully replaced the problematic section")
    else:
        print("❌ Failed to replace the problematic section")
    
    print("\nYou can now run the main program:")
    print("python3 simple_display.py")
    print("If you encounter issues, you can restore from backup:")
    print(f"cp {MAIN_FILE}{BACKUP_SUFFIX} {MAIN_FILE}")

if __name__ == "__main__":
    main() 