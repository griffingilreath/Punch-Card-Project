#!/usr/bin/env python3

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
