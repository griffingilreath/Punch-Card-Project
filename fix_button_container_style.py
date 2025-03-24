#!/usr/bin/env python3
"""
Fix Button Container Style Script - Fixes mismatched quotes in the button container style sheet.
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
BACKUP_SUFFIX = ".bak_button_container_style_fix"

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

def fix_button_container_style():
    """Fix mismatched quotes in the button container style sheet."""
    try:
        with open(MAIN_FILE, 'r') as f:
            lines = f.readlines()
        
        # Fix the button container style sheet
        if 1335 < len(lines):
            # The style sheet starts at line 1335 and ends at line 1339
            
            # Create a properly formatted style sheet
            fixed_style = [
                '                display.button_container.setStyleSheet(f"""\n',
                '                    background-color: {UIStyleHelper.COLORS[\'bg\']};\n',
                '                    border: 1px solid {UIStyleHelper.COLORS[\'border\']};\n',
                '                    border-radius: 3px;\n',
                '                    padding: 5px;\n',
                '                """)\n'
            ]
            
            # Replace the lines
            lines[1334:1340] = fixed_style
            
            # Write the fixed content back to the file
            with open(MAIN_FILE, 'w') as f:
                f.writelines(lines)
            
            logging.info("Fixed button container style sheet")
            return True
        
        logging.warning("Could not access line 1335")
        return False
    
    except Exception as e:
        logging.error(f"Failed to fix button container style: {e}")
        return False

def main():
    """Main function to fix button container style sheet."""
    print("IBM 026 Punch Card Display - Fix Button Container Style")
    print("---------------------------------------------------")
    
    # Create backup
    if not create_backup():
        print("Failed to create backup. Aborting.")
        return
    
    # Fix button container style
    if fix_button_container_style():
        print("✅ Successfully fixed button container style sheet")
    else:
        print("❌ Failed to fix button container style sheet")
    
    print("\nYou can now run the main program:")
    print("python3 simple_display.py")
    print("If you encounter issues, you can restore from backup:")
    print(f"cp {MAIN_FILE}{BACKUP_SUFFIX} {MAIN_FILE}")

if __name__ == "__main__":
    main() 