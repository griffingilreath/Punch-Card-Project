#!/usr/bin/env python3
"""
Fix Console Style Script - Fixes mismatched quotes in the console style sheet.
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
BACKUP_SUFFIX = ".bak_console_style_fix"

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

def fix_console_style():
    """Fix mismatched quotes in the console style sheet."""
    try:
        with open(MAIN_FILE, 'r') as f:
            lines = f.readlines()
        
        # Fix the console style sheet
        if 1270 < len(lines):
            # The issue is around line 1276 where there are mismatched quotes in the style sheet
            
            # Find where the style sheet starts
            style_start = -1
            for i in range(1260, 1270):
                if i < len(lines) and "setStyleSheet" in lines[i]:
                    style_start = i
                    break
            
            if style_start != -1:
                # Find where the style sheet should end
                style_end = 1276
                
                # Extract all the lines between start and end
                style_content = lines[style_start+1:style_end]
                
                # Create a properly formatted style sheet
                if style_start == 1269:  # If the style sheet starts at line 1270 (index 1269)
                    fixed_style = [
                        '        console.setStyleSheet("""\n',
                        '            QTextEdit {\n',
                        '                background-color: #1a1a1a;\n',
                        '                color: #00ff00;\n',
                        '                border: none;\n',
                        '                font-family: \'Courier New\', monospace;\n',
                        '            }\n',
                        '        """)\n'
                    ]
                else:
                    # If the style sheet starts at a different line, log a warning
                    logging.warning(f"Style sheet starts at unexpected line: {style_start+1}")
                    # Still attempt to fix it
                    fixed_style = [
                        f'{lines[style_start]}'.replace('setStyleSheet(', 'setStyleSheet("""'),
                        ''.join(style_content),
                        '            }\n',
                        '        """)\n'
                    ]
                
                # Replace the lines
                lines[style_start:style_end+1] = fixed_style
                
                # Write the fixed content back to the file
                with open(MAIN_FILE, 'w') as f:
                    f.writelines(lines)
                
                logging.info(f"Fixed console style sheet at line {style_start+1}")
                return True
            else:
                logging.warning("Could not locate style sheet start")
                return False
        
        logging.warning("Could not access line 1270")
        return False
    
    except Exception as e:
        logging.error(f"Failed to fix console style: {e}")
        return False

def main():
    """Main function to fix console style sheet."""
    print("IBM 026 Punch Card Display - Fix Console Style")
    print("-------------------------------------------")
    
    # Create backup
    if not create_backup():
        print("Failed to create backup. Aborting.")
        return
    
    # Fix console style
    if fix_console_style():
        print("✅ Successfully fixed console style sheet")
    else:
        print("❌ Failed to fix console style sheet")
    
    print("\nYou can now run the main program:")
    print("python3 simple_display.py")
    print("If you encounter issues, you can restore from backup:")
    print(f"cp {MAIN_FILE}{BACKUP_SUFFIX} {MAIN_FILE}")

if __name__ == "__main__":
    main() 