#!/usr/bin/env python3
"""
Fix Syntax Script - Direct fix for syntax error in line 557.
"""

import os
import re
import shutil
import tempfile
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Target file
MAIN_FILE = "simple_display.py"
BACKUP_SUFFIX = ".bak_syntax_fix"

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

def add_try_before_function():
    """Add a try statement before the function that contains the except at line 557."""
    try:
        # Find the line number of the function that contains the problematic except
        result = subprocess.run([
            "grep", "-n", "-B1", r"^    except Exception as e:", MAIN_FILE
        ], capture_output=True, text=True)
        
        lines = result.stdout.splitlines()
        for i, line in enumerate(lines):
            if "return message" in line:
                # Get the line number from the grep output
                line_num = int(line.split('-')[0].strip())
                except_line_num = line_num + 1
                
                # Read the file
                with open(MAIN_FILE, 'r') as f:
                    file_lines = f.readlines()
                
                # Find the function that contains this except
                func_start = None
                for j in range(except_line_num, 0, -1):
                    if j < len(file_lines) and re.match(r"^\s*def\s+", file_lines[j]):
                        func_start = j
                        break
                
                if func_start is None:
                    logging.error("Could not find function start")
                    continue
                
                # Prepare the output file
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                    # Copy lines up to the function definition
                    for j in range(func_start):
                        temp_file.write(file_lines[j])
                    
                    # Write the function definition
                    temp_file.write(file_lines[func_start])
                    
                    # Add the try statement after the function definition (if docstring exists, after it)
                    j = func_start + 1
                    while j < len(file_lines) and (file_lines[j].strip() == "" or file_lines[j].strip().startswith('"""') or file_lines[j].strip().startswith('#')):
                        temp_file.write(file_lines[j])
                        j += 1
                    
                    # Get the indentation level
                    indent = re.match(r"^\s*", file_lines[j]).group(0)
                    
                    # Add the try statement with the same indentation
                    temp_file.write(f"{indent}try:\n")
                    
                    # Add 4 spaces to indentation for all lines until the except
                    for k in range(j, except_line_num):
                        line = file_lines[k]
                        if line.strip():  # Only adjust non-empty lines
                            curr_indent = re.match(r"^\s*", line).group(0)
                            content = line[len(curr_indent):]
                            temp_file.write(f"{curr_indent}    {content}")
                        else:
                            temp_file.write(line)
                    
                    # Continue with the rest of the file
                    for k in range(except_line_num, len(file_lines)):
                        temp_file.write(file_lines[k])
                
                # Replace the original file with the modified one
                shutil.move(temp_file.name, MAIN_FILE)
                logging.info(f"Added try statement before line {j}")
                return True
        
        logging.error("Could not find 'return message' line before the problematic except")
        return False
    
    except Exception as e:
        logging.error(f"Failed to add try statement: {e}")
        return False

def main():
    """Main function to fix the syntax error."""
    print("IBM 026 Punch Card Display - Fix Syntax")
    print("------------------------------------")
    
    # Create backup
    if not create_backup():
        print("Failed to create backup. Aborting.")
        return
    
    # Add try statement
    if add_try_before_function():
        print("✅ Successfully added try statement before the problematic except")
    else:
        print("❌ Failed to add try statement")
    
    print("\nYou can now run the main program:")
    print("python3 simple_display.py")
    print("If you encounter issues, you can restore from backup:")
    print(f"cp {MAIN_FILE}{BACKUP_SUFFIX} {MAIN_FILE}")

if __name__ == "__main__":
    main() 