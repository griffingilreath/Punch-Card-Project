#!/usr/bin/env python3
"""
Fix Problem Line Script - Adds the missing try statement before the except at line 557.
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
BACKUP_SUFFIX = ".bak_problem_line_fix"

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

def fix_problem_line():
    """Fix the problem line by adding a try statement."""
    try:
        with open(MAIN_FILE, 'r') as f:
            lines = f.readlines()
        
        # Find the function that contains line 557
        function_start = None
        for i in range(557, 0, -1):
            if i < len(lines) and "def generate_message" in lines[i]:
                function_start = i
                break
        
        if function_start is None:
            logging.error("Could not find the generate_message function")
            return False
        
        # Find the first line after the function definition to add the try statement
        first_content_line = None
        for i in range(function_start + 1, 557):
            # Skip comments and empty lines
            if i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('#'):
                first_content_line = i
                break
        
        if first_content_line is None:
            logging.error("Could not find the first content line after function definition")
            return False
        
        # Get the indentation of the first content line
        first_content_indent = len(lines[first_content_line]) - len(lines[first_content_line].lstrip())
        
        # Add the try statement before the first content
        try_statement = ' ' * first_content_indent + "try:\n"
        lines.insert(first_content_line, try_statement)
        
        # Adjust indentation for all lines between the try and the except
        for i in range(first_content_line + 1, 557 + 1):
            if i < len(lines) and lines[i].strip():
                if not lines[i].strip().startswith('#'):  # Skip comment lines
                    current_indent = len(lines[i]) - len(lines[i].lstrip())
                    lines[i] = ' ' * (current_indent + 4) + lines[i].lstrip()
        
        # Write the fixed content back to the file
        with open(MAIN_FILE, 'w') as f:
            f.writelines(lines)
        
        logging.info(f"Added try statement before line {first_content_line}")
        return True
    
    except Exception as e:
        logging.error(f"Failed to fix problem line: {e}")
        return False

def main():
    """Main function to fix the problem line."""
    print("IBM 026 Punch Card Display - Fix Problem Line")
    print("------------------------------------------")
    
    # Create backup
    if not create_backup():
        print("Failed to create backup. Aborting.")
        return
    
    # Fix problem line
    if fix_problem_line():
        print("✅ Successfully added try statement before the except at line 557")
    else:
        print("❌ Failed to add try statement")
    
    print("\nYou can now run the main program:")
    print("python3 simple_display.py")
    print("If you encounter issues, you can restore from backup:")
    print(f"cp {MAIN_FILE}{BACKUP_SUFFIX} {MAIN_FILE}")

if __name__ == "__main__":
    main() 