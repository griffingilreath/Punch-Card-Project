#!/usr/bin/env python3
"""
Fix Docstring Script - Fixes the unterminated docstring issue around line 800.
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
BACKUP_SUFFIX = ".bak_docstring_fix"

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

def fix_docstring():
    """Fix the unterminated docstring issue around line 800."""
    try:
        with open(MAIN_FILE, 'r') as f:
            lines = f.readlines()
        
        # Fix the docstring issue
        if 795 < len(lines):
            # The issue is around line 800 where a docstring is unterminated
            # Let's check if there's a docstring that started but wasn't closed
            # Find the last triple quote before line 800
            docstring_start = -1
            for i in range(790, 800):
                if i < len(lines) and '"""' in lines[i]:
                    docstring_start = i
            
            # If we found a docstring start, let's check for its end
            if docstring_start != -1:
                docstring_end = -1
                for i in range(docstring_start + 1, 810):
                    if i < len(lines) and '"""' in lines[i]:
                        docstring_end = i
                        break
                
                # If no end was found, fix it
                if docstring_end == -1:
                    # Line 800 contains just double quote marks
                    if 800 < len(lines) and lines[800].strip() == '""':
                        lines[800] = '    """\n'
                    else:
                        # Add the proper triple quotes to close the docstring
                        if 801 < len(lines):
                            lines[801] = '    """\n' + lines[801]
                
                # Write the fixed content back to the file
                with open(MAIN_FILE, 'w') as f:
                    f.writelines(lines)
                
                logging.info("Fixed docstring issue around line 800")
                return True
        
        logging.warning("Could not identify the docstring issue")
        return False
    
    except Exception as e:
        logging.error(f"Failed to fix docstring issue: {e}")
        return False

def main():
    """Main function to fix docstring issues."""
    print("IBM 026 Punch Card Display - Fix Docstring")
    print("----------------------------------------")
    
    # Create backup
    if not create_backup():
        print("Failed to create backup. Aborting.")
        return
    
    # Fix docstring issues
    if fix_docstring():
        print("✅ Successfully fixed docstring issue")
    else:
        print("❌ Failed to fix docstring issue")
    
    print("\nYou can now run the main program:")
    print("python3 simple_display.py")
    print("If you encounter issues, you can restore from backup:")
    print(f"cp {MAIN_FILE}{BACKUP_SUFFIX} {MAIN_FILE}")

if __name__ == "__main__":
    main() 