#!/usr/bin/env python3
import os
import sys
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Path to the file
FILE_PATH = 'simple_display.py'

def fix_indentation_directly():
    if not os.path.exists(FILE_PATH):
        logging.error(f"File not found: {FILE_PATH}")
        return False
    
    # Create backup
    backup_path = f"{FILE_PATH}.bak3"
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
    
    # Fix #1: The first indentation issue around line 289
    # This was already fixed in the previous script
    
    # Fix #2: The second indentation issue around line 313
    # Find the line with the problematic except statement
    for i in range(305, 320):
        if i < len(lines) and "except Exception as e:" in lines[i] and not lines[i].strip().endswith(":"):
            # This is a problematic line that's not properly indented
            logging.info(f"Found problematic except at line {i+1}")
            
            # Search backward to find the matching try
            try_level = 0
            for j in range(i-1, 300, -1):
                if "try:" in lines[j]:
                    try_level = len(lines[j]) - len(lines[j].lstrip())
                    logging.info(f"Found matching try at line {j+1} with indentation level {try_level}")
                    break
            
            # Calculate proper indentation
            proper_except_indent = " " * try_level
            proper_body_indent = " " * (try_level + 4)
            
            # Fix the except line
            lines[i] = proper_except_indent + lines[i].strip() + ":\n"
            
            # Fix indentation of the body of the except block
            j = i + 1
            while j < len(lines) and lines[j].strip() and not re.match(r'^\s*except', lines[j]):
                if lines[j].strip():  # Not an empty line
                    current_indent = len(lines[j]) - len(lines[j].lstrip())
                    if current_indent < try_level + 4:
                        lines[j] = proper_body_indent + lines[j].strip() + "\n"
                j += 1
                
            logging.info(f"Fixed indentation in except block from line {i+1} to {j}")
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