#!/usr/bin/env python3
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Path to the file
FILE_PATH = 'simple_display.py'

def fix_try_except_structure():
    if not os.path.exists(FILE_PATH):
        logging.error(f"File not found: {FILE_PATH}")
        return False
    
    # Create backup
    backup_path = f"{FILE_PATH}.bak_final"
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
    
    # Look for the problematic try-except structure
    try_line = None
    exception_line = None
    
    for i, line in enumerate(lines):
        if "try:" in line and 305 <= i <= 310:
            try_line = i
            logging.info(f"Found try at line {i+1}: '{line.strip()}'")
        
        if "except Exception as e:" in line and 310 <= i <= 315:
            exception_line = i
            logging.info(f"Found except at line {i+1}: '{line.strip()}'")
    
    if try_line is not None and exception_line is not None:
        # Add the missing except statement after the try's content
        for i in range(try_line+1, exception_line):
            if "logging.info" in lines[i] and "Successfully installed httpx" in lines[i]:
                # Add the except after this line
                indent = " " * 20  # Match the indentation of the surrounding code
                fixed_line = lines[i]
                fixed_line += f"{indent}except Exception as e:\n"
                lines[i] = fixed_line
                logging.info(f"Added missing except after line {i+1}")
                break
    
    # Write fixed content back to file
    try:
        with open(FILE_PATH, 'w') as f:
            f.writelines(lines)
        logging.info(f"Successfully fixed try-except structure in {FILE_PATH}")
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
    if fix_try_except_structure():
        logging.info("Try-except structure fixed successfully!")
        sys.exit(0)
    else:
        logging.error("Failed to fix try-except structure.")
        sys.exit(1) 