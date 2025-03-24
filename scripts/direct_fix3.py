#!/usr/bin/env python3
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Path to the file
FILE_PATH = 'simple_display.py'

def fix_indentation_directly():
    if not os.path.exists(FILE_PATH):
        logging.error(f"File not found: {FILE_PATH}")
        return False
    
    # Create backup
    backup_path = f"{FILE_PATH}.bak4"
    try:
        with open(FILE_PATH, 'r') as f:
            content = f.read()
        
        with open(backup_path, 'w') as f:
            f.write(content)
        logging.info(f"Created backup at: {backup_path}")
    except Exception as e:
        logging.error(f"Failed to create backup: {e}")
        return False
    
    # Read the file content
    with open(FILE_PATH, 'r') as f:
        lines = f.readlines()
    
    # Target the specific problematic line around 313
    target_line = "    except Exception as e:\n"
    for i, line in enumerate(lines):
        if 310 <= i <= 315 and line.strip() == "except Exception as e:":
            logging.info(f"Found the problematic line at {i+1}: '{line.strip()}'")
            # Remove this line as it's an erroneous duplicate
            lines[i] = ""
            logging.info(f"Removed line {i+1}")
            break
    
    # Write fixed content back to file
    try:
        with open(FILE_PATH, 'w') as f:
            f.writelines(lines)
        logging.info(f"Successfully fixed indentation issues in {FILE_PATH}")
        return True
    except Exception as e:
        logging.error(f"Failed to write fixed file: {e}")
        # Restore backup
        try:
            with open(backup_path, 'r') as f:
                content = f.read()
            with open(FILE_PATH, 'w') as f:
                f.write(content)
            logging.info(f"Restored backup from: {backup_path}")
        except Exception as e2:
            logging.error(f"Failed to restore backup: {e2}")
        return False

if __name__ == "__main__":
    if fix_indentation_directly():
        logging.info("Indentation fixed successfully!")
        sys.exit(0)
    else:
        logging.error("Failed to fix indentation.")
        sys.exit(1) 