#!/usr/bin/env python3
"""
Fix Try-Except Script - Fixes the missing try statement before the except block.
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
BACKUP_SUFFIX = ".bak_try_except_fix"

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

def fix_try_except():
    """Fix the try-except block by adding the missing try statement."""
    try:
        with open(MAIN_FILE, 'r') as f:
            lines = f.readlines()
        
        # Look for patterns to identify the broken try-except block
        # Typically, we'll have "return message" followed by "except Exception as e:"
        return_line = None
        except_line = None
        
        for i, line in enumerate(lines):
            if "return message" in line and 550 <= i <= 560:
                return_line = i
            if "except Exception as e:" in line and 550 <= i <= 570:
                except_line = i
        
        if return_line is None or except_line is None:
            logging.error("Could not find the return message or except line")
            return False
        
        # Check if there's a try statement before the except
        # If not, we need to add it at the beginning of the function
        has_try = False
        for i in range(max(0, return_line - 50), return_line):
            if "try:" in lines[i]:
                has_try = True
                break
        
        if has_try:
            logging.info("Try statement exists, only fixing indentation")
            # The try exists, but there might be indentation issues
            # Fix the except line indentation to match the try
            
            # Get the indentation of the return line (should be same as try block content)
            return_indent = len(lines[return_line]) - len(lines[return_line].lstrip())
            try_indent = max(0, return_indent - 4)  # Try should be 4 spaces less than its content
            
            # Fix the except line
            lines[except_line] = ' ' * try_indent + lines[except_line].lstrip()
            
            # Fix the indentation of everything in the except block
            except_block_indent = try_indent + 4  # Add 4 spaces for the content of except block
            i = except_line + 1
            while i < len(lines):
                # If we find a line with less or equal indentation to the except, we've exited the block
                if lines[i].strip() and len(lines[i]) - len(lines[i].lstrip()) <= try_indent:
                    break
                
                # Fix indentation for non-empty lines
                if lines[i].strip():
                    lines[i] = ' ' * except_block_indent + lines[i].lstrip()
                
                i += 1
        else:
            logging.info("Try statement missing, adding it")
            # Need to completely fix the structure - add a try statement
            
            # Find where to add the try statement - look for function start
            func_start = None
            for i in range(max(0, return_line - 100), return_line):
                if "def generate_message" in lines[i]:
                    func_start = i
                    break
            
            if func_start is None:
                logging.error("Could not find function start")
                return False
            
            # Find the first line with content after the function definition
            # That's where we'll add the try statement
            first_content_line = None
            for i in range(func_start + 1, return_line):
                if lines[i].strip() and not lines[i].strip().startswith("#"):
                    first_content_line = i
                    break
            
            if first_content_line is None:
                logging.error("Could not find first content line after function definition")
                return False
            
            # Get the indentation of the first content line
            first_content_indent = len(lines[first_content_line]) - len(lines[first_content_line].lstrip())
            
            # Add the try statement before the first content
            try_statement = ' ' * first_content_indent + "try:\n"
            lines.insert(first_content_line, try_statement)
            
            # Since we inserted a line, update the indices
            return_line += 1
            except_line += 1
            
            # Adjust indentation for all lines between the try and the return
            for i in range(first_content_line + 1, return_line + 1):
                if lines[i].strip():
                    current_indent = len(lines[i]) - len(lines[i].lstrip())
                    lines[i] = ' ' * (current_indent + 4) + lines[i].lstrip()
            
            # Fix the except line indentation (should be same as try)
            lines[except_line] = ' ' * first_content_indent + lines[except_line].lstrip()
            
            # Fix the indentation of everything in the except block
            except_block_indent = first_content_indent + 4
            i = except_line + 1
            while i < len(lines):
                # If we find a line with less or equal indentation to the except, we've exited the block
                if lines[i].strip() and len(lines[i]) - len(lines[i].lstrip()) <= first_content_indent:
                    break
                
                # Fix indentation for non-empty lines
                if lines[i].strip():
                    lines[i] = ' ' * except_block_indent + lines[i].lstrip()
                
                i += 1
        
        # Now fix any indentation in the except block that may still be wrong
        # We need to make sure everything in the except block is properly indented
        except_line_indent = len(lines[except_line]) - len(lines[except_line].lstrip())
        except_block_indent = except_line_indent + 4
        
        i = except_line + 1
        while i < len(lines):
            # If we find a line with less or equal indentation to the except and it's not empty,
            # we've exited the block
            if lines[i].strip() and len(lines[i]) - len(lines[i].lstrip()) <= except_line_indent:
                break
            
            # Fix indentation for non-empty lines
            if lines[i].strip():
                current_indent = len(lines[i]) - len(lines[i].lstrip())
                if current_indent < except_block_indent:
                    lines[i] = ' ' * except_block_indent + lines[i].lstrip()
            
            i += 1
        
        # Write the fixed content back to the file
        with open(MAIN_FILE, 'w') as f:
            f.writelines(lines)
        
        logging.info(f"Fixed try-except block around line {return_line}")
        return True
    
    except Exception as e:
        logging.error(f"Failed to fix try-except block: {e}")
        return False

def main():
    """Main function to fix the try-except block."""
    print("IBM 026 Punch Card Display - Fix Try-Except")
    print("------------------------------------------")
    
    # Create backup
    if not create_backup():
        print("Failed to create backup. Aborting.")
        return
    
    # Fix try-except block
    if fix_try_except():
        print("✅ Successfully fixed try-except block")
    else:
        print("❌ Failed to fix try-except block")
    
    print("\nYou can now run the main program:")
    print("python3 simple_display.py")
    print("If you encounter issues, you can restore from backup:")
    print(f"cp {MAIN_FILE}{BACKUP_SUFFIX} {MAIN_FILE}")

if __name__ == "__main__":
    main() 