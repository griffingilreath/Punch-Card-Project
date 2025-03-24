#!/usr/bin/env python3
"""
Fix Card Display Style Script - Directly fixes the style sheet at line 1365-1368.
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
BACKUP_SUFFIX = ".bak_card_display_style_fix2"

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

def fix_card_display_style():
    """Fix the duplicated line and improperly closed f-string at line 1365."""
    try:
        with open(MAIN_FILE, 'r') as f:
            lines = f.readlines()
        
        # Check if the file has enough lines
        if len(lines) < 1370:
            logging.error("File does not have enough lines")
            return False
        
        # Define the hardcoded replacement
        card_display_style = [
            '            display.card_display.setStyleSheet(\n',
            '                "background-color: " + UIStyleHelper.COLORS[\'bg\'].name() + ";" +\n',
            '                "color: " + UIStyleHelper.COLORS[\'fg\'].name() + ";" +\n',
            '                "border: 1px solid " + UIStyleHelper.COLORS[\'border\'].name() + ";" +\n',
            '                "padding: 8px;" +\n',
            '                "font-family: \'" + UIStyleHelper.FONTS[\'monospace\'] + "\';" +\n',
            '                "font-size: " + UIStyleHelper.FONTS[\'size_normal\'] + ";"\n',
            '            )\n'
        ]
        
        # Replace lines 1365-1372
        lines[1365:1373] = card_display_style
        
        # Write the fixed content back to the file
        with open(MAIN_FILE, 'w') as f:
            f.writelines(lines)
        
        logging.info("Fixed card display style at line 1365-1372")
        return True
    
    except Exception as e:
        logging.error(f"Failed to fix card display style: {e}")
        return False

def main():
    """Main function to fix card display style."""
    print("IBM 026 Punch Card Display - Fix Card Display Style (Duplicated Line)")
    print("------------------------------------------")
    
    # Create backup
    if not create_backup():
        print("Failed to create backup. Aborting.")
        return
    
    # Fix card display style
    if fix_card_display_style():
        print("✅ Successfully fixed card display style (duplicated line issue)")
    else:
        print("❌ Failed to fix card display style")
    
    print("\nYou can now run the main program:")
    print("python3 simple_display.py")
    print("If you encounter issues, you can restore from backup:")
    print(f"cp {MAIN_FILE}{BACKUP_SUFFIX} {MAIN_FILE}")

if __name__ == "__main__":
    main() 