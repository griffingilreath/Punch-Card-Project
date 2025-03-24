#!/usr/bin/env python3
"""
Fix Indentation Script - Fixes the indentation issues in the try-except block around line 557.
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
BACKUP_SUFFIX = ".bak_indent_fix"

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

def fix_indentation():
    """Fix the indentation of the try-except block around line 557."""
    try:
        with open(MAIN_FILE, 'r') as f:
            lines = f.readlines()
        
        # Find the try statement
        try_line = None
        for i, line in enumerate(lines):
            if re.match(r'^\s*try\s*:', line):
                # Check if this try is around line 550
                if 540 <= i <= 560:
                    try_line = i
                    break
        
        if try_line is None:
            logging.error("Could not find the try statement around line 550")
            return False
        
        # Find the indentation level of the try statement
        try_indent = len(re.match(r'^\s*', lines[try_line]).group(0))
        
        # Find the except statement
        except_line = None
        for i in range(try_line + 1, len(lines)):
            if re.match(r'^\s*except\s+', lines[i]):
                except_line = i
                break
        
        if except_line is None:
            logging.error("Could not find the except statement after the try")
            return False
        
        # Check the indentation of the except statement
        except_indent = len(re.match(r'^\s*', lines[except_line]).group(0))
        
        # If the except statement is not properly indented, fix it
        if except_indent != try_indent:
            logging.info(f"Found incorrectly indented except statement at line {except_line+1}")
            
            # Fix the indentation of the except line
            lines[except_line] = ' ' * try_indent + lines[except_line].lstrip()
            
            # Find the end of the except block
            except_block_end = except_line
            for i in range(except_line + 1, len(lines)):
                line_indent = len(re.match(r'^\s*', lines[i]).group(0))
                if line_indent <= try_indent and lines[i].strip():
                    except_block_end = i - 1
                    break
                except_block_end = i
            
            # Fix the indentation of the except block
            for i in range(except_line + 1, except_block_end + 1):
                # Skip empty lines
                if not lines[i].strip():
                    continue
                
                # Get current indentation
                current_indent = len(re.match(r'^\s*', lines[i]).group(0))
                
                # Adjust indentation - ensure it's more than the try/except level
                # but maintain relative indentation within the block
                if current_indent <= try_indent:
                    # If less than or equal to try indent, add standard block indent
                    lines[i] = ' ' * (try_indent + 4) + lines[i].lstrip()
                else:
                    # Keep relative indentation by adding the difference
                    indent_diff = current_indent - except_indent
                    if indent_diff < 0:
                        indent_diff = 0
                    lines[i] = ' ' * (try_indent + 4 + indent_diff) + lines[i].lstrip()
            
            # Write the fixed content back to the file
            with open(MAIN_FILE, 'w') as f:
                f.writelines(lines)
            
            logging.info(f"Fixed indentation in try-except block from line {try_line+1} to {except_block_end+1}")
            return True
        else:
            logging.info("Except statement appears to be properly indented")
            
            # Let's double check the indentation of the entire block
            for i in range(except_line + 1, len(lines)):
                line_indent = len(re.match(r'^\s*', lines[i]).group(0))
                
                # If we've reached a line with less or equal indentation to the except statement,
                # we're no longer in the except block
                if line_indent <= except_indent and lines[i].strip():
                    if i > except_line + 1:  # Ensure we processed at least one line
                        break
                
                # Skip empty lines
                if not lines[i].strip():
                    continue
                
                # The content of the except block should be indented more than the except statement
                if line_indent <= except_indent:
                    logging.info(f"Found incorrect indentation in except block at line {i+1}")
                    
                    # Fix the indentation - add 4 spaces to except indent level
                    lines[i] = ' ' * (except_indent + 4) + lines[i].lstrip()
                    
                    # Remember to write back the changes
                    with open(MAIN_FILE, 'w') as f:
                        f.writelines(lines)
                    
                    logging.info(f"Fixed indentation in except block at line {i+1}")
                    return True
            
            return True
    
    except Exception as e:
        logging.error(f"Failed to fix indentation: {e}")
        return False

def main():
    """Main function to fix indentation."""
    print("IBM 026 Punch Card Display - Fix Indentation")
    print("------------------------------------------")
    
    # Create backup
    if not create_backup():
        print("Failed to create backup. Aborting.")
        return
    
    # Fix indentation
    if fix_indentation():
        print("✅ Successfully fixed indentation in try-except block")
    else:
        print("❌ Failed to fix indentation")
    
    print("\nYou can now run the main program:")
    print("python3 simple_display.py")
    print("If you encounter issues, you can restore from backup:")
    print(f"cp {MAIN_FILE}{BACKUP_SUFFIX} {MAIN_FILE}")

if __name__ == "__main__":
    main() 