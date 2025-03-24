#!/usr/bin/env python3
"""
Fix ASCII Art Script - Fixes the unterminated string in the MONKEY_ART variable.
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
BACKUP_SUFFIX = ".bak_ascii_art_fix"

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

def fix_monkey_art():
    """Fix the unterminated string in the MONKEY_ART variable."""
    try:
        with open(MAIN_FILE, 'r') as f:
            lines = f.readlines()
        
        # Find the MONKEY_ART definition
        art_start = -1
        for i, line in enumerate(lines):
            if "MONKEY_ART = " in line:
                art_start = i
                break
        
        if art_start == -1:
            logging.error("Could not find MONKEY_ART definition")
            return False
        
        # Create a properly formatted MONKEY_ART variable
        new_art = []
        new_art.append('MONKEY_ART = """\n')
        new_art.append('  ,-.-.\\n')
        new_art.append(' ( o o )  OPENAI CLIENT FIX\\n')
        new_art.append(' |  ^  |\\n')
        new_art.append(' | `-\' |  v0.5.5\\n')
        new_art.append(' `-----\'\\n')
        new_art.append('"""\n')
        
        # Replace the old MONKEY_ART definition with the new one
        lines[art_start:art_start+7] = new_art
        
        # Write the fixed content back to the file
        with open(MAIN_FILE, 'w') as f:
            f.writelines(lines)
        
        logging.info("Fixed MONKEY_ART string")
        return True
    
    except Exception as e:
        logging.error(f"Failed to fix MONKEY_ART: {e}")
        return False

def main():
    """Main function to fix the MONKEY_ART variable."""
    print("IBM 026 Punch Card Display - Fix ASCII Art")
    print("---------------------------------------")
    
    # Create backup
    if not create_backup():
        print("Failed to create backup. Aborting.")
        return
    
    # Fix MONKEY_ART
    if fix_monkey_art():
        print("✅ Successfully fixed MONKEY_ART string")
    else:
        print("❌ Failed to fix MONKEY_ART string")
    
    print("\nYou can now run the main program:")
    print("python3 simple_display.py")
    print("If you encounter issues, you can restore from backup:")
    print(f"cp {MAIN_FILE}{BACKUP_SUFFIX} {MAIN_FILE}")

if __name__ == "__main__":
    main() 