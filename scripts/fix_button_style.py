#!/usr/bin/env python3
"""
Fix Style Sheets Script - Directly fixes both button and card display style sheets.
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
BACKUP_SUFFIX = ".bak_combined_style_fix"

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

def fix_style_sheets():
    """Fix both button and card display style sheets."""
    try:
        with open(MAIN_FILE, 'r') as f:
            lines = f.readlines()
        
        # Check if the file has enough lines
        if len(lines) < 1400:
            logging.error("File does not have enough lines")
            return False
        
        # 1. Fix button container style (lines 1334-1340)
        button_container_style = [
            '                display.button_container.setStyleSheet(\n',
            '                    "background-color: " + UIStyleHelper.COLORS[\'bg\'].name() + ";" +\n',
            '                    "border: 1px solid " + UIStyleHelper.COLORS[\'border\'].name() + ";" +\n',
            '                    "border-radius: 3px;" +\n',
            '                    "padding: 5px;"\n',
            '                )\n'
        ]
        
        # Replace lines 1334-1340
        lines[1334:1340] = button_container_style
        logging.info("Fixed button container style at line 1337")
        
        # 2. Fix card display style (lines 1364-1373)
        # Define clear replacement for card display style
        card_display_replacement = [
            '        # Apply style to the punch card display if possible\n',
            '        if hasattr(display, \'card_display\'):\n',
            '            display.card_display.setStyleSheet(\n',
            '                "background-color: " + UIStyleHelper.COLORS[\'bg\'].name() + ";" +\n',
            '                "color: " + UIStyleHelper.COLORS[\'fg\'].name() + ";" +\n',
            '                "border: 1px solid " + UIStyleHelper.COLORS[\'border\'].name() + ";" +\n',
            '                "padding: 8px;" +\n',
            '                "font-family: \'" + UIStyleHelper.FONTS[\'monospace\'] + "\';" +\n',
            '                "font-size: " + UIStyleHelper.FONTS[\'size_normal\'] + ";"\n',
            '            )\n'
        ]
        
        # Replace lines 1364-1373
        lines[1364:1374] = card_display_replacement
        logging.info("Fixed card display style at line 1365-1374")
        
        # Write the fixed content back to the file
        with open(MAIN_FILE, 'w') as f:
            f.writelines(lines)
        
        return True
    
    except Exception as e:
        logging.error(f"Failed to fix style sheets: {e}")
        return False

def main():
    """Main function to fix style sheets."""
    print("IBM 026 Punch Card Display - Fix Style Sheets")
    print("------------------------------------------")
    
    # Create backup
    if not create_backup():
        print("Failed to create backup. Aborting.")
        return
    
    # Fix style sheets
    if fix_style_sheets():
        print("✅ Successfully fixed all style sheets")
    else:
        print("❌ Failed to fix style sheets")
    
    print("\nYou can now run the main program:")
    print("python3 simple_display.py")
    print("If you encounter issues, you can restore from backup:")
    print(f"cp {MAIN_FILE}{BACKUP_SUFFIX} {MAIN_FILE}")

if __name__ == "__main__":
    main() 