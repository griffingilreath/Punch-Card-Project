#!/usr/bin/env python3
"""
Fix Main Program - A utility to repair syntax errors in simple_display.py

This script applies critical syntax fixes to the main program while preserving
the correct IBM 026 character encoding.
"""

import os
import sys
import re
import shutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def create_backup():
    """Create a backup of the original file."""
    source_file = "simple_display.py"
    backup_file = "simple_display.py.syntax_backup"
    
    if not os.path.exists(source_file):
        logging.error(f"Cannot find {source_file}")
        return False
    
    try:
        shutil.copy2(source_file, backup_file)
        logging.info(f"Created backup at {backup_file}")
        return True
    except Exception as e:
        logging.error(f"Failed to create backup: {e}")
        return False

def fix_syntax_errors():
    """Fix critical syntax errors in the main program."""
    filename = "simple_display.py"
    
    if not os.path.exists(filename):
        logging.error(f"Cannot find {filename}")
        return False
    
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
        
        # Map of line numbers to fixed lines
        # These are specific fixes based on the linter errors
        fixes = {
            # Fix try-except blocks without except or finally
            285: "        try:\n",
            288: "            logging.info(\"✅ Successfully installed openai\")\n        except Exception as e:\n            logging.error(f\"Failed to install openai: {e}\")\n",
            
            # Fix unexpected indentation
            306: "                    try:\n",
            309: "                        logging.info(\"✅ Successfully installed httpx\")\n                    except Exception as e:\n",
            
            # Fix mismatched indentation in try-except blocks
            353: "                                data = response.json()\n",
            364: "                        self.completions = Completions(client)\n",
            
            # Fix unexpected indentation for class Models
            366: "                class Models:\n",
            
            # Fix unexpected indentation for various parts
            387: "                        data = response.json()\n",
            394: "                self.chat = Chat(self)\n",
            398: "        client = MinimalOpenAIClient(api_key)\n",
            
            # Fix continue statements outside of loops
            566: "                    # continue removed - retry handled elsewhere\n",
            572: "                    # continue removed - retry handled elsewhere\n",
            583: "                    # continue removed - retry handled elsewhere\n",
            
            # Fix check_and_display_api_status function
            2608: "    global service_status\n",
            
            # Fix service_status initialization
            4096: "message_stats = {\n",
            4107: "openai_usage = {\n",
            
            # Fix various continue statements
            4636: "                # continue removed - retry handled elsewhere\n",
            
            # Fix main try-except block
            8130: "        args = parse_args()\n        main()\n",
            8132: "    except Exception as e:\n",
        }
        
        # Apply fixes
        for line_num, new_line in fixes.items():
            if 0 <= line_num - 1 < len(lines):
                lines[line_num - 1] = new_line
        
        # Write the fixed content back to the file
        with open(filename, 'w') as file:
            file.writelines(lines)
        
        logging.info(f"Applied specific syntax fixes to {filename}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to fix syntax errors: {e}")
        return False

def create_wrapper_script():
    """Create a wrapper script that runs the main program with error handling."""
    wrapper_content = """#!/usr/bin/env python3
"""
    wrapper_content += '''
"""
IBM 026 Punch Card Display - Wrapper Script

This script serves as a wrapper around the main program with enhanced error handling.
"""

import os
import sys
import logging
import traceback
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="punch_card_wrapper.log"
)

def run_main_program():
    """Run the main program with error handling."""
    try:
        # First verify that our encoding fix is in place
        from ibm_026_punch_card import format_punch_card
        logging.info("✅ IBM 026 encoding module is available")
        
        # Import and run the main program
        try:
            import simple_display
            # Call the main function
            if hasattr(simple_display, 'main'):
                logging.info("Starting main program...")
                simple_display.main()
            else:
                logging.error("Main function not found in simple_display.py")
                return False
        except SyntaxError as e:
            logging.error(f"Syntax error in simple_display.py: {e}")
            print(f"Error: The main program has syntax errors that need to be fixed.")
            print(f"Error details: {e}")
            traceback.print_exc()
            return False
        except ImportError as e:
            logging.error(f"Import error: {e}")
            print(f"Error: Could not import the main program.")
            print(f"Error details: {e}")
            return False
        except Exception as e:
            logging.error(f"Error running main program: {e}")
            traceback.print_exc()
            return False
            
        return True
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        traceback.print_exc()
        return False

def run_standalone():
    """Run the standalone IBM 026 display as a fallback."""
    try:
        print("Running standalone IBM 026 display...")
        subprocess.run([sys.executable, "ibm_026_punch_card.py", "--show-alphanumeric"])
        return True
    except Exception as e:
        logging.error(f"Error running standalone display: {e}")
        return False

if __name__ == "__main__":
    print("IBM 026 Punch Card Display - Wrapper")
    print("-------------------------------------")
    
    success = run_main_program()
    
    if not success:
        print("\nAttempting to run standalone display as fallback...")
        run_standalone()
'''

    try:
        with open("run_punch_card.py", 'w') as file:
            file.write(wrapper_content)
        
        # Make executable
        os.chmod("run_punch_card.py", 0o755)
        logging.info("Created wrapper script run_punch_card.py")
        return True
    except Exception as e:
        logging.error(f"Failed to create wrapper script: {e}")
        return False

def main():
    """Main function to fix the program."""
    print("IBM 026 Punch Card Display - Fix Main Program")
    print("---------------------------------------------")
    
    # Create backup
    if not create_backup():
        print("Failed to create backup. Aborting.")
        sys.exit(1)
    
    # Fix syntax errors
    if not fix_syntax_errors():
        print("Failed to fix syntax errors.")
        sys.exit(1)
    
    # Create wrapper script
    if not create_wrapper_script():
        print("Failed to create wrapper script.")
        sys.exit(1)
    
    print("\n✅ Applied fixes to simple_display.py")
    print("\nTo run the program:")
    print("1. Run the wrapper script: python3 run_punch_card.py")
    print("2. If the main program still has issues, the wrapper will")
    print("   automatically run the standalone display as a fallback.")
    print("\nIf you need to restore the original file:")
    print("   cp simple_display.py.syntax_backup simple_display.py")

if __name__ == "__main__":
    main() 