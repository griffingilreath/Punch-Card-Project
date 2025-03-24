#!/usr/bin/env python3
"""
Fix Line 800 Script - Directly fixes the syntax error at line 800.
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
BACKUP_SUFFIX = ".bak_line800_fix"

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

def fix_line_800():
    """Directly fix line 800 in the file."""
    try:
        with open(MAIN_FILE, 'r') as f:
            lines = f.readlines()
        
        # Check if we can access line 800
        if 800 >= len(lines):
            logging.error("File does not have 800 lines")
            return False
        
        # Log the problematic line for debugging
        logging.info(f"Original line 800: {lines[799].strip()}")
        
        # Fix the specific line by ensuring it's properly commented or in a docstring
        lines[799] = '        """In IBM 026/029 punch card, the row order is: 12, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 (from top to bottom)"""\n'
        
        # Make sure line 800 is properly formatted
        if 800 < len(lines) and lines[800].strip() == '""':
            lines[800] = ''
        
        # Write the fixed content back to the file
        with open(MAIN_FILE, 'w') as f:
            f.writelines(lines)
        
        logging.info("Fixed line 800 directly")
        return True
    
    except Exception as e:
        logging.error(f"Failed to fix line 800: {e}")
        return False

def main():
    """Main function to fix line 800."""
    print("IBM 026 Punch Card Display - Fix Line 800")
    print("----------------------------------------")
    
    # Create backup
    if not create_backup():
        print("Failed to create backup. Aborting.")
        return
    
    # Fix line 800
    if fix_line_800():
        print("✅ Successfully fixed line 800")
    else:
        print("❌ Failed to fix line 800")
    
    print("\nYou can now run the main program:")
    print("python3 simple_display.py")
    print("If you encounter issues, you can restore from backup:")
    print(f"cp {MAIN_FILE}{BACKUP_SUFFIX} {MAIN_FILE}")

if __name__ == "__main__":
    main() 