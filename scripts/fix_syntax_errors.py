#!/usr/bin/env python3
"""
Fix Syntax Errors Script - Fixes syntax errors in the file.
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
BACKUP_SUFFIX = ".bak_syntax_errors_fix"

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

def fix_syntax_errors():
    """Fix syntax errors in the file."""
    try:
        with open(MAIN_FILE, 'r') as f:
            lines = f.readlines()
        
        # Fix the extraneous text at line 8204
        if 8204 < len(lines):
            if "g[:50]}" in lines[8204]:
                logging.info("Found extraneous text at line 8204")
                lines[8204] = ''  # Remove the line
                
                # Write the fixed content back to the file
                with open(MAIN_FILE, 'w') as f:
                    f.writelines(lines)
                
                logging.info("Fixed syntax error at line 8204")
                return True
        
        # Check for other common syntax errors
        fixed = False
        for i in range(len(lines)):
            # Look for unmatched braces
            if re.search(r'[^{]*}[^}]*$', lines[i]) and not re.search(r'{', lines[i]):
                logging.info(f"Found potential unmatched brace at line {i+1}")
                lines[i] = re.sub(r'}', '', lines[i])
                fixed = True
            
            # Look for unmatched quotes
            if lines[i].count('"') % 2 != 0 and lines[i].count('\\"') % 2 == 0:
                logging.info(f"Found potential unmatched quote at line {i+1}")
                lines[i] = re.sub(r'"([^"]*$)', r'\1', lines[i])
                fixed = True
        
        if fixed:
            # Write the fixed content back to the file
            with open(MAIN_FILE, 'w') as f:
                f.writelines(lines)
            
            logging.info("Fixed syntax errors in the file")
            return True
        
        logging.warning("No specific syntax errors found to fix")
        return False
    
    except Exception as e:
        logging.error(f"Failed to fix syntax errors: {e}")
        return False

def main():
    """Main function to fix syntax errors."""
    print("IBM 026 Punch Card Display - Fix Syntax Errors")
    print("-------------------------------------------")
    
    # Create backup
    if not create_backup():
        print("Failed to create backup. Aborting.")
        return
    
    # Fix syntax errors
    if fix_syntax_errors():
        print("✅ Successfully fixed syntax errors")
    else:
        print("❌ Failed to fix syntax errors")
    
    print("\nYou can now run the main program:")
    print("python3 simple_display.py")
    print("If you encounter issues, you can restore from backup:")
    print(f"cp {MAIN_FILE}{BACKUP_SUFFIX} {MAIN_FILE}")

if __name__ == "__main__":
    main() 