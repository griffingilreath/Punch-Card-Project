#!/usr/bin/env python3
"""
Fix Console Style Bracket Script - Fixes the mismatched brackets in the console style sheet.
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
BACKUP_SUFFIX = ".bak_console_style_bracket_fix"

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

def fix_console_style_bracket():
    """Fix the mismatched brackets in the console style sheet."""
    try:
        with open(MAIN_FILE, 'r') as f:
            lines = f.readlines()
        
        # Check if the file has enough lines
        if len(lines) < 1280:
            logging.error("File does not have enough lines")
            return False
        
        # Define the correct console style
        console_style = [
            '        # Set console styling\n',
            '        console.setStyleSheet(\n',
            '            "QTextEdit {" +\n',
            '            "    background-color: #1a1a1a;" +\n',
            '            "    color: #00ff00;" +\n',
            '            "    border: none;" +\n',
            '            "    font-family: \'Courier New\', monospace;" +\n',
            '            "}"\n',
            '        )\n'
        ]
        
        # Replace lines 1269-1278
        lines[1269:1278] = console_style
        
        # Write the fixed content back to the file
        with open(MAIN_FILE, 'w') as f:
            f.writelines(lines)
        
        logging.info("Fixed console style bracket at lines 1269-1278")
        return True
    
    except Exception as e:
        logging.error(f"Failed to fix console style bracket: {e}")
        return False

def main():
    """Main function to fix console style bracket."""
    print("IBM 026 Punch Card Display - Fix Console Style Bracket")
    print("------------------------------------------")
    
    # Create backup
    if not create_backup():
        print("Failed to create backup. Aborting.")
        return
    
    # Fix console style bracket
    if fix_console_style_bracket():
        print("✅ Successfully fixed console style bracket")
    else:
        print("❌ Failed to fix console style bracket")
    
    print("\nYou can now run the main program:")
    print("python3 simple_display.py")
    print("If you encounter issues, you can restore from backup:")
    print(f"cp {MAIN_FILE}{BACKUP_SUFFIX} {MAIN_FILE}")

if __name__ == "__main__":
    main() 