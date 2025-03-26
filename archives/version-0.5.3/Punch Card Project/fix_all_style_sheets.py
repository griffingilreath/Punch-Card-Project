#!/usr/bin/env python3
"""
Fix All Style Sheets Script - Locates and fixes all style sheet issues in the file.
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
BACKUP_SUFFIX = ".bak_all_style_sheets_fix"

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

def fix_all_style_sheets():
    """Find and fix all style sheet issues in the file."""
    try:
        with open(MAIN_FILE, 'r') as f:
            content = f.read()
        
        # Find all the style sheet blocks that are not properly quoted
        # Pattern: setStyleSheet(f"" followed by CSS until "") - missing triple quotes
        # We'll replace them with proper triple quotes
        
        # Pattern for style sheet start
        pattern_start = r'(setStyleSheet\(f)"'
        # Pattern for style sheet end
        pattern_end = r'([^"])""\)'
        
        # Replace the start pattern with triple quotes
        fixed_content = re.sub(pattern_start, r'\1"""', content)
        # Replace the end pattern with triple quotes
        fixed_content = re.sub(pattern_end, r'\1""")', fixed_content)
        
        # Write the fixed content back to the file
        with open(MAIN_FILE, 'w') as f:
            f.write(fixed_content)
        
        logging.info("Fixed all style sheet issues with automatic detection")
        
        # Now manually fix some known problematic areas
        with open(MAIN_FILE, 'r') as f:
            lines = f.readlines()
        
        # Fix specific areas where the automatic detection might have missed
        # Line 1368 and nearby
        if 1360 < len(lines) and 1375 > len(lines):
            button_style_found = False
            for i in range(1360, 1375):
                if "button.setStyleSheet" in lines[i]:
                    button_style_found = True
                    # Check if the style sheet is properly formatted
                    if 'f"""' not in lines[i] and 'f"' in lines[i]:
                        lines[i] = lines[i].replace('f"', 'f"""')
                        # Find the end of the style sheet
                        for j in range(i+1, i+10):
                            if j < len(lines) and '"")' in lines[j]:
                                lines[j] = lines[j].replace('"")', '""")')
                                break
                    break
            
            if button_style_found:
                logging.info("Fixed button style sheet manually")
            else:
                logging.warning("Button style sheet not found for manual fix")
            
            # Write the fixed content back to the file
            with open(MAIN_FILE, 'w') as f:
                f.writelines(lines)
        
        return True
    
    except Exception as e:
        logging.error(f"Failed to fix all style sheets: {e}")
        return False

def fix_remaining_issues():
    """Fix any remaining issues that might have been missed."""
    try:
        with open(MAIN_FILE, 'r') as f:
            lines = f.readlines()
        
        # Try to find and fix specific areas that are known to be problematic
        changes_made = 0
        
        # Check each line in the file
        for i in range(len(lines)):
            # Look for lines that are likely to be the beginning of a style sheet
            if "setStyleSheet" in lines[i] and ('f"' in lines[i] or "f'" in lines[i]) and '"""' not in lines[i]:
                # This is likely the start of a problematic style sheet
                start_line = i
                logging.info(f"Found potential problematic style sheet at line {start_line+1}: {lines[start_line].strip()}")
                
                # Fix the start of the style sheet
                if 'f"' in lines[start_line]:
                    lines[start_line] = lines[start_line].replace('f"', 'f"""')
                elif "f'" in lines[start_line]:
                    lines[start_line] = lines[start_line].replace("f'", 'f"""')
                
                # Look for the end of the style sheet
                for j in range(start_line+1, min(start_line+15, len(lines))):
                    if '""")' not in lines[j] and ('"")' in lines[j] or "'')'" in lines[j]):
                        # Found the end of the style sheet
                        if '"")' in lines[j]:
                            lines[j] = lines[j].replace('"")', '""")')
                        elif "'')'" in lines[j]:
                            lines[j] = lines[j].replace("'')'", "''')'")
                        
                        logging.info(f"Fixed style sheet from line {start_line+1} to {j+1}")
                        changes_made += 1
                        break
        
        # Write the fixed content back to the file
        with open(MAIN_FILE, 'w') as f:
            f.writelines(lines)
        
        logging.info(f"Fixed {changes_made} additional style sheet issues")
        return True
    
    except Exception as e:
        logging.error(f"Failed to fix remaining issues: {e}")
        return False

def main():
    """Main function to fix all style sheet issues."""
    print("IBM 026 Punch Card Display - Fix All Style Sheets")
    print("----------------------------------------------")
    
    # Create backup
    if not create_backup():
        print("Failed to create backup. Aborting.")
        return
    
    # Fix all style sheets
    if fix_all_style_sheets() and fix_remaining_issues():
        print("✅ Successfully fixed all style sheet issues")
    else:
        print("❌ Failed to fix some style sheet issues")
    
    print("\nYou can now run the main program:")
    print("python3 simple_display.py")
    print("If you encounter issues, you can restore from backup:")
    print(f"cp {MAIN_FILE}{BACKUP_SUFFIX} {MAIN_FILE}")

if __name__ == "__main__":
    main() 