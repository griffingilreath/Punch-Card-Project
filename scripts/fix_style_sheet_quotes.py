#!/usr/bin/env python3
"""
Fix Style Sheet Quotes Script - Fixes the mismatched quotes in the style sheet definition.
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
BACKUP_SUFFIX = ".bak_style_sheet_quotes_fix"

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

def fix_style_sheet_quotes():
    """Fix the mismatched quotes in the style sheet definition."""
    try:
        with open(MAIN_FILE, 'r') as f:
            lines = f.readlines()
        
        # Fix the style sheet quotes
        if 975 < len(lines):
            # Replace the entire style sheet definition with a corrected version
            fixed_style_sheet = [
                '        # Set dark theme\n',
                '        self.setStyleSheet(f"""\n',
                '            QDialog {\n',
                '                background-color: {COLORS[\'background\'].name()};\n',
                '                color: {COLORS[\'text\'].name()};\n',
                '            }\n',
                '            \n',
                '            QLabel, QSpinBox, QCheckBox {\n',
                '                color: {COLORS[\'text\'].name()};\n',
                '            }\n',
                '        """)\n'
            ]
            
            # Replace the lines
            lines[976:987] = fixed_style_sheet
            
            # Write the fixed content back to the file
            with open(MAIN_FILE, 'w') as f:
                f.writelines(lines)
            
            logging.info("Fixed style sheet quotes")
            return True
        
        logging.warning("Could not locate the style sheet area")
        return False
    
    except Exception as e:
        logging.error(f"Failed to fix style sheet quotes: {e}")
        return False

def main():
    """Main function to fix style sheet quotes."""
    print("IBM 026 Punch Card Display - Fix Style Sheet Quotes")
    print("------------------------------------------------")
    
    # Create backup
    if not create_backup():
        print("Failed to create backup. Aborting.")
        return
    
    # Fix style sheet quotes
    if fix_style_sheet_quotes():
        print("✅ Successfully fixed style sheet quotes")
    else:
        print("❌ Failed to fix style sheet quotes")
    
    print("\nYou can now run the main program:")
    print("python3 simple_display.py")
    print("If you encounter issues, you can restore from backup:")
    print(f"cp {MAIN_FILE}{BACKUP_SUFFIX} {MAIN_FILE}")

if __name__ == "__main__":
    main() 