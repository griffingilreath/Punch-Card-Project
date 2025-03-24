#!/usr/bin/env python3
"""
Fix Models Response Script - Fixes mismatched parentheses in the ModelsResponse type definition.
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
BACKUP_SUFFIX = ".bak_models_response_fix"

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

def fix_models_response():
    """Fix the mismatched parentheses in the ModelsResponse type definition."""
    try:
        with open(MAIN_FILE, 'r') as f:
            lines = f.readlines()
        
        # Fix the specific area with mismatched parentheses
        fixed_area = [
            '                        data = response.json()\n',
            '                        return type(\'ModelsResponse\', (), {\n',
            '                            \'data\': data[\'data\']\n',
            '                        })\n'
        ]
        
        # Replace the lines with fixed parentheses
        if 380 < len(lines):
            lines[382:386] = fixed_area
            
            # Write the fixed content back to the file
            with open(MAIN_FILE, 'w') as f:
                f.writelines(lines)
            
            logging.info("Fixed mismatched parentheses in ModelsResponse type definition")
            return True
        
        logging.warning("Could not locate the area with mismatched parentheses")
        return False
    
    except Exception as e:
        logging.error(f"Failed to fix mismatched parentheses: {e}")
        return False

def main():
    """Main function to fix mismatched parentheses in ModelsResponse."""
    print("IBM 026 Punch Card Display - Fix Models Response")
    print("----------------------------------------------")
    
    # Create backup
    if not create_backup():
        print("Failed to create backup. Aborting.")
        return
    
    # Fix mismatched parentheses
    if fix_models_response():
        print("✅ Successfully fixed mismatched parentheses in ModelsResponse")
    else:
        print("❌ Failed to fix mismatched parentheses in ModelsResponse")
    
    print("\nYou can now run the main program:")
    print("python3 simple_display.py")
    print("If you encounter issues, you can restore from backup:")
    print(f"cp {MAIN_FILE}{BACKUP_SUFFIX} {MAIN_FILE}")

if __name__ == "__main__":
    main() 