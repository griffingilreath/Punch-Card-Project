#!/usr/bin/env python3
"""
Direct Fix Script - Directly fixes the indentation issues in the specific try-except block.
"""

import os
import shutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Target file
MAIN_FILE = "simple_display.py"
BACKUP_SUFFIX = ".bak_direct_fix"

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

def direct_fix():
    """Directly fix the indentation of the try-except block."""
    try:
        with open(MAIN_FILE, 'r') as f:
            lines = f.readlines()
        
        # Find the return message line
        return_line = None
        except_line = None
        
        for i, line in enumerate(lines):
            if "return message" in line and 550 <= i <= 560:
                return_line = i
            if "except Exception as e:" in line and 550 <= i <= 570:
                except_line = i
        
        if return_line is None or except_line is None:
            logging.error("Could not find the return message or except line")
            return False
        
        # Get the indentation of the return line to determine the try block indentation
        return_indent = len(lines[return_line]) - len(lines[return_line].lstrip())
        
        # The except line should have the same indentation as the try block
        # We'll determine the try block indentation based on the return statement
        correct_indent = ' ' * return_indent
        
        # Fix the except line indentation
        lines[except_line] = correct_indent + lines[except_line].lstrip()
        
        # Fix the indentation of the except block (everything after the except line)
        block_indent = correct_indent + '    '  # Add 4 spaces for block content
        
        # We'll fix the indentation until we find a line with less indentation than the except line
        i = except_line + 1
        while i < len(lines):
            stripped_line = lines[i].lstrip()
            
            # If we find a line with less indentation and it's not blank, we've exited the block
            if len(stripped_line) > 0 and len(lines[i]) - len(stripped_line) <= return_indent:
                break
                
            # Fix indentation for non-empty lines
            if stripped_line:
                lines[i] = block_indent + stripped_line
                
            i += 1
        
        # Write the fixed content back to the file
        with open(MAIN_FILE, 'w') as f:
            f.writelines(lines)
        
        logging.info(f"Fixed indentation in try-except block from line {return_line+1} to {i}")
        return True
    
    except Exception as e:
        logging.error(f"Failed to fix indentation: {e}")
        return False

def main():
    """Main function to fix indentation."""
    print("IBM 026 Punch Card Display - Direct Fix")
    print("--------------------------------------")
    
    # Create backup
    if not create_backup():
        print("Failed to create backup. Aborting.")
        return
    
    # Fix indentation
    if direct_fix():
        print("✅ Successfully fixed indentation in try-except block")
    else:
        print("❌ Failed to fix indentation")
    
    print("\nYou can now run the main program:")
    print("python3 simple_display.py")
    print("If you encounter issues, you can restore from backup:")
    print(f"cp {MAIN_FILE}{BACKUP_SUFFIX} {MAIN_FILE}")

if __name__ == "__main__":
    main() 